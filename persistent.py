import sqlite3

def extract_all_signalsecret_keys(sqlite_path):
    try:
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()

        # 1. SignalSecret alias 가진 모든 keyentry.id 가져오기
        cursor.execute("SELECT id FROM keyentry WHERE alias = 'SignalSecret'")
        results = cursor.fetchall()

        if not results:
            print("[!] SignalSecret alias가 존재하지 않습니다.")
            return []

        extracted_keys = []
        for idx, (key_id,) in enumerate(results):
            print(f"[+] SignalSecret #{idx+1} id: {key_id}")

            # 2. blobentry에서 해당 BLOB 추출
            cursor.execute("SELECT blob FROM blobentry WHERE keyentryid = ?", (key_id,))
            blob_result = cursor.fetchone()
            if not blob_result:
                print(f"[!] BLOB 누락됨 (keyentryid: {key_id})")
                continue

            key_blob = blob_result[0]
            if len(key_blob) < 5 + 16:
                print(f"[!] BLOB 길이가 너무 짧음 (len={len(key_blob)})")
                continue

            key_material = key_blob[5:5+16]
            print(f"    → 추출된 복호화 키 (16바이트 hex): {key_material.hex()}")

            extracted_keys.append(key_material)

        return extracted_keys

    except Exception as e:
        print(f"[!] 오류 발생: {e}")
        return []

# 사용 예시
if __name__ == "__main__":
    sqlite_path = "extracted_files/persistent.sqlite"
    extract_all_signalsecret_keys(sqlite_path)

