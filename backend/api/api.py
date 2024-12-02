import os
import json
from flask import Flask, render_template

api = Flask(__name__)

# Register the API routes here
# Ping route (for testing)
@api.route('/api/ping')
def ping():
    return 'pong'

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