# decrypted_files

이 폴더는 복호화가 완료된 Signal 메신저의 데이터베이스 파일들을 저장하는 공간입니다.  
복호화된 결과물은 `.sqlite` 확장자로 저장되며, 다음과 같은 형태로 변환됩니다:

- `signal.db` → `dec_signal.sqlite`
- `signal-logs.db` → `dec_signal-logs.sqlite`

이 폴더에 저장된 파일들은 SQLCipher 복호화가 완료된 상태로, 일반 SQLite 뷰어(DB Browser 등)를 통해 열람할 수 있습니다.
