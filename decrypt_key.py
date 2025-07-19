from preferences import extract_and_convert_data_iv
from persistent import extract_all_signalsecret_keys
from Crypto.Cipher import AES

def get_sqlcipher_key():
    
    xml_path = "extracted_files/org.thoughtcrime.securesms_preferences.xml"
    ciphertext, gcm_tag, iv = extract_and_convert_data_iv(xml_path)
    if not ciphertext:
        return None

    
    sqlite_path = "extracted_files/persistent.sqlite"
    key_list = extract_all_signalsecret_keys(sqlite_path)
    if not key_list:
        return None

    
    for idx, key in enumerate(key_list):
        print(f"\n[*] SignalSecret #{idx+1} 복호화 시도 중...")
        try:
            cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
            plaintext = cipher.decrypt_and_verify(ciphertext, gcm_tag)
            hex_key = plaintext.hex()
            print(f"[+] 복호화 성공! SQLCipher Key (hex): {hex_key}")
            return hex_key
        except Exception:
            continue

    print("[!] 모든 SignalSecret 후보 키로 복호화 실패했습니다.")
    return None
