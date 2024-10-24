from flask import Flask, request, jsonify, send_file
from gtts import gTTS
import os
import speech_recognition as sr
import io
from pydub import AudioSegment

app = Flask(__name__)

# Route for Text-to-Speech (TTS)
@app.route('/tts', methods=['POST'])
def tts():
    data = request.json
    text = data.get("text", "")
    
    if text:
        try:
            tts = gTTS(text)
            file_path = os.path.join(os.getcwd(), "output.mp3")
            tts.save(file_path)
            return send_file(file_path, as_attachment=True)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "No text provided"}), 400

# Route for Speech-to-Text (STT)
@app.route('/stt', methods=['POST'])
def stt():
    if 'file' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['file']
    
    try:
        audio_format = audio_file.filename.split('.')[-1].lower()
        
        if audio_format == 'mp3':
            audio_data = io.BytesIO(audio_file.read())
            audio = AudioSegment.from_mp3(audio_data)
            wav_data = io.BytesIO()
            audio.export(wav_data, format='wav')
            wav_data.seek(0)
        elif audio_format == 'wav':
            wav_data = io.BytesIO(audio_file.read())
        else:
            return jsonify({"error": "Unsupported file format; please provide MP3 or WAV"}), 400

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_data) as source:
            audio = recognizer.record(source)

        text = recognizer.recognize_google(audio)
        return jsonify({"text": text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
