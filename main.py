from fastapi import FastAPI, WebSocket
from typing import List
import json
import os
from datetime import datetime
from flask import Flask, render_template
import threading

app = FastAPI()
flask_app = Flask(__name__)

received_data = []

DATA_FILE = "received_data.json"

def write_to_json(data):
    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
        with open(DATA_FILE, 'r+') as file:
            try:
                file_data = json.load(file)
            except json.JSONDecodeError:
                file_data = []
            file_data.append(data)
            file.seek(0)
            json.dump(file_data, file, indent=4)
    else:
        with open(DATA_FILE, 'w') as file:
             json.dump([data], file, indent=4)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            try:
                json_data = json.loads(data)
                print(f"Received data: {json_data}")
                global received_data
                received_data.append(json_data)
                write_to_json(json_data)
            except json.JSONDecodeError as e:
                print(f"Received non-JSON data: {data}")
                print(f"Error decoding json: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await websocket.close()

@flask_app.route("/")
def index():
    global received_data
    return render_template("index.html", markers=received_data)

def run_flask_app():
    flask_app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)

if __name__ == "__main__":
    import uvicorn

    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.start()

    uvicorn.run(app, host="0.0.0.0", port=8000)