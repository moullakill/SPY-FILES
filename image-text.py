import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel
from PIL import Image, ImageTk
import base64
from io import BytesIO
import uuid
import os
import time
import threading
import requests
import os
import sys


# Configuration
PASSWORD = "coffee 007"
HUMAN_LOG_PATH = "human_log.txt"
MACHINE_LOG_PATH = "machine_log.txt"
GITHUB_REPO_URL = "https://raw.githubusercontent.com/moullakill/SPY-FILES/main/"
GITHUB_TOKEN = "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"
GITHUB_API_URL = "https://api.github.com/repos/moullakill/SPY-FILES/contents/"

# Se place dans le répertoire du script, même en double-cliquant
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

class PasswordWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🔐 Authentification")
        self.geometry("400x200")
        self.configure(bg="black")
        tk.Label(self, text="Entrez le mot de passe :", fg="lime", bg="black").pack(pady=10)
        self.entry = tk.Entry(self, show="*", width=30)
        self.entry.pack(pady=10)
        self.entry.bind("<Return>", self.check_password)
        tk.Button(self, text="Valider", command=self.check_password).pack()

    def check_password(self, event=None):
        if self.entry.get() == PASSWORD:
            self.destroy()
            LoadingWindow()
        else:
            messagebox.showerror("Erreur", "Mot de passe incorrect.")

class LoadingWindow:
    def __init__(self):
        self.win = tk.Tk()
        self.win.title("Chargement")
        self.win.geometry("500x300")
        self.win.configure(bg="black")
        try:
            img = Image.open("logo.jpg")
            img.thumbnail((150, 150))
            self.logo = ImageTk.PhotoImage(img)
            tk.Label(self.win, image=self.logo, bg="black").pack(pady=10)
        except:
            pass
        tk.Label(self.win, text="Chargement des modules...", fg="lime", bg="black", font=("Courier", 14)).pack(pady=20)
        self.win.after(2000, self.launch_app)
        self.win.mainloop()

    def launch_app(self):
        self.win.destroy()
        root = tk.Tk()
        ImageConverterApp(root)
        root.mainloop()

class ImageConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🕵️ Agent Secret - Convertisseur Image ↔ Texte")
        self.root.attributes('-fullscreen', True)
        self.obscure_mode = False
        self.monitoring = False
        self.image_data_list = []
        self.current_image_data = None
        self.observed_files = set()

        self.frame_main = tk.Frame(root, bg="#1a1a1a")
        self.frame_main.pack(fill=tk.BOTH, expand=True)

        self.frame_left = tk.Frame(self.frame_main, width=300, bg="#1a1a1a")
        self.frame_left.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.frame_right = tk.Frame(self.frame_main, width=300, bg="#1a1a1a")
        self.frame_right.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        self.frame_center = tk.Frame(self.frame_main, bg="#1a1a1a")
        self.frame_center.pack(fill=tk.BOTH, expand=True)

        tk.Label(self.frame_left, text="Images enregistrées", font=("Courier", 12), bg="#1a1a1a", fg="lime").pack()
        self.listbox_images = tk.Listbox(self.frame_left, bg="black", fg="lime")
        self.listbox_images.pack(fill=tk.BOTH, expand=True)
        self.listbox_images.bind("<Double-Button-1>", self.load_selected_image)

        tk.Label(self.frame_right, text="Titres UUID", font=("Courier", 12), bg="#1a1a1a", fg="lime").pack()
        self.listbox_titles = tk.Listbox(self.frame_right, bg="black", fg="lime")
        self.listbox_titles.pack(fill=tk.BOTH, expand=True)

        self.img_label = tk.Label(self.frame_center, text="Aucun aperçu", font=("Courier", 14), bg="#1a1a1a", fg="white")
        self.img_label.pack(pady=10)

        button_style = {"font": ("Courier", 10), "bg": "#333", "fg": "lime"}
        tk.Button(self.frame_center, text="📂 Ouvrir Images", command=self.open_images, **button_style).pack(pady=5)
        tk.Button(self.frame_center, text="📅 Importer Logs", command=self.import_logs, **button_style).pack(pady=5)
        tk.Button(self.frame_center, text="🌑 Mode Obscur ON/OFF", command=self.toggle_obscure_mode, **button_style).pack(pady=5)
        tk.Button(self.frame_center, text="🖼️ Galerie", command=self.open_gallery, **button_style).pack(pady=5)
        tk.Button(self.frame_center, text="☁️ Synchroniser GitHub", command=self.sync_with_github, **button_style).pack(pady=5)
        tk.Button(self.frame_center, text="❌ Quitter", command=self.quit_app, **button_style).pack(pady=5)

        self.console = tk.Text(self.root, height=5, bg="black", fg="lime", font=("Courier", 10))
        self.console.pack(fill=tk.X)

        self.log("Application démarrée.")
        self.load_logs()

    def quit_app(self):
        self.log("Fermeture.")
        self.root.destroy()

    def log(self, msg):
        self.console.insert(tk.END, f"[LOG] {msg}\n")
        self.console.see(tk.END)

    def open_images(self):
        files = filedialog.askopenfilenames(filetypes=[("Images", "*.png *.jpg *.jpeg *.webp")])
        for f in files:
            self.store_image(f)
            self.log(f"Image importée : {f}")

    def store_image(self, file_path):
        with open(file_path, "rb") as f:
            data = f.read()
        name = os.path.basename(file_path)
        uid = str(uuid.uuid4())
        self.image_data_list.append((name, data, uid))
        self.listbox_images.insert(tk.END, uid)
        self.listbox_titles.insert(tk.END, f"{name} ==> {uid}")
        self.save_logs(name, data, uid)

    def save_logs(self, name, data, uid):
        encoded = base64.b64encode(data).decode("utf-8")
        with open(HUMAN_LOG_PATH, "a") as f1, open(MACHINE_LOG_PATH, "a") as f2:
            f1.write(f"{name}:{uid}\n")
            f2.write(f"{uid}:{encoded}\n")

    def load_logs(self):
        if not (os.path.exists(HUMAN_LOG_PATH) and os.path.exists(MACHINE_LOG_PATH)):
            return
        self.image_data_list.clear()
        self.listbox_images.delete(0, tk.END)
        self.listbox_titles.delete(0, tk.END)
        uuid_map = {}
        with open(MACHINE_LOG_PATH, "r") as f:
            for line in f:
                line = line.strip()
                if ":" in line:
                    try:
                        uid, data = line.split(":", 1)
                        uuid_map[uid] = base64.b64decode(data)
                    except Exception as e:
                        self.log(f"Erreur décodage ligne: {line} | {e}")
        with open(HUMAN_LOG_PATH, "r") as f:
            for line in f:
                line = line.strip()
                if ":" in line:
                    name, uid = line.split(":", 1)
                    if uid in uuid_map:
                        self.image_data_list.append((name, uuid_map[uid], uid))
                        self.listbox_images.insert(tk.END, uid)
                        self.listbox_titles.insert(tk.END, f"{name} ==> {uid}")

    def import_logs(self):
        human = filedialog.askopenfilename(title="Log humain", filetypes=[("Text", "*.txt")])
        machine = filedialog.askopenfilename(title="Log machine", filetypes=[("Text", "*.txt")])
        if human and machine:
            global HUMAN_LOG_PATH, MACHINE_LOG_PATH
            HUMAN_LOG_PATH = human
            MACHINE_LOG_PATH = machine
            self.load_logs()
            self.log("Logs importés.")

    def load_selected_image(self, event):
        sel = self.listbox_images.curselection()
        if sel:
            _, data, _ = self.image_data_list[sel[0]]
            img = Image.open(BytesIO(data))
            img.thumbnail((200, 200))
            tk_img = ImageTk.PhotoImage(img)
            self.img_label.config(image=tk_img, text="")
            self.img_label.image = tk_img
            self.show_preview(data)

    def toggle_obscure_mode(self):
        self.obscure_mode = not self.obscure_mode
        color = "#8B0000" if self.obscure_mode else "#1a1a1a"
        self.set_bg(self.root, color)
        self.log(f"Mode Obscur {'activé' if self.obscure_mode else 'désactivé'}.")

    def set_bg(self, widget, color):
        try:
            widget.configure(bg=color)
            for child in widget.winfo_children():
                self.set_bg(child, color)
        except:
            pass

    def show_preview(self, data):
        top = Toplevel(self.root)
        top.title("Prévisualisation")
        img = Image.open(BytesIO(data))
        tk_img = ImageTk.PhotoImage(img)
        lbl = tk.Label(top, image=tk_img)
        lbl.image = tk_img
        lbl.pack()

    def open_gallery(self):
        gal = Toplevel(self.root)
        gal.title("Galerie")
        gal.configure(bg="#1a1a1a")
        canvas = tk.Canvas(gal, bg="#1a1a1a")
        scroll = tk.Scrollbar(gal, orient="vertical", command=canvas.yview)
        frame = tk.Frame(canvas, bg="#1a1a1a")
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        for i, (name, data, uid) in enumerate(self.image_data_list):
            try:
                img = Image.open(BytesIO(data))
                img.thumbnail((100, 100))
                tk_img = ImageTk.PhotoImage(img)
                btn = tk.Button(frame, image=tk_img, bg="#1a1a1a", command=lambda d=data: self.show_preview(d))
                btn.image = tk_img
                btn.grid(row=i//6, column=i%6, padx=5, pady=5)
            except:
                pass

        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        self.log("Galerie ouverte.")
    def sync_with_github(self):
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }

        def read_remote_logs():
            for log_name in ["human_log.txt", "machine_log.txt"]:
                response = requests.get(GITHUB_REPO_URL + log_name, headers=headers)
                if response.status_code == 200:
                    with open(log_name, "w", encoding="utf-8") as f:
                        f.write(response.text)
                    self.log(f"{log_name} synchronisé (lecture).")
                else:
                    self.log(f"Erreur lecture {log_name} depuis GitHub : {response.status_code}")
    
        def write_local_logs():
            for local_path, remote_name in [(HUMAN_LOG_PATH, "human_log.txt"), (MACHINE_LOG_PATH, "machine_log.txt")]:
                if os.path.exists(local_path):
                    with open(local_path, "rb") as f:
                        content = base64.b64encode(f.read()).decode("utf-8")
    
                    # Récupérer le SHA actuel du fichier sur GitHub
                    sha = None
                    r_get = requests.get(GITHUB_API_URL + remote_name, headers=headers)
                    if r_get.status_code == 200:
                        sha = r_get.json().get("sha")

                    put_data = {
                        "message": f"update {remote_name}",
                        "content": content,
                        "branch": "main",
                    }
                    if sha:
                        put_data["sha"] = sha  # nécessaire pour mise à jour

                    r_put = requests.put(GITHUB_API_URL + remote_name, headers=headers, json=put_data)
                    if r_put.status_code in [200, 201]:
                        self.log(f"{remote_name} synchronisé (écriture).")
                    else:
                        self.log(f"Erreur écriture {remote_name} : {r_put.status_code} - {r_put.text}")

        threading.Thread(target=lambda: [read_remote_logs(), write_local_logs(), self.load_logs()], daemon=True).start()


if __name__ == "__main__":
    PasswordWindow().mainloop()
