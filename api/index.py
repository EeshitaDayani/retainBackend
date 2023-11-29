from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import pytesseract
from pydub import AudioSegment
import speech_recognition as sr
# from sentence_transformers import SentenceTransformer
# from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
CORS(app)

referenceText = ""
userInput = ""

@app.route("/api/home", methods=['GET'])
def return_home():
    global referenceText
    referenceText = request.args.get('value', default='default_value')

    return jsonify({
        'message': 'success'
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
    sound = AudioSegment.from_file(audio_path, format="webm")
    sound.export("temp_audio.wav", format="wav")

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

@app.route("/api/getUserAttempt", methods=['POST'])
def extract_user_input():
    global userInput
    audio_file = request.files['audio']
    # Save the uploaded audio temporarily
    audio_path = 'temp_audio.webm'
    audio_file.save(audio_path)

    # Convert the webm format to wav using pydub
    sound = AudioSegment.from_file(audio_path, format="webm")
    sound.export("temp_audio.wav", format="wav")

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

# @app.route("/api/compareTexts", methods=['GET'])
# def compareTexts():
#     model = SentenceTransformer('bert-base-nli-mean-tokens')
#     comp = model.encode([referenceText, userInput])
#     similarity = (cosine_similarity([comp[0]], comp[1:])[0][0])*100//10

#     return jsonify({
#         'score': similarity
#     })

if __name__ == "__main__":
    app.run(debug=True)
