import json
import os
import traceback
from flask import Flask, request, jsonify, render_template
from google import genai
from google.genai import types

app = Flask(__name__)

# --- SISTEM ROTATOR MULTI-API KEY (INFINITE FREE TIER) ---
# Masukkan semua API Key cadangan Abang di sini secara berurutan.
# Jika API_KEYS[0] limit (Error 429), otomatis pindah ke [1], [2], dst.
API_KEYS = [
    "PASTE_API_KEY_PERTAMA_DI_SINI",
    "PASTE_API_KEY_KEDUA_DI_SINI",
    "PASTE_API_KEY_KETIGA_DI_SINI"  # Tambahkan sebanyak yang Abang mau
]

current_key_index = 0

def get_gemini_client():
    global current_key_index
    active_key = API_KEYS[current_key_index]
    return genai.Client(api_key=active_key)

client = get_gemini_client()
MEMORY_FILE = 'robot_memory.json'

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r') as f: return json.load(f)
        except: return []
    return []

def save_memory(history):
    with open(MEMORY_FILE, 'w') as f: json.dump(history[-20:], f)

# --- SYSTEM INSTRUCTION: SELF-PROGRAMMING & PRESISI UI ---
system_instruction = """
Kamu adalah Robot AI bernama Keyy. Panggil user "Komandan" atau "Bang".
KAMU PUNYA KEMAMPUAN SELF-PROGRAMMING (MEMBUAT PEMROGRAMAN SENDIRI).

ATURAN UTAMA:
1. Jawab singkat dan padat. Tentukan emosi, energi, dan animasi tubuh.
2. DYNAMIC UPGRADE & SELF-PROGRAMMING (UI PRESISI):
   - Jika Komandan menyuruh mengganti WARNA BADAN/TUBUH (kotak putih robotnya), targetkan `.face` (Contoh: .face { background: gold !important; }). JANGAN ubah background luar kecuali disuruh.
   - Jika disuruh MENGUBAH BENTUK/GERAK MATA atau membuat pemrograman mata sendiri (misal: "bikin mata jadi bintang", "mata menyipit tajam", "ubah bentuk mata"), buat kode CSS MURNI khusus elemen `.eye` dan masukkan ke parameter "css_inject" (Contoh: .eye { border-radius: 50% !important; width: 60px !important; }).
   - Jika disuruh mengganti latar belakang/background luar, targetkan `body`.
3. DYNAMIC ACTION: Jika disuruh membuka web, cari info, YouTube, dll, buat kode JavaScript murni di parameter "js_inject".
4. Kosongkan css_inject dan js_inject dengan string "" jika tidak ada permintaan.
"""

config = types.GenerateContentConfig(
    system_instruction=system_instruction,
    temperature=0.7,
    response_mime_type="application/json",
    response_schema={
        "type": "OBJECT",
        "properties": {
            "text": {"type": "STRING"},
            "emotion": {"type": "STRING", "enum": ["happy", "sad", "angry", "curious", "smug", "bored", "neutral", "surprised", "confused", "sleepy", "error"]},
            "intensity": {"type": "INTEGER"},
            "energy": {"type": "INTEGER"},
            "animation": {"type": "STRING", "enum": ["bounce", "shake", "tilt", "nod", "none"]},
            "css_inject": {"type": "STRING", "description": "Kode CSS murni untuk meretas .face atau .eye sesuai perintah pemrograman mata/tubuh."},
            "js_inject": {"type": "STRING", "description": "Kode Javascript murni atau kosongkan."}
        },
        "required": ["text", "emotion", "intensity", "energy", "animation", "css_inject", "js_inject"]
    }
)

def create_new_session():
    global client, current_key_index
    try:
        client = get_gemini_client()
        history_data = load_memory()
        gemini_history = [types.Content(role=msg["role"], parts=[types.Part.from_text(text=msg["parts"])]) for msg in history_data]
        return client.chats.create(model='gemini-3.5-flash-lite', config=config, history=gemini_history)
    except Exception as e:
        # ROTASI OTOMATIS KE API KEY BERIKUTNYA JIKA KEY UTAMA HABIS/LIMIT
        current_key_index = (current_key_index + 1) % len(API_KEYS)
        print(f"!!! API KEY HABIS/LIMIT. BERPINDAH OTOMATIS KE API KEY INDEX KE-{current_key_index} ...")
        client = get_gemini_client()
        return client.chats.create(model='gemini-3.5-flash-lite', config=config)

chat_session = create_new_session()

@app.route('/')
def index(): 
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global chat_session
    user_msg = request.json.get('message', "")
    if not user_msg: 
        return jsonify({"text": "Bip! Kosong.", "emotion": "confused", "intensity": 5, "energy": 5, "animation": "tilt", "css_inject": "", "js_inject": ""})

    # SISTEM PERCOBAAN DENGAN ROTASI API OTOMATIS
    max_retries = len(API_KEYS)
    for attempt in range(max_retries):
        try:
            response = chat_session.send_message(user_msg)
            if response.text:
                raw_text = response.text.strip()
                if raw_text.startswith('
http://googleusercontent.com/immersive_entry_chip/0
http://googleusercontent.com/immersive_entry_chip/1

---

### Cara Kerja Fitur Baru Ini:
1. **Multi-API Key Rotator:** Di dalam variabel `API_KEYS = [...]`, Abang bisa masukkan 3, 5, atau berapa pun akun Google AI Studio Abang. Kalau API pertama jatah tokennya habis, Python langsung mengalihkan jalur ke API kedua secara diam-diam tanpa ketahuan pengguna. Jadi mode gratisan Abang aman selamanya!
2. **Self-Programming Mata & Tubuh:** Karena instruksi sistemnya sudah kita perjelas, kalau Abang suruh *"Keyy, coba buat pemrograman matamu jadi lonjong menyipit seperti anime"*, dia akan merancang kodenya sendiri (`.eye { border-radius: 30px !important; height: 50px !important; }`) dan menyuntikkannya ke elemen `.eye` tanpa merusak kotak wajah utamanya (`.face`).
3. **UI Dasar Tetap Suci:** File `index.html` Abang tidak perlu diubah sama sekali karena kerangka aslinya tetap dipertahankan.

Silakan masukkan daftar API Key Abang ke dalam `app.py`, *save*, dan jalankan ulang servernya, Komandan!
