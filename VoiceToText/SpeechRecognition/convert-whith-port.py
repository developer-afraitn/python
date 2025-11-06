# stt_server.py
import socket
import json
import speech_recognition as sr
from pathlib import Path
import threading

HOST = '127.0.0.1'
PORT = 5000

def handle_client(conn):
    try:
        # دریافت طول داده
        data = b""
        while len(data) < 4:
            packet = conn.recv(4 - len(data))
            if not packet:
                return
            data += packet
        length = int.from_bytes(data, 'big')

        # دریافت JSON
        data = b""
        while len(data) < length:
            packet = conn.recv(min(4096, length - len(data)))
            if not packet:
                return
            data += packet

        req = json.loads(data.decode('utf-8'))
        file_path = req.get('file_path')

        lang = 'fa-IR'
        select_lang = req.get('lang')

        match select_lang:
            case 'en': lang = 'en-US'
            case 'fa': lang = 'fa-IR'

        # چک کردن وجود فایل
        if not file_path or not Path(file_path).exists():
            response = json.dumps({"error": "فایل پیدا نشد"}).encode('utf-8')
            conn.send(len(response).to_bytes(4, 'big') + response)
            return

        # تشخیص صدا
        r = sr.Recognizer()
        with sr.AudioFile(file_path) as source:
            audio = r.record(source)

        try:
            text = r.recognize_google(audio, language=lang)
            response = json.dumps({"text": text}).encode('utf-8')
        except sr.UnknownValueError:
            response = json.dumps({"error": "صدا تشخیص داده نشد"}).encode('utf-8')
        except sr.RequestError as e:
            response = json.dumps({"error": f"خطا در اتصال به گوگل: {e}"}).encode('utf-8')

        conn.send(len(response).to_bytes(4, 'big') + response)

    except Exception as e:
        err = json.dumps({"error": str(e)}).encode('utf-8')
        conn.send(len(err).to_bytes(4, 'big') + err)
    finally:
        conn.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"سرور STT روی {HOST}:{PORT} فعال شد...")

    while True:
        conn, _ = server.accept()
        threading.Thread(target=handle_client, args=(conn,), daemon=True).start()

if __name__ == "__main__":
    main()