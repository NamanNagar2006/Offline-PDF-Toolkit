import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pypdf import PdfWriter
from PyPDF2 import PdfReader, PdfWriter as SplitWriter
import os

# ---------------- ROOT ---------------- #
root = tk.Tk()
root.title("Offline PDF Toolkit")
root.geometry("520x580")
root.resizable(False, False)

style = ttk.Style()
style.theme_use("clam")

# ---------------- TITLE ---------------- #
tk.Label(root, text="Offline PDF Toolkit", font=("Arial", 16, "bold")).pack(pady=(12, 0))
tk.Label(root, text="No uploads • Works offline • Private", font=("Arial", 9)).pack(pady=(0, 12))

# ---------------- SECTION 1: FILES ---------------- #
frame_files = tk.LabelFrame(root, text="Select Files", padx=10, pady=10)
frame_files.pack(fill="x", padx=15, pady=8)

list_frame = tk.Frame(frame_files)
list_frame.pack()

scrollbar = tk.Scrollbar(list_frame)
scrollbar.pack(side="right", fill="y")

file_listbox = tk.Listbox(list_frame, height=8, width=58, yscrollcommand=scrollbar.set)
file_listbox.pack(side="left")

scrollbar.config(command=file_listbox.yview)

def update_buttons():
    has_files = file_listbox.size() > 0
    merge_btn.config(state="normal" if has_files else "disabled")

def add_files():
    files = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
    for f in files:
        file_listbox.insert(tk.END, f)
    update_buttons()

def clear_files():
    file_listbox.delete(0, tk.END)
    update_buttons()

def move_up():
    try:
        i = file_listbox.curselection()[0]
        if i == 0:
            return
        text = file_listbox.get(i)
        file_listbox.delete(i)
        file_listbox.insert(i-1, text)
        file_listbox.select_set(i-1)
    except:
        pass

def move_down():
    try:
        i = file_listbox.curselection()[0]
        if i == file_listbox.size() - 1:
            return
        text = file_listbox.get(i)
        file_listbox.delete(i)
        file_listbox.insert(i+1, text)
        file_listbox.select_set(i+1)
    except:
        pass

btn_frame = tk.Frame(frame_files)
btn_frame.pack(pady=8)

tk.Button(btn_frame, text="Add PDFs", width=12, command=add_files).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="Clear", width=10, command=clear_files).grid(row=0, column=1, padx=5)
tk.Button(btn_frame, text="Up", width=8, command=move_up).grid(row=0, column=2, padx=5)
tk.Button(btn_frame, text="Down", width=8, command=move_down).grid(row=0, column=3, padx=5)

# ---------------- SECTION 2: ACTIONS ---------------- #
frame_actions = tk.LabelFrame(root, text="Actions", padx=10, pady=10)
frame_actions.pack(fill="x", padx=15, pady=8)

progress = ttk.Progressbar(frame_actions, orient="horizontal", length=360, mode="determinate")
progress.pack(pady=6)

def merge_pdfs():
    files = file_listbox.get(0, tk.END)
    if not files:
        messagebox.showerror("Error", "Please add PDF files first.")
        return

    save_path = filedialog.asksaveasfilename(defaultextension=".pdf")
    if not save_path:
        return

    try:
        merger = PdfWriter()
        progress["maximum"] = len(files)
        progress["value"] = 0

        for i, file in enumerate(files):
            merger.append(file)
            progress["value"] = i + 1
            root.update_idletasks()

        merger.write(save_path)
        merger.close()

        messagebox.showinfo("Success", f"Merged successfully.\n\nSaved at:\n{save_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to merge PDFs.\n{str(e)}")

def split_pdf():
    file = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
    if not file:
        return

    try:
        n_pages = int(page_entry.get())
        if n_pages <= 0:
            raise ValueError
    except:
        messagebox.showerror("Error", "Enter a valid number of pages.")
        return

    folder = filedialog.askdirectory()
    if not folder:
        return

    try:
        reader = PdfReader(file)
        total = len(reader.pages)

        progress["maximum"] = total
        progress["value"] = 0

        for i in range(0, total, n_pages):
            writer = SplitWriter()
            for page in reader.pages[i:i+n_pages]:
                writer.add_page(page)

            output_path = os.path.join(folder, f"part_{i//n_pages+1}.pdf")
            with open(output_path, "wb") as f:
                writer.write(f)

            progress["value"] = min(i + n_pages, total)
            root.update_idletasks()

        messagebox.showinfo("Success", f"Split completed.\n\nSaved in:\n{folder}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to split PDF.\n{str(e)}")

def extract_text():
    file = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
    if not file:
        return

    save_path = filedialog.asksaveasfilename(defaultextension=".txt")
    if not save_path:
        return

    try:
        reader = PdfReader(file)
        total = len(reader.pages)

        progress["maximum"] = total
        progress["value"] = 0

        text_output = ""
        for i, page in enumerate(reader.pages):
            text_output += page.extract_text() or ""
            progress["value"] = i + 1
            root.update_idletasks()

        with open(save_path, "w", encoding="utf-8") as f:
            f.write(text_output)

        messagebox.showinfo("Success", f"Text extracted.\n\nSaved at:\n{save_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to extract text.\n{str(e)}")

# Centered buttons
action_btn_frame = tk.Frame(frame_actions)
action_btn_frame.pack(pady=6)

merge_btn = tk.Button(action_btn_frame, text="Merge PDFs", width=28, command=merge_pdfs, state="disabled")
merge_btn.pack(pady=3)

tk.Button(action_btn_frame, text="Split PDF", width=28, command=split_pdf).pack(pady=3)
tk.Button(action_btn_frame, text="Extract Text", width=28, command=extract_text).pack(pady=3)

# ---------------- SECTION 3: OPTIONS ---------------- #
frame_options = tk.LabelFrame(root, text="Options", padx=10, pady=10)
frame_options.pack(fill="x", padx=15, pady=8)

options_row = tk.Frame(frame_options)
options_row.pack(pady=5)

tk.Label(options_row, text="Pages per split:", width=18, anchor="w").pack(side="left")
page_entry = tk.Entry(options_row, width=15, justify="center")
page_entry.pack(side="left", padx=5)
page_entry.insert(0, "2")

# ---------------- FOOTER ---------------- #
tk.Label(root, text="No internet required • Files never leave your device",
         font=("Arial", 8), fg="gray").pack(pady=10)

root.mainloop()