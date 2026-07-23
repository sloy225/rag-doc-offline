from collections import deque

class ConversationMemory:

    def __init__(self, max_messages=6):
        self.history = deque(maxlen=max_messages)

    def add_user(self, message):
        self.history.append(("user", message))

    def add_assistant(self, message):
        self.history.append(("assistant", message))

    def get_context(self):
        text = ""

        for role, msg in self.history:
            text += f"{role}: {msg}\n"

        return text