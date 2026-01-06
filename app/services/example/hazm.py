from hazm import Normalizer, word_tokenize, Stemmer, Lemmatizer
from collections import Counter

# لیست stopwords ساده فارسی
STOPWORDS = set([
    "و", "به", "در", "از", "که", "را", "با", "این", "آن", "برای", "یک", "های",
    "است", "بود", "می", "تا", "هم", "اما", "کن", "شد", "یا", "اگر", "هر"
])
class Hazm:
    def __init__(self):
        self.normalizer = Normalizer()
        self.stemmer = Stemmer()
        self.lemmatizer = Lemmatizer()


    def normalize(self, text):
        return self.normalizer.normalize(text)

    def tokenize(self, text):
        normalized = self.normalize(text)
        return word_tokenize(normalized)

    def remove_stopwords(self, tokens):
        return [t for t in tokens if t not in STOPWORDS]

    def stem_tokens(self, tokens):
        return [self.stemmer.stem(t) for t in tokens]

    def lemmatize_tokens(self, tokens):
        return [self.lemmatizer.lemmatize(t) for t in tokens]

    def extract_entities_simple(self, tokens):
        """
        شناسایی ساده موجودیت‌ها:
        هر کلمه‌ای که با حرف بزرگ فارسی شروع شود یا اسم خاص باشد.
        توجه: این روش تقریبی است.
        """
        entities = []
        for t in tokens:
            if t[0].isupper():  # ساده، حروف بزرگ فارسی
                entities.append(t)
        return entities
    
    
    def analyze_text(self, text):
        normalized = self.normalize(text)
        tokens = self.tokenize(normalized)
        tokens_no_stop = self.remove_stopwords(tokens)
        stemmed = self.stem_tokens(tokens_no_stop)
        lemmatized = self.lemmatize_tokens(tokens_no_stop)
        most_common = Counter(tokens_no_stop).most_common(5)
        entities = self.extract_entities_simple(tokens_no_stop)

        return {
            "original": text,
            "normalized": normalized,
            "tokens": tokens,
            "tokens_no_stopwords": tokens_no_stop,
            "stemmed": stemmed,
            "lemmatized": lemmatized,
            "word_count": len(tokens),
            "char_count": len(normalized),
            "most_common_tokens": most_common,
            "entities": entities
        }

