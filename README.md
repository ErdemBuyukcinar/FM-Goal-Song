# ⚽ FM Gol Müziği Asistanı

Football Manager (veya skor tabelası olan herhangi bir oyun) oynarken takımınız gol attığında belirlediğiniz gol müziğini otomatik olarak çalan bir Python asistanı. 

Uygulama, ekranda belirlediğiniz skor bölgesini anlık olarak okur (OCR) ve skor arttığında müziği tetikler.

## 🚀 Özellikler
* **Canlı Skor Takibi:** Tesseract OCR ile ekrandaki skoru gerçek zamanlı okur.
* **Özelleştirilebilir Ses:** Kendi gol müziğinizi (.mp3, .wav, .ogg) seçebilir, çalma süresini ve ses seviyesini ayarlayabilirsiniz.
* **Klavye Kısayolları:** Oyunu alta almadan tek tuşla (örn: F9) takibi başlatıp durdurabilirsiniz.
* **Çoklu Dil Desteği:** Türkçe ve İngilizce arayüz seçeneği.
* **Otomatik Kayıt:** Ayarlarınız arka planda kaydedilir, uygulamayı her açtığınızda tekrar ayarlamak zorunda kalmazsınız.

## 🛠️ Gereksinimler ve Kurulum

Uygulamanın düzgün çalışması için bilgisayarınızda **Python** ve **Tesseract OCR** kurulu olmalıdır.

### 1. Tesseract OCR Kurulumu (Zorunlu)
Uygulamanın ekrandaki sayıları okuyabilmesi için Tesseract gereklidir.
* [Tesseract Windows Kurulum Dosyası](https://github.com/UB-Mannheim/tesseract/wiki)'nı indirin ve kurun.
* **Önemli:** Kurulumu varsayılan dizine (`C:\Program Files\Tesseract-OCR`) yapın. Farklı bir yere kurarsanız kaynak kod içindeki `TESSERACT_PATH` değişkenini kendi yolunuza göre güncellemeniz gerekir.

### 2. Projeyi Çalıştırma
Projeyi bilgisayarınıza indirdikten sonra proje klasöründe terminali (veya komut satırını) açın ve gerekli kütüphaneleri kurun:

```bash
pip install customtkinter
pip install pygame
pip install keyboard
pip install pytesseract
pip install Pillow
```

###ENGLISH
# ⚽ FM Goal Music Assistant

A Python assistant that automatically plays your selected goal music when your team scores a goal while playing Football Manager (or any game with a scoreboard). 

The application reads the score area you specify on the screen in real-time (OCR) and triggers the music when the score increases.

## 🚀 Features
* **Live Score Tracking:** Reads the score on the screen in real-time using Tesseract OCR.
* **Customizable Audio:** Choose your own goal music (.mp3, .wav, .ogg) and adjust the playback duration and volume.
* **Keyboard Shortcuts:** Start or stop tracking with a single key (e.g., F9) without minimizing the game.
* **Multi-Language Support:** Turkish and English interface options.
* **Auto-Save:** Your settings are saved in the background, so you don't have to reconfigure them every time you open the app.

## 🛠️ Requirements and Installation

To run the application properly, you must have **Python** and **Tesseract OCR** installed on your computer.

### 1. Tesseract OCR Installation (Required)
Tesseract is required for the application to read the numbers on the screen.
* Download and install the [Tesseract Windows Installer](https://github.com/UB-Mannheim/tesseract/wiki).
* **Important:** Install it in the default directory (`C:\Program Files\Tesseract-OCR`). If you install it in a different location, you will need to update the `TESSERACT_PATH` variable in the source code according to your path.

### 2. Running the Project
After downloading the project to your computer, open a terminal (or command prompt) in the project folder and install the required libraries:

```bash
pip install customtkinter
pip install pygame
pip install keyboard
pip install pytesseract
pip install Pillow
