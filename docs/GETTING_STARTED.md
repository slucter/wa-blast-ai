# Getting Started Guide

Panduan lengkap untuk memulai menggunakan WhatsApp Bot ini dari awal.

## 📋 Daftar Isi

1. [Instalasi](#instalasi)
2. [Setup Session Pertama](#setup-session-pertama)
3. [Mengirim Pesan Pertama](#mengirim-pesan-pertama)
4. [Template & Personalization](#template--personalization)
5. [Multi-Session Setup](#multi-session-setup)

## 🚀 Instalasi

### Windows

```powershell
# Jalankan installer PowerShell
.\install.ps1
```

### Linux/macOS

```bash
# Berikan permission execute
chmod +x install.sh

# Jalankan installer
./install.sh
```

### Manual Install

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install Playwright browsers
playwright install chromium

# 3. Install system dependencies (Linux only)
playwright install-deps chromium

# 4. Buat direktori
mkdir -p sessions logs data templates
```

## 🔐 Setup Session Pertama

### Mode GUI (dengan Browser Window)

```bash
python cli/wa_cli.py --action add-session --session-name my_session
```

**Langkah-langkah:**
1. Browser akan terbuka otomatis
2. QR code akan muncul di browser
3. Buka WhatsApp di HP Anda
4. Scan QR code yang muncul
5. Tunggu sampai muncul "✓ Session authenticated"
6. Tekan Ctrl+C untuk menutup

### Mode Headless (SSH/VPS)

```bash
python cli/wa_cli.py --action add-session --session-name my_session --headless
```

**Langkah-langkah:**
1. QR code akan tersimpan di `sessions/my_session_qr.png`
2. Download file QR code:
   ```bash
   # Via SCP
   scp user@server:/path/to/sessions/my_session_qr.png ./
   
   # Via SFTP
   # Gunakan client seperti FileZilla atau WinSCP
   ```
3. Buka file QR code di komputer lokal
4. Scan dengan WhatsApp di HP Anda
5. Bot akan otomatis mendeteksi setelah scan berhasil

**Catatan:**
- QR code otomatis refresh setiap ~20 detik
- QR code baru akan ditampilkan di terminal dan disimpan ke file
- Tunggu sampai muncul "✓ Session authenticated"

## 💬 Mengirim Pesan Pertama

### 1. Kirim ke Satu Nomor

```bash
python cli/wa_cli.py --action send \
  --phone "08123456789" \
  --message "Hello, this is a test message!"
```

### 2. Kirim ke Multiple Nomor (dari File)

**Buat file contacts:**
```txt
# data/contacts.txt
08123456789
08123456790
08123456791
```

**Kirim pesan:**
```bash
python cli/wa_cli.py --action send \
  --numbers data/contacts.txt \
  --message "Hello everyone!"
```

### 3. Menggunakan Template

**Buat template:**
```txt
# templates/welcome.txt
Hi {name}!

Welcome to our service. We're glad to have you!

Best regards,
Team
```

**Kirim dengan template:**
```bash
python cli/wa_cli.py --action send \
  --numbers data/contacts.txt \
  --template templates/welcome.txt
```

## 🎨 Template & Personalization

### Template Dasar

```txt
# templates/simple.txt
Selamat pagi!

Ini adalah pesan dari bot kami.
```

### Template dengan Placeholder

```txt
# templates/personalized.txt
Halo {name},

Terima kasih telah bergabung!

Salam,
Admin
```

### Template Multi-Bubble

Baris kosong = bubble chat baru:

```txt
# templates/multibubble.txt
Halo {name}!

[baris kosong di sini]

Silakan cek produk terbaru kami.
```

### Template dengan Line Break (`\n`)

Gunakan `\n` untuk baris baru dalam 1 bubble:

```txt
# templates/details.txt
Detail Produk:\n\nNama: {product}\nHarga: {price}\nStok: {stock}
```

### Personalization (Auto-Greeting + Name + Address)

**Format file contacts dengan personalization:**
```txt
# data/contacts_personalized.txt
08123456789|John Doe|Jl. Sudirman No. 123
08123456790|Jane Smith|Jl. Thamrin No. 456
```

**Kirim dengan personalization:**
```bash
python cli/wa_cli.py --action send \
  --numbers data/contacts_personalized.txt \
  --template templates/message.txt \
  --personalize
```

**Hasil output:**
```
Selamat siang *John Doe*.

Alamat : Jl. Sudirman No. 123

[isi template message.txt]
```

## 🔄 Multi-Session Setup

### Menambah Multiple Sessions

```bash
# Session 1
python cli/wa_cli.py --action add-session --session-name session_1

# Session 2
python cli/wa_cli.py --action add-session --session-name session_2

# Session 3
python cli/wa_cli.py --action add-session --session-name session_3
```

### Menggunakan Session Tertentu

```bash
# Gunakan 1 session spesifik
python cli/wa_cli.py --action send \
  --numbers data/contacts.txt \
  --template templates/message.txt \
  --use-sessions "session_1"

# Gunakan beberapa session
python cli/wa_cli.py --action send \
  --numbers data/contacts.txt \
  --template templates/message.txt \
  --use-sessions "session_1,session_2"
```

### Strategi Distribusi

```bash
# Round-robin (bagi rata)
python cli/wa_cli.py --action send \
  --numbers data/contacts.txt \
  --template templates/message.txt \
  --use-sessions "session_1,session_2,session_3" \
  --session-strategy round-robin

# Random (acak)
python cli/wa_cli.py --action send \
  --numbers data/contacts.txt \
  --template templates/message.txt \
  --use-sessions "session_1,session_2,session_3" \
  --session-strategy random

# Weighted (berdasarkan health score)
python cli/wa_cli.py --action send \
  --numbers data/contacts.txt \
  --template templates/message.txt \
  --use-sessions "session_1,session_2,session_3" \
  --session-strategy weighted
```

## 📊 Tips & Best Practices

### 1. Mulai dengan Session Sedikit
```bash
# Mulai dengan 1-2 session dulu
python cli/wa_cli.py --action send \
  --sessions 1 \
  ...
```

### 2. Monitor Session Health
- List session secara berkala
- Hapus session yang bermasalah
- Buat session baru jika diperlukan

### 3. Gunakan Template dengan Personalization
- Meningkatkan engagement
- Terlihat lebih natural
- Mengurangi risiko spam

### 4. Rotasi Session
- Hapus dan buat ulang session secara berkala
- Jangan gunakan session yang sama terus-menerus
- Distribusikan beban ke semua session

### 5. Delay yang Wajar
- Jangan terlalu cepat (< 3 detik)
- Gunakan delay dinamis (default sudah optimal)
- Tambah delay untuk batch besar

## ❓ Troubleshooting

### Session Tidak Connect

1. Cek koneksi internet
2. Pastikan Playwright terinstall: `playwright install chromium`
3. Coba dengan GUI mode: `--headless=false`
4. Hapus dan buat ulang: `--force`

### QR Code Tidak Muncul (Headless)

1. Cek file: `sessions/{session_name}_qr.png`
2. QR code refresh otomatis setiap ~20 detik
3. Download file QR code dan scan

### Pesan Tidak Terkirim

1. Pastikan session sudah authenticated
2. Cek format nomor telepon
3. Kurangi jumlah parallel sessions
4. Coba dengan 1 session dulu

## 📚 Langkah Selanjutnya

- Baca [README.md](../README.md) untuk dokumentasi lengkap
- Lihat [Template Guide](guide_md/TEMPLATE_GUIDE.md) untuk template advanced
- Lihat [SSH Setup Guide](guide_md/SSH_SETUP.md) untuk setup di VPS

