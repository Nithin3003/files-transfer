from flask import Flask, request, jsonify, render_template
from flask_pymongo import PyMongo
from gridfs import GridFS
import string
import random

app = Flask(__name__)

# Configure MongoDB connection
app.config['MONGO_URI'] = 'mongodb+srv://msnithin84:Nithin@cluster0.wob2cfi.mongodb.net/files_test'  # Replace with your MongoDB connection string
mongo = PyMongo(app)
gfs = GridFS(mongo.db)

@app.route('/')
def home():
    return render_template('index.html')


def generate_random_id(length):
    return ''.join(random.choice(string.digits) for _ in range(length))

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file:
        filename = file.filename
        random_id = generate_random_id(6)  # Generate a 6-digit random ID
        file_id = gfs.put(file, filename=filename)
        mongo.db.ids.insert_one({'r_id' :random_id, '_id' :file_id})
        return  file_id
    else:
        return jsonify({'error': 'No file provided'}), 400

@app.route('/download/<file_id>', methods=['GET'])
def download_file(file_id):
    try:
        # file_id = request.args.get('file_id')
        file_id ='758224'
        file = mongo.db.ids.find_one({'r_id': file_id})
        if not gfs.exists(file_id) and file :
            return jsonify({'error': 'Invalid random ID. File not found.'}), 404

        file = gfs.get('66fe9f5bb2a144e2351d35f5')
        if file:
            return file
        else:  # This shouldn't happen if random ID verification passes
            return jsonify({'error': 'An unexpected error occurred.'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)