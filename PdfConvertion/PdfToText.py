from PyPDF2 import PdfReader
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

file = open("comp.pdf","rb")
reader=PdfReader(file)
page1=reader.pages[1]
pdfData=page1.extract_text()

text = pdfData
text = text.lower()

# Tokenization
tokens = word_tokenize(text)

# Remove punctuation and non-alphanumeric characters
tokens = [word for word in tokens if word.isalnum()]


# Remove stop words
stop_words = set(stopwords.words('english'))
filtered_tokens = [word for word in tokens if word not in stop_words]

# Stemming (using Porter Stemmer)
stemmer = PorterStemmer()
stemmed_tokens = [stemmer.stem(word) for word in filtered_tokens]

