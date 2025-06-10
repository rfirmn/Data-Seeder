# Data-Seeder
Data Seeder for simple report database schema

# MySQL Data Seeder

Skrip Python ini dirancang untuk mengotomatiskan proses penyiapan database MySQL dan mengisinya dengan volume data palsu (*fake data*) yang besar dan realistis. Cocok digunakan oleh pengembang yang perlu dengan cepat membuat lingkungan pengujian atau pengembangan untuk aplikasi yang melibatkan manajemen pengguna, kategori, pengaduan, dan komentar.

---

## ✨ Fitur

* **Pembuatan Database dan Tabel**: Membuat database `pengaduan` dan semua tabel yang diperlukan (`pengguna`, `kategori`, `pengaduan`, `komentar`) jika belum ada.
* **Data Palsu Realistis**: Menggunakan pustaka [Faker](https://faker.readthedocs.io/en/master/) untuk menghasilkan data palsu yang kontekstual seperti nama, email, konten, dan status.
* **Indikator Kemajuan**: Menampilkan log selama proses penyisipan data agar pengguna mengetahui progres.
* **Penanganan Koneksi Tangguh**: Menangani error koneksi MySQL dan memastikan koneksi ditutup dengan benar.

---

🌐 Visualisasi ERD

Berikut adalah visualisasi Entity Relationship Diagram (ERD) untuk database pengaduan yang digunakan oleh skrip ini:

+------------+        +------------+        +-----------------+        +--------------+
|  pengguna  |        |  kategori  |        |    pengaduan    |        |   komentar   |
+------------+        +------------+        +-----------------+        +--------------+
| id (PK)    |<----+  | id (PK)    |<----+  | id (PK)         |<----+  | id (PK)      |
| nama       |        | nama       |        | user_id (FK)    |        |user_id (FK)  |
| email      |        +------------+        | kategori_id(FK) |        |pengaduan_id  |
| password   |                              | isi_pengaduan   |        |isi_komentar  |
| role       |                              | status          |        |created_at    |
| created_at |                              | created_at      |        +--------------+
| updated_at |                              | updated_at      |
+------------+                              +-----------------+


Visualisasi ini membantu dalam memahami hubungan antar tabel dan kunci asing (foreign key) yang digunakan.


---

## 🚀 Memulai

### 📆 Prasyarat

* Python 3.x
* Server MySQL yang berjalan
* Pustaka Python:

```bash
pip install mysql-connector-python Faker
```

### 📝 Konfigurasi Database

Secara default, skrip menggunakan kredensial berikut:

* **Host**: `localhost`
* **User**: `root`
* **Password**: `rootpassword`
* **Database Awal**: `mydb` *(hanya untuk koneksi awal sebelum membuat database `pengaduan`)*

> ⚠️ Jika kredensial atau host Anda berbeda, ubah bagian `mysql.connector.connect()` dalam fungsi `test_mysql_connection`.

---

## 🚧 Menjalankan Skrip

1. Simpan skrip sebagai `data_seeder.py`
2. Buka terminal atau command prompt
3. Navigasi ke direktori tempat Anda menyimpan skrip
4. Jalankan:

```bash
python3 data_seeder.py
```

### Skrip akan:

* Menghubungkan ke server MySQL
* Membuat database `pengaduan` dan semua tabel terkait
* Mengisi tabel dengan data palsu
* Mencetak log progres dan ringkasan waktu eksekusi

---

## ⚖️ Kustomisasi

### Mengubah Jumlah Data

Atur nilai variabel `data` di awal skrip:

```python
# Contoh:
data = 1000000  # default
# data = 50000  # untuk pengisian menengah
# data = 1000   # untuk pengujian cepat
```

> ℹ️ Nilai besar akan memakan waktu cukup lama, disarankan mulai dari nilai kecil.

### Menyesuaikan Detail Koneksi

Modifikasi di bagian koneksi:

```python
connection = mysql.connector.connect(
    host='host_Anda',
    user='user_Anda',
    password='password_Anda',
    database='mydb'
)
```

### Menyesuaikan Data Faker

Faker dapat dikustomisasi sesuai kebutuhan:

```python
# Default
nama = fake.name()
email = fake.email()

# Alternatif
nama = fake.first_name() + " " + fake.last_name()
email = fake.free_email()
```

Juga bisa ubah `random_int(min, max)` untuk foreign key agar sesuai dengan data yang tersedia.

### Memodifikasi Skema Tabel

Misalnya, menambahkan kolom `address` ke tabel pengguna:

```sql
CREATE TABLE IF NOT EXISTS pengguna (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('RT', 'warga') NOT NULL DEFAULT 'warga',
    address VARCHAR(255), -- kolom baru
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

Jangan lupa untuk menyesuaikan juga bagian `INSERT INTO` dan data Faker-nya.

---

## 📁 Struktur Proyek

```
.
└── data_seeder.py
```

---

## ✉️ Lisensi

Skrip ini bebas digunakan dan dimodifikasi untuk keperluan pembelajaran dan pengembangan.

---

> Dibuat dengan ❤️ untuk membantu proses pengujian basis data dengan cepat dan efisien.



