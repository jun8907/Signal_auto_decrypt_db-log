# extracted_files

Signal 메신저의 내부 데이터 복호화에 필요한 원본 파일들을 저장하는 폴더입니다.  
이 폴더에는 다음의 중요 파일들이 포함됩니다:

- `/data/misc/keystore/persistent.sqlite`  
  → Android Keystore (복호화 키 저장소)

- `/data/data/org.thoughtcrime.securesms/databases/signal.db`  
  → Signal 메시지 DB

- `/data/data/org.thoughtcrime.securesms/databases/signal-logs.db`  
  → Signal 로그 DB

- `/data/data/org.thoughtcrime.securesms/shared_prefs/org.thoughtcrime.securesms_preferences.xml`  
  → Signal 앱 설정 및 암호화 키 정보

> 이 파일들은 루팅된 안드로이드 기기에서 ADB 및 `su` 명령어를 이용해 추출됩니다.
