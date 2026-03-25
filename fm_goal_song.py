import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import pygame
import keyboard
import time
import threading
import os
import json
import pytesseract
import re
from PIL import ImageGrab, ImageTk, ImageEnhance, ImageOps

# Tesseract varsayılan kurulum yolu
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# Tema ayarları
ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("blue")  

TRANSLATIONS = {
    "TR": {
        "title": "FM Gol Müziği Asistanı",
        "main_header": "⚽ FOOTBALL MANAGER GOL MÜZİĞİ",
        "music_settings": "🎵 Şarkı ve Ses Ayarları",
        "browse": "Gözat",
        "duration": "Süre (sn):",
        "volume": "🔊 Ses:",
        "coords": "📍 Skor Koordinatları",
        "info_tooltip": "KUSURSUZ ÇALIŞMASI İÇİN ÖNEMLİ:\nTakımınızın sadece gol sayısının yazdığı rakamı çok dar\nbir kutu içine alarak seçin.\n\nÖrn: FEN 1 - 0 GAL yazıyorsa, logoları veya rakip skoru dahil\netmeyin. Sadece '1' rakamını seçin.",
        "select_screen": "🎯 Ekranda Seç",
        "save": "💾 Kaydet",
        "hotkey": "⌨️ Başlat/Durdur Kısayolu:",
        "assign_key": "Tuşu Ata",
        "start_tracking": "▶ GOL TAKİBİNİ BAŞLAT",
        "stop_tracking": "⏹ TAKİBİ DURDUR",
        "status_waiting": "Durum: Bekleniyor...",
        "status_tracking": "Durum: Skorunuz izleniyor... Gözler skorda!",
        "status_stopped": "Durum: İzleme durduruldu.",
        "status_goal": "GOOOOOL! Yeni Skor: {}",
        "msg_success": "Başarılı",
        "msg_hotkey_set": "Kısayol '{}' olarak ayarlandı.\nOyundayken bu tuşa basarak takibi başlatıp durdurabilirsiniz!",
        "msg_error": "Hata",
        "msg_invalid_hotkey": "Geçersiz bir kısayol girdiniz! (Örn: f9, alt+k)",
        "msg_small_area": "Çok küçük bir alan seçtiniz, lütfen sürükleyerek net bir kutu çizin.",
        "msg_settings_saved": "Tüm ayarlar kaydedildi!",
        "msg_missing": "Eksik",
        "msg_no_tesseract": "Tesseract bulunamadı! Lütfen kurulu olduğundan emin olun.",
        "msg_no_music": "Lütfen önce çalınacak Gol Şarkısını seçin!",
        "msg_no_coords": "Lütfen önce ekranda skorun yerini seçin!",
    },
    "EN": {
        "title": "FM Goal Music Assistant",
        "main_header": "⚽ FOOTBALL MANAGER GOAL MUSIC",
        "music_settings": "🎵 Song and Volume Settings",
        "browse": "Browse",
        "duration": "Duration (s):",
        "volume": "🔊 Volume:",
        "coords": "📍 Score Coordinates",
        "info_tooltip": "CRITICAL FOR PERFECT OPERATION:\nSelect ONLY the number showing your team's goals,\nmaking the box as tight as possible.\n\nE.g.: If it says FEN 1 - 0 GAL, do not include logos\nor the opponent's score. Select ONLY the '1'.",
        "select_screen": "🎯 Select Screen",
        "save": "💾 Save",
        "hotkey": "⌨️ Start/Stop Hotkey:",
        "assign_key": "Assign Key",
        "start_tracking": "▶ START GOAL TRACKING",
        "stop_tracking": "⏹ STOP TRACKING",
        "status_waiting": "Status: Waiting...",
        "status_tracking": "Status: Tracking your score... Eyes on the score!",
        "status_stopped": "Status: Tracking stopped.",
        "status_goal": "GOOOOAL! New Score: {}",
        "msg_success": "Success",
        "msg_hotkey_set": "Hotkey set to '{}'.\nPress this key while in-game to start/stop tracking!",
        "msg_error": "Error",
        "msg_invalid_hotkey": "Invalid hotkey entered! (e.g.: f9, alt+k)",
        "msg_small_area": "Area too small, please drag to draw a clear box.",
        "msg_settings_saved": "All settings saved!",
        "msg_missing": "Missing",
        "msg_no_tesseract": "Tesseract not found! Please ensure it is installed.",
        "msg_no_music": "Please select a Goal Song to play first!",
        "msg_no_coords": "Please select the score location on the screen first!",
    }
}

