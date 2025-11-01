# Panduan Template Pesan

## Format Template

### Line Break dalam 1 Bubble Chat

Gunakan `\n` (backslash + n) untuk membuat baris baru dalam **1 bubble chat yang sama**.

**Contoh template:**
```
Baris pertama pesan\nBaris kedua pesan\nBaris ketiga pesan
```

**Hasil di WhatsApp:**
```
Baris pertama pesan
Baris kedua pesan
Baris ketiga pesan
```
*(Semua dalam 1 bubble chat)*

### Perbedaan dengan Line Break Normal

**Jika menggunakan line break normal (Enter di file):**
```
Baris pertama pesan
Baris kedua pesan
Baris ketiga pesan
```
**Hasil:** Akan menjadi **3 bubble chat terpisah**

**Jika menggunakan `\n`:**
```
Baris pertama pesan\nBaris kedua pesan\nBaris ketiga pesan
```
**Hasil:** Akan menjadi **1 bubble chat dengan 3 baris**

## Contoh Template

### Template dengan `\n`:
```
Selamat pagi, ini adalah pesan test.\n\nSilakan hubungi kami jika ada pertanyaan.\n\nTerima kasih.
```

**Hasil:**
```
Selamat pagi, ini adalah pesan test.

Silakan hubungi kami jika ada pertanyaan.

Terima kasih.
```
*(Semua dalam 1 bubble)*

### Template untuk Produk:
```
Saya ingin memperkenalkan produk unggulan kami.\n\nDetail produk dapat dilihat di:\nhttps://olshopku.com/produk/123\n\nHubungi kami untuk informasi lebih lanjut.
```

## Kombinasi dengan Personalisasi

Ketika menggunakan `--personalize`, format pesan akan menjadi:

**Template:**
```
Ini adalah pesan test.\n\nSilakan hubungi kami jika ada pertanyaan.
```

**Dengan personalisasi:**
```
Selamat siang *Nama*.

Alamat : Alamat Kontak

Ini adalah pesan test.

Silakan hubungi kami jika ada pertanyaan.
```

*(Semua dalam 1 bubble chat)*

## Tips

1. **Gunakan `\n` untuk line break dalam bubble:**
   - Baik untuk formatting pesan panjang
   - Membuat pesan lebih terorganisir
   - Tetap dalam 1 bubble chat

2. **Gunakan line break normal untuk bubble terpisah:**
   - Jika ingin mengirim beberapa pesan terpisah
   - Untuk efek dramatis atau penekanan

3. **Kombinasi:**
   - Bisa menggunakan keduanya dalam 1 template
   - Line break normal = bubble baru
   - `\n` = baris baru dalam bubble sama

## Contoh File Template

**File: `templates/message.txt`**
```
Halo, ini adalah pesan dari bot.\n\nPesan ini menggunakan \\n untuk line break.\n\nSemua dalam 1 bubble chat.
```

**Command:**
```bash
python cli/wa_cli.py --action send \
  --numbers data/contacts.txt \
  --template templates/message.txt
```

**Catatan:** Di file template, tulis `\n` sebagai `\n` (backslash + n), bukan sebagai actual line break.

