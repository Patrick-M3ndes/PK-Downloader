import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import yt_dlp
import os
import threading
import json

# ------------------- ARQUIVO DE CONFIG -------------------
CONFIG_FILE = "pk_config.json"

# Carrega pasta salva (se existir)
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)
        pasta_destino = config.get("ultima_pasta", os.path.join(os.path.expanduser("~"), "Downloads", "PK Downloader"))
else:
    pasta_destino = os.path.join(os.path.expanduser("~"), "Downloads", "PK Downloader")

os.makedirs(pasta_destino, exist_ok=True)

# Salva configuração
def salvar_config():
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({"ultima_pasta": pasta_destino}, f)

# ------------------- JANELA -------------------
janela = tk.Tk()
janela.title("PK Downloader 2025")
janela.geometry("750x620")
janela.configure(bg="#0d1117")
janela.resizable(False, False)

# ------------------- VARIÁVEIS -------------------
progresso_var = tk.DoubleVar()
label_status = None
progress_bar = None
btn_baixar = None
entry_link = None
label_pasta = None

var_tipo = tk.StringVar(value="video")
var_resolucao = tk.StringVar(value="720p")

resolucoes = {
    "360p": "best[height<=360][ext=mp4]/best",
    "480p": "best[height<=480][ext=mp4]/best",
    "720p": "best[height<=720][ext=mp4]/best",
    "1080p": "best[height<=1080]/best",
    "Melhor possível (até 4K)": "bestvideo+bestaudio/best"
}

# ------------------- FUNÇÕES -------------------
def escolher_pasta():
    global pasta_destino
    pasta = filedialog.askdirectory(initialdir=pasta_destino, title="Escolher pasta de destino")
    if pasta:
        pasta_destino = pasta
        label_pasta.config(text=f"Salvando em:\n{pasta_destino}")
        salvar_config()

def atualizar_resolucao(*args):
    if var_tipo.get() == "video":
        frame_res.pack(pady=10)
    else:
        frame_res.pack_forget()

var_tipo.trace("w", atualizar_resolucao)

def progresso_hook(d):
    if d['status'] == 'downloading':
        try:
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            if total > 0:
                pct = (d['downloaded_bytes'] / total) * 100
                progresso_var.set(pct)
                label_status.config(text=f"Baixando... {pct:.1f}%")
                janela.update_idletasks()
        except: pass
    elif d['status'] == 'finished':
        progresso_var.set(100)
        label_status.config(text="Finalizando...")
        janela.update_idletasks()

def executar_download():
    url = entry_link.get().strip()
    if not url:
        messagebox.showwarning("Atenção", "Cole o link primeiro!")
        return

    progresso_var.set(0)
    progress_bar.pack(pady=15)
    btn_baixar.config(state="disabled")
    label_status.config(text="Processando...", fg="#ffa500")

    def thread():
        try:
            if var_tipo.get() == "audio":
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(pasta_destino, '%(title)s [%(id)s].%(ext)s'),
                    'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '320'}],
                    'progress_hooks': [progresso_hook],
                    'quiet': False,
                    'no_warnings': False,
                }
                tipo_txt = "Áudio (MP3)"
            else:
                formato = resolucoes[var_resolucao.get()]
                ydl_opts = {
                    'format': formato,
                    'outtmpl': os.path.join(pasta_destino, '%(title)s [%(id)s].%(ext)s'),
                    'merge_output_format': 'mp4',
                    'progress_hooks': [progresso_hook],
                    'concurrent_fragment_downloads': 15,
                    'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
                }
                tipo_txt = f"Vídeo - {var_resolucao.get()}"

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                titulo = info.get('title', 'Arquivo')

            messagebox.showinfo("Concluído", f'"{titulo}" baixado com sucesso!\n\n{tipo_txt}\n\nLocal: {pasta_destino}')
            label_status.config(text="Concluído", fg="#00ff88")
        except Exception as e:
            erro = str(e).lower()
            if "ffmpeg" in erro or "postprocessor" in erro:
                messagebox.showwarning("FFmpeg necessário", "Para 1080p, 4K ou MP3, coloque ffmpeg.exe e ffprobe.exe na mesma pasta do programa.")
            else:
                messagebox.showerror("Erro", str(e))
            label_status.config(text="Erro", fg="red")
        finally:
            btn_baixar.config(state="normal")
            progress_bar.pack_forget()
            progresso_var.set(0)

    threading.Thread(target=thread, daemon=True).start()

# ------------------- INTERFACE -------------------
tk.Label(janela, text="PK Downloader", font=("Segoe UI", 28, "bold"), fg="#00ff88", bg="#0d1117").pack(pady=25)
tk.Label(janela, text="YouTube • Instagram • TikTok • Twitter/X • Facebook • SoundCloud • +1500 sites", font=("Arial", 10), fg="#888", bg="#0d1117").pack(pady=(0,20))

entry_link = tk.Entry(janela, width=82, font=("Consolas", 11), bg="#161b22", fg="white", insertbackground="white")
entry_link.pack(pady=10, ipady=12)
entry_link.focus()

# Tipo
frame_tipo = tk.Frame(janela, bg="#0d1117")
frame_tipo.pack(pady=15)
tk.Radiobutton(frame_tipo, text="Vídeo (MP4)", variable=var_tipo, value="video", fg="white", bg="#0d1117", selectcolor="#333", font=("Arial", 12)).pack(side=tk.LEFT, padx=60)
tk.Radiobutton(frame_tipo, text="Áudio (MP3)", variable=var_tipo, value="audio", fg="white", bg="#0d1117", selectcolor="#333", font=("Arial", 12)).pack(side=tk.LEFT, padx=60)

# Resolução (Somente em vídeo)
frame_res = tk.Frame(janela, bg="#0d1117")
tk.Label(frame_res, text="Resolução:", fg="white", bg="#0d1117", font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
combo_res = ttk.Combobox(frame_res, textvariable=var_resolucao, values=list(resolucoes.keys()), state="readonly", width=30)
combo_res.pack(side=tk.LEFT)
combo_res.set("720p")

# Pasta
frame_pasta = tk.Frame(janela, bg="#0d1117")
frame_pasta.pack(pady=15)
tk.Button(frame_pasta, text="Escolher pasta", command=escolher_pasta, bg="#333", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=10)
label_pasta = tk.Label(frame_pasta, text=f"Salvando em:\n{pasta_destino}", fg="#aaa", bg="#0d1117", font=("Arial", 9))
label_pasta.pack(side=tk.LEFT, padx=10)

# Botão baixar
btn_baixar = tk.Button(janela, text="BAIXAR AGORA", font=("Arial", 18, "bold"), bg="#00ff88", fg="black", command=executar_download, height=2, width=32, cursor="hand2")
btn_baixar.pack(pady=25)

label_status = tk.Label(janela, text="Aguardando link...", fg="#888", bg="#0d1117", font=("Arial", 11))
label_status.pack(pady=5)

progress_bar = ttk.Progressbar(janela, variable=progresso_var, maximum=100, length=620, mode="determinate")
style = ttk.Style()
style.configure("TProgressbar", background='#00ff88', troughcolor='#333')

# Estado inicial
atualizar_resolucao()

janela.mainloop()