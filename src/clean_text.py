import nltk
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
import string


def give_clean_words_list(text):
    name_list = []
    tokens = nltk.tokenize.word_tokenize(text)
    pos = nltk.pos_tag(tokens)
    sentences = nltk.ne_chunk(pos, binary=False)
    for subtree in sentences.subtrees():
        if subtree.label() == 'PERSON':
            for leaf in subtree.leaves():
                name_list.append(leaf[0].lower())

    tokens = [w.lower() for w in tokens]
    lmtzr = WordNetLemmatizer()
    table = str.maketrans('', '', string.punctuation)
    stripped = [w.translate(table) for w in tokens]
    words = [word for word in stripped if word.isalpha()]
    stop_words = set(stopwords.words('english'))
    clean_words = []
    for word in words:
        if word not in stop_words and word not in name_list:
            lemm_word = lmtzr.lemmatize(word, 'v')
            if lemm_word == word:
                clean_words.append(lmtzr.lemmatize(word))
            else:
                clean_words.append(lemm_word)
    return clean_words
