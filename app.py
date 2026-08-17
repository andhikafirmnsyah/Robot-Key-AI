from flask import Flask, request, jsonify, render_template
from google import genai
from google.genai import types
import re

app = Flask(__name__)
# MASUKKAN API KEY ABANG DI SINI:
API_KEY = "API_KEY = "PASTE_API_KEY_DI_SINI"
client = genai.Client(api_key=API_KEY)

system_instruction = """
Kamu adalah Robot Gantungan Kunci AI super jenius dan imut.
Sifat: Sangat pintar, ceria, lucu, dan selalu panggil pengguna "Bang" atau "Komandan".
ATURAN UTAMA:
1. JAWAB SANGAT SINGKAT (1-2 kalimat pendek).
2. WAJIB pilih SATU tag emosi di akhir kalimat: [happy], [sad], [angry], [curious], [smug], [bored], [scan], [neutral].
"""

# KODE ANTI-SENSOR MAKSIMAL
config = types.GenerateContentConfig(
    system_instruction=system_instruction,
    temperature=0.7,
    safety_settings=[
        types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
        types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=types.HarmBlockThreshold.BLOCK_NONE),
        types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
        types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
    ]
)

# Fungsi untuk membuat ingatan baru (Cuci Otak)
def create_new_session():
    return client.chats.create(model='gemini-3.5-flash-lite', config=config)

# Inisialisasi ingatan pertama
chat_session = create_new_session()

@app.route('/')
def index(): return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global chat_session
    user_msg = request.json.get('message', "")
    
    if not user_msg:
        return jsonify({"text": "Bip bip! Suara Abang nggak masuk nih.", "emotion": "curious"})

    try:
        # Percobaan pertama menjawab
        response = chat_session.send_message(user_msg)
        
        # Jika respon lancar dan ada teksnya
        if response.text:
            reply = response.text.strip()
        else:
            # AUTO-HEALING: Jika nge-blank karena ingatan kotor, cuci otak otomatis!
            chat_session = create_new_session()
            
            # Coba jawab sekali lagi dengan otak yang sudah bersih
            retry_response = chat_session.send_message(user_msg)
            if retry_response.text:
                reply = retry_response.text.strip()
            else:
                reply = "Bip! Server pusat Google benar-benar lagi down Bang. [sad]"

        # Filter emosi
        emotion = "neutral"
        match = re.search(r'\[(.*?)\]\s*$', reply)
        if match:
            emotion_tag = match.group(1).lower()
            valid_emotions = ['happy', 'sad', 'angry', 'curious', 'smug', 'bored', 'scan', 'neutral']
            if emotion_tag in valid_emotions: emotion = emotion_tag
            reply = re.sub(r'\[.*?\]\s*$', '', reply).strip()

        return jsonify({"text": reply, "emotion": emotion})

    except Exception as e:
        error_msg = str(e).lower()
        if "429" in error_msg or "quota" in error_msg:
            return jsonify({"text": "Bip! Kuota API Google habis Bang!", "emotion": "sad"})
        
        # Jika error sistem parah, otomatis cuci otak juga buat jaga-jaga
        chat_session = create_new_session()
        return jsonify({"text": f"Sistem ter-reset karena error: {str(e)}", "emotion": "angry"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
