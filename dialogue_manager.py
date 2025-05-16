import uuid, os, json
from openai import OpenAI

class DialogueManager:
    def __init__(self):
        self.store = {}  # session_id -> list of {"role","content"}

    def handle_message(self, session_id, user_msg):
        if not session_id or session_id not in self.store:
            session_id = str(uuid.uuid4())
            self.store[session_id] = [{"role":"system","content":"You are Nova, an AI assistant."}]
        history = self.store[session_id]
        history.append({"role":"user","content":user_msg})

        # call OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=history
        )
        assistant_msg = resp.choices[0].message.content
        history.append({"role":"assistant","content":assistant_msg})
        return assistant_msg, session_id
