import sys
import os
import json
from flask import Flask, render_template, request, jsonify
# from backend import NaiveRAG
from llama_index.core.schema import Document as LLamaDocument
from backend import Application

SYSTEM_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(SYSTEM_PATH)

application = Application()
api = Flask(__name__)

__all__ = ['api', 'ping', 'process_query']
# naive_rag = NaiveRAG(
#     resource_path='./resources/test-big-database',
#     embed_model_path='./resources/models/',
# )

# Register the API routes here
# Ping route (for testing)
@api.route('/api/ping')
def ping():
    return 'pong'

# @api.route('/api/chat-naiverag', methods=['POST'])
# def chat_naiverag():
#     """
#     Flask API endpoint for the NaiveRAG system.
#     Accepts a POST request with JSON payload containing the user query.
#     """
#     try:
#         # Get JSON data from request
#         data = request.get_json()
#         user_query = data.get("query", "")
        
#         if not user_query:
#             return jsonify({"error": "Query not provided"}), 400
        
#         # Process the user query through NaiveRAG
#         answer = naive_rag.process_query(user_query)
        
#         return jsonify({"query": user_query, "response": answer}), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

@api.route('/api/text/<fragment_id>', methods=['GET'])
def get_text(fragment_id: str):
    """
    Flask API endpoint to retrieve a text document using fragement id.
    """
    try:
        # Get the document using the fragment id
        text = application.get_all_text_from_fragment_id(fragment_id)
        return jsonify({"text": text}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/api/process-query', methods=['POST'])
def process_query():

    """
    Flask API endpoint for the NaiveRAG system.
    Accepts a POST request with JSON payload containing the user query.
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        user_query = data.get("query", "")
        if not user_query:
            return jsonify({"error": "Query not provided"}), 400
        
        # Process the user query through NaiveRAG
        # answer = naive_rag.process_query(user_query)
        answer = application.process_query(user_query)
        # print(answer)
        return answer, 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@api.route('/api/search_text_query', methods=['POST'])
def search_text_query():
    """
    Flask API endpoint for the NaiveRAG system.
    Accepts a POST request with JSON payload containing the user query.
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        user_query = data.get("query", "")
        if not user_query:
            return jsonify({"error": "Query not provided"}), 400
        
        # Process the user query through NaiveRAG
        # answer = naive_rag.process_query(user_query)
        answer = application.preprocess_query(user_query)
        # return jsonify(answer), 200
        return jsonify({"response": answer}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Index route, transfer control to the React frontend
# https://flask.palletsprojects.com/en/stable/patterns/singlepageapplications/
@api.route('/', defaults={'path': ''})
@api.route('/<path:path>')
def catch_all(path):
    entry_path = os.getenv('VITE_ENTRY_PATH')
    if entry_path is not None:
        # Development mode
        if os.getenv('FLASK_ENV') == 'development':
            return render_template('index-dev.html', entry_path=entry_path)
        # Production mode
        with open('./backend/api/static/dist/.vite/manifest.json') as f:
            manifest = json.load(f)
            entry_stylesheet = 'dist/' + manifest[entry_path]['css'][0]
            entry_script = 'dist/' + manifest[entry_path]['file']
            return render_template('index.html', entry_stylesheet=entry_stylesheet, entry_script=entry_script)
    else:
        raise Exception('VITE_ENTRY_PATH environment variable not set')
        