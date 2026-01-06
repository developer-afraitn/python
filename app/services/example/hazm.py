from hazm import Normalizer, word_tokenize, Stemmer, Lemmatizer
from collections import Counter

class Hazm:
    def __init__(self):
        self.normalizer = Normalizer()
        self.stemmer = Stemmer()
        self.lemmatizer = Lemmatizer()
        
    def process_text(self, text):
        """عملیات جامع روی متن و خروجی به صورت دیکشنری"""
        normalized = self.normalizer.normalize(text)
        tokens = word_tokenize(normalized)
        stemmed = [self.stemmer.stem(token) for token in tokens]
        lemmatized = [self.lemmatizer.lemmatize(token) for token in tokens]

        word_count = len(tokens)
        char_count = len(normalized)
        unique_tokens = list(set(tokens))
        most_common_tokens = Counter(tokens).most_common(5)  # 5 کلمه پر تکرار

        return {
            "original": text,
            "normalized": normalized,
            "tokens": tokens,
            "stemmed": stemmed,
            "lemmatized": lemmatized,
            "word_count": word_count,
            "char_count": char_count,
            "unique_tokens": unique_tokens,
            "most_common_tokens": most_common_tokens
        }

