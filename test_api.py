import requests
import random

class DIALOG_HANDLR:
    def __init__(self):
        self.session_id = random.randint(10000000, 500000000)

    def test(self):
        print(self.session_id)

    def communicate(self, asr_text):
        response = requests.post(
            f"http://eez115.ece.ust.hk:5000/dialogue",
            json={"text": asr_text, "session_id": self.session_id, "redo": False},
        )
        return response.json()
