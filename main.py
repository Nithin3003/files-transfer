from flask import Flask, request, render_template, send_file, abort, url_for, redirect
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from gridfs import GridFS, NoFile
from io import BytesIO
import random
import base64
import qrcode
import os

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

    download_url = url_for(f'http://127.0.0.1:500/download_by_qr/{random_id}')
    # qr_data = random_id
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(download_url)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
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
                oid = fs.put(file, content_type=file.content_type, filename=file.filename)
                if oid:
                    # file_ids[random_id].append(str(oid))
                    store(r_id=random_id, o_id=oid)
                else:
                    return f"Failed to upload file: {file.filename}"
            qr_code_img = generate_qr_code(random_id)
            qr_code_base64 = base64.b64encode(qr_code_img.getvalue()).decode('utf-8')
            return render_template('index.html', qr_code_base64=qr_code_base64, random_id=random_id)
        else:
            return "No valid files to upload."
    # return '''<form  method="post" enctype="multipart/form-data">
          
    #           <input type="file" name='file' required id="file-input">
        
    #       <input type="submit" value="Save file">
    #   </form>
    #   <form id="uploadForm" method="post" enctype="multipart/form-data">
    #   <input type="file" name="file" >
    #   <input type="submit" value="Upload">
    # </form>
    #   '''
    return render_template('index.html', qr_code_base64=qr_code_base64, random_id=random_id)


@app.route('/download', methods=['POST'])
def download_file():
   
    file_id =request.form['file_id']
    
    try:
        # id=  mongo.db.ids.find_one_or_404({file_id})
        # print(id['id'])
        id = find_oid(r_id=file_id)
        if   id:
            # file = fs.get(ObjectId(id['id']))
            file = fs.get(ObjectId(id))
            print(id)
            return send_file(BytesIO(file.read()), download_name=file.filename, mimetype=file.content_type, as_attachment=True)
        else:
            
            return '''    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css" integrity="sha512-Kc323vGBEqzTmouAECnVceyQqyqdsSiqLQISBL29aUW4U/M7pSPA/gEUZQqv1cwx4OnYxTxve5UMg5GT6L4JJg==" crossorigin="anonymous" referrerpolicy="no-referrer" />
    <a href="/" >
    <i class="fa-solid fa-circle-arrow-left"></i>  </a><br>
  <h1>Enter correct or no file found for this id.</h1>'''
        
    except Exception as e:
        print(e)
    return e



@app.route('/download_by_qr/<int:id>',methods=['GET'])
def download_by_qr(id):
    
    id = find_oid(r_id=id)
    try:
        if   id:
            # file = fs.get(ObjectId(id['id']))
            file = fs.get(ObjectId(id))
            print(id)
            return send_file(BytesIO(file.read()), download_name=file.filename, mimetype=file.content_type, as_attachment=True)
        else:
            
            return '''    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css" integrity="sha512-Kc323vGBEqzTmouAECnVceyQqyqdsSiqLQISBL29aUW4U/M7pSPA/gEUZQqv1cwx4OnYxTxve5UMg5GT6L4JJg==" crossorigin="anonymous" referrerpolicy="no-referrer" />
    <a href="/" >
    <i class="fa-solid fa-circle-arrow-left"></i>  </a><br>
  <h1>Enter correct or no file found for this id.</h1>'''
        
    except Exception as e:
        print(e)
    return e

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
def error_hi(error):
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
    <p></p>
    <a href="/">Go back to Home</a>''',200




if __name__ == '__main__':
    # print(mongo.db.ids.find({}))
    app.run(debug=True)

# updated by