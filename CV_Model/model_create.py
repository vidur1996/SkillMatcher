import json
from nltk.tokenize import word_tokenize
from gensim.models import Word2Vec

# Load JSON data
with open('tokenized_data.json', 'r', encoding="utf-8") as file:
    data = json.load(file)

# Extract skills information
skills_data = [record['Skills'] for record in data]

# Preprocess and tokenize the skills data
tokenized_skills = skills_data


# Initialize and train the Word2Vec model
model = Word2Vec(sentences=tokenized_skills, vector_size=100, window=5, min_count=1, sg=0)

# Save the trained model
model.save('skills_word2vec.model')
print ("model created")
print ("run finish")