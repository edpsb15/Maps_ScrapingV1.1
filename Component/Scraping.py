import pandas as pd
import random
import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium.webdriver.common.action_chains import ActionChains
import os
import csv
import sys
import re
import glob
# Regex to find latitude and longitude after "3d" and "4d" in the URL

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Fungsi untuk mendapatkan informasi dari Google Maps berdasarkan nama tempat
def get_place_info(place_name, retries=3):
    max_retries = 20 # for long lat 
    retry_delay = 0.5 # in seconds
    options = Options()
    # options.add_argument('--headless')
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")  # Adjust this to simulate scaling
    # options.add_argument("--force-device-scale-factor=0.7")  # 0.7 represents 70% scale
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    
    all_results = []  # Store info for up to five top results

    for attempt in range(retries):
        try:
            driver = webdriver.Chrome(options=options)
            # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            driver.get('https://www.google.com/maps')

            # Find the search box
            search_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'searchboxinput')))
            logging.info(f"Kotak pencarian ditemukan untuk: {place_name}")

            # Enter the place name and press Enter
            search_box.send_keys(place_name)
            search_box.send_keys(webdriver.common.keys.Keys.RETURN)

            try:
                j=1
                while True:
                    # Check for the presence of the first element
                    element_present = driver.find_elements(By.CSS_SELECTOR, '.hfpxzc')

                    # Check for the presence of the second element
                    element_visible = driver.find_elements(By.CSS_SELECTOR, '[data-item-id="address"]')

                    element_rute = driver.find_elements(By.CSS_SELECTOR, '[data-item-id="Rute"]')

                    if element_present or element_visible or element_rute:
                        break
                    
                    # Optional: Wait for a short period before checking again to prevent a tight loop
                    time.sleep(1)
                    if j > 60:
                        break
                    j = j+ 1 

                element_present = driver.find_elements(By.CSS_SELECTOR, '.hfpxzc')
                element_visible = driver.find_elements(By.CSS_SELECTOR, '[data-item-id="address"]')
                element_rute = driver.find_elements(By.CSS_SELECTOR, '[data-item-id="Rute"]')
                # print("error 1")


                if element_present:
                    # print("error 2")
                    search_results = driver.find_elements(By.CSS_SELECTOR, "div[role='feed']>div>div[jsaction]:not([aria-label])")[:5]  # Get up to 5 search results
                    for i, result in enumerate(search_results):
                    # Click on the result
                        result.click()
                        logging.info(f"Mengambil informasi dari hasil pencarian ke-{i + 1} untuk: {place_name}")
                        
                        info = {}

                        # Fetch address
                        try:
                            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-item-id="address"]')))
                            address = driver.find_element(By.CSS_SELECTOR, '[data-item-id="address"]').text
                            info['Address'] = address.strip() if address else "Alamat tidak ditemukan"
                        except:
                            info['Address'] = "Alamat tidak ditemukan"
                            
                        try:
                            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-item-id="address"]')))
                            address = driver.find_element(By.CSS_SELECTOR, '[data-item-id="address"]').text
                            info['Address'] = address.strip() if address else "Alamat tidak ditemukan"
                        except:
                            info['Address'] = "Alamat tidak ditemukan"

                        # Fetch phone number
                        try:
                            phone_element = WebDriverWait(driver, 1).until(
                                EC.visibility_of_element_located((By.XPATH, '//*[@aria-label[contains(.,"Telepon")]]'))
                            )
                            phone_number = phone_element.text.strip() if phone_element.text else "Nomor telepon tidak ditemukan"
                            info['Phone Number'] = phone_number
                            logging.info(f"Nomor telepon ditemukan: {phone_number}")
                        except:
                            info['Phone Number'] = "Nomor telepon tidak ditemukan"

                        # Fetch phone number
                        try:
                            phone_element = WebDriverWait(driver, 1).until(
                                EC.presence_of_element_located((By.XPATH, '//*[@aria-label[contains(.,"Telepon")]]'))
                            )
                            phone_number = phone_element.text.strip() if phone_element.text else "Nomor telepon tidak ditemukan"
                            info['Phone Number'] = phone_number
                            logging.info(f"Nomor telepon ditemukan: {phone_number}")
                        except:
                            info['Phone Number'] = "Nomor telepon tidak ditemukan"

                        # Fetch website
                        try:
                            WebDriverWait(driver, 1).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-item-id="authority"]')))
                            website = driver.find_element(By.CSS_SELECTOR, '[data-item-id="authority"]').get_attribute('href')
                            info['Website'] = website.strip() if website else "Alamat web tidak ditemukan"
                        except:
                            info['Website'] = "Alamat web tidak ditemukan"
                            
                        # Fetch website
                        try:
                            WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-item-id="authority"]')))
                            website = driver.find_element(By.CSS_SELECTOR, '[data-item-id="authority"]').get_attribute('href')
                            info['Website'] = website.strip() if website else "Alamat web tidak ditemukan"
                        except:
                            info['Website'] = "Alamat web tidak ditemukan"

                        try:
                            # Ambil nama tempat
                            WebDriverWait(driver, 1).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'h1.DUwDvf.lfPIob')))
                            actual_place_name = driver.find_element(By.CSS_SELECTOR, 'h1.DUwDvf.lfPIob').text
                            info['Actual Place Name'] = actual_place_name.strip() if actual_place_name else "Nama tempat tidak ditemukan"
                            logging.info(f"Nama tempat yang diambil: {actual_place_name}")
                        except Exception as e:
                            info['Actual Place Name'] = "Nama tempat tidak ditemukan"
                            logging.error(f"Error saat mengambil nama tempat: {e}")
                            
                        try:
                            # Ambil nama tempat
                            WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.DUwDvf.lfPIob')))
                            actual_place_name = driver.find_element(By.CSS_SELECTOR, 'h1.DUwDvf.lfPIob').text
                            info['Actual Place Name'] = actual_place_name.strip() if actual_place_name else "Nama tempat tidak ditemukan"
                            logging.info(f"Nama tempat yang diambil: {actual_place_name}")
                        except Exception as e:
                            info['Actual Place Name'] = "Nama tempat tidak ditemukan"
                            logging.error(f"Error saat mengambil nama tempat: {e}")

                        # Fetch latitude and longitude from URL

                        for attempt in range(max_retries):
                            try:
                                url = driver.current_url
                                matches = re.findall(r"3d(-?\d+\.\d+)!4d(-?\d+\.\d+)", url)
                                
                                if matches:
                                    latitude, longitude = matches[0]
                                    info['Latitude'] = latitude
                                    info['Longitude'] = longitude
                                    break  # Exit the loop once successful
                                else:
                                    info['Latitude'] = "Latitude not found"
                                    info['Longitude'] = "Longitude not found"
                                
                            except Exception as e:
                                info['Latitude'] = "Latitude not found"
                                info['Longitude'] = "Longitude not found"
                            
                            time.sleep(retry_delay)  # Wait before retrying
                        else:
                            # If loop completes without breaking, log final message
                            print("Failed to retrieve latitude and longitude after multiple attempts.")

                        # Fetch place type
                        try:
                            place_type_button = driver.find_element(By.CSS_SELECTOR, 'button.DkEaL')
                            place_type = place_type_button.text
                            info['Place Type'] = place_type.strip() if place_type else "Jenis tempat tidak ditemukan"
                        except:
                            info['Place Type'] = "Jenis tempat tidak ditemukan"

                        # Fetch latest review and review date
                        # Klik tombol "Ulasan" dan ambil ulasan terbaru
                        try:
                            review_button = WebDriverWait(driver, 3).until(
                                EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Ulasan')]"))
                            )
                            driver.execute_script("arguments[0].click();", review_button)
                            logging.info(f"Bagian ulasan ditemukan dan diklik untuk: {place_name}")

                            # Tunggu hingga ulasan terbaru dimuat
                            try:
                                WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.wiI7pd')))
                                logging.info(f"Ulasan telah dimuat untuk: {place_name}")
                            except:
                                try:
                                    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.wiI7pd')))
                                    logging.info(f"Ulasan telah dimuat untuk: {place_name}")
                                except:
                                    logging.info(f"Ulasan gagal dimuat untuk: {place_name}")

                            # Coba klik tombol urutkan ulasan
                            try:
                                urutkan_button = WebDriverWait(driver, 10).until(
                                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Urutkan ulasan"]'))
                                )
                                logging.info("Tombol urutkan ulasan diklik")
                            except Exception as e:
                                # Jika tombol "Urutkan ulasan" tidak ditemukan, coba "Paling relevan"
                                urutkan_button = WebDriverWait(driver, 10).until(
                                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Paling relevan"]'))
                                )
                                logging.info("Tombol 'Paling relevan' diklik")

                            urutkan_button.click()

                            # Pilih opsi 'Terbaru'
                            try:
                                terbaru_option = WebDriverWait(driver, 10).until(
                                    EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[data-index="1"]'))
                                )
                                logging.info("Tombol urutkan terbaru diklik")
                                ActionChains(driver).move_to_element(terbaru_option).click().perform()
                                # Tunggu sampai elemen ulasan terbaru dimuat
                                WebDriverWait(driver, 20).until(
                                    EC.visibility_of_element_located((By.CSS_SELECTOR, '.wiI7pd'))
                                )
                                logging.info(f"Ulasan telah dimuat untuk: {place_name}")
                            except:
                                try:
                                    terbaru_option = WebDriverWait(driver, 10).until(
                                        EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-index="1"]'))
                                    )
                                    logging.info("Tombol urutkan terbaru diklik")
                                    ActionChains(driver).move_to_element(terbaru_option).click().perform()
                                    # Tunggu sampai elemen ulasan terbaru dimuat
                                    WebDriverWait(driver, 20).until(
                                        EC.presence_of_element_located((By.CSS_SELECTOR, '.wiI7pd'))
                                    )
                                    logging.info(f"Ulasan telah dimuat untuk: {place_name}")
                                except:
                                    logging.info(f"Ulasan gagal dimuat untuk: {place_name}")
                            # Ambil ulasan terbaru
                            
                            try:
                                time.sleep(5)
                                # review_text = driver.find_element(By.XPATH,f".//span[{cl_templ.format(c=text_span_class)}]").text
                                latest_review = driver.find_element(By.CSS_SELECTOR, '.wiI7pd').text
                                info['Latest Review'] = latest_review.strip() if latest_review else "Ulasan tidak ditemukan"
                            except Exception as e:
                                info['Latest Review'] = "Ulasan tidak ditemukan"
                                logging.error(f"Error saat mengambil ulasan terbaru: {e}")

                            try:
                                try:
                                    review_date = driver.find_element(By.CSS_SELECTOR, '.rsqaWe').text
                                except:
                                    review_date = driver.find_element(By.CSS_SELECTOR, '.xRkPPb').text
                                info['Review Date'] = review_date.strip() if review_date else "Tanggal tidak ditemukan"
                            except Exception as e:
                                info['Review Date'] = "Tanggal tidak ditemukan"
                                logging.error(f"Error saat mengambil tanggal ulasan: {e}")

                        except Exception as e:
                            logging.error(f"Bagian ulasan tidak ditemukan atau gagal diklik untuk: {place_name}. Error: {e}")
                            info['Latest Review'] = "Tidak ada review"
                            info['Review Date'] = "Tidak ada review"

                        all_results.append({'Place': place_name, **info})

                        # Go back to the search results page to select the next result
                        # driver.back()
                        # WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.hfpxzc')))

                    driver.quit()
                    return all_results  # Return top 5 results or however many were gathered
                
                elif element_visible:
                    # print("error 3")
                    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-item-id="address"]')))
                    info = {}
                    # Ambil alamat
                    try:
                        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-item-id="address"]')))
                        address = driver.find_element(By.CSS_SELECTOR, '[data-item-id="address"]').text
                        info['Address'] = address.strip() if address else "Alamat tidak ditemukan"
                    except:
                        info['Address'] = "Alamat tidak ditemukan"
                        
                    try:
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-item-id="address"]')))
                        address = driver.find_element(By.CSS_SELECTOR, '[data-item-id="address"]').text
                        info['Address'] = address.strip() if address else "Alamat tidak ditemukan"
                    except:
                        info['Address'] = "Alamat tidak ditemukan"

                    # Fetch phone number
                    try:
                        phone_element = WebDriverWait(driver, 1).until(
                            EC.visibility_of_element_located((By.XPATH, '//*[@aria-label[contains(.,"Telepon")]]'))
                        )
                        phone_number = phone_element.text.strip() if phone_element.text else "Nomor telepon tidak ditemukan"
                        info['Phone Number'] = phone_number
                        logging.info(f"Nomor telepon ditemukan: {phone_number}")
                    except:
                        info['Phone Number'] = "Nomor telepon tidak ditemukan"

                    # Fetch phone number
                    try:
                        phone_element = WebDriverWait(driver, 1).until(
                            EC.presence_of_element_located((By.XPATH, '//*[@aria-label[contains(.,"Telepon")]]'))
                        )
                        phone_number = phone_element.text.strip() if phone_element.text else "Nomor telepon tidak ditemukan"
                        info['Phone Number'] = phone_number
                        logging.info(f"Nomor telepon ditemukan: {phone_number}")
                    except:
                        info['Phone Number'] = "Nomor telepon tidak ditemukan"

                    # Fetch website
                    try:
                        WebDriverWait(driver, 1).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-item-id="authority"]')))
                        website = driver.find_element(By.CSS_SELECTOR, '[data-item-id="authority"]').get_attribute('href')
                        info['Website'] = website.strip() if website else "Alamat web tidak ditemukan"
                    except:
                        info['Website'] = "Alamat web tidak ditemukan"
                        
                    # Fetch website
                    try:
                        WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-item-id="authority"]')))
                        website = driver.find_element(By.CSS_SELECTOR, '[data-item-id="authority"]').get_attribute('href')
                        info['Website'] = website.strip() if website else "Alamat web tidak ditemukan"
                    except:
                        info['Website'] = "Alamat web tidak ditemukan"

                    try:
                        # Ambil nama tempat
                        WebDriverWait(driver, 1).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'h1.DUwDvf.lfPIob')))
                        actual_place_name = driver.find_element(By.CSS_SELECTOR, 'h1.DUwDvf.lfPIob').text
                        info['Actual Place Name'] = actual_place_name.strip() if actual_place_name else "Nama tempat tidak ditemukan"
                        logging.info(f"Nama tempat yang diambil: {actual_place_name}")
                    except Exception as e:
                        info['Actual Place Name'] = "Nama tempat tidak ditemukan"
                        logging.error(f"Error saat mengambil nama tempat: {e}")
                        
                    try:
                        # Ambil nama tempat
                        WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.DUwDvf.lfPIob')))
                        actual_place_name = driver.find_element(By.CSS_SELECTOR, 'h1.DUwDvf.lfPIob').text
                        info['Actual Place Name'] = actual_place_name.strip() if actual_place_name else "Nama tempat tidak ditemukan"
                        logging.info(f"Nama tempat yang diambil: {actual_place_name}")
                    except Exception as e:
                        info['Actual Place Name'] = "Nama tempat tidak ditemukan"
                        logging.error(f"Error saat mengambil nama tempat: {e}")

                    # Fetch latitude and longitude from URL

                    for attempt in range(max_retries):
                        try:
                            url = driver.current_url
                            matches = re.findall(r"3d(-?\d+\.\d+)!4d(-?\d+\.\d+)", url)
                            
                            if matches:
                                latitude, longitude = matches[0]
                                info['Latitude'] = latitude
                                info['Longitude'] = longitude
                                break  # Exit the loop once successful
                            else:
                                info['Latitude'] = "Latitude not found"
                                info['Longitude'] = "Longitude not found"
                            
                        except Exception as e:
                            info['Latitude'] = "Latitude not found"
                            info['Longitude'] = "Longitude not found"
                        
                        time.sleep(retry_delay)  # Wait before retrying
                    else:
                        # If loop completes without breaking, log final message
                        print("Failed to retrieve latitude and longitude after multiple attempts.")

                    # Fetch place type
                    try:
                        place_type_button = driver.find_element(By.CSS_SELECTOR, 'button.DkEaL')
                        place_type = place_type_button.text
                        info['Place Type'] = place_type.strip() if place_type else "Jenis tempat tidak ditemukan"
                    except:
                        info['Place Type'] = "Jenis tempat tidak ditemukan"

                    # Fetch latest review and review date
                    # Klik tombol "Ulasan" dan ambil ulasan terbaru
                    try:
                        review_button = WebDriverWait(driver, 3).until(
                            EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Ulasan')]"))
                        )
                        driver.execute_script("arguments[0].click();", review_button)
                        logging.info(f"Bagian ulasan ditemukan dan diklik untuk: {place_name}")

                        # Tunggu hingga ulasan terbaru dimuat
                        try:
                            WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.wiI7pd')))
                            logging.info(f"Ulasan telah dimuat untuk: {place_name}")
                        except:
                            try:
                                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.wiI7pd')))
                                logging.info(f"Ulasan telah dimuat untuk: {place_name}")
                            except:
                                logging.info(f"Ulasan gagal dimuat untuk: {place_name}")

                        # Coba klik tombol urutkan ulasan
                        try:
                            urutkan_button = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Urutkan ulasan"]'))
                            )
                            logging.info("Tombol urutkan ulasan diklik")
                        except Exception as e:
                            # Jika tombol "Urutkan ulasan" tidak ditemukan, coba "Paling relevan"
                            urutkan_button = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Paling relevan"]'))
                            )
                            logging.info("Tombol 'Paling relevan' diklik")

                        urutkan_button.click()

                        # Pilih opsi 'Terbaru'
                        try:
                            terbaru_option = WebDriverWait(driver, 10).until(
                                EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[data-index="1"]'))
                            )
                            logging.info("Tombol urutkan terbaru diklik")
                            ActionChains(driver).move_to_element(terbaru_option).click().perform()
                            # Tunggu sampai elemen ulasan terbaru dimuat
                            WebDriverWait(driver, 20).until(
                                EC.visibility_of_element_located((By.CSS_SELECTOR, '.wiI7pd'))
                            )
                            logging.info(f"Ulasan telah dimuat untuk: {place_name}")
                        except:
                            try:
                                terbaru_option = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-index="1"]'))
                                )
                                logging.info("Tombol urutkan terbaru diklik")
                                ActionChains(driver).move_to_element(terbaru_option).click().perform()
                                # Tunggu sampai elemen ulasan terbaru dimuat
                                WebDriverWait(driver, 20).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, '.wiI7pd'))
                                )
                                logging.info(f"Ulasan telah dimuat untuk: {place_name}")
                            except:
                                logging.info(f"Ulasan gagal dimuat untuk: {place_name}")
                        # Ambil ulasan terbaru
                        
                        try:
                            time.sleep(5)
                            # review_text = driver.find_element(By.XPATH,f".//span[{cl_templ.format(c=text_span_class)}]").text
                            latest_review = driver.find_element(By.CSS_SELECTOR, '.wiI7pd').text
                            info['Latest Review'] = latest_review.strip() if latest_review else "Ulasan tidak ditemukan"
                        except Exception as e:
                            info['Latest Review'] = "Ulasan tidak ditemukan"
                            logging.error(f"Error saat mengambil ulasan terbaru: {e}")

                        try:
                            try:
                                review_date = driver.find_element(By.CSS_SELECTOR, '.rsqaWe').text
                            except:
                                review_date = driver.find_element(By.CSS_SELECTOR, '.xRkPPb').text
                            info['Review Date'] = review_date.strip() if review_date else "Tanggal tidak ditemukan"
                        except Exception as e:
                            info['Review Date'] = "Tanggal tidak ditemukan"
                            logging.error(f"Error saat mengambil tanggal ulasan: {e}")

                    except Exception as e:
                        logging.error(f"Bagian ulasan tidak ditemukan atau gagal diklik untuk: {place_name}. Error: {e}")
                        info['Latest Review'] = "Tidak ada review"
                        info['Review Date'] = "Tidak ada review"

                    # print("sampai_sini_1")
                    # Membersihkan hasil alamat dari karakter aneh
                    if 'Address' in info:
                        info['Address'] = info['Address'].replace('\ue0c8', '').strip()
                    if 'Phone Number' in info:
                        info['Phone Number'] = info['Phone Number'].replace('', '').replace('\ue0c8', '').strip()
                    # print("sampai_sini_2")
                    driver.quit()
                    return {'Place': place_name, **info}

                elif element_rute:
                    print(f"Tidak ada nama tempat {place_name}")
                    return [{'Place': place_name, 'Address': 'Tempat tidak ada', 'Phone Number': 'Tempat tidak ada', 'Website': 'Tempat tidak ada','Actual Place Name' : 'Tempat tidak ada' , 'Latitude': 'Tempat tidak ada', 'Longitude': 'Tempat tidak ada', 'Place Type': 'Tempat tidak ada', 'Latest Review': 'Tempat tidak ada', 'Review Date': 'Tempat tidak ada'}]
                else :
                    logging.error(f"Gagal mengambil informasi untuk {place_name} setelah {retries} percobaan.")
                    return [{'Place': place_name, 'Address': 'Gagal', 'Phone Number': 'Gagal', 'Website': 'Gagal', 'Actual Place Name' : 'Gagal' , 'Latitude': 'Gagal', 'Longitude': 'Gagal', 'Place Type': 'Gagal','Latest Review': 'Gagal', 'Review Date': 'Gagal'}]

            except:
                logging.error(f"Error saat mengambil informasi untuk {place_name} (percobaan {attempt + 1}): {e}")
                print(f"Error saat mengambil informasi untuk {place_name} (percobaan {attempt + 1}): {e}")

        
        except Exception as e:
            logging.error(f"Error saat mengambil informasi untuk {place_name} (percobaan {attempt + 1}): {e}")
            print(f"Error saat mengambil informasi untuk {place_name} (percobaan {attempt + 1}): {e}")
            driver.quit()

        if attempt < retries - 1:
            print(f"Retrying {place_name}... (attempt {attempt + 2})")
            logging.info(f"Retrying {place_name}... (attempt {attempt + 2})")
            time.sleep(random.randint(1, 3))  # Small delay before retry

    print(f"Gagal mengambil informasi untuk {place_name} setelah {retries} percobaan.")
    logging.error(f"Gagal mengambil informasi untuk {place_name} setelah {retries} percobaan.")
    return [{'Place': place_name, 'Address': 'Gagal','Phone Number': 'Gagal', 'Website': 'Gagal', 'Actual Place Name' : 'Gagal',  'Latitude': 'Gagal', 'Longitude': 'Gagal', 'Place Type': 'Gagal', 'Latest Review': 'Gagal', 'Review Date': 'Gagal'}]


