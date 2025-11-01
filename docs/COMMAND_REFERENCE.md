# Command Reference

Referensi lengkap untuk semua command dan opsi yang tersedia.

## 📋 Table of Contents

- [CLI Commands](#cli-commands)
- [Command Options](#command-options)
- [Examples](#examples)

## 🔧 CLI Commands

### `--action`

Action yang akan dilakukan. Opsi yang tersedia:

- `send` - Mengirim pesan
- `add-session` - Menambah session baru
- `list-sessions` - List semua session
- `delete-session` - Hapus session
- `status` - Cek status sistem

### Send Command

```bash
python cli/wa_cli.py --action send [OPTIONS]
```

**Required:**
- `--numbers FILE` atau `--phone NUMBER` - Target penerima
- `--message TEXT` atau `--template FILE` - Pesan yang akan dikirim

**Optional:**
- `--sessions N` - Jumlah session (default: 1, 0 = semua)
- `--use-sessions "name1,name2"` - Session spesifik
- `--session-strategy STRATEGY` - Strategi distribusi
- `--country-code CODE` - Kode negara default (default: 62)
- `--personalize` - Enable personalization

### Add Session Command

```bash
python cli/wa_cli.py --action add-session [OPTIONS]
```

**Optional:**
- `--session-name NAME` - Nama session (default: default)
- `--headless` - Mode headless (untuk SSH/VPS)
- `--force` - Force create (hapus existing jika ada)

### List Sessions Command

```bash
python cli/wa_cli.py --action list-sessions
```

### Delete Session Command

```bash
python cli/wa_cli.py --action delete-session --session-name NAME
```

**Required:**
- `--session-name NAME` - Nama session yang akan dihapus

### Status Command

```bash
python cli/wa_cli.py --action status
```

## ⚙️ Command Options

### `--numbers FILE`

Path ke file yang berisi daftar nomor telepon.

**Format file:**
```
08123456789
08123456790
08123456791
```

**Atau dengan nama dan alamat (untuk personalization):**
```
08123456789|Nama|Alamat
08123456790|Nama|Alamat
```

**Example:**
```bash
--numbers data/contacts.txt
```

### `--phone NUMBER`

Nomor telepon tunggal (alternatif dari `--numbers`).

**Example:**
```bash
--phone "08123456789"
```

### `--message TEXT`

Pesan langsung (tanpa file template).

**Example:**
```bash
--message "Hello, this is a test message!"
```

### `--template FILE`

Path ke file template pesan.

**Example:**
```bash
--template templates/welcome.txt
```

### `--sessions N`

Jumlah session yang akan digunakan.

- `N > 0`: Gunakan N session pertama
- `N = 0`: Gunakan semua session yang tersedia
- Default: `1`

**Example:**
```bash
--sessions 3        # Gunakan 3 session pertama
--sessions 0        # Gunakan semua session
```

### `--use-sessions "name1,name2"`

Gunakan session spesifik (comma-separated).

**Example:**
```bash
--use-sessions "session_1,session_2,session_3"
```

**Note:** Jika menggunakan opsi ini, `--sessions` akan diabaikan.

### `--session-strategy STRATEGY`

Strategi distribusi nomor ke session.

**Options:**
- `round-robin` - Bagi rata secara berurutan (default)
- `random` - Assign secara acak
- `weighted` - Berdasarkan health score session

**Example:**
```bash
--session-strategy round-robin
--session-strategy random
--session-strategy weighted
```

### `--session-name NAME`

Nama session (untuk add-session atau delete-session).

**Example:**
```bash
--session-name "my_session"
```

### `--headless`

Jalankan browser dalam mode headless (tanpa GUI).

**Use case:**
- SSH/VPS tanpa GUI
- Server production
- Automated scripts

**Example:**
```bash
--headless
```

**Note:** Di headless mode, QR code akan disimpan ke file PNG.

### `--force`

Force create session baru (hapus session existing jika ada).

**Example:**
```bash
--force
```

### `--country-code CODE`

Kode negara default untuk format nomor telepon.

**Default:** `62` (Indonesia)

**Example:**
```bash
--country-code 62   # Indonesia
--country-code 1    # USA
```

### `--personalize`

Enable personalization (auto-greeting + name + address).

**Requires:** Format contacts dengan `nomor|nama|alamat`

**Example:**
```bash
--personalize
```

## 💡 Examples

### Basic Send

```bash
# Send to single number
python cli/wa_cli.py --action send \
  --phone "08123456789" \
  --message "Hello!"

# Send to multiple numbers
python cli/wa_cli.py --action send \
  --numbers data/contacts.txt \
  --template templates/message.txt
```

### Session Management

```bash
# Add session
python cli/wa_cli.py --action add-session --session-name session_1

# List sessions
python cli/wa_cli.py --action list-sessions

# Delete session
python cli/wa_cli.py --action delete-session --session-name session_1
```

### Advanced Send

```bash
# Use specific sessions with personalization
python cli/wa_cli.py --action send \
  --numbers data/contacts_personalized.txt \
  --template templates/welcome.txt \
  --use-sessions "session_1,session_2" \
  --session-strategy weighted \
  --personalize

# Use all sessions with random distribution
python cli/wa_cli.py --action send \
  --numbers data/contacts.txt \
  --template templates/message.txt \
  --sessions 0 \
  --session-strategy random
```

### Headless Mode (SSH/VPS)

```bash
# Add session in headless mode
python cli/wa_cli.py --action add-session \
  --session-name vps_session \
  --headless

# Force create new session
python cli/wa_cli.py --action add-session \
  --session-name new_session \
  --headless \
  --force
```

## 📊 Option Combinations

### Valid Combinations

✅ **Send dengan phone dan message:**
```bash
--action send --phone "..." --message "..."
```

✅ **Send dengan numbers dan template:**
```bash
--action send --numbers "..." --template "..."
```

✅ **Send dengan session selection:**
```bash
--action send --numbers "..." --template "..." --use-sessions "..."
```

✅ **Send dengan strategy:**
```bash
--action send --numbers "..." --template "..." --session-strategy "..."
```

### Invalid Combinations

❌ **Send tanpa target:**
```bash
--action send --message "..."  # Missing --phone or --numbers
```

❌ **Send tanpa message:**
```bash
--action send --phone "..."  # Missing --message or --template
```

❌ **Delete session tanpa nama:**
```bash
--action delete-session  # Missing --session-name
```

## 🔍 Help

Untuk melihat help/usage:

```bash
python cli/wa_cli.py --help
```

atau

```bash
python cli/wa_cli.py --action send --help
```

