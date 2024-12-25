import os
import uvicorn
from dotenv import load_dotenv
from backend import api

if __name__ == '__main__':
    load_dotenv()
    port = int(os.getenv('PORT', 4000))
    hot_reload = os.getenv('HOT_RELOAD', 'false').lower() == 'true'
    uvicorn.run(api, port=port, reload=hot_reload)