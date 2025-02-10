import io
import shutil
import tempfile
import traceback

from gtts import gTTS
from flask import Flask, request, send_file, jsonify, render_template

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate-audio", methods=["POST"])
def generate_audio_endpoint():
    data = request.get_json()

    if "text" not in data or not data["text"].strip():
        return jsonify({"error": "Text input is required"}), 400

    text = data["text"]

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = f"{temp_dir}/output.mp3"

            # Save to disk
            tts = gTTS(text)
            tts.save(temp_file_path)

            # Read file bytes into memory
            audio_io = io.BytesIO()
            with open(temp_file_path, "rb") as temp_file:
                shutil.copyfileobj(temp_file, audio_io)

            audio_io.seek(0)
            return send_file(
                audio_io,
                as_attachment=True,
                mimetype="audio/mpeg",
                download_name="output.mp3",
            )
    except PermissionError:
        traceback.print_exc()
        return (
            jsonify(
                {
                    "error": "Permission denied: Unable to access the file. Please check file permissions."
                }
            ),
            500,
        )
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Something unexpected happened."}), 500


if __name__ == "__main__":
    app.run(debug=True)
