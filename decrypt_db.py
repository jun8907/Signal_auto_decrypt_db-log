from sqlcipher3 import dbapi2 as sqlcipher
import sqlite3
import os
import csv
import xml.etree.ElementTree as ET

from decrypt_key import get_sqlcipher_key

def decrypt_and_export_db(encrypted_db_path, output_db_path, key_plaintext):
    try:
        print(f"[*] 복호화 시도: {encrypted_db_path}")

        # SQLCipher DB 열고 복호화
        conn = sqlcipher.connect(encrypted_db_path)
        cursor = conn.cursor()

        cursor.execute(f"PRAGMA key = '{key_plaintext}';")
        cursor.execute("PRAGMA cipher_page_size = 4096;")
        cursor.execute("PRAGMA kdf_iter = 1;")
        cursor.execute("PRAGMA cipher_hmac_algorithm = HMAC_SHA1;")
        cursor.execute("PRAGMA cipher_kdf_algorithm = PBKDF2_HMAC_SHA1;")

        cursor.execute("SELECT count(*) FROM sqlite_master;")
        print("[+] 복호화 성공!")

        # 새 SQLite DB로 백업 
        print(f"[*] 백업 중 → {output_db_path}")
        with sqlite3.connect(output_db_path) as out_conn:
            out_cursor = out_conn.cursor()
            cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
            for table_name, create_stmt in cursor.fetchall():
                if table_name == "sqlite_sequence" or not create_stmt:
                    continue
                if "fts5" in create_stmt.lower():
                    print(f"[!] FTS5 테이블 제외됨: {table_name}")
                    continue

                out_cursor.execute(create_stmt)
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                if not rows:
                    continue

                placeholders = ",".join(["?"] * len(rows[0]))
                for row in rows:
                    out_cursor.execute(
                        f"INSERT INTO {table_name} VALUES ({placeholders})", row
                    )
            out_conn.commit()

        print(f"[+] 백업 완료: {output_db_path}")

        # CSV 및 XML로도 내보내기
        base_name = os.path.splitext(os.path.basename(output_db_path))[0]
        dir_parent = os.path.dirname(output_db_path)
        csv_dir = os.path.join(dir_parent, f"{base_name}_csv")
        xml_dir = os.path.join(dir_parent, f"{base_name}_xml")
        os.makedirs(csv_dir, exist_ok=True)
        os.makedirs(xml_dir, exist_ok=True)

        
        with sqlite3.connect(output_db_path) as export_conn:
            export_cursor = export_conn.cursor()
            export_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [t[0] for t in export_cursor.fetchall()]

            for table in tables:
                
                export_cursor.execute(f"PRAGMA table_info({table})")
                cols = [info[1] for info in export_cursor.fetchall()]
                export_cursor.execute(f"SELECT * FROM {table}")
                rows = export_cursor.fetchall()

                
                csv_path = os.path.join(csv_dir, f"{table}.csv")
                with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    writer.writerow(cols)
                    for row in rows:
                        out = []
                        for col, val in zip(cols, row):
                            
                            if table == 'message' and col == 'message_extras' and isinstance(val, (bytes, bytearray)):
                                hexstr = val.hex()
                                hexpairs = ' '.join(hexstr[i:i+2] for i in range(0, len(hexstr), 2))
                                out.append(hexpairs)
                            else:
                                if isinstance(val, (bytes, bytearray)):
                                    out.append(val.hex())
                                else:
                                    out.append(val)
                        writer.writerow(out)
                print(f"[+] CSV 저장: {csv_path}")

                
                root = ET.Element(f"{table}_rows")
                for row in rows:
                    row_elem = ET.SubElement(root, table)
                    for col_name, value in zip(cols, row):
                        col_elem = ET.SubElement(row_elem, col_name)
                        
                        if table == 'message' and col_name == 'message_extras' and isinstance(value, (bytes, bytearray)):
                            hexstr = value.hex()
                            hexpairs = ' '.join(hexstr[i:i+2] for i in range(0, len(hexstr), 2))
                            col_elem.text = hexpairs
                        else:
                            col_elem.text = '' if value is None else str(value)
                xml_path = os.path.join(xml_dir, f"{table}.xml")
                ET.ElementTree(root).write(xml_path, encoding='utf-8', xml_declaration=True)
                print(f"[+] XML 저장: {xml_path}")

        
        cursor.execute("SELECT name, seq FROM sqlite_sequence")
        seq_rows = cursor.fetchall()
        if seq_rows:
            # CSV
            csv_seq = os.path.join(csv_dir, "sqlite_sequence.csv")
            with open(csv_seq, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['name','seq'])
                writer.writerows(seq_rows)
            print(f"[+] CSV 저장: {csv_seq}")

            # XML
            root = ET.Element("sqlite_sequence_rows")
            for name, seq in seq_rows:
                elem = ET.SubElement(root, "sqlite_sequence")
                n = ET.SubElement(elem, "name"); n.text = str(name)
                s = ET.SubElement(elem, "seq");  s.text = str(seq)
            xml_seq = os.path.join(xml_dir, "sqlite_sequence.xml")
            ET.ElementTree(root).write(xml_seq, encoding='utf-8', xml_declaration=True)
            print(f"[+] XML 저장: {xml_seq}")

        conn.close()
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
        ("extracted_files/signal.db",      "decrypted_files/dec_signal.sqlite"),
        ("extracted_files/signal-logs.db", "decrypted_files/dec_signal-logs.sqlite")
    ]

    for enc_db, out_db in db_targets:
        decrypt_and_export_db(enc_db, out_db, sqlcipher_plaintext_key)
