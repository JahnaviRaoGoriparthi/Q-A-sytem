from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from gtts import gTTS
import os
import speech_recognition as sr
import io
from pydub import AudioSegment

app = Flask(__name__)
# Enable CORS for all routes
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Route for Text-to-Speech (TTS)
@app.route('/tts', methods=['POST', 'OPTIONS'])
def tts():
    if request.method == 'OPTIONS':
        return handle_options()
        
    data = request.json
    text = data.get("text", "")
    
    if text:
        try:
            tts = gTTS(text)
            file_path = os.path.join(os.getcwd(), "output.mp3")
            tts.save(file_path)
            
            response = send_file(
                file_path,
                as_attachment=True,
                download_name="output.mp3",
                mimetype="audio/mpeg"
            )
            
            # Add CORS headers to the response
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
            
        except Exception as e:
            return create_error_response(str(e), 500)
    return create_error_response("No text provided", 400)

# Route for Speech-to-Text (STT)
@app.route('/stt', methods=['POST', 'OPTIONS'])
def stt():
    if request.method == 'OPTIONS':
        return handle_options()
        
    if 'file' not in request.files:
        return create_error_response("No audio file provided", 400)

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
            return create_error_response("Unsupported file format; please provide MP3 or WAV", 400)

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_data) as source:
            audio = recognizer.record(source)

        text = recognizer.recognize_google(audio)
        return create_success_response({"text": text})

    except Exception as e:
        return create_error_response(str(e), 500)

# Helper function to handle OPTIONS requests
def handle_options():
    response = jsonify({'status': 'OK'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

# Helper function to create error responses with CORS headers
def create_error_response(message, status_code):
    response = jsonify({"error": message})
    response.status_code = status_code
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# Helper function to create success responses with CORS headers
def create_success_response(data):
    response = jsonify(data)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# Global error handler
@app.errorhandler(Exception)
def handle_error(error):
    return create_error_response(str(error), 500)

if __name__ == '__main__':
    app.run(debug=True)
