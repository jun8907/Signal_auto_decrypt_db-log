from sqlcipher3 import dbapi2 as sqlcipher
import sqlite3
import os
from descrypt_key import get_sqlcipher_key

def decrypt_and_export_db(encrypted_db_path, output_db_path, key_plaintext):
    try:
        print(f"[*] 복호화 시도: {encrypted_db_path}")

        
        conn = sqlcipher.connect(encrypted_db_path)
        cursor = conn.cursor()

        
        cursor.execute(f"PRAGMA key = '{key_plaintext}';")
        cursor.execute("PRAGMA cipher_page_size = 4096;")
        cursor.execute("PRAGMA kdf_iter = 1;")
        cursor.execute("PRAGMA cipher_hmac_algorithm = HMAC_SHA1;")
        cursor.execute("PRAGMA cipher_kdf_algorithm = PBKDF2_HMAC_SHA1;")

        
        cursor.execute("SELECT count(*) FROM sqlite_master;")
        print("[+] 복호화 성공!")

        print(f"[*] 백업 중 → {output_db_path}")
        with sqlite3.connect(output_db_path) as out_conn:
            out_cursor = out_conn.cursor()

            
            cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
            table_info = cursor.fetchall()

            for table_name, create_stmt in table_info:
                if table_name == "sqlite_sequence":
                    continue  

                if not create_stmt:
                    continue

                if "fts5" in create_stmt.lower():
                    print(f"[!] FTS5 테이블 제외됨: {table_name}")
                    continue

                
                out_cursor.execute(create_stmt)

                
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                if not rows:
                    continue

                placeholders = ','.join(['?'] * len(rows[0]))
                for row in rows:
                    out_cursor.execute(f"INSERT INTO {table_name} VALUES ({placeholders})", row)

            out_conn.commit()

        conn.close()
        print(f"[+] 백업 완료: {output_db_path}")
        return True

    except Exception as e:
        print(f"[!] 복호화 또는 백업 실패: {e}")
        return False



if __name__ == "__main__":
    sqlcipher_plaintext_key = get_sqlcipher_key()
    if sqlcipher_plaintext_key is None:
        print("[!] SQLCipher 키 복호화 실패, 프로그램 종료")
        exit(1)

    os.makedirs("decrypted_files", exist_ok=True)

    
    db_targets = [
        ("extracted_files/signal.db", "decrypted_files/des_signal.sqlite"),
        ("extracted_files/signal-logs.db", "decrypted_files/des_signal-logs.sqlite")
    ]

    for enc_db, out_db in db_targets:
        decrypt_and_export_db(enc_db, out_db, sqlcipher_plaintext_key)
