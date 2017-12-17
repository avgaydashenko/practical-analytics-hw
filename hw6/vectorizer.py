import nltk

class Vectorizer:
    
    def __init__(self):
        self.stemmer = nltk.stem.snowball.RussianStemmer()
        
    def set_terms(self, terms):
        self.terms = terms

    def preprocess_text(self, text):
        return [self.stemmer.stem(w) for w in nltk.tokenize.word_tokenize(text.lower())
                                if w.isalpha() and w not in nltk.corpus.stopwords.words('russian')]
        
    def get_features(self, text):
        if type(text) == str:
            text = self.preprocess_text(text)
        features = {}
        for w in self.terms:
            features["w_%s" % w] = w in text
        return features