import os
import json
import uuid
import threading

from flask import (
    Flask, request, jsonify, send_from_directory,
    Response, stream_with_context
)
from openai import OpenAI
from spec_agent import interpret_spec
from site_generator import generate_site


# ——— Config & Globals ——————————————————————————————————

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set")

client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__, static_folder="dist", static_url_path="")

SESSIONS_FILE = "sessions.json"
_sessions = {}  # in-memory store, persisted to disk
_lock = threading.Lock()

# ——— Session Persistence ————————————————————————————


def load_sessions():
    global _sessions
    try:
        with open(SESSIONS_FILE, encoding="utf-8") as f:
            _sessions = json.load(f)
    except FileNotFoundError:
        _sessions = {}


def save_sessions():
    with _lock:
        with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(_sessions, f)


# Load on startup
load_sessions()

# ——— Routes ——————————————————————————————————————


# Serve static files
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path and os.path.exists(os.path.join("dist", path)):
        return send_from_directory("dist", path)
    return send_from_directory("dist", "index.html")


# Simple non‐streaming chat
@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json() or {}
        sid = data.get("session_id")
        user_msg = data.get("message", "")

        if not sid or sid not in _sessions:
            sid = str(uuid.uuid4())
            _sessions[sid] = [{
                "role":
                "system",
                "content":
                "You are Nova, an intelligent site-building assistant."
            }]

        history = _sessions[sid]
        history.append({"role": "user", "content": user_msg})

        resp = client.chat.completions.create(model="gpt-3.5-turbo",
                                              messages=history)
        assistant_msg = resp.choices[0].message.content
        history.append({"role": "assistant", "content": assistant_msg})

        save_sessions()
        return jsonify({"session_id": sid, "reply": assistant_msg})

    except Exception as e:
        app.logger.exception(e)
        return jsonify({"error": str(e)}), 500


# Streaming chat via SSE
@app.route("/api/chat-stream", methods=["POST"])
def chat_stream():
    data = request.get_json() or {}
    sid = data.get("session_id")
    user_msg = data.get("message", "")

    if not sid or sid not in _sessions:
        sid = str(uuid.uuid4())
        _sessions[sid] = [{
            "role":
            "system",
            "content":
            "You are Nova, an intelligent site-building assistant."
        }]

    history = _sessions[sid]
    history.append({"role": "user", "content": user_msg})

    def generate():
        yield 'data: {"type":"start"}\n\n'
        try:
            for chunk in client.chat.completions.create(model="gpt-3.5-turbo",
                                                        messages=history,
                                                        stream=True):
                delta = chunk.choices[0].delta.get("content", "")
                if delta:
                    payload = {"type": "delta", "content": delta}
                    yield f"data: {json.dumps(payload)}\n\n"

            yield 'data: {"type":"end"}\n\n'
            # Append full reply to history after stream ends
            full_reply = "".join(
                c.choices[0].delta.get("content", "")
                for c in client.chat.completions.create(model="gpt-3.5-turbo",
                                                        messages=history,
                                                        stream=False).choices)
            history.append({"role": "assistant", "content": full_reply})
            save_sessions()

        except Exception as e:
            err = {"type": "error", "message": str(e)}
            yield f"data: {json.dumps(err)}\n\n"

    return Response(stream_with_context(generate()),
                    mimetype="text/event-stream")


# Build endpoint
@app.route("/api/build", methods=["POST"])
def build():
    try:
        data = request.get_json() or {}
        prompt = data.get("prompt", "").strip()
        if not prompt:
            return jsonify({
                "success": False,
                "error": "Prompt cannot be empty."
            }), 400

        # 1) Interpret spec
        spec = interpret_spec(prompt)

        # 2) Write spec.json
        with open("spec.json", "w", encoding="utf-8") as f:
            json.dump(spec, f, indent=2)

        # 3) Generate site
        generate_site()

        return jsonify({"success": True, "preview": "/"})

    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400

    except Exception as e:
        app.logger.exception(e)
        return jsonify({
            "success": False,
            "error": "Internal server error."
        }), 500


# ——— Main ————————————————————————————————————————

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)
