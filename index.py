from flask import Flask, request, send_file
from cryptography.fernet import Fernet
import os
import uuid
import json
from flask import send_from_directory

app = Flask(__name__)
encrypted_folder = "encrypted_files/"
decrypted_folder = "decrypted_files/"
filename_path = "./filename.json"
key_path = "./key.txt"

def write_filename_to_json(encrypted_filename, filename):
    new_data = {
        encrypted_filename : filename
    }
    data = {}
    if os.path.exists(filename_path):
        with open('filename.json', 'r') as file:
            data = json.load(file)
    data.update(new_data)
    with open("filename.json", "w") as write_file:
         json.dump(data, write_file)

def get_filename_from_json(file_code):
    with open("filename.json", 'r') as file:
        json_data = json.load(file)
    if file_code in json_data:
        return json_data[file_code]
        
def generate_key():
    if not os.path.exists(key_path):
        key = Fernet.generate_key()
        with open(key_path, 'wb') as file_key:
            file_key.write(key)

def get_key():
    with open(key_path, 'rb') as file_key:
        key = file_key.read()
    return key

def encrypt_file(file,filename):
    if not os.path.exists(encrypted_folder):
        os.makedirs(encrypted_folder)
    key = get_key()
    cipher = Fernet(key)
    data = file.read()
    encrypted_data = cipher.encrypt(data)
    encrypted_filename = str(uuid.uuid4().hex) + ".enc"
    write_filename_to_json(encrypted_filename, filename)
    with open(os.path.join(encrypted_folder, encrypted_filename), 'wb') as encrypted_file:
        encrypted_file.write(encrypted_data)
    return encrypted_filename
    
def decrypt_file(file_code):
    if not os.path.exists(decrypted_folder):
        os.makedirs(decrypted_folder)
    key = get_key()
    cipher = Fernet(key)
    with open(os.path.join(encrypted_folder, file_code), 'rb') as encrypted_file:
        encrypted_data = encrypted_file.read()
        decrypted_data = cipher.decrypt(encrypted_data)
        decrypted_filename = get_filename_from_json(file_code)
        print(decrypted_filename)
        with open(os.path.join(decrypted_folder, decrypted_filename), 'wb') as decrypted_file:
            decrypted_file.write(decrypted_data)
        return decrypted_filename

@app.route('/')
def send_report():
    return send_from_directory('./public', 'index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    filename = file.filename
    encrypted_filename = encrypt_file(file, filename)
    return f'File "{filename}" uploaded and encrypted. File Code:{encrypted_filename}.'

@app.route('/download/<file_code>', methods=['GET'])
def download(file_code):
    decrypted_filename = decrypt_file(file_code)
    path_decrypted_file = os.path.join(decrypted_folder, decrypted_filename)
    return send_file(path_decrypted_file, as_attachment=True)

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


if __name__ == '__main__':
    key = generate_key()
    app.run()
