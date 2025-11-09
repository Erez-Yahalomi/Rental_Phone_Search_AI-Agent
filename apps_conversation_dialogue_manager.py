import openai
from enum import Enum, auto
from config.settings import settings

openai.api_key = settings.OPENAI_API_KEY

class DialogueState(Enum):
    INTRO = auto()
    ASKING = auto()
    CLARIFY = auto()
    WRAPUP = auto()
    END = auto()

class GPTDialogueManager:
    """
    GPT-powered dialogue manager:
    - Uses GPT-4 to interpret ambiguous answers.
    - Generates clarifications or follow-up questions dynamically.
    - Produces natural prompts instead of fixed strings.
    """

    def __init__(self, listing_context, questions):
        self.listing = listing_context
        self.questions = questions
        self.answers = {}
        self.state = DialogueState.INTRO
        self.current_index = 0

    def next_prompt(self, last_response: str = None) -> str:
        """
        Generate the next prompt using GPT-4.
        """
        if self.state == DialogueState.INTRO:
            addr = self.listing.get("address") or self.listing.get("title") or "the rental"
            return f"Hi, I'm calling about {addr}. Do you have a moment to answer a few quick questions?"

        if self.state == DialogueState.ASKING:
            return self.questions[self.current_index]

        if self.state == DialogueState.CLARIFY:
            # Ask GPT to generate a clarification prompt
            prompt = f"""
You are a rental inquiry assistant. The user gave a vague answer: "{last_response}".
Generate a polite clarification question to get more detail.
"""
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "system", "content": "You clarify vague answers."},
                          {"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=100
            )
            return response.choices[0].message["content"].strip()

        if self.state == DialogueState.WRAPUP:
            return "Thank you for your time. I will summarize our conversation and follow up if needed."

        return ""

    def handle_response(self, text: str):
        """
        Process a response, store it, and advance the state machine.
        """
        if self.state == DialogueState.INTRO:
            self.state = DialogueState.ASKING
            return

        if self.state == DialogueState.ASKING:
            q = self.questions[self.current_index]
            self.answers[q] = text or ""
            if not text or len(text.strip()) < 4:
                self.state = DialogueState.CLARIFY
                return
            self.current_index += 1
            if self.current_index >= len(self.questions):
                self.state = DialogueState.WRAPUP
            else:
                self.state = DialogueState.ASKING
            return

        if self.state == DialogueState.CLARIFY:
            q = self.questions[self.current_index]
            self.answers[q] = (self.answers.get(q, "") + " " + (text or "")).strip()
            self.current_index += 1
            if self.current_index >= len(self.questions):
                self.state = DialogueState.WRAPUP
            else:
                self.state = DialogueState.ASKING
            return

        if self.state == DialogueState.WRAPUP:
            self.state = DialogueState.END
