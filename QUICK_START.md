# Quick Start Guide - WhatsApp Bot

## 🎉 Session Berhasil Ditambahkan!

Sekarang Anda bisa mulai mengirim pesan. Berikut langkah-langkahnya:

## 1. Siapkan File Kontak

Edit file `data/contacts.txt` dan masukkan nomor telepon target:

```
08123456789
081234567890
628123456789
```

**Format nomor yang didukung:**
- 08123456789 (format lokal)
- 628123456789 (format internasional)
- +62-812-3456-7890 (format dengan tanda +)

## 2. Siapkan Template Pesan (Opsional)

Edit file `templates/message.txt` dengan pesan yang ingin dikirim:

```
Halo! Ini adalah pesan dari WhatsApp Bot.

Terima kasih!
```

Atau gunakan pesan langsung di command line.

## 3. Kirim Pesan via CLI

### Mengirim dengan Template File:
```bash
python cli/wa_cli.py --action send \
  --numbers data/contacts.txt \
  --template templates/message.txt \
  --sessions 1 \
  --country-code 62
```

### Mengirim dengan Pesan Langsung:
```bash
python cli/wa_cli.py --action send \
  --numbers data/contacts.txt \
  --message "Halo! Ini adalah pesan test." \
  --sessions 1
```

### Parameter yang Tersedia:
- `--numbers`: Path ke file kontak (required)
- `--template`: Path ke file template pesan (opsional, jika tidak pakai --message)
- `--message`: Pesan langsung (opsional, jika tidak pakai --template)
- `--sessions`: Jumlah session paralel (default: 1, max: 3-5 untuk keamanan)
- `--country-code`: Kode negara default (default: 62 untuk Indonesia)

## 4. Atau Gunakan API Server

### Start API Server:
```bash
uvicorn api.server:app --reload --port 8000
```

### Kirim via API (curl):
```bash
curl -X POST http://localhost:8000/send \
  -H "Content-Type: application/json" \
  -d '{
    "numbers": ["08123456789", "081234567890"],
    "message": "Halo! Ini adalah pesan test.",
    "sessions": 1,
    "priority": "normal"
  }'
```

### Check Job Status:
```bash
curl http://localhost:8000/job/{job_id}
```

## 5. Contoh Penggunaan

### Contoh 1: Single Message Test
```bash
# Buat file contacts_test.txt dengan 1 nomor
echo "08123456789" > data/contacts_test.txt

# Kirim pesan test
python cli/wa_cli.py --action send \
  --numbers data/contacts_test.txt \
  --message "Test message dari bot" \
  --sessions 1
```

### Contoh 2: Bulk Message dengan Template
```bash
python cli/wa_cli.py --action send \
  --numbers data/contacts.txt \
  --template templates/message.txt \
  --sessions 2 \
  --country-code 62
```

### Contoh 3: Multiple Sessions (Lebih Cepat)
```bash
python cli/wa_cli.py --action send \
  --numbers data/contacts.txt \
  --template templates/message.txt \
  --sessions 3
```

## 📊 Monitoring

### List Sessions:
```bash
python cli/wa_cli.py --action list-sessions
```

### Check Status:
```bash
python cli/wa_cli.py --action status
```

## ⚠️ Tips Penting

1. **Mulai dengan Session Tunggal**: Gunakan `--sessions 1` untuk test pertama
2. **Jangan Terlalu Cepat**: Sistem sudah otomatis mengatur delay untuk keamanan
3. **Periksa Nomor**: Pastikan nomor sudah benar sebelum mengirim
4. **Test dengan Nomor Sendiri**: Selalu test dengan nomor Anda sendiri terlebih dahulu
5. **Session Management**: Session yang sudah dibuat akan tersimpan di folder `sessions/`

## 🚨 Perhatian

- **Rate Limiting**: Sistem otomatis mengatur delay antara pesan (5-15 detik)
- **Anti-Ban**: Pesan otomatis divariasi untuk menghindari deteksi spam
- **Session Health**: Monitor kesehatan session secara berkala
- **Legal**: Hanya kirim ke kontak yang sudah memberikan izin

## 📝 Catatan

- Pesan akan dikirim dengan delay otomatis untuk keamanan
- Setiap 50 pesan akan ada break 30-60 detik
- Sistem akan memberikan progress update setiap 10 pesan
- Session tersimpan di `sessions/` dan bisa digunakan kembali

## 🆘 Troubleshooting

### Session Tidak Terdeteksi:
```bash
# Cek session yang tersedia
python cli/wa_cli.py --action list-sessions

# Buat session baru jika perlu
python cli/wa_cli.py --action add-session --session-name default
```

### Pesan Gagal Terkirim:
- Pastikan session masih aktif
- Periksa format nomor telepon
- Cek koneksi internet
- Pastikan WhatsApp Web masih terhubung

### Error Rate Limit:
- Kurangi jumlah session paralel
- Tingkatkan delay (edit config/optimal_settings.yaml)
- Gunakan lebih sedikit pesan per batch

