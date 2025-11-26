import time
import random
import os
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import sys
from paddleocr import PaddleOCR, draw_ocr
from Component import OCR
from Component import Scraping
import csv
from pathlib import Path
import glob

# Mendapatkan path ke folder MAPS_SCRAPING secara dinamis
# import Scraping

base_path = os.path.dirname(os.path.abspath(__file__))  # Path ke folder skrip saat ini
ocr_model = PaddleOCR(lang='id',det_box_type='quad', max_text_length=50, det_db_thresh=0.3, det_db_box_thresh=0.6, scales = [4, 8, 16, 32, 64], layout=True,det_limit_side_len=1920) #(lang='id', det_box_type='poly', max_text_length=50, min_subgraph_size=30)
output_path = os.path.join(base_path, '..', 'Output', 'OCR')  # Path ke folder OCR

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--kiosk")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--log-level=3")  # Reduce logging


# chrome_options.add_argument("user-data-dir=C:\\Users\\Acer\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 1")  # Adjust the path
driver = webdriver.Chrome(options=chrome_options)
driver.implicitly_wait(86400)

# Function to open Google Maps at a specific latitude, longitude
def open_google_maps(lat, lon, zoom=20.8, retries=4):
    google_maps_url = f"https://www.google.com/maps/@{lat},{lon},{zoom}z/data=!5m1!1e4"
    for attempt in range(retries):
        driver.get(google_maps_url)
        try:
            WebDriverWait(driver,60).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'canvas')))
            print(f"Page loaded successfully on attempt {attempt + 1}")
            break  # Exit the loop if the page loads successfully
        except Exception as e:
            print(f"Request Timed Out on attempt {attempt + 1}: {e}")
            if attempt < retries - 1:
                print("Refreshing the page...")
                driver.refresh()  # Refresh the page if it's not the last retry
            else:
                print("Failed after maximum retries")
            
# Fungsi untuk mengambil screenshot
def capture_screenshot(filename, nmkec, nmdesa, folder_path=None):
    if folder_path is None:
        # Buat path folder berdasarkan nmkec dan nmdesa
        folder_path = os.path.join(base_path, '..', 'Output', 'Screenshoot', nmkec, nmdesa)
        
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)  # Membuat struktur folder jika belum ada
        
    file_path = os.path.join(folder_path, filename)
    driver.save_screenshot(file_path)
    return file_path  # Kembalikan path file untuk digunakan nanti

# Function to check if a point is inside the polygon for the current kelurahan
def is_point_in_polygon(lat, lon, polygon):
    point = Point(lon, lat)  # Note that Point takes (longitude, latitude)
    return polygon.contains(point)

# Optimized function to slide and capture screenshots within the polygon boundaries
def slide_and_capture(ocr_models,kecamatan_name, desa_name, kdgab, polygon, bottom_left, top_right, save_file_ss_ocr_2, step_x=0.001, step_y=0.0018):
    current_lat, current_lon = bottom_left
    step_lat = step_x
    step_lon = step_y
    #output_path = os.path.join(base_path, '..', '..', 'Output', 'OCR')  # Path ke folder OCR
    # save_file_ss_ocr_2
    i=0
    if os.path.exists(save_file_ss_ocr_2):
        with open(save_file_ss_ocr_2, 'r') as file:
            content = file.read()  # Reads the entire content of the file
            content = int(content)
    else:
        print("File does not exist.")
    # i=1
    while current_lat <= top_right[0]:
        while current_lon <= top_right[1]:
            # Check if the current point is inside the polygon
            if is_point_in_polygon(current_lat, current_lon, polygon) :
                if i >= content:
                    open_google_maps(current_lat, current_lon)
                    capture_screenshot(f"{kecamatan_name}_{desa_name}_screenshot_{current_lat}_{current_lon}.png", kecamatan_name, desa_name)
                    file_name = f"{kecamatan_name}_{desa_name}_screenshot_{current_lat}_{current_lon}.png"
                    image_path = capture_screenshot(file_name, kecamatan_name, desa_name)
                    #Fungsi manggil OCR
                    combined_box = OCR.process_image_file(image_path,ocr_models)
                    # Ubah nama file CSV berdasarkan nama kecamatan
                    file_path = os.path.join(output_path, kdgab[:-3], f"{kdgab}_data.csv")
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Create only the directory part
                    with open(file_path, 'a', newline='') as file:
                        writer = csv.writer(file)
                        for item in combined_box:
                            # print([item])
                            writer.writerow([item])  # Write each element in a new row
                    print(f"Berhasil Screenshoot Kecamatan : {kecamatan_name}, Desa/Kelurahan: {desa_name}, ini screenshoot-ke: {content}")
                    time.sleep(random.uniform(3, 4))
                    i += 1
                    content +=1
                    with open(save_file_ss_ocr_2, 'w') as file:
                        file.write(str(content))  # Writes '0' only if the file doesn't exist
                    # time.sleep(random.uniform(3, 6))
                else:
                    print(f"Skip screenshoot ke-{i}")
                    i +=1
            current_lon += step_lon

            if current_lon > top_right[1]:
                break
        current_lon = bottom_left[1]  # Reset longitude for the next row
        current_lat += step_lat

        if current_lat > top_right[0]:
            break

