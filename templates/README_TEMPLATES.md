# Template Pesan WhatsApp Bot

## Template Tawaran Produk

### 1. product_offer.txt (Versi Standar)
Template profesional untuk tawaran produk dengan penjelasan lengkap.
**Cocok untuk:** Produk umum, penawaran rutin

### 2. product_offer_short.txt (Versi Singkat)
Template singkat dan to the point.
**Cocok untuk:** Follow-up, reminder, produk cepat

### 3. product_offer_premium.txt (Versi Premium)
Template lebih formal dan mendetail.
**Cocok untuk:** Produk premium, B2B, klien penting

## Cara Menggunakan Template

### Dengan Personalisasi:
```bash
python cli/wa_cli.py --action send \
  --numbers data/contacts_personalized.txt \
  --template templates/product_offer.txt \
  --personalize
```

### Tanpa Personalisasi:
```bash
python cli/wa_cli.py --action send \
  --numbers data/contacts.txt \
  --template templates/product_offer.txt
```

## Format Hasil dengan Personalisasi

**Jika dikirim siang:**
```
Selamat siang *Irhash*.

Alamat : *Jl. Contoh No. 123, Jakarta*

Saya ingin menawarkan produk berkualitas yang mungkin sesuai dengan kebutuhan Anda. Produk ini telah teruji dan banyak diminati oleh pelanggan kami.

Silakan kunjungi link berikut untuk melihat detail produk:
https://olshopku.com/produk/123

Jika ada pertanyaan atau butuh informasi lebih lanjut, jangan ragu untuk menghubungi kami. Terima kasih atas perhatiannya.
```

## Kustomisasi Template

Edit file template dan ganti link produk:
- Buka file template (misal: `templates/product_offer.txt`)
- Ganti `https://olshopku.com/produk/123` dengan link produk Anda
- Simpan file

## Tips Penggunaan

1. **Pilih Template yang Sesuai:**
   - `product_offer.txt` - Untuk kebanyakan kasus
   - `product_offer_short.txt` - Untuk follow-up atau reminder
   - `product_offer_premium.txt` - Untuk klien VIP atau B2B

2. **Ganti Link Produk:**
   - Pastikan link produk sudah benar sebelum mengirim
   - Test link terlebih dahulu

3. **Kombinasi dengan Personalisasi:**
   - Gunakan `--personalize` untuk menambah greeting dan alamat
   - Format kontak: `nomor|nama|alamat`

4. **Waktu Pengiriman:**
   - Pagi: 08:00 - 12:00
   - Siang: 12:00 - 15:00
   - Sore: 15:00 - 18:00
   - Hindari malam hari untuk pesan bisnis

## Template Lainnya

- `message.txt` - Template umum
- `sample.txt` - Template contoh dengan placeholder

