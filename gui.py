# gui.py
import tkinter as tk
from tkinter import filedialog, messagebox, Listbox
from ttkbootstrap import Style
from ttkbootstrap.widgets import Frame, Button, Entry, Label
import album_manager as am

def run_gui():
    # GUI callbacks
    def update_album_list():
        album_list.delete(0, tk.END)
        for album in am.get_albums():
            album_list.insert(tk.END, album)

    def update_file_list():
        selected = album_list.curselection()
        if not selected:
            return
        album = album_list.get(selected[0])
        file_list.delete(0, tk.END)
        for path in am.get_files(album):
            file_list.insert(tk.END, path)

    def create_album():
        name = album_name.get().strip()
        if am.create_album(name):
            update_album_list()
        album_name.delete(0, tk.END)

    def delete_album():
        selected = album_list.curselection()
        if not selected:
            return
        name = album_list.get(selected[0])
        if messagebox.askyesno("Delete", f"Delete album '{name}'?"):
            am.delete_album(name)
            update_album_list()
            file_list.delete(0, tk.END)

    def add_file_to_album():
        selected = album_list.curselection()
        if not selected:
            return
        album = album_list.get(selected[0])
        files = filedialog.askopenfilenames(
            filetypes=[("Documents", "*.pdf *.doc *.docx *.ppt *.pptx")]
        )
        am.add_files_to_album(album, files)
        update_file_list()

    def open_file():
        selected = file_list.curselection()
        if not selected:
            return
        path = file_list.get(selected[0])
        if not am.open_file(path):
            messagebox.showerror("Error", "File not found.")

    # Setup UI
    style = Style("cosmo")
    root = style.master
    root.title("Smart File Organizer")
    root.geometry("700x500")

    frame = Frame(root, padding=10)
    frame.pack(fill="both", expand=True)

    # Album creation section
    Label(frame, text="New Album:").grid(row=0, column=0, sticky="w")
    album_name = Entry(frame)
    album_name.grid(row=0, column=1, sticky="ew")
    Button(frame, text="Create", command=create_album).grid(row=0, column=2, padx=5)

    # Album list
    album_list = Listbox(frame, height=10)
    album_list.grid(row=1, column=0, columnspan=3, sticky="nsew")
    album_list.bind("<<ListboxSelect>>", lambda e: update_file_list())

    # Album controls
    Button(frame, text="Delete Album", command=delete_album).grid(row=2, column=0, columnspan=3, pady=5)
    Button(frame, text="Add Files", command=add_file_to_album).grid(row=3, column=0, columnspan=3, pady=5)

    # File list in album
    Label(frame, text="Files in Album:").grid(row=4, column=0, columnspan=3, sticky="w")
    file_list = Listbox(frame, height=10)
    file_list.grid(row=5, column=0, columnspan=3, sticky="nsew")
    file_list.bind("<Double-Button-1>", lambda e: open_file())

    frame.columnconfigure(1, weight=1)
    frame.rowconfigure(5, weight=1)

    update_album_list()
    root.mainloop()
