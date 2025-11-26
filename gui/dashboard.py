import customtkinter as ctk
from tkinter import ttk
from Component import Maps
from Component import Bot_Gabung
from Component import clip_osm_kab
from Component import Scraping
import sys
import threading
import os
import webbrowser


# CustomTkinter setup
ctk.set_appearance_mode("light")  # You can choose "light" or "dark" mode
ctk.set_default_color_theme("blue")  # You can choose "blue", "green", or "dark-blue"

class RedirectStdout:
    def __init__(self, text_widget, max_lines=10):
        self.text_widget = text_widget
        self.max_lines = max_lines

    def write(self, message):
        self.text_widget.insert("end", message)
        self.text_widget.see("end")
        lines = int(self.text_widget.index("end-1c").split(".")[0])
        if lines > self.max_lines:
            self.text_widget.delete("1.0", f"{lines - self.max_lines + 1}.0")

    def flush(self):
        pass

nama_kelurahan = Maps.read_geopandas_json()

# Function to populate the progress table with data
def show_table(tree, data):
    # Clear existing data in the Treeview
    for item in tree.get_children():
        tree.delete(item)

    # Insert new data with conditional row coloring
    for row in data:
        # Count the number of "Belum" values in columns 2, 3, and 4
        belum_count = row[1:4].count("Belum")

        # Determine the background color based on the count of "Belum" values
        if belum_count == 3:
            bg_color = "white"          # All "Belum"
        elif belum_count == 2:
            bg_color = "orange"         # 2 "Belum"
        elif belum_count == 1:
            bg_color = "lightgreen"     # 1 "Belum"
        else:
            bg_color = "green"          # 0 "Belum" (all "Berhasil")

        # Insert the row with the determined color tag
        item_id = tree.insert("", ctk.END, values=row, tags=(bg_color,))

    # Configure tags with specific background colors
    tree.tag_configure("white", background="white")
    tree.tag_configure("orange", background="orange")
    tree.tag_configure("lightgreen", background="lightgreen")
    tree.tag_configure("green", background="green")


def submit_action():
    selected_value = selected_option.get()
    submit_button.configure(state="disabled")
    update_button.configure(state="disabled")
    def enable_button_after_task():
        submit_button.configure(state="normal")
        update_button.configure(state="normal")
    thread = threading.Thread(target=lambda: [Bot_Gabung.start_screenshoot(selected_value, update_progress_table), enable_button_after_task()])
    thread.start()

def update_action():
    print("1")
    # print(nama_kelurahan[1])
    selected_value = selected_option.get()
    submit_button.configure(state="disabled")
    update_button.configure(state="disabled")
    def enable_button_after_task_2():
        submit_button.configure(state="normal")
        update_button.configure(state="normal")
    thread = threading.Thread(target=lambda: [Scraping.mulai_scraping_2(selected_value,nama_kelurahan[1]), enable_button_after_task_2()])
    thread.start()

def update_progress_table():
    folder_path = "save/"
    os.makedirs(os.path.dirname(folder_path), exist_ok=True)
    kelurahan_status = {}
    for kecamatan_folder in os.listdir(folder_path):
        kecamatan_path = os.path.join(folder_path, kecamatan_folder)
        if os.path.isdir(kecamatan_path):
            for filename in os.listdir(kecamatan_path):
                if filename.endswith(".txt"):
                    parts = filename.split("_")
                    kelurahan_id = parts[0]
                    column_number = int(parts[1])
                    status_code = parts[2].replace(".txt", "").strip()
                    if kelurahan_id not in kelurahan_status:
                        kelurahan_status[kelurahan_id] = ["Belum", "Belum", "Belum"]
                    if status_code == "2":
                        kelurahan_status[kelurahan_id][column_number - 1] = "Berhasil"
    sample_data = [
        (
            kelurahan,
            kelurahan_status.get(kelurahan, ["Belum", "Belum", "Belum"])[0],
            kelurahan_status.get(kelurahan, ["Belum", "Belum", "Belum"])[1],
            kelurahan_status.get(kelurahan, ["Belum", "Belum", "Belum"])[2]
        )
        for kelurahan in nama_kelurahan[1:]
    ]
    show_table(progress_tree, sample_data)
    update_progress_bar(sample_data)

def update_progress_bar(data):
    total_rows = len(data)
    completed_rows = sum(1 for row in data if row[1:4].count("Belum") <= 1)
    progress_percentage = (completed_rows / total_rows) * 100 if total_rows > 0 else 0
    progress_bar.set(completed_rows / total_rows)
    progress_label.configure(text=f"{int(progress_percentage)}%")

def update_map():
    first_row = nama_kelurahan[1]
    selected_value = selected_option.get()
    clip_osm_kab.show_map(selected_value)
    base_path = os.path.dirname(os.path.abspath(__file__))  # Path ke folder skrip saat ini
    map_path = os.path.join(base_path,"..","Output","Map")
    if (selected_value=='All'):
        map_path = os.path.join(map_path, f"{first_row[:4]}.html")
        RdFile = webbrowser.open(map_path)  #Full path to your file
        update_progress_table()
    else :
        map_path = os.path.join(map_path, selected_value[:-3],f"{selected_value}.html")
        RdFile = webbrowser.open(map_path)  #Full path to your file
        update_progress_table()



