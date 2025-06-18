from flask import Flask, request, jsonify, send_file
from openai import OpenAI
from flask_cors import CORS
import tempfile

app = Flask(__name__)
CORS(app)
client = OpenAI()

@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.json
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "No text provided"}), 400
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Summarize the following text in clear English."},
                {"role": "user", "content": text}
            ],
            temperature=0.5
        )
        summary = response.choices[0].message.content
        return jsonify({"summary": summary})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/speak", methods=["POST"])
def speak():
    data = request.json
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "No text provided"}), 400
    try:
        speech = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=text
        )
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        speech.stream_to_file(tmp.name)
        return send_file(tmp.name, mimetype="audio/mpeg", as_attachment=False)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


from flask import request
import tempfile

@app.route("/transcribe", methods=["POST"])
def transcribe():
    audio_file = request.files.get("file")
    if not audio_file:
        return jsonify({"error": "No audio file provided"}), 400
    try:
        # 一時ファイルとして保存
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp:
            audio_file.save(temp.name)

            # Whisperで音声認識（transcription）
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=open(temp.name, "rb"),
                response_format="json"
            )

        return jsonify({"text": transcription.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
