# IR project
# Guilde to set up 
```bash
Project structure
├───ir-project
│   ├───backend
│   ├───database
│   ├───frontend
│   └───test-scripts
├───models
├───small-database
├───big-database
├───venv
└───.env
```
## Project structure overview

Git repo: ir-project directory
```bash
backend: contains all the code for handling the core backend logic, include:
    nested packages

database: contains scripts and utilities related to data management, include:
    crawling
    indexing
    parsing
    schema
    some database code can be written in backend, but in databased is encourage

frontend: contains the ui code

test-scripts: contains various test scripts that verify the functionality of different parts of the project
```
Outer layer: You MUST create these directory/files manually
```bash
models: contains any local llm or embed models

database: contain databse, both raw and indexed (small is for test, big for real deploy)

venv: python venv for this project

.env: contain open ai api key
```

This set up is design for easy push and pull git by seperating data part and source code part.

## Quick start

1. Create a new directory name <anyname> you wish, clone this repo in this directory, the structure should be
```bash
anyname
└───ir-project
```
2. Create python venv. Make sure you got python 3.12 installed.
Open ir-project in vscode, open terminal
```bash
cd ..
py -3.12 -m venv venv
``` 
Then, select the python interpreter to venv/Script/python.exe.

3. Check if venv created correctly 
Close vscode, then re-open
```bash
pip --version
```
If it prints something like anyname\venv\Lib\site-packages\pip (python 3.12)
Then you got it right.
This step may seem foolish but in my experience, restart vscode should be done.

4. Install dependencies
```bash
pip install -r requirements.txt
```

If you set up correctly, try 'py .\test-scripts\hello_gpt.py'. You will see a message from ChatGPT :)

## Frontend setup
Require node.js version 20 and above.

1. Install the root `package.json`:
```bash
npm run install
```

2. Install the packages for `frontend`:
```bash
npm run sync:frontend
```

3. Add the following lines to the end of your `.env` file:
```bash
VITE_ENTRY_PATH=src/main.tsx
FLASK_ENV=development # remove/overwrite this var for production mode 
```

4. Run this command to start the development server with hot reload:
```bash
npm run dev
```

## Production build
Run this command to build the static 
```bash
npm run build
```