# Fungsi utama untuk menjalankan scraping untuk semua tempat
def mulai_scraping(kelurahan_kotor,desa_name,nama_kec,nama_kab,nama_des,kd_gabungan):
    print(f"Mulai proses scraping dengan file: {kelurahan_kotor}")
    places_df = pd.read_csv(kelurahan_kotor,header=None, encoding='ISO-8859-1')
    #fungsi cleaning + fungsi tambah nama kecamatan dan kabupaten

    # Path to the CSV file and Excel file
    csv_file_path = f"Output/Scraping/{kd_gabungan[:-3]}/{kd_gabungan}.csv"
    os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)

    excel_file_path = f"Output/Scraping/{kd_gabungan[:-3]}/{kd_gabungan}.xlsx"

    # Menghitung jumlah kemunculan setiap nilai dari kolom pertama
    value_counts = places_df[0].value_counts()

    # Memfilter nilai yang kemunculannya kurang dari 4
    below_4 = value_counts[value_counts < 4]
    # Mengatur indeks dan memfilter berdasarkan panjang string
    below_4 = below_4.reset_index()
    below_4 = below_4[below_4[0].str.len() > 3]
    below_4[0] = below_4[0].str.replace(r'[^a-zA-Z0-9\s]', '', regex=True)
    below_4[0] = below_4[0].replace('0', 'O').replace('1', 'I').replace('5', 'S')

    # Menggunakan 'index' dari below_4 untuk scraping
    #places_to_scrape = below_4[0].tolist()  # Mengonversi ke list untuk digunakan dalam scraping

    # Mengonversi ke list dan menambahkan nama_kec dan nama_des
    places_to_scrape = [f"{place} {desa_name} ,kecamatan {nama_kec}, {nama_kab} " for place in below_4[0].tolist()]

    print(f'Jumlah query yang dicari{len(places_to_scrape)}')

    results = []

    #Mendapatkan path ke folder MAPS_SCRAPING secara dinamis
    base_path = os.path.dirname(os.path.abspath(__file__))

    # Nama file input, misalnya 'Desa_OK_Terakhir.csv'
    input_file_name = os.path.basename(kelurahan_kotor)  # kecamatan_kotor adalah path file input CSV
    input_name_only = os.path.splitext(input_file_name)[0]  # Menghilangkan ekstensi .csv

    # Membuat nama file output dengan nama file input + 'scraping'
    output_file_name = f"{input_name_only}_scraping.xlsx"
    output_file_path = os.path.join(base_path, '..', 'Output', 'Scraping', output_file_name)
    save_file_path = os.path.join(base_path, '..', 'save',kd_gabungan[:-3], f"{kd_gabungan}_2_1.txt")
    save_file_path_selesai = os.path.join(base_path, '..','save', kd_gabungan[:-3], f"{kd_gabungan}_2_2.txt")

    # Load saved progress from file
    completed_places = set()
    if os.path.exists(save_file_path):
        with open(save_file_path, 'r') as file:
            completed_places = set(line.strip() for line in file.readlines())

    # Menggunakan ThreadPoolExecutor untuk menjalankan scraping secara paralel
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {}

        # Submit tasks, skipping already-completed places
        for place in places_to_scrape:
            if place in completed_places:
                print(f"Skipping {place} (already processed)")
                continue

            # Submit task and track it with futures
            future = executor.submit(get_place_info, place)
            futures[future] = place

        for future in as_completed(futures):
            place = futures[future]

            try:
                result = future.result()
                # Check if result is a dictionary

                if isinstance(result, dict):
                    results.append(result)  # Append the single dictionary
                elif isinstance(result, list):
                    results.extend(result)  # Extend results with the list of dictionaries
                
                # i += 1
                with open(save_file_path, 'a') as file:
                    file.write(f"{place}\n")
                # print(csv_file_path)
                # print(results)
                # Determine if the header is needed (write it only once)
                write_header = not os.path.isfile(csv_file_path)
                # Write the current result to CSV with header only if the file doesn't exist
                pd.DataFrame([result] if isinstance(result, dict) else result).to_csv(
                    csv_file_path, mode='a', sep='|', header=write_header, index=False
                )
                print(f"Berhasil mengambil {place}")
                logging.info(f"Tempat: {place}, Informasi: {result}\n")
            except Exception as e:
                logging.error(f"Error saat mengambil informasi untuk {place}: {e}")
    # Validasi apakah ada hasil scraping
    if results:
        print("Data yang berhasil diambil:", results)
    else:
        print("Tidak ada data yang diambil.")
    # Menyimpan DataFrame ke file Excel pada path yang ditentukan
    results_df =  pd.read_csv(csv_file_path, delimiter='|')
    
    results_df.to_excel(excel_file_path, index=False)
    os.rename(save_file_path, save_file_path_selesai)  # Tandai proses OCR selesai
    logging.info(f"Informasi tempat telah disimpan ke {excel_file_path}")

