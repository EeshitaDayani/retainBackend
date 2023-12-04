from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import pytesseract
import speech_recognition as sr
import requests
import tempfile
import io

app = Flask(__name__)
CORS(app)

referenceText = ""
userInput = ""

@app.route("/api/textInput", methods=['POST'])
def return_text_input():
    global referenceText
    referenceText = request.args.get('value', default='default_value')

    return jsonify({
        'message': referenceText
    })

@app.route("/api/extractTextFromImage", methods=['POST'])
def extract_text_image():
    global referenceText

    try:
        file = request.files['file']

        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        image_path = os.path.join(temp_dir, 'temp_image.png')

        # Save the uploaded image temporarily
        file.save(image_path)

        # Use Tesseract to extract text from the image
        referenceText = pytesseract.image_to_string(Image.open(image_path)).strip()

        # Remove the temporary image file and directory
        os.remove(image_path)
        os.rmdir(temp_dir)

        return jsonify({
            'text': referenceText
        })
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return jsonify({
            'text': ''
        })

@app.route("/api/extractTextFromAudio", methods=['POST'])
def extract_text_from_audio():
    global referenceText

    try:
        # Set the audio file
        audio_file = request.files['audio']

        # Use SpeechRecognition to transcribe the audio
        recognizer = sr.Recognizer()
        
        with sr.AudioFile(io.BytesIO(audio_file.read())) as source:
            audio_data = recognizer.record(source)
            extracted_text = recognizer.recognize_google(audio_data, show_all=True)
            referenceText = extracted_text['alternative'][0]['transcript']

        return jsonify({
            'text': referenceText
        })

    except Exception as e:
        print(f"Error processing audio: {str(e)}")
        return jsonify({
            'error': 'Error processing audio'
        }), 500

@app.route("/api/getUserAttempt", methods=['POST'])
def extract_user_input():
    global userInput

    try:
        # Set the audio file path
        audio_file = request.files['audio']

        # Save the audio file temporarily
        temp_dir = tempfile.mkdtemp()
        audio_path = os.path.join(temp_dir, 'temp_audio.wav')
        audio_file.save(audio_path)

        # Use SpeechRecognition to transcribe the audio
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
            extracted_text = recognizer.recognize_google(audio_data)

        userInput = extracted_text

        # Remove the temporary directory and its contents
        os.rmdir(temp_dir)

        return jsonify({
            'text': userInput
        })

    except Exception as e:
        print(f"Error processing audio: {str(e)}")
        return jsonify({
            'error': 'Error processing audio'
        }), 500

@app.route("/api/compareTexts", methods=['GET'])
def compareTexts():
    api_token = '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'
    API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/all-mpnet-base-v2"
    headers = {"Authorization": f"Bearer {api_token}"}
    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()
    
    similarity = query(
        {
            "inputs": {
                "source_sentence": referenceText,
                "sentences": [
                    userInput
                ]
            }
        })
    
    return jsonify({
        'score': round((similarity[0] * 100), 2)
    })
    

if __name__ == "__main__":
    app.run(debug=True)