class ToolTip:
    def __init__(self, widget, text='widget info'):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.tw = None

    def enter(self, event=None):
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tw, text=self.text, justify='left',
                         background="#2c3e50", foreground="white", relief='solid', borderwidth=1,
                         font=("Arial", 10, "bold"), padx=10, pady=5)
        label.pack(ipadx=1)

    def leave(self, event=None):
        if self.tw:
            self.tw.destroy()
            self.tw = None

class FMGolMuzigiUygulamasi:
    def __init__(self, root):
        self.root = root
        self.root.geometry("520x560")
        self.root.resizable(False, False)

        self.ayar_dosyasi = "fm_ayarlari.json"
        self.takip_aktif = False
        self.son_skor = None
        self.aktif_kisayol = None
        self.dil = "TR"

        self.arayuz_olustur()
        self.ayarlari_yukle()

    def get_text(self, key):
        return TRANSLATIONS[self.dil][key]

    def arayuz_olustur(self):
        baslik_font = ctk.CTkFont(family="Roboto", size=14, weight="bold")
        normal_font = ctk.CTkFont(family="Roboto", size=12)

        self.ana_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.ana_frame.pack(fill="both", expand=True, padx=20, pady=15)

        ust_frame = ctk.CTkFrame(self.ana_frame, fg_color="transparent")
        ust_frame.pack(fill="x", pady=(0, 10))
        
        self.baslik = ctk.CTkLabel(ust_frame, text="", font=ctk.CTkFont(family="Roboto", size=18, weight="bold"), text_color="#3498db")
        self.baslik.pack(side="left", expand=True)

        self.dil_secici = ctk.CTkOptionMenu(ust_frame, values=["TR", "EN"], width=60, command=self.dil_degistir)
        self.dil_secici.set(self.dil)
        self.dil_secici.pack(side="right")

        kart1 = ctk.CTkFrame(self.ana_frame, corner_radius=10)
        kart1.pack(fill="x", pady=5, ipady=10)
        
        self.kart1_baslik = ctk.CTkLabel(kart1, text="", font=baslik_font)
        self.kart1_baslik.pack(anchor="w", padx=15, pady=(10, 5))
        
        sarki_frame = ctk.CTkFrame(kart1, fg_color="transparent")
        sarki_frame.pack(fill="x", padx=15, pady=5)
        self.skor_muzik_yolu = ctk.StringVar()
        
        self.gozat_btn = ctk.CTkButton(sarki_frame, text="", command=self.gol_muzik_sec, width=70)
        self.gozat_btn.pack(side="left", padx=(0, 10))
        
        ctk.CTkEntry(sarki_frame, textvariable=self.skor_muzik_yolu, state="readonly", width=340).pack(side="left")

        ayarlar_frame = ctk.CTkFrame(kart1, fg_color="transparent")
        ayarlar_frame.pack(fill="x", padx=15, pady=(10, 0))
        
        self.sure_label = ctk.CTkLabel(ayarlar_frame, text="", font=normal_font)
        self.sure_label.pack(side="left")
        
        self.sure_entry = ctk.CTkEntry(ayarlar_frame, width=50, height=25)
        self.sure_entry.insert(0, "15")
        self.sure_entry.pack(side="left", padx=(5, 20))
        
        self.ses_label = ctk.CTkLabel(ayarlar_frame, text="", font=normal_font)
        self.ses_label.pack(side="left")
        
        self.ses_slider = ctk.CTkSlider(ayarlar_frame, from_=0, to=100, command=self.ayarlari_kaydet_event)
        self.ses_slider.set(50)
        self.ses_slider.pack(side="left", padx=(5, 0), fill="x", expand=True)

        kart2 = ctk.CTkFrame(self.ana_frame, corner_radius=10)
        kart2.pack(fill="x", pady=10, ipady=10)
        
        baslik_frame = ctk.CTkFrame(kart2, fg_color="transparent")
        baslik_frame.pack(fill="x", padx=15, pady=(10, 5))
        
        self.kart2_baslik = ctk.CTkLabel(baslik_frame, text="", font=baslik_font)
        self.kart2_baslik.pack(side="left")
        
        bilgi_ikon = ctk.CTkLabel(baslik_frame, text=" ℹ️ ", font=ctk.CTkFont(size=16), text_color="#f39c12", cursor="hand2")
        bilgi_ikon.pack(side="left", padx=5)
        self.bilgi_tooltip = ToolTip(bilgi_ikon, text="")

        secim_frame = ctk.CTkFrame(kart2, fg_color="transparent")
        secim_frame.pack(fill="x", padx=15, pady=5)
        
        self.ekran_sec_btn = ctk.CTkButton(secim_frame, text="", command=self.ekran_secim_baslat, width=100, fg_color="#2ecc71", hover_color="#27ae60")
        self.ekran_sec_btn.pack(side="left", padx=(0, 15))
        
        self.skor_x = ctk.CTkEntry(secim_frame, width=50, height=28, placeholder_text="X"); self.skor_x.pack(side="left", padx=2)
        self.skor_y = ctk.CTkEntry(secim_frame, width=50, height=28, placeholder_text="Y"); self.skor_y.pack(side="left", padx=2)
        self.skor_w = ctk.CTkEntry(secim_frame, width=50, height=28, placeholder_text="W"); self.skor_w.pack(side="left", padx=2)
        self.skor_h = ctk.CTkEntry(secim_frame, width=50, height=28, placeholder_text="H"); self.skor_h.pack(side="left", padx=2)

        self.kaydet_btn = ctk.CTkButton(secim_frame, text="", command=self.ayarlari_kaydet_mesajli, width=60, fg_color="gray", hover_color="#555555")
        self.kaydet_btn.pack(side="right", padx=(10, 0))

        kisayol_frame = ctk.CTkFrame(self.ana_frame, fg_color="transparent")
        kisayol_frame.pack(fill="x", pady=(10, 5))

        self.kisayol_label = ctk.CTkLabel(kisayol_frame, text="", font=baslik_font)
        self.kisayol_label.pack(side="left", padx=(0, 10))
        
        self.kisayol_entry = ctk.CTkEntry(kisayol_frame, width=80, height=28)
        self.kisayol_entry.insert(0, "f9")
        self.kisayol_entry.pack(side="left", padx=5)

        self.tusu_ata_btn = ctk.CTkButton(kisayol_frame, text="", command=self.kisayol_ata, width=80, fg_color="#8e44ad", hover_color="#9b59b6")
        self.tusu_ata_btn.pack(side="left", padx=5)

        self.takip_buton = ctk.CTkButton(self.ana_frame, text="", command=self.takip_toggle, height=45, font=ctk.CTkFont(size=15, weight="bold"))
        self.takip_buton.pack(fill="x", pady=(10, 10))
        
        self.skor_durum_label = ctk.CTkLabel(self.ana_frame, text="", text_color="gray")
        self.skor_durum_label.pack()

        self.metinleri_guncelle()

    def metinleri_guncelle(self):
        self.root.title(self.get_text("title"))
        self.baslik.configure(text=self.get_text("main_header"))
        self.kart1_baslik.configure(text=self.get_text("music_settings"))
        self.gozat_btn.configure(text=self.get_text("browse"))
        self.sure_label.configure(text=self.get_text("duration"))
        self.ses_label.configure(text=self.get_text("volume"))
        self.kart2_baslik.configure(text=self.get_text("coords"))
        self.bilgi_tooltip.text = self.get_text("info_tooltip")
        self.ekran_sec_btn.configure(text=self.get_text("select_screen"))
        self.kaydet_btn.configure(text=self.get_text("save"))
        self.kisayol_label.configure(text=self.get_text("hotkey"))
        self.tusu_ata_btn.configure(text=self.get_text("assign_key"))
        
        if self.takip_aktif:
            self.takip_buton.configure(text=self.get_text("stop_tracking"))
            if self.son_skor is None:
                self.skor_durum_label.configure(text=self.get_text("status_tracking"))
        else:
            self.takip_buton.configure(text=self.get_text("start_tracking"))
            self.skor_durum_label.configure(text=self.get_text("status_waiting"))

    def dil_degistir(self, yeni_dil):
        self.dil = yeni_dil
        self.metinleri_guncelle()
        self.ayarlari_kaydet()

    def kisayol_ata(self, sessiz=False):
        yeni_kisayol = self.kisayol_entry.get().strip()
        if not yeni_kisayol:
            return

        if self.aktif_kisayol:
            try: 
                keyboard.remove_hotkey(self.aktif_kisayol)
            except Exception as e: 
                print(f"Kısayol kaldırılamadı: {e}")

        try:
            keyboard.add_hotkey(yeni_kisayol, lambda: self.root.after(0, self.takip_toggle))
            self.aktif_kisayol = yeni_kisayol
            self.ayarlari_kaydet()
            
            if not sessiz:
                mesaj = self.get_text("msg_hotkey_set").format(yeni_kisayol)
                messagebox.showinfo(self.get_text("msg_success"), mesaj)
        except ValueError:
            if not sessiz:
                messagebox.showerror(self.get_text("msg_error"), self.get_text("msg_invalid_hotkey"))

    def ekran_secim_baslat(self):
        self.root.withdraw()
        time.sleep(0.5)
        
        ekran_resmi = ImageGrab.grab()
        
        self.secim_penceresi = ctk.CTkToplevel(self.root)
        self.secim_penceresi.attributes('-fullscreen', True)
        self.secim_penceresi.attributes('-topmost', True)
        self.secim_penceresi.config(cursor="cross")
        
        self.canvas = tk.Canvas(self.secim_penceresi, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.tk_ekran_resmi = ImageTk.PhotoImage(ekran_resmi)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_ekran_resmi)
        
        self.baslangic_x = None; self.baslangic_y = None; self.cizilen_kutu = None
        
        self.canvas.bind("<ButtonPress-1>", self.fare_basildi)
        self.canvas.bind("<B1-Motion>", self.fare_suruklendi)
        self.canvas.bind("<ButtonRelease-1>", self.fare_birakildi)
        self.secim_penceresi.bind("<Escape>", lambda e: self.secimi_iptal_et())

    def fare_basildi(self, event):
        self.baslangic_x = event.x
        self.baslangic_y = event.y
        self.cizilen_kutu = self.canvas.create_rectangle(self.baslangic_x, self.baslangic_y, 1, 1, outline='#e74c3c', width=3)

    def fare_suruklendi(self, event):
        self.canvas.coords(self.cizilen_kutu, self.baslangic_x, self.baslangic_y, event.x, event.y)

    def fare_birakildi(self, event):
        x = min(self.baslangic_x, event.x)
        y = min(self.baslangic_y, event.y)
        w = abs(self.baslangic_x - event.x)
        h = abs(self.baslangic_y - event.y)
        
        self.secim_penceresi.destroy()
        self.root.deiconify()
        
        if w < 5 or h < 5:
            messagebox.showwarning(self.get_text("msg_error"), self.get_text("msg_small_area"))
            return

        self.skor_x.delete(0, tk.END); self.skor_x.insert(0, str(x))
        self.skor_y.delete(0, tk.END); self.skor_y.insert(0, str(y))
        self.skor_w.delete(0, tk.END); self.skor_w.insert(0, str(w))
        self.skor_h.delete(0, tk.END); self.skor_h.insert(0, str(h))
            
        self.ayarlari_kaydet()

    def secimi_iptal_et(self):
        self.secim_penceresi.destroy()
        self.root.deiconify()

    def ayarlari_kaydet_event(self, value=None):
        self.ayarlari_kaydet()

    def ayarlari_kaydet_mesajli(self):
        self.ayarlari_kaydet()
        messagebox.showinfo(self.get_text("msg_success"), self.get_text("msg_settings_saved"))

    def ayarlari_kaydet(self):
        ayarlar = {
            "dil": self.dil,
            "gol_sarkisi": self.skor_muzik_yolu.get(),
            "sure": self.sure_entry.get(),
            "ses": self.ses_slider.get(),
            "kisayol": self.kisayol_entry.get(),
            "skor_koordinatlar": [self.skor_x.get(), self.skor_y.get(), self.skor_w.get(), self.skor_h.get()]
        }
        try:
            with open(self.ayar_dosyasi, "w", encoding="utf-8") as f:
                json.dump(ayarlar, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Ayar kaydetme hatası: {e}")

    def ayarlari_yukle(self):
        if os.path.exists(self.ayar_dosyasi):
            try:
                with open(self.ayar_dosyasi, "r", encoding="utf-8") as f:
                    skor = json.load(f)
                    
                    self.dil = skor.get("dil", "TR")
                    self.dil_secici.set(self.dil)
                    
                    self.skor_muzik_yolu.set(skor.get("gol_sarkisi", ""))
                    self.sure_entry.delete(0, tk.END); self.sure_entry.insert(0, skor.get("sure", "15"))
                    self.ses_slider.set(float(skor.get("ses", 50)))
                    
                    self.kisayol_entry.delete(0, tk.END)
                    self.kisayol_entry.insert(0, skor.get("kisayol", "f9"))
                    self.kisayol_ata(sessiz=True) 
                    
                    koor = skor.get("skor_koordinatlar", ["", "", "", ""])
                    self.skor_x.delete(0, tk.END); self.skor_x.insert(0, koor[0])
                    self.skor_y.delete(0, tk.END); self.skor_y.insert(0, koor[1])
                    self.skor_w.delete(0, tk.END); self.skor_w.insert(0, koor[2])
                    self.skor_h.delete(0, tk.END); self.skor_h.insert(0, koor[3])

                    self.metinleri_guncelle()
            except Exception as e:
                print(f"Ayar yükleme hatası: {e}")

    def gol_muzik_sec(self):
        dosya = filedialog.askopenfilename(filetypes=[("Ses Dosyaları", "*.mp3 *.wav *.ogg")])
        if dosya: 
            self.skor_muzik_yolu.set(dosya)
            self.ayarlari_kaydet()

    def muzik_cal_tetikle(self):
        dosya = self.skor_muzik_yolu.get()
        if not dosya:
            return
            
        try: 
            sure = float(self.sure_entry.get())
        except ValueError: 
            sure = 15.0 
            
        ses_oran = self.ses_slider.get() / 100.0 
        threading.Thread(target=self.muzik_cal, args=(dosya, sure, ses_oran), daemon=True).start()

    def muzik_cal(self, dosya, sure, ses_oran):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.stop() 
            pygame.mixer.music.set_volume(ses_oran)
            pygame.mixer.music.load(dosya)
            pygame.mixer.music.play()
            time.sleep(sure)
            pygame.mixer.music.stop()
        except Exception as e:
            print(f"Müzik çalınamadı: {e}")

    def takip_toggle(self):
        if not os.path.exists(pytesseract.pytesseract.tesseract_cmd):
            messagebox.showerror(self.get_text("msg_error"), self.get_text("msg_no_tesseract"))
            return
        if not self.skor_muzik_yolu.get():
            messagebox.showwarning(self.get_text("msg_missing"), self.get_text("msg_no_music"))
            return
        if not self.skor_x.get():
            messagebox.showwarning(self.get_text("msg_missing"), self.get_text("msg_no_coords"))
            return

        if not self.takip_aktif:
            self.ayarlari_kaydet()
            self.takip_aktif = True
            self.son_skor = None
            
            self.takip_buton.configure(text=self.get_text("stop_tracking"), fg_color="#e74c3c", hover_color="#c0392b")
            self.skor_durum_label.configure(text=self.get_text("status_tracking"), text_color="#2ecc71")
            
            threading.Thread(target=self.skor_okuma_dongusu, daemon=True).start()
        else:
            self.takip_aktif = False
            self.takip_buton.configure(text=self.get_text("start_tracking"), fg_color=['#3a7ebf', '#1f538d'], hover_color=['#325882', '#14375e'])
            self.skor_durum_label.configure(text=self.get_text("status_stopped"), text_color="gray")

    def skor_okuma_dongusu(self):
        while self.takip_aktif:
            try:
                x = int(self.skor_x.get()); y = int(self.skor_y.get())
                w = int(self.skor_w.get()); h = int(self.skor_h.get())
                
                ekran_kesiti = ImageGrab.grab(bbox=(x, y, x + w, y + h))
                ekran_kesiti = ImageOps.grayscale(ekran_kesiti)
                enhancer = ImageEnhance.Contrast(ekran_kesiti)
                ekran_kesiti = enhancer.enhance(2.0)
                
                okunan_metin = pytesseract.image_to_string(ekran_kesiti, config='--psm 10 -c tessedit_char_whitelist=0123456789')
                sayilar = re.findall(r'\d+', okunan_metin)
                
                if sayilar: 
                    guncel_skor = int(sayilar[0]) 
                    
                    if self.son_skor is None:
                        self.son_skor = guncel_skor
                    elif guncel_skor > self.son_skor:
                        mesaj = self.get_text("status_goal").format(guncel_skor)
                        self.skor_durum_label.configure(text=mesaj, text_color="#f1c40f")
                        self.muzik_cal_tetikle()
                        self.son_skor = guncel_skor 
            except Exception as e:
                print(f"Okuma döngüsü hatası: {e}")
            
            time.sleep(1)

if __name__ == "__main__":
    try:
        pygame.mixer.init()
    except Exception as e:
        print(f"Ses modülü başlatılamadı: {e}")
        
    root = ctk.CTk()
    uygulama = FMGolMuzigiUygulamasi(root)
    root.mainloop()