def mulai_scraping_2(input1, kd_gabungan):
    if input1=='All':
        #Baca satu satu file excel 
        kd_gabungan = kd_gabungan
        excel_file_path = f"Output/Scraping/"
        print(excel_file_path)
        excel_file_path = glob.glob(os.path.join(excel_file_path, f'{kd_gabungan[:4]}*', '*.xlsx'), recursive=True)
        print(excel_file_path)
        # Baca setiap file Excel dan tambahkan ke list
        for file_path in excel_file_path:
            print(file_path)
            df = pd.read_excel(file_path)
            # Create a new DataFrame with rows where 'Actual Place Name' is "Gagal"
            df_new = df[df['Actual Place Name'] == "Gagal"].copy()

            # Optionally, drop those rows from the original DataFrame if you want to remove them
            df = df[df['Actual Place Name'] != "Gagal"]

            results = []

            # Menggunakan ThreadPoolExecutor untuk menjalankan scraping secara paralel
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = {executor.submit(get_place_info, place): place for place in df_new['Place'] if place}
                
                for future in as_completed(futures):
                    place = futures[future]
                    try:
                        result = future.result()
                        print(result)
                        if isinstance(result, dict):
                            results.append(result)  # Append the single dictionary
                        elif isinstance(result, list):
                            results.extend(result)  # Extend results with the list of dictionaries
                        logging.info(f"Tempat: {place}, Informasi: {result}\n")
                        print(f"Update berhasil untuk mengambil {place}")
                    except Exception as e:
                        logging.error(f"Error saat mengambil informasi untuk {place}: {e}")
            results_df = pd.DataFrame(results)
            results_df = pd.concat([df, results_df], ignore_index=True)
            # excel_file_path = f"Output/Scraping/"
            # updated_excel = os.path.join(excel_file_path, f'{kd_gabungan[:-3]}',f'{kd_gabungan}.xlsx')

            results_df.to_excel(file_path, index=False)

        excel_file_path = f"Output/Scraping/"
        excel_file_path = glob.glob(os.path.join(excel_file_path, f'{kd_gabungan[:4]}*', '*.xlsx'), recursive=True)
        
        excel_file_path_all = f"Output/Scraping/{kd_gabungan[:4]}.xlsx"

        
        # List untuk menyimpan DataFrames dari masing-masing file
        dataframes = []

        # Baca setiap file Excel dan tambahkan ke list
        for file_path in excel_file_path:
            df = pd.read_excel(file_path)
            dataframes.append(df)

        # Gabungkan semua DataFrame
        combined_df = pd.concat(dataframes, ignore_index=True)

        # Simpan hasil gabungan ke file baru
        combined_df.to_excel(excel_file_path_all, index=False)
        
        print(f"Update berhasil untuk kelurahan {kd_gabungan}")
        
    else :
        #Baca satu satu file excel 
        excel_file_path = f"Output/Scraping/"
        excel_file_path = os.path.join(excel_file_path, input1[:-3], f'{input1}.xlsx')

        # Baca setiap file Excel dan tambahkan ke list
        df = pd.read_excel(excel_file_path)
        # Create a new DataFrame with rows where 'Actual Place Name' is "Gagal"
        df_new = df[df['Actual Place Name'] == "Gagal"].copy()

        # Optionally, drop those rows from the original DataFrame if you want to remove them
        df = df[df['Actual Place Name'] != "Gagal"]
        
        print(f'banyak tempat gagal{len(df_new)}')

        results = []

        # Menggunakan ThreadPoolExecutor untuk menjalankan scraping secara paralel
        with ThreadPoolExecutor(max_workers=None) as executor:
            futures = {executor.submit(get_place_info, place): place for place in df_new['Place'] if place}
            
            for future in as_completed(futures):
                place = futures[future]
                try:
                    result = future.result()
                    print(result)
                    logging.info(result)
                    if isinstance(result, dict):
                        results.append(result)  # Append the single dictionary
                    elif isinstance(result, list):
                        results.extend(result)  # Extend results with the list of dictionaries
                    logging.info(f"Tempat: {place}, Informasi: {result}\n")
                    print(f"Update berhasil untuk mengambil {place}")
                except Exception as e:
                    logging.error(f"Error saat mengambil informasi untuk {place}: {e}")
                    
        results_df = pd.DataFrame(results)
        results_df = pd.concat([df, results_df], ignore_index=True)
        excel_file_path = f"Output/Scraping/"
        updated_excel = os.path.join(excel_file_path, f'{input1[:-3]}',f'{input1}.xlsx')
        results_df.to_excel(updated_excel, index=False)
        print(f"Update berhasil untuk kelurahan {input1}")
        
        


