import random

class SentenceEngine:
    def __init__(self):
        # 1. Token Mappings (Vocabulary Expansion)
        # Maps a single gesture to multiple possible contextual meanings
        self.token_map = {
            "Yes": ["yes", "okay", "good", "approved"],
            "No": ["no", "not okay", "bad", "reject"],
            "Victory": ["victory", "peace", "success", "winner"],
            "2": ["victory", "peace", "success", "winner"],
            "I Love You": ["love", "thank you", "appreciate"],
            "Hello": ["hello", "hi", "greetings"],
            "Help": ["help", "assist", "emergency"]
        }

        # 2. Sentence Templates (The "Perception Hack")
        # Logic: Tuple of tokens -> Natural Sentence
        self.templates = {
            # Basic Greetings
            ("Hello",): "Hello, whats up",
            ("Hello", "Yes"): "Hello! Everything looks good.",
            ("Hello", "No"): "Hello, I am afraid I cannot do that.",
            ("Hello", "Victory"): "Greetings! We have achieved success.",
            ("Hello", "2"): "Greetings! We have achieved success.",
            
            # Emotional / Interaction
            ("I Love You",): "I truly appreciate you.",
            ("Hello", "I Love You"): "Hello! It is wonderful to see you.",
            ("Victory", "Yes"): "Yes! We are the champions.",
            ("2", "Yes"): "Yes! We are the champions.",
            
            # Complex/Negative
            ("No", "Help"): "I am in trouble, please help me immediately.",
            ("Yes", "Help"): "Yes, I need some assistance please.",
            
            # Default single token fallbacks
            ("Yes",): "Yes, that is correct.",
            ("No",): "No, I disagree.",
            ("Victory",): "Victory is ours!",
            ("2",): "Two.",
            ("3",): "Three.",
            ("4",): "Four.",
            ("5",): "Five.",
            ("Help",): "Please help me!",
        }

    def construct_sentence(self, tokens):
        """
        Converts a list of sign tokens ["Hello", "Yes"] into a natural sentence.
        """
        if not tokens:
            return ""

        # 1. Try Exact Match (Sequence)
        # Convert to tuple for dictionary lookup
        token_tuple = tuple(tokens)
        if token_tuple in self.templates:
            return self.templates[token_tuple]

        # 2. Try Subset Match (Trailing logic)
        # If we have [A, B, C] and no match, try [B, C] or [A, B]? 
        # For this demo, let's keep it simple: Join with logical connectives.
        
        # 3. Fallback: Smart Join
        # "Hello" + "Yes" -> "Hello, Yes."
        return ", ".join(tokens) + "."

sentence_engine = SentenceEngine()
