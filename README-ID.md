# Bot Testnet Huddle01

Bot berbasis Python yang dirancang untuk mengotomatisasi partisipasi di ruang testnet Huddle01 menggunakan beberapa akun. Bot ini menangani autentikasi, manajemen sesi, komunikasi WebSocket, dan bertujuan untuk mempertahankan kehadiran di ruang Huddle01 yang ditentukan.

## Fitur

* **Dukungan Multi-Akun:** Muat beberapa kunci privat Ethereum untuk bergabung ke ruang dengan peserta yang berbeda.
* **Gabung Ruang Otomatis:** Secara otomatis menangani proses bergabung ke ruang Huddle01.
* **Autentikasi Dompet:** Mengimplementasikan mekanisme tanda tangan tantangan-respons untuk login Huddle01.
* **Manajemen Sesi:** Mempertahankan nama tampilan dan agen pengguna untuk akun di seluruh sesi (`session.json`).
* **Agen Pengguna Acak:** Menghasilkan agen pengguna yang acak, namun masuk akal, untuk setiap akun.
* **Komunikasi WebSocket:** Membangun dan mengelola koneksi WebSocket untuk interaksi di dalam ruang.
* **Penutupan yang Elegan (Graceful Shutdown):** Menangani `SIGINT` (Ctrl+C) dan `SIGTERM` untuk proses penutupan yang bersih.
* **Pemantauan Koneksi & Sambung Ulang Otomatis:** Memantau koneksi aktif dan mencoba menyambung ulang jika sesi terputus.
* **Penggunaan Akun yang Dapat Dikonfigurasi:** Tentukan jumlah akun yang akan digunakan atau gunakan semua yang tersedia dari `private_key.txt`.
* **Input ID Ruang Dinamis:** Menerima ID ruang secara langsung atau mengekstraknya dari URL ruang Huddle01 lengkap.
* **Partisipasi Testnet:** Mencakup fungsionalitas yang bertujuan untuk berinteraksi dengan fitur khusus testnet (misalnya, pengumpulan poin).

## Prasyarat

* Python 3.8 atau lebih tinggi
* `pip` (penginstal paket Python)

## Pengaturan dan Instalasi

1.  **Kloning repositori:**
    ```bash
    git clone https://github.com/rasputingrigori/huddle01-testnet.git
    cd huddle01-testnet
    ```

2.  **Buat dan aktifkan lingkungan virtual (disarankan):**
    ```bash
    python -m venv venv
    ```
    ### Di Windows
    ```bash
    venv\Scripts\activate
    ```
    ### Di macOS/Linux
    ```bash
    source venv/bin/activate
    ```

4.  **Instal dependensi:**

    Pastikan `requirements.txt` Anda terlihat seperti ini sebelum menginstal:
    ```txt
    aiohttp==3.9.5
    websockets==12.0
    eth-account==0.12.0
    Faker==25.8.0
    colorama==0.4.6
    brotli==1.1.0
    ```
    Kemudian instal:
    ```bash
    pip install -r requirements.txt
    ```

## Konfigurasi

1.  **`private_key.txt`:**
    * Buat file bernama `private_key.txt` di direktori *root* proyek (setingkat dengan `main.py`).
    * Tambahkan kunci privat Ethereum Anda ke file ini, satu kunci privat per baris.
    * Kunci dapat dengan atau tanpa awalan `0x`.
    * Contoh:
        ```
        0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890
        fedcba0987654321fedcba0987654321fedcba0987654321fedcba0987654321
        ```

2.  **`session.json`:**
    * File ini akan secara otomatis dibuat dan diperbarui oleh `account_manager.py` saat bot berjalan pertama kali dengan kunci privat baru.
    * Ini menyimpan nama tampilan dan agen pengguna yang dihasilkan yang terkait dengan setiap kunci privat untuk menjaga konsistensi antar sesi. Anda umumnya tidak perlu mengedit file ini secara manual.

3.  **`config.py`:**
    * File ini berisi *endpoint* API dan `NEXTJS_BUILD_ID`.
    * `NEXTJS_BUILD_ID`: ID ini digunakan untuk mengambil data ruang tertentu. Jika Huddle01 memperbarui *frontend*-nya, ID ini mungkin berubah, berpotensi menyebabkan kesalahan saat bot mencoba mengambil metadata ruang. Jika Anda mengalami masalah seperti itu, Anda mungkin perlu menemukan dan memperbarui nilai ini dengan memeriksa permintaan jaringan di situs web Huddle01.

