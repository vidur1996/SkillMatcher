import json
import string
import re
from gensim.models import Word2Vec
from nltk import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer

# Load the trained Word2Vec model
model = Word2Vec.load('CV_Model/skills_word2vec.model')


def identify_skills_from_information(information):
    # Tokenize the input text
    tokenized_text = word_tokenize(information.lower())

    # Initialize an empty list to store identified skills
    identified_skills = []
    # Remove punctuation and non-alphanumeric characters
    tokens =  [word for word in tokenized_text if not re.search(r'\d', word)]

    # Define a string containing all punctuation characters
    punctuation = string.punctuation

    # Filter out tokens that are not punctuation
    filtered_punc_tokens = [word for word in tokens if word not in punctuation]

    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in filtered_punc_tokens if word not in stop_words]

    # Initialize the lemmatizer
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in filtered_tokens]
    # Iterate through the tokens and check if they are in the model's vocabulary
    for token in lemmatized_tokens:
        if len(token) > 1 and token != "skill" and token in model.wv:
            identified_skills.append(token)

    return identified_skills


def findTopSkills():
    # Load JSON data
    with open('information.json', 'r') as file:
        data = json.load(file)

    # Initialize TF-IDF Vectorizer
    vectorizer = TfidfVectorizer()

    # Iterate through CVs and identify skills
    for cv_record in data:
        information = cv_record['Information']
        identified_skills = identify_skills_from_information(information)

        # Get the top 5 keywords using TF-IDF
        tfidf_scores = vectorizer.fit_transform([" ".join(identified_skills)])
        feature_names = vectorizer.get_feature_names_out()
        top_keywords_indices = tfidf_scores.indices[tfidf_scores.data.argsort()[-5:][::-1]]
        top_keywords = [feature_names[index] for index in top_keywords_indices]

    return top_keywords
