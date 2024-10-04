from flask import Flask, request, render_template, send_file, abort, url_for,redirect
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from gridfs import GridFS, NoFile
from io import BytesIO
import random
import base64
import qrcode
import logging

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://msnithin84:Nithin@cluster0.wob2cfi.mongodb.net/gridfs_server_test"
mongo = PyMongo(app)
fs = GridFS(mongo.db)

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'pptx'])

file_ids = {}

def store(r_id,o_id ):
    stored = mongo.db.ids.insert_one({ 'r_id': r_id ,'o_id': str(o_id)})
    return stored if stored else False

def find_oid(r_id):
    result=mongo.db.ids.find_one({'r_id':r_id })
    return result['o_id'] if result else False

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_random_id():
    return str(random.randint(10000000, 99999999))

def generate_qr_code(random_id):
    # download_url = url_for('download_file', _external=True)
    qr_data = str(random_id)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img_byte_arr = BytesIO()
    img.save(img_byte_arr)#, format='jpeg'
    img_byte_arr.seek(0)
    return img_byte_arr

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    qr_code_base64 = None
    random_id = None
    if request.method == 'POST':
        files = request.files.getlist('file')
        valid_files = [file for file in files if file and allowed_file(file.filename)]
        
        if valid_files:
            random_id = generate_random_id()
            file_ids[random_id] = []
            for file in valid_files:
                try:
                    file_id = fs.put(file, content_type=file.content_type, filename=file.filename)
                    # Handle successful upload
                except Exception as e:
                    # Handle errors here
                    print(f"Error uploading file: {e}")                

            qr_code_img = generate_qr_code(random_id)
            qr_code_base64 = base64.b64encode(qr_code_img.getvalue()).decode('utf-8')
            return render_template('index.html', qr_code_base64=qr_code_base64, random_id=random_id)
        else:
            return "No valid files to upload."
    # return '''<form  method="post" enctype="multipart/form-data">
          
    #           <input type="file" name='file' required id="file-input">
        
    #       <input type="submit" value="Save file">
    #   </form>/home/msnithin84/my_project/includ
    #   <form id="uploadForm" method="post" enctype="multipart/form-data">
    #   <input type="file" name="file" >
    #   <input type="submit" value="Upload">
    # </form>
    #   '''
    return render_template('index.html', qr_code_base64=qr_code_base64, random_id=random_id)



from flask import send_file, abort, jsonify
from bson.objectid import ObjectId

@app.route('/download', methods=['POST'])
def download_file():
    file_id = request.form['file_id']

    try:
        id = find_oid(r_id=file_id)
        if id:  # Check if id is not None
            file = fs.get(ObjectId(str(id)))

            # Handle missing file gracefully
            if not file:
                return abort(404, description="File not found")

            return send_file(BytesIO(file.read()), download_name=file.filename, mimetype=file.content_type, as_attachment=True)
        else:
            # Handle invalid ID case
            return abort(400, description="Invalid file ID")
    except Exception as e:
        # Handle any unexpected errors gracefully
        return jsonify({"error": str(e)}), 500  # Internal Server Error




# @app.route('/download', methods=['POST'])
def download_files():
    file_id = request.form['file_id']

    try:
        id = find_oid(r_id=file_id)
        if id:  # Check if id is not None
            file = fs.get(ObjectId(str(id)))
            logging.info(f"Found file with ID: {id}")  # Log successful file retrieval
            return send_file(BytesIO(file.read()), download_name=file.filename, mimetype=file.content_type, as_attachment=True)
    #     else:
    #         return abort(404, description="File not found for this ID.")
    # except NoFile:
    #     return abort(404, description="File not found for this ID.")
    # except (OSError, IOError) as e:  # Catch potential file access errors
    #     logging.error(f"Error downloading file: {e}")
    #     return abort(500, description="Internal Server Error")
    except Exception as e:  # Catch other unexpected exceptions
        return e
    #     logging.exception(f"Unexpected error downloading file: {e}")
    #     return abort(500, description="Internal Server Error")

# @app.errorhandler(404)
def page_not_found(Exception):
    return ''' <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 50px;
        }
        h1 {
            font-size: 50px;
        }
        p {
            font-size: 20px;
        }
        a {
            color: #007BFF;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
    
    <h1>404</h1>
    <p>Page Not Found </p>
    <a href="/">Go back to Home</a>''', 200

# @app.errorhandler(Exception)
def error(Exception):
    return ''' <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 50px;
        }
        h1 {
            font-size: 50px;
        }
        p {
            font-size: 20px;
        }
        a {
            color: #007BFF;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
    
    <h1>404</h1>
    <p>Error</p>
    <a href="/">Go back to Home</a>'''
if __name__ == '__main__':
    # print(mongo.db.ids.find({}))
    app.run(debug=True)
