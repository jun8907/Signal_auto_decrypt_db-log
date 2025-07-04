import subprocess
import os

def su_pull(remote_path, local_filename):
    temp_path = f"/sdcard/{local_filename}"
    local_output = os.path.join("extracted_files", local_filename)

    try:
        print(f"[*] su 권한으로 {remote_path} → {temp_path} 복사 중...")
        subprocess.run(["adb", "shell", f"su -c 'cp {remote_path} {temp_path}'"], shell=True, check=True)

        print(f"[*] {temp_path} → {local_output} 로컬로 추출 중...")
        subprocess.run(["adb", "pull", temp_path, local_output], check=True)

        print(f"[+] 추출 완료: {local_output}")
    except subprocess.CalledProcessError as e:
        print(f"[!] 오류 발생 ({local_filename}): {e}")

def pull_all_artifacts():
    os.makedirs("extracted_files", exist_ok=True)

    package = "org.thoughtcrime.securesms"
    # 1. shared_prefs
    su_pull(f"/data/data/{package}/shared_prefs/{package}_preferences.xml", f"{package}_preferences.xml")
    
    # 2. signal.db
    su_pull(f"/data/data/{package}/databases/signal.db", "signal.db")

    # 3. signal-logs.db
    su_pull(f"/data/data/{package}/databases/signal-logs.db", "signal-logs.db")

    # 4. persistent.sqlite
    su_pull("/data/misc/keystore/persistent.sqlite", "persistent.sqlite")

# 실행
if __name__ == "__main__":
    pull_all_artifacts()
