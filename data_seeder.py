import sys
import mysql.connector
from faker import Faker
import time

fake = Faker()
data = 1000000

def mysql_connection():
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
        print("Database berhasil dibuat dan telah digunakan")

        statement_pengguna = """
        CREATE TABLE IF NOT EXISTS pengguna (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nama VARCHAR(50) NOT NULL,
            email VARCHAR(100) NOT NULL,
            password VARCHAR(255) NOT NULL,
            role ENUM('RT', 'warga') NOT NULL DEFAULT 'warga',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );
        """

        statement_kategori = """
        CREATE TABLE IF NOT EXISTS kategori (
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
            FOREIGN KEY (user_id) REFERENCES pengguna(id),
            kategori_id INT NOT NULL,
            FOREIGN KEY (kategori_id) REFERENCES kategori(id),
            judul VARCHAR(255) NOT NULL,
            isi TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            lampiran VARCHAR(255) DEFAULT NULL,
            status ENUM('pending', 'proses', 'selesai') NOT NULL DEFAULT 'pending'
        );
        """

        statement_komentar = """
        CREATE TABLE IF NOT EXISTS komentar (
            id INT AUTO_INCREMENT PRIMARY KEY,
            pengaduan_id INT NOT NULL,
            FOREIGN KEY (pengaduan_id) REFERENCES pengaduan(id),
            user_id INT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES pengguna(id),
            isi TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );
        """

        cur.execute(statement_pengguna)
        print("Table 'pengguna' created successfully.")
        cur.execute(statement_kategori)
        print("Table 'kategori' created successfully.")
        cur.execute(statement_pengaduan)
        print("Table 'pengaduan' created successfully.")
        cur.execute(statement_komentar)
        print("Table 'komentar' created successfully.")

        # Insert fake data into pengguna table
        print("Inserting fake data into 'pengguna' table...")
        start_time = time.time()
        for i in range(data):
            nama = fake.name()
            email = fake.email()
            password = fake.password()
            role = 'warga' if i % 2 == 0 else 'RT'
            cur.execute("INSERT INTO pengguna (nama, email, password, role) VALUES (%s, %s, %s, %s)",
                (nama, email, password, role))
            print(f"Inserted {i + 1} rows into 'pengguna'...")
        print(f"Fake data inserted into 'pengguna' table successfully")

        # Insert fake data into kategori table
        print("Inserting fake data into 'kategori' table...")
        kategori_list = [
            "infrastruktur", "keamanan", "lingkungan", "layanan publik",
            "transportasi", "pendidikan", "kesehatan", "sosial"
        ]
        for i, nama in enumerate(kategori_list):
            cur.execute("INSERT INTO kategori (nama) VALUES (%s)", (nama,))
            print(f"Inserted kategori {i + 1}/{len(kategori_list)}: {nama}")
        print("Fake data inserted into 'kategori' table successfully.")

        # Insert fake data into pengaduan table
        print("Inserting fake data into 'pengaduan' table...")
        for i in range(data):
            user_id = fake.random_int(min=1, max=5)
            kategori_id = fake.random_int(min=1, max=len(kategori_list))
            judul = fake.sentence()
            isi = fake.text()
            lampiran = fake.file_path(depth=1, category='image')
            status = fake.random_element(elements=('pending', 'proses', 'selesai'))
            cur.execute("INSERT INTO pengaduan (user_id, kategori_id, judul, isi, lampiran, status) VALUES (%s, %s, %s, %s, %s, %s)",
            (user_id, kategori_id, judul, isi, lampiran, status))
            print(f"Inserted {i + 1} rows into 'pengaduan'...")
        print(f"Fake data inserted into 'pengaduan' table successfully")
        
        # Insert fake data into komentar table
        print("Inserting fake data into 'komentar' table...")
        for i in range(data):
            pengaduan_id = fake.random_int(min=1, max=5)
            user_id = fake.random_int(min=1, max=5)
            isi = fake.text()
            cur.execute("INSERT INTO komentar (pengaduan_id, user_id, isi) VALUES (%s, %s, %s)",
                (pengaduan_id, user_id, isi))
            print(f"Inserted {i + 1} rows into 'komentar'...")
        print(f"Fake data inserted into 'komentar' table successfully ")

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Total time taken to insert fake data: {elapsed_time:.2f} seconds")

        # Commit the changes
        connection.commit()
        print("Data committed successfully.")
        cur.close()

        if connection.is_connected():
            print("Connection to MySQL database was successful.")
            return True
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("MySQL connection is closed.")

if __name__ == "__main__":
    if mysql_connection():
        print("MySQL connection test passed.")
    else:
        print("MySQL connection test failed.")
        sys.exit(1)
    sys.exit(0)
