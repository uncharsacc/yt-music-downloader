import tkinter as tk
from tkinter import messagebox
import subprocess

def descargar():
    url = entry.get()

    if not url:
        messagebox.showerror("Error", "Pon una URL")
        return

    comando = [
        "yt-dlp.exe",
        "-x",
        "--audio-format", "mp3",
        "-o", "%(playlist_index)s - %(title)s.%(ext)s",
        url
    ]

    try:
        subprocess.run(comando)
        messagebox.showinfo("Listo", "Descarga terminada 😎")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Ventana
ventana = tk.Tk()
ventana.title("Descargador YouTube MP3")
ventana.geometry("400x150")

tk.Label(ventana, text="Pega la URL:").pack(pady=5)

entry = tk.Entry(ventana, width=50)
entry.pack(pady=5)

tk.Button(ventana, text="Descargar MP3", command=descargar).pack(pady=10)

ventana.mainloop()