# Loop through each kecamatan in the GeoDataFrame and process the coordinates
# i=1

def start_screenshoot(input_1, update_progress_callback=None):
    # Tentukan path ke file input GeoJSON yang berisi data desa

    inputan_directory = os.path.join(base_path, '..', 'Inputan', 'Desa')

    json_files_path = os.path.join(inputan_directory, '*.json')

    # Get the list of all JSON files in the specified directory
    inputan_path = glob.glob(json_files_path) 

    # Tentukan path untuk menyimpan file hasil
    save_path = os.path.join(base_path, '..', 'save')

    # Muat file GeoJSON yang berisi data poligon desa
    gdf = gpd.read_file(inputan_path[0])  # Menggunakan 'inputan_path' sebagai variabel path file
    gdf = gdf.sort_values(by='iddesa',ascending=True)

    # Inisialisasi nama kecamatan
    kecamatan_name = None

    #cek apkah kabupaten itu sudah selesai
    # Tentukan path untuk file status proses OCR
    cek_all = os.path.join(save_path,f'scraping_kabupaten_{gdf.iloc[0]['nmkab']}_selesai.txt')
    os.makedirs(os.path.dirname(cek_all), exist_ok=True)  # Buat direktori jika belum ada

    # Loop melalui setiap baris dalam file GeoJSON
    for index, row in gdf.iterrows():
        # Ambil informasi nama kecamatan, desa, kabupaten, dan kode gabungan
        kecamatan_name = row['nmkec']
        desa_name = row['nmdesa']
        kab_name = row['nmkab']
        kd_gabungan = str(row['kdprov']) + str(row['kdkab']) + str(row['kdkec']) + str(row['kddesa'])

        # Dapatkan geometri poligon untuk wilayah saat ini
        polygon = row['geometry']
        bounds = polygon.bounds  # Mendapatkan batas (min_lon, min_lat, max_lon, max_lat)
        bottom_left = (bounds[1], bounds[0])  # Sudut kiri bawah
        top_right = (bounds[3], bounds[2])    # Sudut kanan atas

        # Tentukan path untuk file status proses OCR
        save_file_ss_ocr = os.path.join(save_path, kd_gabungan[:-3], f"{kd_gabungan}_1_1.txt")
        os.makedirs(os.path.dirname(save_file_ss_ocr), exist_ok=True)  # Buat direktori jika belum ada

        # Tentukan path untuk file status OCR selesai
        save_file_ss_selesai = os.path.join(save_path, kd_gabungan[:-3], f"{kd_gabungan}_1_2.txt")
        save_file_scraping_selesai = os.path.join(save_path, kd_gabungan[:-3], f"{kd_gabungan}_2_2.txt")
        
        # Cek apakah proses scraping belum selesai
        if not os.path.exists(save_file_scraping_selesai):
            if input_1 == "All":
                # Jalankan proses jika OCR belum selesai
                if not os.path.exists(save_file_ss_selesai):
                    if not os.path.exists(save_file_ss_ocr):
                        # Buat file status OCR jika belum ada dan isi dengan '0'
                        with open(save_file_ss_ocr, 'w') as file:
                            file.write('0')
                    
                    # Jalankan fungsi slide_and_capture untuk OCR
                    slide_and_capture(ocr_model, kecamatan_name, desa_name, kd_gabungan, polygon, bottom_left, top_right, save_file_ss_ocr)
                    os.rename(save_file_ss_ocr, save_file_ss_selesai)  # Tandai OCR selesai
                    if update_progress_callback:
                        update_progress_callback()
                    # Siapkan path untuk file scraping belum selesai
                    save_file_scraping = os.path.join(save_path, kd_gabungan[:-3], f"{kd_gabungan}_2_1.txt")
                    os.makedirs(os.path.dirname(save_file_scraping), exist_ok=True)

                    # Buat file status scraping jika belum ada
                    if not os.path.exists(save_file_scraping):
                        with open(save_file_scraping, 'w') as file:
                            file.write('')
                            
                else:
                    # Jika OCR selesai, mulai proses scraping
                    print("SKIP Screenshoot dan OCR karena telah selesai")

                # Cek apakah file CSV untuk scraping sudah dibuat
                file_path = os.path.join(output_path, kd_gabungan[:-3], f"{kd_gabungan}_data.csv")
                if os.path.exists(file_path):
                    print("File CSV ditemukan, mulai scraping...")
                    Scraping.mulai_scraping(file_path, desa_name, kecamatan_name, kab_name, desa_name, kd_gabungan,)
                    print(f"Scraping untuk kelurahan {desa_name} telah selesai")
                    if update_progress_callback:
                        update_progress_callback()

            else:
                # Jalankan proses untuk kode tertentu jika 'input_1' bukan 'All'
                if kd_gabungan == input_1:
                    if not os.path.exists(save_file_ss_selesai):
                        if not os.path.exists(save_file_ss_ocr):
                            # Buat file OCR jika belum ada
                            with open(save_file_ss_ocr, 'w') as file:
                                file.write('0')
                        
                        # Jalankan proses slide_and_capture OCR
                        slide_and_capture(ocr_model, kecamatan_name, desa_name, kd_gabungan, polygon, bottom_left, top_right, save_file_ss_ocr)
                        os.rename(save_file_ss_ocr, save_file_ss_selesai)
                        if update_progress_callback:
                            update_progress_callback()

                        # Siapkan path untuk file status scraping
                        save_file_scraping = os.path.join(save_path, kd_gabungan[:-3], f"{kd_gabungan}_1_1.txt")
                        os.makedirs(os.path.dirname(save_file_scraping), exist_ok=True)

                        if not os.path.exists(save_file_scraping):
                            # Buat file status scraping jika belum ada
                            with open(save_file_scraping, 'w') as file:
                                file.write('0')
                    else:
                        # Jika OCR selesai, mulai proses scraping
                        print(f"SKIP Screenshoot dan OCR karena telah selesai untuk {kecamatan_name}_{desa_name}")
                        
                        # Cek apakah file CSV untuk scraping sudah ada
                    file_path = os.path.join(output_path, kd_gabungan[:-3], f"{kd_gabungan}_data.csv")
                    if os.path.exists(file_path):
                        print("File CSV ditemukan, mulai scraping...")
                        Scraping.mulai_scraping(file_path, desa_name, kecamatan_name, kab_name, desa_name, kd_gabungan)
                        print(f"Scraping untuk kelurahan {desa_name} telah selesai")
                        if update_progress_callback:
                            update_progress_callback()
        else:
            # Jika scraping selesai, beri tahu user
            print(f"Scraping untuk kelurahan {desa_name} telah selesai")
        
    if input_1 == "All":
        #gabung semua kelurahan excel to 1 excel
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

    # Tutup driver browser setelah semua kecamatan diproses
    driver.quit()