root = ctk.CTk(fg_color="white")
root.title("SNAPWangi - Combined View")
root.geometry("1200x600")

# Top title frame
title_frame = ctk.CTkFrame(root, fg_color="#FFCC00", height=80)
title_frame.pack(fill="x", padx=20)
title_label = ctk.CTkLabel(title_frame, text="SNAPWangi", font=ctk.CTkFont(size=36, weight="bold"), text_color="#000000")
title_label.pack(pady=10)

# Main Frame for left and right columns
main_frame = ctk.CTkFrame(root, fg_color="#FFFFFF")
main_frame.pack(expand=True, fill="both", padx=10, pady=10)

# Left Frame for Input and Progress
left_frame = ctk.CTkFrame(main_frame, fg_color="#FFFFFF", width=200)
left_frame.pack(side="left", fill="y", padx=10, pady=10)

# Frames stacked vertically inside left_frame
input_frame = ctk.CTkFrame(left_frame, fg_color="#FFEB99", width=100)
input_frame.pack(side="top", fill="x", padx=10, pady=10)

border_progress_frame = ctk.CTkFrame(left_frame, fg_color="#FFCC00", width=100)  # Change color as needed
border_progress_frame.pack(side="top", fill="x", padx=10, pady=10)

progress_frame = ctk.CTkFrame(border_progress_frame, fg_color="white")
progress_frame.pack(expand=True, fill="both", padx=4, pady=2)

map_frame = ctk.CTkFrame(left_frame, fg_color="white", width=100)
map_frame.pack(side="top", fill="x", padx=10, pady=10)

input_label = ctk.CTkLabel(input_frame, text="DESA / KELURAHAN YANG AKAN DI-SCRAPING", font=ctk.CTkFont(size=14, weight="bold"))
input_label.pack(padx=10,pady=(0, 10))

selected_option = ctk.StringVar(value=nama_kelurahan[0])
dropdown = ctk.CTkComboBox(input_frame, variable=selected_option, values=nama_kelurahan)
dropdown.pack(pady=(0, 20))

submit_button = ctk.CTkButton(input_frame, text="Submit", command=submit_action, font=ctk.CTkFont(size=14), fg_color="#FFCC00", text_color="black" )
submit_button.pack(pady=(10, 5))

update_button = ctk.CTkButton(input_frame, text="Update", command=update_action, font=ctk.CTkFont(size=14), fg_color="#FFCC00", text_color="black" )
update_button.pack(pady=(5, 20))

# Progress Label with Bold Font
progress_label_2 = ctk.CTkLabel(progress_frame, text="Progress", font=ctk.CTkFont(size=12, weight="bold"))
progress_label_2.pack()

# Frame for Progress Bar and Percentage Label
progress_container = ctk.CTkFrame(progress_frame, fg_color="transparent")
progress_container.pack(pady=(5, 10), fill="x", expand=True)

# Progress Bar with Light Yellow Background
progress_bar = ctk.CTkProgressBar(progress_container, width=180, progress_color="yellow")  # Light yellow
progress_bar.pack(side="left", padx=(60, 10))

# Percentage Label Side by Side with Progress Bar
progress_label = ctk.CTkLabel(progress_container, text="20%", font=ctk.CTkFont(size=12))
progress_label.pack(side="left")

map_button = ctk.CTkButton(map_frame, text="Lihat Peta", command=update_map, font=ctk.CTkFont(size=14, weight="bold"), fg_color="#FFCC00", text_color="black", height=50)
map_button.pack(pady=(20, 20),fill="x")

# Right Frame for Progress Table and Log Output
right_frame = ctk.CTkFrame(main_frame, fg_color="white")
right_frame.pack(side="right", expand=True, fill="both", padx=10, pady=10)

# progress_title_label = ctk.CTkLabel(right_frame, text="Progress Tahapan", font=ctk.CTkFont(size=18, weight="bold"))
# progress_title_label.pack(pady=(0, 10))

progress_tree = ttk.Treeview(right_frame, columns=("Nama Kelurahan", "Screenshoot & OCR", "Scraping", "Clipping"), show="headings")
progress_tree.heading("Nama Kelurahan", text="Nama Kelurahan")
progress_tree.heading("Screenshoot & OCR", text="Screenshot & OCR")
progress_tree.heading("Scraping", text="Scraping")
progress_tree.heading("Clipping", text="Clipping")
for col in ("Nama Kelurahan", "Screenshoot & OCR", "Scraping", "Clipping"):
    progress_tree.column(col, width=150)
progress_tree.pack(fill="both", expand=True)

log_label = ctk.CTkLabel(right_frame, text="Log Output:", font=ctk.CTkFont(size=14,weight="bold"))
log_label.pack(fill="x")
log_text = ctk.CTkTextbox(right_frame, height=12, wrap="word", fg_color="#FFEB99")
log_text.pack(fill="both", expand=True, pady=(5, 10))

# Menambahkan Label untuk lisensi di pojok kiri bawah
license_label = ctk.CTkLabel(root, text="© Dibuat oleh Lare Oesing 62 X BPS Banyuwangi", font=("Arial", 10))
license_label.place(relx=0, rely=1, anchor='sw', x=10, y=-10)

sys.stdout = RedirectStdout(log_text)
update_progress_table()

root.mainloop()
