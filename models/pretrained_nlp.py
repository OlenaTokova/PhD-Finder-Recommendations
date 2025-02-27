# pretrained_nlp.py

# Import necessary libraries
import nltk
from sentence_transformers import SentenceTransformer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Ensure nltk resources are available
nltk.download('punkt')
nltk.download('stopwords')

class PretrainedNLP:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Initializes the pre-trained NLP model for generating embeddings.
        Default model: 'all-MiniLM-L6-v2' (a lightweight, efficient model)
        """
        self.model = SentenceTransformer(model_name)
        self.stop_words = set(stopwords.words('english'))

    def process_text(self, text):
        """
        Tokenizes the input text and removes stop words.
        :param text: String, raw text input from the user
        :return: List of filtered words
        """
        words = word_tokenize(text)
        filtered_words = [w for w in words if w.lower() not in self.stop_words]
        return filtered_words

    def get_embedding(self, text):
        """
        Generates an embedding for the processed text using the pre-trained NLP model.
        :param text: String, raw text input from the user
        :return: Embedding vector (array of floats)
        """
        processed_text = ' '.join(self.process_text(text))  # Join words back into a string
        embedding = self.model.encode(processed_text)
        return embedding

# Example usage
if __name__ == "__main__":
    nlp = PretrainedNLP()
    user_input = "I am interested in neural networks and deep learning in healthcare."
    
    # Process and generate embedding
    embedding = nlp.get_embedding(user_input)
    
    print("Processed Text:", nlp.process_text(user_input))
    print("User Embedding (sample):", embedding[:5], "...")  # Print a sample of the embedding
