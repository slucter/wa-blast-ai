# Panduan Personalisasi Pesan

## Fitur Personalisasi

Fitur personalisasi memungkinkan Anda mengirim pesan yang dipersonalisasi dengan:
1. **Greeting otomatis** berdasarkan waktu (Pagi/Siang/Sore/Malam)
2. **Nama kontak** (jika tersedia)
3. **Alamat kontak** (jika tersedia)

## Format File Kontak

Format kontak yang didukung: `nomor|nama|alamat`

### Contoh:

```
085523509300|Irhash|Jl. Contoh No. 123, Jakarta
08123456789|Budi Santoso|Jl. Merdeka No. 45, Bandung
628987654321|Siti Nurhaliza|
08111111111||Jl. Tanpa Nama No. 1
```

**Format fleksibel:**
- Jika tidak ada nama: `nomor||alamat` atau `nomor|`
- Jika tidak ada alamat: `nomor|nama|` atau `nomor|nama`
- Jika hanya nomor: `nomor`

## Cara Penggunaan

### 1. Buat File Kontak dengan Format Personalisasi

Edit file `data/contacts_personalized.txt`:
```
085523509300|Irhash|Jl. Contoh No. 123, Jakarta
08123456789|Budi|Jl. Merdeka No. 45
628987654321|Siti|
```

### 2. Kirim dengan Personalisasi

```bash
python cli/wa_cli.py --action send \
  --numbers data/contacts_personalized.txt \
  --message "Terima kasih atas kepercayaannya" \
  --personalize
```

### 3. Hasil Pesan

**Jika dikirim pagi (5-12):**
```
Selamat pagi *Irhash*, Terima kasih atas kepercayaannya

📍 Alamat: Jl. Contoh No. 123, Jakarta
```

**Jika dikirim siang (12-15):**
```
Selamat siang *Budi*, Terima kasih atas kepercayaannya

📍 Alamat: Jl. Merdeka No. 45
```

**Jika dikirim sore (15-19):**
```
Selamat sore *Siti*, Terima kasih atas kepercayaannya
```

**Jika dikirim malam (19-5):**
```
Selamat malam *Irhash*, Terima kasih atas kepercayaannya

📍 Alamat: Jl. Contoh No. 123, Jakarta
```

## Logika Personalisasi

1. **Greeting Otomatis:**
   - Pagi (05:00-11:59): "Selamat pagi"
   - Siang (12:00-14:59): "Selamat siang"
   - Sore (15:00-18:59): "Selamat sore"
   - Malam (19:00-04:59): "Selamat malam"

2. **Nama:**
   - Jika ada nama: Ditambahkan setelah greeting dengan format **bold** (*nama*)
   - Jika tidak ada nama: Greeting tanpa nama

3. **Alamat:**
   - Jika ada alamat: Ditambahkan di akhir dengan format `📍 Alamat: [alamat]`
   - Jika tidak ada alamat: Tidak ditambahkan

## Contoh Lengkap

### File Kontak: `data/contacts.txt`
```
085523509300|John Doe|Jakarta
08123456789|Jane Smith|
628987654321||Bandung
08111111111
```

### Command:
```bash
python cli/wa_cli.py --action send \
  --numbers data/contacts.txt \
  --message "Jangan lupa meeting besok jam 10" \
  --personalize
```

### Pesan yang Terkirim:

**Untuk John Doe (dengan nama dan alamat):**
```
Selamat siang *John Doe*, Jangan lupa meeting besok jam 10

📍 Alamat: Jakarta
```

**Untuk Jane Smith (dengan nama, tanpa alamat):**
```
Selamat siang *Jane Smith*, Jangan lupa meeting besok jam 10
```

**Untuk kontak tanpa nama (dengan alamat):**
```
Selamat siang, Jangan lupa meeting besok jam 10

📍 Alamat: Bandung
```

**Untuk kontak tanpa nama dan alamat:**
```
Selamat siang, Jangan lupa meeting besok jam 10
```

## Tanpa Personalisasi

Jika tidak menggunakan `--personalize`, pesan tetap bisa menggunakan placeholder:

```
08123456789|Budi|Jakarta
```

```bash
python cli/wa_cli.py --action send \
  --numbers data/contacts.txt \
  --message "Halo {name}, alamat Anda di {address}"
```

Hasil: `Halo Budi, alamat Anda di Jakarta`

## Tips

1. **Nama dengan Bold:** Nama otomatis diformat bold dengan `*nama*` di WhatsApp
2. **Kosongkan dengan benar:** Gunakan `||` jika tidak ada nama atau alamat
3. **Komentar:** Baris yang dimulai dengan `#` akan diabaikan
4. **Kombinasi:** Bisa dikombinasikan dengan template file

## Contoh dengan Template

File `templates/personalized.txt`:
```
Ini adalah pesan penting untuk Anda.

Mohon konfirmasi terima kasih.
```

Command:
```bash
python cli/wa_cli.py --action send \
  --numbers data/contacts_personalized.txt \
  --template templates/personalized.txt \
  --personalize
```

Hasil untuk "Selamat siang":
```
Selamat siang *Irhash*, Ini adalah pesan penting untuk Anda.

Mohon konfirmasi terima kasih.

📍 Alamat: Jl. Contoh No. 123, Jakarta
```

