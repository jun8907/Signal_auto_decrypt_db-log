import xml.etree.ElementTree as ET
import json
import base64

def extract_and_convert_data_iv(xml_path):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        for elem in root.findall("string"):
            if elem.attrib.get("name") == "pref_database_encrypted_secret":
                json_str = elem.text
                data_obj = json.loads(json_str)

                
                data_bytes = base64.b64decode(data_obj["data"])
                iv_b64 = data_obj["iv"]
                iv_bytes = base64.b64decode(iv_b64)

                
                ciphertext = data_bytes[:-16]
                gcm_tag = data_bytes[-16:]

                print(f"[+] data (hex)       : {data_bytes.hex()}")
                print(f"[+] ciphertext (hex) : {ciphertext.hex()}")
                print(f"[+] GCM tag (hex)    : {gcm_tag.hex()}")
                print(f"[+] iv (base64)      : {iv_b64}")

                return ciphertext, gcm_tag, iv_bytes

        print("[!] 'pref_database_encrypted_secret' 항목을 찾을 수 없습니다.")
        return None, None, None

    except Exception as e:
        print(f"[!] 오류 발생: {e}")
        return None, None, None


if __name__ == "__main__":
    xml_path = "extracted_files/org.thoughtcrime.securesms_preferences.xml"
    extract_and_convert_data_iv(xml_path)