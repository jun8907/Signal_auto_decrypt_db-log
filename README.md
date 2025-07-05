# Signal_auto_descrypt_mms 🔐

복호화되지 않은 Signal 메신저의 signal.db, signal-logs.db 파일을 복호화하는 코드입니다.

<br><br>

## 🧪 사용법

```bash
python pull.py
python decrypt_db.py
```

<br><br>

## 🔧 코드 설명

- pull.py
- preferences.py
- persistent.py
- descrypt_key.py
- descrypt_db.py
<br><br>
### pull.py

루팅된 Android 디바이스에서 Signal 메신저의 db 파일 및 복호화에 필요한 핵심 파일들을 자동으로 추출하는 코드입니다.
db 파일과 복호화에 필요한 파일들은 `extracted_files/` 디렉터리에 저장

```python
[실행 결과]
[*] su 권한으로 /data/data/org.thoughtcrime.securesms/shared_prefs/org.thoughtcrime.securesms_preferences.xml → /sdcard/org.thoughtcrime.securesms_preferences.xml 복사 중...
[*] /sdcard/org.thoughtcrime.securesms_preferences.xml → extracted_files\org.thoughtcrime.securesms_preferences.xml 로컬로 추출 중...
/sdcard/org.thoughtcrime.securesms_preferences.xml: 1 file pulled, 0 skipped. 0.1 MB/s (2142 bytes in 0.022s)     
[+] 추출 완료: extracted_files\org.thoughtcrime.securesms_preferences.xml
[*] su 권한으로 /data/data/org.thoughtcrime.securesms/databases/signal.db → /sdcard/signal.db 복사 중...
[*] /sdcard/signal.db → extracted_files\signal.db 로컬로 추출 중...
/sdcard/signal.db: 1 file pulled, 0 skipped. 15.3 MB/s (3219456 bytes in 0.201s)
[+] 추출 완료: extracted_files\signal.db
[*] su 권한으로 /data/data/org.thoughtcrime.securesms/databases/signal-logs.db → /sdcard/signal-logs.db 복사 중...
[*] /sdcard/signal-logs.db → extracted_files\signal-logs.db 로컬로 추출 중...
/sdcard/signal-logs.db: 1 file pulled, 0 skipped. 5.5 MB/s (4079616 bytes in 0.709s)                              
[+] 추출 완료: extracted_files\signal-logs.db
[*] su 권한으로 /data/misc/keystore/persistent.sqlite → /sdcard/persistent.sqlite 복사 중...
[*] /sdcard/persistent.sqlite → extracted_files\persistent.sqlite 로컬로 추출 중...
/sdcard/persistent.sqlite: 1 file pulled, 0 skipped. 4.2 MB/s (139264 bytes in 0.032s)
[+] 추출 완료: extracted_files\persistent.sqlite
```

### preferences_attachment, database.py

Signal 메신저의 /share_pref/org.thoughtcrime.securesms_preferences.xml 파일에서 SQLCipher에 사용된 패스프레이즈를 추출
- `data (hex)`
- `input (hex)`
- `GCM Tag (hex)`
- `iv (base64)`

```python
[실행 결과]
[+] data (hex)       : 7d7db165c6054cb75bee9c5f98c9ef94e694a17231b0e8145a4c5e31b71cb1bb1cd5fd259b07db76d62b7f8238af4ea4
[+] ciphertext (hex) : 7d7db165c6054cb75bee9c5f98c9ef94e694a17231b0e8145a4c5e31b71cb1bb
[+] GCM tag (hex)    : 1cd5fd259b07db76d62b7f8238af4ea4
[+] iv (base64)      : bfOgEB/EMhcm8rOh
```

### persistent.py

Android 기기에서 추출한 Signal 메신저의 `persistent.sqlite` 키스토어 DB에서 `SignalSecret` alias에 해당하는 복호화 키(16바이트)를 자동으로 추출하는 코드입니다.

```python
[실행 결과]
[+] SignalSecret #1 id: 7284520658499830241
    → 추출된 복호화 키 (16바이트 hex): d1ccc1ae4d0e3a5ef0b1074794e076b7
[+] SignalSecret #2 id: 6456924783388765775
    → 추출된 복호화 키 (16바이트 hex): d843d662011f92d82c69659c4311904f
```

### descrypt_key.py

Android의 Signal 메신저에서 추출한 설정 파일 (`shared_prefs`)과 키 저장소(`persistent.sqlite`)를 이용하여, SQLCipher로 암호화된 Signal DB의 복호화 키(SQLCipher Key)를 자동으로 복원해주는 코드 입니다.

### descrypt_db.py

암호화된 Signal 데이터베이스(`signal.db`, `signal-logs.db`)를 복호화하여 일반 SQLite 형식으로 변환 및 저장해주는 코드 입니다.

```python
[실행 결과]
[*] 복호화 시도: extracted_files/signal.db
[+] 복호화 성공!
[*] 백업 중 → decrypted_files/des_signal.sqlite
[!] FTS5 테이블 제외됨: message_fts
[+] 백업 완료: decrypted_files/des_signal.sqlite
[*] 복호화 시도: extracted_files/signal-logs.db
[+] 복호화 성공!
[*] 백업 중 → decrypted_files/des_signal-logs.sqlite
[+] 백업 완료: decrypted_files/des_signal-logs.sqlite
```
