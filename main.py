import os
from dotenv import load_dotenv
from backend import api

if __name__ == '__main__':
    load_dotenv()
    port = int(os.getenv('PORT', 4000))
    mode = os.getenv('FLASK_ENV')
    if mode == 'development':
        api.run(debug=True, port=port, load_dotenv=False)
    else:
        from waitress import serve
        serve(api, port=port, host='0.0.0.0')