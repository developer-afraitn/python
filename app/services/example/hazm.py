from hazm import Normalizer, word_tokenize, Stemmer, Lemmatizer, sent_tokenize
from collections import Counter

# Stopwords فارسی گسترده‌تر
STOPWORDS = set([
    "و", "به", "در", "از", "که", "را", "با", "این", "آن", "برای", "یک", "های",
    "است", "بود", "می", "تا", "هم", "اما", "کن", "شد", "یا", "اگر", "هر", "او"
])

# دیکشنری پیشرفته تحلیل احساسات
POSITIVE_WORDS = {
    "خوب", "شاد", "زیبا", "عالی", "دوست داشتنی", "خوشحال", "موفق", "علاقه", "لذت", "بهترین"
}
NEGATIVE_WORDS = {
    "بد", "زشت", "ناراحت", "افتضاح", "غمگین", "سخت", "ناموفق", "ترس", "ناکامی", "بدترین"
}

# کلمات کلیدی برای خلاصه سازی ساده
KEYWORDS = POSITIVE_WORDS.union(NEGATIVE_WORDS)

class Hazm:
    def __init__(self):
        self.normalizer = Normalizer()
        self.stemmer = Stemmer()
        self.lemmatizer = Lemmatizer()

    def normalize(self, text):
        return self.normalizer.normalize(text)

    def tokenize(self, text):
        return word_tokenize(self.normalize(text))

    def remove_stopwords(self, tokens):
        return [t for t in tokens if t not in STOPWORDS]

    def stem_tokens(self, tokens):
        return [self.stemmer.stem(t) for t in tokens]

    def lemmatize_tokens(self, tokens):
        return [self.lemmatizer.lemmatize(t) for t in tokens]

    def extract_entities(self, tokens):
        """
        شناسایی تقریبی موجودیت‌ها:
        - اسم افراد و مکان‌ها (حروف بزرگ یا کلمات کلیدی خاص)
        """
        entities = []
        for t in tokens:
            if t[0].isupper() or t in ["تهران","مشهد","ایران","مردم","سازمان"]:
                entities.append(t)
        return entities

    def sentiment_analysis(self, tokens):
        pos_count = sum(1 for t in tokens if t in POSITIVE_WORDS)
        neg_count = sum(1 for t in tokens if t in NEGATIVE_WORDS)
        total = len(tokens)
        sentiment_score = (pos_count - neg_count) / (total+1)  # اضافه کردن 1 برای جلوگیری از تقسیم بر صفر

        if sentiment_score > 0.05:
            sentiment = "مثبت"
        elif sentiment_score < -0.05:
            sentiment = "منفی"
        else:
            sentiment = "خنثی"

        return {
            "sentiment": sentiment,
            "positive_count": pos_count,
            "negative_count": neg_count,
            "score": sentiment_score
        }

    def summarize_sentences(self, sentences):
        """
        خلاصه سازی ساده: جملاتی که بیشترین تعداد کلمات کلیدی دارند انتخاب می‌شوند
        """
        scored = []
        for s in sentences:
            tokens = self.tokenize(s)
            score = sum(1 for t in tokens if t in KEYWORDS)
            scored.append((s, score))
        # مرتب‌سازی بر اساس بیشترین امتیاز
        scored.sort(key=lambda x: x[1], reverse=True)
        summary = [s for s, score in scored if score > 0]
        return summary[:3]  # حداکثر 3 جمله مهم

    def analyze_text(self, text):
        normalized = self.normalize(text)
        sentences = sent_tokenize(normalized)
        tokens = self.tokenize(normalized)
        tokens_no_stop = self.remove_stopwords(tokens)
        stemmed = self.stem_tokens(tokens_no_stop)
        lemmatized = self.lemmatize_tokens(tokens_no_stop)
        most_common = Counter(tokens_no_stop).most_common(5)
        entities = self.extract_entities(tokens_no_stop)
        sentiment = self.sentiment_analysis(tokens_no_stop)
        summary = self.summarize_sentences(sentences)

        return {
            "original": text,
            "normalized": normalized,
            "sentences": sentences,
            "summary": summary,
            "tokens": tokens,
            "tokens_no_stopwords": tokens_no_stop,
            "stemmed": stemmed,
            "lemmatized": lemmatized,
            "word_count": len(tokens),
            "char_count": len(normalized),
            "most_common_tokens": most_common,
            "entities": entities,
            "sentiment": sentiment
        }

