import sys
import mysql.connector
from faker import Faker
import time
import random

fake = Faker()
data = 1000000 # Jumlah catatan palsu yang akan dimasukkan

def mysql_connection():
    connection = None
    cur = None
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='rootpassword',
        )

        cur = connection.cursor()
        dbname = "pengaduan"
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {dbname};")
        cur.execute(f"USE {dbname};")
        print("Database 'pengaduan' berhasil dibuat dan telah digunakan.")

        # Pernyataan pembuatan tabel
        statement_users = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            email VARCHAR(100) NOT NULL,
            password VARCHAR(255) NOT NULL,
            role ENUM('rt', 'warga') NOT NULL DEFAULT 'warga',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );
        """

        statement_kategoris = """
        CREATE TABLE IF NOT EXISTS kategoris (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nama VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );
        """

        statement_pengaduan = """
        CREATE TABLE IF NOT EXISTS pengaduan (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            kategori_id INT NOT NULL,
            FOREIGN KEY (kategori_id) REFERENCES kategoris(id),
            judul VARCHAR(255) NOT NULL,
            isi TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            lampiran VARCHAR(255) DEFAULT NULL,
            status ENUM('pending', 'proses', 'selesai') NOT NULL DEFAULT 'pending'
        );
        """

        statement_comments = """
        CREATE TABLE IF NOT EXISTS comments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            pengaduan_id INT NOT NULL,
            FOREIGN KEY (pengaduan_id) REFERENCES pengaduan(id),
            user_id INT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            isi TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );
        """

        cur.execute(statement_users)
        print("Tabel 'users' berhasil dibuat.")
        cur.execute(statement_kategoris)
        print("Tabel 'kategoris' berhasil dibuat.")
        cur.execute(statement_pengaduan)
        print("Tabel 'pengaduan' berhasil dibuat.")
        cur.execute(statement_comments)
        print("Tabel 'comments' berhasil dibuat.")

        start_time = time.time() # Mulai pengukuran waktu total

        # --- Masukkan data ke tabel users ---
        print(f"Memasukkan {data} baris data palsu ke tabel 'users'...")
        users_to_insert = []
        use_role = ['warga', 'rt']
        # Mengumpulkan data dalam batch untuk executemany
        for i in range(data):
            name = fake.name()
            email = fake.email()
            password = fake.password()
            role = random.choice(use_role) # Pilih secara acak antara 'warga' dan 'rt'
            users_to_insert.append((name, email, password, role))
            
            # Eksekusi batch setiap 10.000 baris atau di akhir
            if (i + 1) % 10000 == 0 or (i + 1) == data:
                cur.executemany("INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)", users_to_insert)
                connection.commit() # Commit batch
                print(f"Telah memasukkan {i + 1} baris ke 'users'...")
                users_to_insert = [] # Kosongkan daftar untuk batch berikutnya
        
        print(f"Data palsu berhasil dimasukkan ke tabel 'users'.")

        # Dapatkan semua ID pengguna untuk hubungan foreign key
        cur.execute("SELECT id FROM users;")
        user_ids = [row[0] for row in cur.fetchall()]
        if not user_ids:
            print("Peringatan: Tidak ada pengguna yang ditemukan setelah penyisipan. Tidak dapat melanjutkan dengan tabel terkait.")
            return False

        # --- Masukkan data ke tabel kategoris ---
        print("Memasukkan data palsu ke tabel 'kategoris'...")
        kategori_list = [
            "infrastruktur", "keamanan", "lingkungan", "layanan publik",
            "transportasi", "pendidikan", "kesehatan", "sosial"
        ]
        kategoris_to_insert = [(nama,) for nama in kategori_list]
        cur.executemany("INSERT INTO kategoris (nama) VALUES (%s)", kategoris_to_insert)
        connection.commit() # Commit setelah kategori
        print("Data palsu berhasil dimasukkan ke tabel 'kategoris'.")

        # Dapatkan semua ID kategori
        cur.execute("SELECT id FROM kategoris;")
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
            lampiran = f"/uploads/{fake.uuid4()}.jpg" # Contoh jalur yang lebih realistis
            status = random.choice(['pending', 'proses', 'selesai'])
            pengaduan_to_insert.append((user_id, kategori_id, judul, isi, lampiran, status))

            if (i + 1) % 10000 == 0 or (i + 1) == data:
                cur.executemany("INSERT INTO pengaduan (user_id, kategori_id, judul, isi, lampiran, status) VALUES (%s, %s, %s, %s, %s, %s)", pengaduan_to_insert)
                connection.commit() # Commit batch
                print(f"Telah memasukkan {i + 1} baris ke 'pengaduan'...")
                pengaduan_to_insert = []

        print(f"Data palsu berhasil dimasukkan ke tabel 'pengaduan'.")
        
        # Dapatkan semua ID pengaduan untuk hubungan foreign key
        cur.execute("SELECT id FROM pengaduan;")
        pengaduan_ids = [row[0] for row in cur.fetchall()]
        if not pengaduan_ids:
            print("Peringatan: Tidak ada pengaduan yang ditemukan setelah penyisipan. Tidak dapat melanjutkan dengan komentar.")
            return False

        # --- Masukkan data ke tabel comments ---
        print(f"Memasukkan {data} baris data palsu ke tabel 'comments'...")
        comments_to_insert = []
        for i in range(data):
            pengaduan_id = random.choice(pengaduan_ids)
            user_id = random.choice(user_ids)
            isi = fake.text()
            comments_to_insert.append((pengaduan_id, user_id, isi))

            if (i + 1) % 10000 == 0 or (i + 1) == data:
                cur.executemany("INSERT INTO comments (pengaduan_id, user_id, isi) VALUES (%s, %s, %s)", comments_to_insert)
                connection.commit() # Commit batch
                print(f"Telah memasukkan {i + 1} baris ke 'comments'...")
                comments_to_insert = []

        print(f"Data palsu berhasil dimasukkan ke tabel 'comments'.")

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Total waktu yang dibutuhkan untuk memasukkan semua data palsu: {elapsed_time:.2f} detik")
        print("Semua transaksi data telah selesai dan di-commit.") # Pesan akhir

        return True
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        if connection:
            connection.rollback() # Rollback perubahan jika terjadi kesalahan
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
