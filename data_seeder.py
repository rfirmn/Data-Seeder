import sys
import mysql.connector
from faker import Faker
import time
import random

fake = Faker()
data = 1000 # Jumlah catatan palsu yang akan dimasukkan

def mysql_connection():
    connection = None
    cur = None
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root'
            # password='your_mysql_password' # Tambahkan jika Anda punya kata sandi MySQL
        )

        cur = connection.cursor()
        dbname = "pengaduan"
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {dbname};")
        cur.execute(f"USE {dbname};")
        print("Database 'pengaduan' berhasil dibuat dan telah digunakan.")

        # Pernyataan pembuatan tabel disesuaikan dengan ERD
        statement_pengguna = """
        CREATE TABLE IF NOT EXISTS pengguna (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            nama VARCHAR(50) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            role ENUM('RT', 'warga') NOT NULL DEFAULT 'warga',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );
        """

        statement_kategori = """
        CREATE TABLE IF NOT EXISTS kategori (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            nama VARCHAR(100) NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );
        """

        statement_pengaduan = """
        CREATE TABLE IF NOT EXISTS pengaduan (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            user_id BIGINT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES pengguna(id) ON DELETE RESTRICT,
            kategori_id BIGINT NOT NULL,
            FOREIGN KEY (kategori_id) REFERENCES kategori(id) ON DELETE RESTRICT,
            judul VARCHAR(255) NOT NULL,
            isi TEXT NOT NULL,
            lampiran VARCHAR(255) DEFAULT NULL,
            status ENUM('pending', 'proses', 'selesai') NOT NULL DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );
        """

        statement_komentar = """
        CREATE TABLE IF NOT EXISTS komentar (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            pengaduan_id BIGINT NOT NULL,
            FOREIGN KEY (pengaduan_id) REFERENCES pengaduan(id) ON DELETE CASCADE,
            user_id BIGINT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES pengguna(id) ON DELETE RESTRICT,
            isi TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );
        """
        
        # Tambahan untuk tabel Laravel bawaan (cache, cache_locks, jobs, sessions)
        # Anda tidak perlu menyertakan ini dalam script ini jika Anda hanya ingin mengisi data inti aplikasi.
        # Namun, jika Anda ingin membuat semua tabel sesuai ERD, Anda bisa menambahkannya di sini.
        # Untuk tujuan data dummy aplikasi, saya akan fokus pada `pengguna`, `kategori`, `pengaduan`, dan `komentar`.

        cur.execute(statement_pengguna)
        print("Tabel 'pengguna' berhasil dibuat.")
        cur.execute(statement_kategori)
        print("Tabel 'kategori' berhasil dibuat.")
        cur.execute(statement_pengaduan)
        print("Tabel 'pengaduan' berhasil dibuat.")
        cur.execute(statement_komentar)
        print("Tabel 'komentar' berhasil dibuat.")

        start_time = time.time() # Mulai pengukuran waktu total

        # --- Masukkan data ke tabel pengguna ---
        print(f"Memasukkan {data} baris data palsu ke tabel 'pengguna'...")
        pengguna_to_insert = []
        use_role = ['warga', 'RT'] # Sesuaikan dengan ENUM di ERD
        for i in range(data):
            nama = fake.name()
            email = fake.unique.email() # Pastikan email unik
            password = fake.password()
            role = random.choice(use_role)
            pengguna_to_insert.append((nama, email, password, role))
            
            if (i + 1) % 100 == 0 or (i + 1) == data:
                cur.executemany("INSERT INTO pengguna (nama, email, password, role) VALUES (%s, %s, %s, %s)", pengguna_to_insert)
                connection.commit()
                print(f"Telah memasukkan {i + 1} baris ke 'pengguna'...")
                pengguna_to_insert = []
        # Update created_at dan updated_at yang NULL pada tabel pengguna
        cur.execute("UPDATE pengguna SET created_at = NOW() WHERE created_at IS NULL;")
        cur.execute("UPDATE pengguna SET updated_at = NOW() WHERE updated_at IS NULL;")
        connection.commit()
        print(f"Data palsu berhasil dimasukkan ke tabel 'pengguna'.")

        cur.execute("SELECT id FROM pengguna;")
        user_ids = [row[0] for row in cur.fetchall()]
        if not user_ids:
            print("Peringatan: Tidak ada pengguna yang ditemukan setelah penyisipan. Tidak dapat melanjutkan dengan tabel terkait.")
            return False

        # --- Masukkan data ke tabel kategori ---
        print("Memasukkan data palsu ke tabel 'kategori'...")
        kategori_list = [
            "Infrastruktur", "Keamanan", "Lingkungan", "Layanan Publik",
            "Transportasi", "Pendidikan", "Kesehatan", "Sosial"
        ]
        kategoris_to_insert = [(nama,) for nama in kategori_list]
        cur.executemany("INSERT INTO kategori (nama) VALUES (%s)", kategoris_to_insert)
        connection.commit()
        cur.execute("UPDATE kategori SET created_at = NOW() WHERE created_at IS NULL;")
        cur.execute("UPDATE kategori SET updated_at = NOW() WHERE updated_at IS NULL;")
        print("Data palsu berhasil dimasukkan ke tabel 'kategori'.")

        cur.execute("SELECT id FROM kategori;")
        kategori_ids = [row[0] for row in cur.fetchall()]
        if not kategori_ids:
            print("Peringatan: Tidak ada kategori yang ditemukan setelah penyisipan. Tidak dapat melanjutkan dengan tabel terkait.")
            return False

        # --- Masukkan data ke tabel pengaduan ---
        print(f"Memasukkan {data} baris data palsu ke tabel 'pengaduan'...")
        pengaduan_to_insert = []
        for i in range(data):
            user_id = random.choice(user_ids)
            kategori_id = random.choice(kategori_ids)
            judul = fake.sentence()
            isi = fake.text()
            lampiran = f"/uploads/{fake.uuid4()}.jpg"
            status = random.choice(['pending', 'proses', 'selesai'])
            pengaduan_to_insert.append((user_id, kategori_id, judul, isi, lampiran, status))

            if (i + 1) % 100 == 0 or (i + 1) == data:
                cur.executemany("INSERT INTO pengaduan (user_id, kategori_id, judul, isi, lampiran, status) VALUES (%s, %s, %s, %s, %s, %s)", pengaduan_to_insert)
                connection.commit()
                print(f"Telah memasukkan {i + 1} baris ke 'pengaduan'...")
                pengaduan_to_insert = []

        cur.execute("UPDATE pengaduan SET created_at = NOW() WHERE created_at IS NULL;")
        cur.execute("UPDATE pengaduan SET updated_at = NOW() WHERE updated_at IS NULL;")

        print(f"Data palsu berhasil dimasukkan ke tabel 'pengaduan'.")
        
        cur.execute("SELECT id FROM pengaduan;")
        pengaduan_ids = [row[0] for row in cur.fetchall()]
        if not pengaduan_ids:
            print("Peringatan: Tidak ada pengaduan yang ditemukan setelah penyisipan. Tidak dapat melanjutkan dengan komentar.")
            return False

        # --- Masukkan data ke tabel komentar ---
        print(f"Memasukkan {data} baris data palsu ke tabel 'komentar'...")
        komentar_to_insert = []
        for i in range(data):
            pengaduan_id = random.choice(pengaduan_ids)
            user_id = random.choice(user_ids)
            isi = fake.text()
            komentar_to_insert.append((pengaduan_id, user_id, isi))

            if (i + 1) % 100 == 0 or (i + 1) == data:
                cur.executemany("INSERT INTO komentar (pengaduan_id, user_id, isi) VALUES (%s, %s, %s)", komentar_to_insert)
                connection.commit()
                print(f"Telah memasukkan {i + 1} baris ke 'komentar'...")
                komentar_to_insert = []
        cur.execute("UPDATE pengaduan SET created_at = NOW() WHERE created_at IS NULL;")
        cur.execute("UPDATE pengaduan SET updated_at = NOW() WHERE updated_at IS NULL;")
        print(f"Data palsu berhasil dimasukkan ke tabel 'komentar'.")

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Total waktu yang dibutuhkan untuk memasukkan semua data palsu: {elapsed_time:.2f} detik")
        print("Semua transaksi data telah selesai dan di-commit.")

        return True
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        if connection:
            connection.rollback()
            print("Transaksi di-rollback karena kesalahan.")
        return False
    finally:
        if cur:
            cur.close()
            print("Kursor MySQL ditutup.")
        if connection and connection.is_connected():
            connection.close()
            print("Koneksi MySQL ditutup.")

if __name__ == "__main__":
    print("Memulai penyiapan database dan penyisipan data...")
    if mysql_connection():
        print("Penyiapan database dan penyisipan data berhasil diselesaikan.")
        sys.exit(0)
    else:
        print("Penyiapan database dan penyisipan data gagal.")
        sys.exit(1)
