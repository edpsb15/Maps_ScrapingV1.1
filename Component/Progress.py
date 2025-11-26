import tkinter as tk
from tkinter import ttk

def create_progress_window(nama_kelurahan):
    # Create a Toplevel window instead of a new Tk instance
    progress_window = tk.Toplevel()
    progress_window.title("SNAPWangi Progress")

    # Set the window size and background color
    progress_window.geometry("600x400")
    progress_window.configure(bg="#e0f7fa")  # Light cyan background

    # Create a frame for better layout control
    frame = tk.Frame(progress_window, bg="#ffffff", padx=20, pady=20)
    frame.pack(expand=True, fill=tk.BOTH)

    # Create a title label
    title_label = tk.Label(frame, text="SnapWangi", font=("Arial", 36, "bold"), bg="#ffffff", fg="#00796b")  # Dark cyan text
    title_label.pack(pady=(0, 20))

    # Create a question label
    question_label = tk.Label(frame, text="Progress Tahapan", 
                            font=("Arial", 20), bg="#ffffff", fg="#004d40")
    question_label.pack(pady=(0, 20))

    # Create a Treeview widget to display the table
    tree = ttk.Treeview(frame, columns=("Nama Kelurahan", "Screenshoot + OCR", "Scraping", "Clipping"), show="headings")

    # Define the column headings
    tree.heading("Nama Kelurahan", text="Nama Kelurahan")
    tree.heading("Screenshoot + OCR", text="Screenshoot + OCR")
    tree.heading("Scraping", text="Scraping")
    tree.heading("Clipping", text="Clipping")

    # Set the column width
    tree.column("Nama Kelurahan", width=100)
    tree.column("Screenshoot + OCR", width=100)
    tree.column("Scraping", width=100)
    tree.column("Clipping", width=100)

    # Add a scrollbar
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Pack the Treeview
    tree.pack(expand=True, fill=tk.BOTH)

    # Populate data based on the `nama_kelurahan` list, with other columns set to 0
    sample_data = [(kelurahan, "Berhasil", "Berhasil", "Berhasil") if kelurahan == "PAKIS" else (kelurahan, "Belum", "Belum", "Belum") for kelurahan in nama_kelurahan[1:]]

    # Show the table directly when the window is created
    show_table(tree, sample_data)

    return progress_window

def show_table(tree, data):
    # Clear the existing Treeview (if needed)
    for item in tree.get_children():
        tree.delete(item)

    # Insert data into the Treeview with conditional coloring
    for row in data:
        if row[1] == "Berhasil":  # Check if the status is "Berhasil"
            tree.insert("", tk.END, values=row, tags=('success',))
        else:
            tree.insert("", tk.END, values=row)

    # Configure the tag to change background color
    tree.tag_configure('success', background='lightgreen')  # Set green background for success rows
