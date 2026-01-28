import difflib

class NLUUtils:
    def __init__(self):
        # Critical keywords that trigger specific logic
        self.CORE_VOCAB = [
            'play', 'stop', 'pause', 'resume', 'next', 'previous',
            'open', 'close', 'search', 'find', 'google', 'youtube',
            'time', 'date', 'weather', 'shutdown', 'restart',
            'volume', 'mute', 'unmute', 'increase', 'decrease',
            'screenshot', 'generate', 'image', 'picture', 'photo',
            'who', 'what', 'where', 'when', 'why', 'how',
            'hello', 'hi', 'hey', 'sami',
            'deep', 'fast', 'quick', 'mode', 'enable', 'disable',
            'research', 'analyze', 'scan', 'read',
            'price', 'cost', 'buy', 'shop', 'latest', 'news',
            'code', 'vscode', 'visual', 'studio'
        ]

    def autocorrect_sentence(self, sentence):
        """
        Corrects typos in a sentence by matching strictly against core vocab.
        Only corrects words that look very similar to known commands.
        """
        if not sentence:
            return ""
            
        words = sentence.split()
        corrected_words = []
        
        for word in words:
            # Clean word (remove punctuation for matching, but keep for output? simplified here)
            clean_word = word.lower().strip(".,?!")
            
            # 1. Exact Match (Fast)
            if clean_word in self.CORE_VOCAB:
                corrected_words.append(word) # Keep original casing if match found
                continue
                
            # 2. Fuzzy Match
            # cutoff=0.6 allows for typos like 'plya' -> 'play'
            matches = difflib.get_close_matches(clean_word, self.CORE_VOCAB, n=1, cutoff=0.6)
            
            if matches:
                # Replace with best match
                # Use the match from vocab (lowercase)
                corrected_words.append(matches[0]) 
            else:
                # Keep original word if no good match found (likely a proper noun or unknown word)
                corrected_words.append(word)
                
        return " ".join(corrected_words)
