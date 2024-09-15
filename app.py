from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.utils import secure_filename
from translator import translate_text, get_available_languages
from web_scraper import scrape_and_process
import config
import os
import logging
import secrets

app = Flask(__name__)

# Set the secret key
app.config['SECRET_KEY'] = secrets.token_hex(16)

# Configure logging
logging.basicConfig(filename='app.log', level=logging.DEBUG)

# Configure upload folder
UPLOAD_FOLDER = os.path.abspath('uploads')
ALLOWED_EXTENSIONS = {'xlsx', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html', languages=get_available_languages(), search_engines=config.SEARCH_ENGINES)

@app.route('/config', methods=['GET', 'POST'])
def config_page():
    if request.method == 'POST':
        # Update config with form data
        config.GPT_API_URL = request.form.get('GPT_API_URL', config.GPT_API_URL)
        config.GPT_API_KEY = request.form.get('GPT_API_KEY', config.GPT_API_KEY)
        config.OLLAMA_API_URL = request.form.get('OLLAMA_API_URL', config.OLLAMA_API_URL)
        config.COHERE_API_URL = request.form.get('COHERE_API_URL', config.COHERE_API_URL)
        config.COHERE_API_KEY = request.form.get('COHERE_API_KEY', config.COHERE_API_KEY)
        config.COHERE_MODEL = request.form.get('COHERE_MODEL', config.COHERE_MODEL)
        config.CHROME_DRIVER_PATH = request.form.get('CHROME_DRIVER_PATH', config.CHROME_DRIVER_PATH)
        config.OUTPUT_FILE_PATH = request.form.get('OUTPUT_FILE_PATH', config.OUTPUT_FILE_PATH)
        
        # Update config.SEARCH_ENGINES with new entries
        search_engine_names = request.form.getlist('search_engine_name[]')
        search_engine_urls = request.form.getlist('search_engine_url[]')
        config.SEARCH_ENGINES = {name: url for name, url in zip(search_engine_names, search_engine_urls) if name and url}
        
        # Save the updated configuration to the config file
        with open('config.py', 'w') as f:
            for key, value in vars(config).items():
                if not key.startswith('__'):
                    f.write(f"{key} = {repr(value)}\n")
        
        flash('Configuration updated successfully', 'success')
        return redirect(url_for('index'))
    
    return render_template('config.html', config=config)

@app.route('/process', methods=['POST'])
def process():
    query = request.form.get('query')
    languages_to_translate = request.form.getlist('languages')
    selected_model = request.form.get('model')
    search_engines = request.form.getlist('search_engines')
    numero_pagine = int(request.form.get('numero_pagine', 1))
    process_type = request.form.get('process_type', 'web')

    use_ollama = selected_model in ['Ollama', 'Ollama and GPT', 'Both', 'All']
    use_cohere = selected_model in ['Cohere', 'Cohere and GPT', 'Both', 'All']
    use_gpt = selected_model in ['GPT', 'Ollama and GPT', 'Cohere and GPT', 'Both', 'All']

    translations = translate_text(query, languages_to_translate)

    try:
        if process_type == 'web':
            scrape_and_process(
                query=query,
                translations=translations,
                chrome_driver_path=config.CHROME_DRIVER_PATH,
                numero_pagine=numero_pagine,
                use_ollama=use_ollama,
                use_cohere=use_cohere,
                use_gpt=use_gpt,
                search_engines=search_engines
            )
        elif process_type == 'file':
            if 'file' not in request.files or not allowed_file(request.files['file'].filename):
                flash('Invalid file type or no file selected', 'error')
                return redirect(request.url)
            
            file = request.files['file']
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            scrape_and_process(
                query=query,
                translations=translations,
                chrome_driver_path=config.CHROME_DRIVER_PATH,
                use_ollama=use_ollama,
                use_cohere=use_cohere,
                use_gpt=use_gpt,
                process_file_path=filepath
            )
        else:
            flash('Invalid process type', 'error')
            return redirect(request.url)

        with open(config.OUTPUT_FILE_PATH, 'r') as file:
            output_content = file.read()
    except FileNotFoundError:
        logging.error(f"Output file not found: {config.OUTPUT_FILE_PATH}")
        output_content = "No output available."
    except Exception as e:
        logging.exception("Error during processing")
        flash(f'Error during processing: {str(e)}', 'error')
        return redirect(request.url)

    return render_template('process_result.html', query=query, translations=translations, output=output_content)

if __name__ == '__main__':
    app.run(debug=True)
