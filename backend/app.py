import openai
import numpy as np
import faiss
from flask import Flask, request, jsonify
from flask_cors import CORS 
import os

# Initialize the Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app)  # Allow CORS for all routes by default

# Set your OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Load the FAISS index and the saved questions/answers
index = faiss.read_index('faiss_index.index')  # Load the pre-built FAISS index
questions = np.load('questions.npy')  # Load the questions from the .npy file
answers = np.load('answers.npy', allow_pickle=True)  # Load the answers from the .npy file

def get_gpt4_embedding(text):
    """
    Function to get embedding from OpenAI's text-embedding-ada-002 model.
    """
    response = openai.Embedding.create(
        model="text-embedding-ada-002",  # Correct the model used for embeddings
        input=[text]
    )
    return np.array(response['data'][0]['embedding'])

# Check the dimensionality of the FAISS index
embedding_dim_faiss = index.d

@app.route('/ask', methods=['POST'])
def ask():
    user_query = request.json.get('query')
    if not user_query:
        return jsonify({'error': 'No query provided.'}), 400
    
    query_embedding = get_gpt4_embedding(user_query)

    if query_embedding.shape[0] != embedding_dim_faiss:
        return jsonify({'error': 'Embedding dimensionality mismatch.'}), 400

    D, I = index.search(np.array([query_embedding]), k=1)  # k=1 for closest match
    closest_answer = answers[I[0][0]]
    
    return jsonify({'answer': closest_answer})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
