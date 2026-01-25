#!/usr/bin/env python3
"""
Transcription Server for Smart Dictaphone
Receives audio from M5Stack Cardputer ADV and returns transcription

Run: python transcribe_server.py
Or with Whisper API: OPENAI_API_KEY=xxx python transcribe_server.py
"""

import os
import io
import tempfile
from flask import Flask, request, jsonify

app = Flask(__name__)

# Choose transcription backend
USE_OPENAI = os.environ.get('OPENAI_API_KEY') is not None
USE_LOCAL_WHISPER = False  # Set True if you have whisper installed locally

if USE_OPENAI:
    from openai import OpenAI
    client = OpenAI()
    print("Using OpenAI Whisper API")
elif USE_LOCAL_WHISPER:
    import whisper
    model = whisper.load_model("base")  # or "small", "medium", "large"
    print("Using local Whisper model")
else:
    print("WARNING: No transcription backend configured!")
    print("Set OPENAI_API_KEY env var or install whisper locally")


@app.route('/transcribe', methods=['POST'])
def transcribe():
    """Receive audio and return transcription"""

    # Get audio data
    if request.content_type == 'audio/wav':
        audio_data = request.data
    elif 'file' in request.files:
        audio_data = request.files['file'].read()
    else:
        return jsonify({'error': 'No audio data'}), 400

    print(f"Received {len(audio_data)} bytes of audio")

    # Save to temp file
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        f.write(audio_data)
        temp_path = f.name

    try:
        # Transcribe
        if USE_OPENAI:
            text = transcribe_openai(temp_path)
        elif USE_LOCAL_WHISPER:
            text = transcribe_local(temp_path)
        else:
            text = "[No transcription backend configured]"

        print(f"Transcription: {text}")

        return jsonify({
            'text': text,
            'audio_size': len(audio_data)
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

    finally:
        # Cleanup
        os.unlink(temp_path)


def transcribe_openai(audio_path):
    """Transcribe using OpenAI Whisper API"""
    with open(audio_path, 'rb') as f:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            language="ru"  # Change to your language or remove for auto-detect
        )
    return response.text


def transcribe_local(audio_path):
    """Transcribe using local Whisper model"""
    result = model.transcribe(audio_path, language="ru")
    return result["text"]


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'backend': 'openai' if USE_OPENAI else ('local' if USE_LOCAL_WHISPER else 'none')
    })


@app.route('/', methods=['GET'])
def index():
    """Info page"""
    return """
    <h1>Dictaphone Transcription Server</h1>
    <p>POST /transcribe - Send audio, get text</p>
    <p>GET /health - Health check</p>
    <hr>
    <p>Backend: {}</p>
    """.format('OpenAI' if USE_OPENAI else ('Local Whisper' if USE_LOCAL_WHISPER else 'None'))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Transcription Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind')
    parser.add_argument('--debug', action='store_true', help='Debug mode')

    args = parser.parse_args()

    print(f"\nStarting server on http://{args.host}:{args.port}")
    print("Endpoints:")
    print("  POST /transcribe - Send audio for transcription")
    print("  GET /health - Health check")
    print()

    app.run(host=args.host, port=args.port, debug=args.debug)
