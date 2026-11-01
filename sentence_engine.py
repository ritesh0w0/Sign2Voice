"""
Sentence Formulation Engine for Sign2Voice.
Maps sequences of sign tokens into natural, grammatically structured sentences.
"""

class SentenceEngine:
    def __init__(self):
        # 1. Token Vocabulary Mappings
        self.token_map = {
            "Yes": ["yes", "okay", "good", "approved", "affirmative"],
            "No": ["no", "not okay", "bad", "reject", "negative"],
            "Victory": ["victory", "peace", "success", "winner"],
            "2": ["two", "victory", "peace", "success"],
            "I Love You": ["love", "thank you", "appreciate"],
            "Hello": ["hello", "hi", "greetings"],
            "Help": ["help", "assist", "emergency"],
            "OK": ["okay", "agreed", "confirmed"],
            "Rock": ["awesome", "rock on"],
            "Fist": ["power", "strength", "stop"]
        }

        # 2. Heuristic Sentence Templates
        self.templates = {
            # Basic Greetings
            ("Hello",): "Hello, whats up",
            ("Hello", "Yes"): "Hello! Everything looks good.",
            ("Hello", "No"): "Hello, I am afraid I cannot do that.",
            ("Hello", "Victory"): "Greetings! We have achieved success.",
            ("Hello", "2"): "Greetings! We have achieved success.",
            ("Hello", "OK"): "Hello, everything is confirmed and okay.",

            # Emotional / Interaction
            ("I Love You",): "I truly appreciate you.",
            ("Hello", "I Love You"): "Hello! It is wonderful to see you.",
            ("Victory", "Yes"): "Yes! We are the champions.",
            ("2", "Yes"): "Yes! We are the champions.",

            # Emergency / Assistance
            ("No", "Help"): "I am in trouble, please help me immediately.",
            ("Yes", "Help"): "Yes, I need some assistance please.",
            ("Help",): "Please help me!",

            # Single Gestures
            ("Yes",): "Yes, that is correct.",
            ("No",): "No, I disagree.",
            ("Victory",): "Victory is ours!",
            ("2",): "Two.",
            ("1",): "One.",
            ("3",): "Three.",
            ("4",): "Four.",
            ("5",): "Five.",
            ("OK",): "Okay, sounds good.",
            ("Rock",): "Awesome, rock on!",
            ("Fist",): "Stop and stay strong.",
            ("L",): "Letter L.",
            ("Y",): "Letter Y.",

            # Multi-Token Sequences
            ("Hello", "Yes", "2"): "Hello! All systems are good, and we won!",
            ("Hello", "Yes", "Victory"): "Hello! All systems are good, and we won!",
            ("No", "No", "Help"): "Emergency! Immediate assistance required!"
        }

    def construct_sentence(self, tokens: list[str]) -> str:
        """
        Converts a list of sign tokens ["Hello", "Yes"] into a natural sentence.
        """
        if not tokens:
            return ""

        # Normalize tokens (filter blanks and unknowns)
        clean_tokens = [t.strip() for t in tokens if t and t not in ["Unknown Sign", "No Hand Detected"]]
        if not clean_tokens:
            return ""

        # 1. Try Exact Match (Sequence)
        token_tuple = tuple(clean_tokens)
        if token_tuple in self.templates:
            return self.templates[token_tuple]

        # 2. Try Subset Match (Trailing logic)
        if len(clean_tokens) >= 2:
            trailing_2 = tuple(clean_tokens[-2:])
            if trailing_2 in self.templates:
                prefix = ", ".join(clean_tokens[:-2])
                return f"{prefix}. {self.templates[trailing_2]}"

        # 3. Fallback: Smart Join
        return ", ".join(clean_tokens) + "."


sentence_engine = SentenceEngine()
