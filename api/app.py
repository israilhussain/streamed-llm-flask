from flask import Flask, request, Response, stream_with_context
import requests
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()  # This loads variables from .env file

ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
DATAIKU_SERVER_URL = os.environ.get("DATAIKU_SERVER_URL")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes and origins

# Forward streaming response from API A
@app.route('/proxy_llm_stream', methods=['POST'])
def proxy_llm_stream():
    if not request.is_json:
        return {"error": "Expected JSON"}, 400

    data = request.get_json()
    user_message = data.get("message", "")
    if not user_message:
        return {"error": "Message is required"}, 400

    # Send request to original API (API A)
    def stream():
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }

        with requests.post(
            DATAIKU_SERVER_URL,
            json={"message": user_message},
            headers=headers,
            stream=True
        ) as r:
            for line in r.iter_lines(decode_unicode=True):
                if line:
                    yield line + "\n"

    return Response(
        stream_with_context(stream()),
        mimetype='text/event-stream',
        headers={'X-Accel-Buffering': 'no'}
    )
    
    
@app.route('/ping', methods=['GET'])
def ping():
    return "pong"


# # Vercel expects this exported handler
# def handler(request, context):
#     return app(request.environ, start_response=None)


# Run locally for testing
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

