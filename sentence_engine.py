"""
Sentence Formulation Engine for Sign2Voice.
Maps individual sign tokens into natural, grammatically coherent sentences.
"""

class SentenceEngine:
    def __init__(self):
        # 1. Token Vocabulary Mappings
        self.token_map = {
            "Yes": ["yes", "okay", "good", "approved", "affirmative"],
            "No": ["no", "not okay", "bad", "reject", "negative"],
            "Victory": ["victory", "peace", "success", "winner"],
            "2": ["two", "victory", "peace"],
            "I Love You": ["love", "thank you", "appreciate"],
            "Hello": ["hello", "hi", "greetings"],
            "Help": ["help", "assist", "emergency"]
        }

        # 2. Heuristic Sentence Templates
        self.templates = {
            # Single Gestures
            ("Hello",): "Hello! How can I assist you?",
            ("Yes",): "Yes, that is correct.",
            ("No",): "No, I disagree.",
            ("Victory",): "Victory and peace to everyone!",
            ("2",): "Two.",
            ("1",): "One.",
            ("3",): "Three.",
            ("4",): "Four.",
            ("5",): "Five.",
            ("I Love You",): "I truly appreciate and love you.",
            ("Help",): "I need help right away, please assist me.",
            ("L",): "Letter L.",
            ("Y",): "Letter Y.",

            # Two-Token Sequences
            ("Hello", "Yes"): "Hello! Everything looks good.",
            ("Hello", "No"): "Hello, I am afraid that won't work.",
            ("Hello", "Victory"): "Greetings! We have achieved success.",
            ("Hello", "2"): "Greetings! We have achieved success.",
            ("Hello", "I Love You"): "Hello! It is wonderful to see you.",
            ("Hello", "Help"): "Hello, could you please help me?",
            ("Victory", "Yes"): "Yes! We are victorious.",
            ("2", "Yes"): "Yes! We are victorious.",
            ("No", "Help"): "I am facing an issue, please help me immediately.",
            ("Yes", "Help"): "Yes, I would appreciate some assistance.",
            ("Yes", "I Love You"): "Yes, thank you very much for your care.",
            ("Help", "No"): "Please help, something is wrong.",

            # Multi-Token Sequences
            ("Hello", "Yes", "Victory"): "Hello! All systems are good, and we won!",
            ("Hello", "Help", "Yes"): "Hello, please assist me with this.",
            ("No", "No", "Help"): "Emergency! Immediate assistance required!"
        }

    def construct_sentence(self, tokens: list[str]) -> str:
        """
        Converts a sequence of detected sign tokens into natural fluent speech.
        """
        if not tokens:
            return ""

        # Normalize tokens (filter blanks and unknowns)
        clean_tokens = [t.strip() for t in tokens if t and t not in ["Unknown Sign", "No Hand Detected"]]
        if not clean_tokens:
            return ""

        # 1. Exact sequence match
        token_tuple = tuple(clean_tokens)
        if token_tuple in self.templates:
            return self.templates[token_tuple]

        # 2. Trailing sequence sub-match if longer
        if len(clean_tokens) >= 2:
            trailing_2 = tuple(clean_tokens[-2:])
            if trailing_2 in self.templates:
                prefix = ", ".join(clean_tokens[:-2])
                return f"{prefix}. {self.templates[trailing_2]}"

        # 3. Intelligent fallback join
        return ", ".join(clean_tokens) + "."


sentence_engine = SentenceEngine()
