#!/usr/bin/env python3
"""
Transcription Server for Smart Dictaphone
Receives audio from M5Stack Cardputer ADV and returns transcription

Run with OpenRouter:
  OPENROUTER_API_KEY=sk-or-xxx python transcribe_server.py

Or with OpenAI Whisper:
  OPENAI_API_KEY=sk-xxx python transcribe_server.py
"""

import os
import base64
import requests
import tempfile
from flask import Flask, request, jsonify

app = Flask(__name__)

# Choose transcription backend
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# OpenRouter model for audio transcription
OPENROUTER_MODEL = os.environ.get('OPENROUTER_MODEL', 'google/gemini-2.5-flash')

if OPENROUTER_API_KEY:
    print(f"Using OpenRouter API with model: {OPENROUTER_MODEL}")
elif OPENAI_API_KEY:
    from openai import OpenAI
    client = OpenAI()
    print("Using OpenAI Whisper API")
else:
    print("WARNING: No API key configured!")
    print("Set OPENROUTER_API_KEY or OPENAI_API_KEY env var")


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

    try:
        # Transcribe
        if OPENROUTER_API_KEY:
            text = transcribe_openrouter(audio_data)
        elif OPENAI_API_KEY:
            text = transcribe_openai(audio_data)
        else:
            text = "[No API key configured]"

        print(f"Transcription: {text}")

        return jsonify({
            'text': text,
            'audio_size': len(audio_data)
        })

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


def transcribe_openrouter(audio_data):
    """Transcribe using OpenRouter API (Gemini, etc.)"""
    # Encode audio to base64
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "Cardputer Dictaphone"
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Transcribe this audio. Return ONLY the transcribed text, nothing else. If the audio is in Russian, transcribe in Russian."
                    },
                    {
                        "type": "input_audio",
                        "input_audio": {
                            "data": audio_base64,
                            "format": "wav"
                        }
                    }
                ]
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    result = response.json()
    return result['choices'][0]['message']['content']


def transcribe_openai(audio_data):
    """Transcribe using OpenAI Whisper API"""
    # Save to temp file (Whisper API needs file)
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        f.write(audio_data)
        temp_path = f.name

    try:
        with open(temp_path, 'rb') as f:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language="ru"  # Change or remove for auto-detect
            )
        return response.text
    finally:
        os.unlink(temp_path)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    backend = 'openrouter' if OPENROUTER_API_KEY else ('openai' if OPENAI_API_KEY else 'none')
    return jsonify({
        'status': 'ok',
        'backend': backend,
        'model': OPENROUTER_MODEL if OPENROUTER_API_KEY else 'whisper-1'
    })


@app.route('/', methods=['GET'])
def index():
    """Info page"""
    backend = 'OpenRouter' if OPENROUTER_API_KEY else ('OpenAI Whisper' if OPENAI_API_KEY else 'None')
    model = OPENROUTER_MODEL if OPENROUTER_API_KEY else 'whisper-1'
    return f"""
    <h1>Dictaphone Transcription Server</h1>
    <p>POST /transcribe - Send audio WAV, get text</p>
    <p>GET /health - Health check</p>
    <hr>
    <p>Backend: {backend}</p>
    <p>Model: {model}</p>
    """


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
