# Setup WhatsApp Bot di SSH Server (Tanpa GUI)

## Prerequisites

1. **SSH Access** ke server Linux
2. **Playwright dengan browser** terinstall
3. **Python 3.8+** terinstall

## Instalasi di SSH Server

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libxshmfence1 \
    libxss1 \
    fonts-liberation
```

### 2. Setup Display untuk Headless Browser

```bash
# Set display (walaupun headless, beberapa browser perlu ini)
export DISPLAY=:99

# Atau install virtual display (Xvfb)
sudo apt-get install -y xvfb
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99
```

## Menggunakan Add Session di SSH

### Cara 1: Menggunakan --headless flag

```bash
python cli/wa_cli.py --action add-session --session-name testing --headless
```

**Hasil:**
- QR code akan disimpan ke file: `sessions/testing_qr.png`
- File bisa di-download via SCP/SFTP
- Terminal akan menampilkan path file

### Cara 2: Download QR Code File

Setelah menjalankan add-session, QR code akan tersimpan di:
```
sessions/{session_name}_qr.png
```

**Download dari server:**
```bash
# Via SCP (dari local machine)
scp user@server:/path/to/waBlast/sessions/testing_qr.png .

# Via SFTP
sftp user@server
get sessions/testing_qr.png
```

### Cara 3: Setup dengan VNC (Optional)

Jika ingin melihat browser langsung:

```bash
# Install VNC server
sudo apt-get install -y tigervnc-standalone-server

# Start VNC (dari SSH)
export DISPLAY=:1
vncserver :1 -geometry 1920x1080 -depth 24

# Connect via VNC client
# Address: server_ip:5901
```

Lalu jalankan tanpa `--headless`:
```bash
python cli/wa_cli.py --action add-session --session-name testing
```

## Langkah-langkah Setup Session di SSH

### 1. Buat Session Baru (Headless)

```bash
python cli/wa_cli.py --action add-session \
  --session-name production \
  --headless
```

### 2. Download QR Code

QR code akan tersimpan di `sessions/production_qr.png`

```bash
# Download ke local machine
scp user@server:/path/to/waBlast/sessions/production_qr.png .
```

### 3. Scan QR Code

- Buka file `production_qr.png` di komputer local
- Buka WhatsApp mobile app
- Settings → Linked Devices → Link a Device
- Scan QR code dari file gambar

### 4. Verifikasi Session

Setelah scan, sistem akan otomatis mendeteksi login dan menyimpan session.

## Troubleshooting

### Error: "No display"

```bash
# Setup virtual display
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 &
```

### QR Code tidak muncul di file

- Pastikan browser berhasil launch
- Check permission folder `sessions/`
- Lihat error message di terminal

### Session tidak tersimpan

- Pastikan folder `sessions/` writable
- Check disk space
- Pastikan autentikasi berhasil (tunggu sampai muncul "authenticated successfully")

## Best Practices untuk SSH

1. **Gunakan Screen/Tmux:**
```bash
screen -S whatsapp
python cli/wa_cli.py --action add-session --headless
# Ctrl+A+D untuk detach
```

2. **Background Process:**
```bash
nohup python cli/wa_cli.py --action add-session --headless > session.log 2>&1 &
```

3. **Monitor Progress:**
```bash
tail -f session.log
```

## Workflow Lengkap di SSH

```bash
# 1. Setup environment
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 &

# 2. Create session
python cli/wa_cli.py --action add-session \
  --session-name my_session \
  --headless

# 3. Download QR (dari local machine)
scp user@server:sessions/my_session_qr.png .

# 4. Scan QR code dengan WhatsApp mobile

# 5. Verify session tersimpan
python cli/wa_cli.py --action list-sessions

# 6. Start sending
python cli/wa_cli.py --action send \
  --numbers data/contacts.txt \
  --template templates/message.txt \
  --personalize
```

## Catatan Penting

- QR code file akan otomatis dihapus setelah autentikasi berhasil
- Jika timeout, file QR tetap ada untuk di-scan manual
- Session tersimpan di `sessions/{session_name}/` dan bisa digunakan kembali tanpa scan QR

