import os
import tkinter as tk
from tkinter import filedialog, messagebox
from ttkbootstrap import Style
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import Frame, Button, Entry, Label, Combobox
from db import get_connection

ICONS = {
    'red': '📂', 'green': '📁', 'blue': '📀',
    'yellow': '📃', 'purple': '📄'
}

class SmartFileManager:
    def __init__(self, root):
        self.root = root
        self.root.title("SMART FILE MANAGER")
        self.style = Style("darkly")
        self.conn = get_connection()
        self.cur = self.conn.cursor()
        self.user_id = self.get_last_user()
        self.layout = 'grid'

        self.create_ui()
        self.load_user_files()

    def get_last_user(self):
        try:
            with get_connection() as c:
                cur = c.cursor()
                cur.execute("SELECT user_id FROM session WHERE id=1")
                row = cur.fetchone()
                return row[0] if row else None
        except:
            return None

    def set_session(self, user_id):
        self.cur.execute("DELETE FROM session")
        self.cur.execute("INSERT INTO session (id, user_id) VALUES (1, %s)", (user_id,))
        self.conn.commit()

    def clear_session(self):
        self.cur.execute("DELETE FROM session")
        self.conn.commit()

    def create_ui(self):
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)
        account_menu = tk.Menu(self.menu, tearoff=0)
        account_menu.add_command(label="Login/Create Account", command=self.login_ui)
        account_menu.add_command(label="Logout", command=self.logout)
        self.menu.add_cascade(label="☰", menu=account_menu)

        toolbar = Frame(self.root)
        toolbar.pack(fill=X)
        Button(toolbar, text="Add Album", command=self.add_album_ui).pack(side=LEFT, padx=5)
        Button(toolbar, text="Favorites", command=self.show_favorites).pack(side=LEFT)
        Button(toolbar, text="Add File", command=self.add_file_to_album).pack(side=LEFT, padx=5)
        cb = Combobox(toolbar, values=["small", "medium", "large"], state="readonly", width=8)
        cb.pack(side=RIGHT)
        cb.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        self.main_frame = Frame(self.root)
        self.main_frame.pack(fill=BOTH, expand=YES)

    def login_ui(self):
        win = tk.Toplevel(self.root)
        win.title("Login/Create Account")
        Label(win, text="User ID:").pack()
        uid = Entry(win)
        uid.pack()
        Label(win, text="Password:").pack()
        pw = Entry(win, show="*")
        pw.pack()

        def try_login():
            self.cur.execute("SELECT * FROM users WHERE user_id=%s AND password=%s", (uid.get(), pw.get()))
            if self.cur.fetchone():
                self.user_id = uid.get()
                self.set_session(self.user_id)
                self.refresh()
                win.destroy()
            else:
                messagebox.showerror("Error", "Login failed")

        def try_create():
            try:
                self.cur.execute("INSERT INTO users VALUES (%s, %s)", (uid.get(), pw.get()))
                self.conn.commit()
                messagebox.showinfo("Success", "Account created!")
            except:
                messagebox.showerror("Error", "Account exists")

        Button(win, text="Login", command=try_login).pack(pady=5)
        Button(win, text="Create", command=try_create).pack()

    def logout(self):
        self.clear_session()
        self.user_id = None
        self.refresh()

    def add_album_ui(self):
        if not self.user_id:
            messagebox.showerror("Login Required", "Please login first.")
            return
        win = tk.Toplevel(self.root)
        win.title("New Album")
        Label(win, text="Album Name").pack()
        name = Entry(win)
        name.pack()
        Label(win, text="Icon Color").pack()
        color = Combobox(win, values=list(ICONS.keys()), state="readonly")
        color.pack()

        def create_album():
            self.cur.execute("INSERT INTO albums (user_id, name, icon) VALUES (%s, %s, %s)",
                             (self.user_id, name.get(), color.get()))
            self.conn.commit()
            self.refresh()
            win.destroy()

        Button(win, text="Create", command=create_album).pack()

    def add_file_to_album(self):
        if not self.user_id:
            messagebox.showerror("Login Required", "Please login first.")
            return
        self.cur.execute("SELECT album_id, name FROM albums WHERE user_id=%s", (self.user_id,))
        albums = self.cur.fetchall()
        if not albums:
            messagebox.showerror("No Albums", "Create an album first")
            return
        win = tk.Toplevel(self.root)
        win.title("Add File")
        file_path = filedialog.askopenfilename()
        if not file_path:
            return
        Label(win, text="Choose Album").pack()
        cb = Combobox(win, values=[f"{a[0]}: {a[1]}" for a in albums], state="readonly")
        cb.pack()

        def add():
            album_id = int(cb.get().split(":")[0])
            self.cur.execute("INSERT INTO files (album_id, path) VALUES (%s, %s)", (album_id, file_path))
            self.conn.commit()
            self.refresh()
            win.destroy()

        Button(win, text="Add", command=add).pack()

    def refresh(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.load_user_files()

    def load_user_files(self):
        if not self.user_id:
            Label(self.main_frame, text="No user logged in.").pack()
            return
        self.cur.execute("SELECT album_id, name, icon FROM albums WHERE user_id=%s", (self.user_id,))
        albums = self.cur.fetchall()
        for album_id, name, icon in albums:
            f = Frame(self.main_frame, padding=10)
            f.pack(fill=X)
            Label(f, text=ICONS.get(icon, '📂') + " " + name, font=("Arial", 14)).pack(anchor=W)
            self.cur.execute("SELECT file_id, path, is_fav FROM files WHERE album_id=%s", (album_id,))
            files = self.cur.fetchall()
            for fid, path, is_fav in files:
                row = Frame(f)
                row.pack(anchor=W, padx=30)
                lbl = Label(row, text=os.path.basename(path))
                lbl.pack(side=LEFT)
                Button(row, text="⭐" if not is_fav else "⭐", command=lambda fid=fid: self.toggle_fav(fid)).pack(side=RIGHT)

    def toggle_fav(self, file_id):
        self.cur.execute("UPDATE files SET is_fav = NOT is_fav WHERE file_id = %s", (file_id,))
        self.conn.commit()
        self.refresh()

    def show_favorites(self):
        if not self.user_id:
            messagebox.showinfo("Login Required", "Login to view favorites")
            return
        fav_win = tk.Toplevel(self.root)
        fav_win.title("Favorites")
        self.cur.execute("SELECT path FROM files f JOIN albums a ON a.album_id = f.album_id WHERE f.is_fav=1 AND a.user_id=%s", (self.user_id,))
        favs = self.cur.fetchall()
        for path, in favs:
            Label(fav_win, text=os.path.basename(path)).pack(anchor=W, padx=10)

def run_app():
    root = tk.Tk()
    app = SmartFileManager(root)
    root.mainloop()
    
