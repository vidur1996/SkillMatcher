import matplotlib.pyplot as plt
from wordcloud import WordCloud
from gensim.models import Word2Vec

# Load your trained Word2Vec model
# Replace 'your_model_path' with the actual path to your Word2Vec model file
model = Word2Vec.load('skills_word2vec.model')

# Choose a word to generate a word cloud around
target_word = model.wv.index_to_key[0]

# Get similar words from the Word2Vec model
similar_words = [word for word, _ in model.wv.most_similar(target_word, topn=50)]

# Create a larger word cloud
wordcloud = WordCloud(width=1200, height=600, background_color='white').generate(' '.join(similar_words))

# Display the word cloud using Matplotlib
plt.figure(figsize=(15, 7.5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')

# Save the word cloud as a PNG file
plt.savefig('wordcloud_large.png', bbox_inches='tight')