## Penggunaan

Jalankan skrip `main.py` dari direktori *root* proyek.

**Sintaks dasar:**
```bash
python main.py [room_id_or_url] [-n num_accounts]
```

### Argumen:
room_id_or_url (opsional):

ID Ruang Huddle01 (misalnya, abc-defg-hij).
Atau URL ruang Huddle01 lengkap (misalnya, https://huddle01.app/room/abc-defg-hij).
Jika tidak disediakan, skrip akan meminta Anda untuk memasukkannya.
`-n num_accounts, --num_accounts num_accounts (opsional):`

Jumlah akun yang akan digunakan dari `private_key.txt.`
Jika 0 (standar) atau tidak ditentukan, semua akun yang valid dari `private_key.txt` akan digunakan. Jika diberikan angka positif, sejumlah akun tersebut akan dimuat.

Jika akun yang tersedia lebih sedikit dari yang diminta, peringatan akan ditampilkan, dan semua akun yang tersedia akan digunakan.
Angka negatif akan diperlakukan sebagai permintaan untuk semua akun.

### Contoh:
Gabung ke ruang menggunakan ID-nya dengan semua akun:

```bash
python main.py abc-defg-hij
```
Gabung ke ruang menggunakan URL-nya dengan 5 akun pertama dari private_key.txt:

```bash
python main.py https://huddle01.app/room/abc-defg-hij -n 5
```
Jalankan tanpa argumen (akan meminta ID Ruang):

```bash
python main.py
```
Bot kemudian akan bertanya: `Enter the Huddle01 room ID to join:`

Bot akan mencatat tindakannya ke konsol, termasuk informasi tentang koneksi akun, kesalahan, dan peristiwa WebSocket. Tekan Ctrl+C untuk memulai penutupan yang elegan.

## Ikhtisar Struktur File
```yaml
├── main.py                    # Titik masuk utama untuk bot
├── requirements.txt           # Dependensi paket Python
├── config.py                  # Konfigurasi untuk endpoint API, ID build
├── src/
│   ├── helpers/
│   │   ├── account_manager.py # Mengelola kunci privat dan data sesi
│   │   ├── api_client.py      # Menangani interaksi HTTP API dengan Huddle01
│   │   ├── main_controller.py # Mengatur instance bot dan koneksi
│   │   └── websocket_handler.py # Mengelola koneksi dan pesan WebSocket
│   └── utils/
│       ├── utils.py           # Fungsi utilitas (logging, pembuatan UA)
│       └── banner.py          # Untuk menampilkan banner startup
├── private_key.txt            # (Dibuat pengguna) Menyimpan kunci privat
└── session.json               # (Dibuat secara otomatis) Menyimpan detail sesi akun
```

## Dependensi
Dependensi utama tercantum dalam requirements.txt dan meliputi:

- `aiohttp`: Untuk permintaan HTTP asinkron.
- `websockets`: Untuk komunikasi WebSocket.
- `eth-account`: Untuk penanganan akun dan tanda tangan Ethereum.
- `Faker`: Untuk menghasilkan nama tampilan acak.
- `colorama`: Untuk output konsol berwarna.
- `brotli`: Untuk kompresi data.

## Kontribusi
Kontribusi sangat disambut! Jangan ragu untuk mengirimkan pull request atau membuka issue untuk bug, fitur, atau peningkatan apa pun.

## Penafian
Bot ini ditujukan untuk tujuan pendidikan dan pengujian, khususnya untuk berinteraksi dengan lingkungan testnet Huddle01.
Pengguna bertanggung jawab penuh untuk memastikan penggunaan bot ini sesuai dengan ketentuan layanan Huddle01 dan kebijakan platform yang berlaku.
Pengelola proyek ini tidak bertanggung jawab atas penyalahgunaan, pembatasan akun, atau konsekuensi lain yang timbul dari penggunaan bot ini.

## Lisensi
Tidak ada Lisensi MIT, "Proyek ini tidak berlisensi."