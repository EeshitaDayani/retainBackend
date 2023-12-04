from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import pytesseract
#from pydub import AudioSegment
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_audio
import speech_recognition as sr
import requests


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
    file = request.files['file']
    # Save the uploaded image temporarily
    image_path = 'temp_image.png'
    file.save(image_path)

    # Use Tesseract to extract text from the image
    referenceText = pytesseract.image_to_string(Image.open(image_path)).strip()

    # Remove the temporary image file
    import os
    os.remove(image_path)

    return jsonify({
        'text': referenceText
    })

@app.route("/api/extractTextFromAudio", methods=['POST'])
def extract_text_from_audio():
    global referenceText
    audio_file = request.files['audio']
    # Save the uploaded audio temporarily
    audio_path = 'temp_audio.webm'
    audio_file.save(audio_path)

    # Convert the webm format to wav using pydub
    #sound = AudioSegment.from_file(audio_path, format="webm")
    #sound.export("temp_audio.wav", format="wav")
    ffmpeg_extract_audio(audio_path, "temp_audio.wav")
    #sound = moviepy.VideoFileClip(audio_path)
    #sound.audio.write_audiofile("temp_audio.wav")

    # Use SpeechRecognition to transcribe the audio
    recognizer = sr.Recognizer()
    with sr.AudioFile("temp_audio.wav") as source:
        audio_data = recognizer.record(source)
        extracted_text = recognizer.recognize_google(audio_data, show_all=True)
        referenceText = extracted_text['alternative'][0]['transcript']

        # Remove the temporary audio files
        import os
        os.remove(audio_path)
        os.remove("temp_audio.wav")

        return jsonify({
            'text': referenceText
        })


@app.route("/api/extractedText", methods=['GET'])
def extractedText():
    return jsonify({
        'message': referenceText
    })


@app.route("/api/getUserAttempt", methods=['POST'])
def extract_user_input():
    global userInput
    audio_file = request.files['audio']
    # Save the uploaded audio temporarily
    audio_path = 'temp_audio.webm'
    audio_file.save(audio_path)

    # Convert the webm format to wav using pydub
    # sound = AudioSegment.from_file(audio_path, format="webm")
    # sound.export("temp_audio.wav", format="wav")
    ffmpeg_extract_audio(audio_path, "temp_audio.wav")
    # sound = moviepy.VideoFileClip(audio_path)
    # sound.audio.write_audiofile("temp_audio.wav")

    # Use SpeechRecognition to transcribe the audio
    recognizer = sr.Recognizer()
    with sr.AudioFile("temp_audio.wav") as source:
        global userInput
        audio_data = recognizer.record(source)
        extracted_text = recognizer.recognize_google(audio_data, show_all=True)
        userInput = extracted_text['alternative'][0]['transcript']

        # Remove the temporary audio files
        import os
        os.remove(audio_path)
        os.remove("temp_audio.wav")

        return jsonify({
            'text': userInput
        })

@app.route("/api/compareTexts", methods=['GET'])
def compareTexts():
    api_token = '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'
    API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/all-mpnet-base-v2"
    headers = {"Authorization": f"Bearer {api_token}"}
    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        print(response.json())
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
    app.run(debug=True, port=8080)
