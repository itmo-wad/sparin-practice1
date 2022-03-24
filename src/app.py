import os
import random
from flask import Flask, abort, flash, make_response, redirect, render_template, request, send_file, send_from_directory, url_for
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from LoginForm import LoginForm
from SignUpForm import SignUpForm

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/practice-1"
app.config['UPLOAD_FOLDER'] = './src/uploaded/'
app.config['SECRET_KEY'] = 'the random string'
mongo = PyMongo(app)

active_sessions = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup", methods=["POST","GET"])
def signup():
    form = SignUpForm(request.form)
    if request.method == 'POST' and form.validate():
        
        userExists = mongo.db.users.find_one(filter={ "username": form.username.data })
        if userExists != None:
            form.username.errors.append("User is already exists")
            return render_template("signup.html", form=form)

        hashed_password = generate_password_hash(form.password.data)
        mongo.db.users.insert_one({"username": form.username.data, "password": hashed_password})
        return redirect(url_for('login'))
    
    return render_template("signup.html", form=form)

@app.route("/auth", methods=["POST","GET"])
def login():
    form = LoginForm(request.form)

    if request.method == 'GET':
        return render_template("login.html", form=form)

    user = mongo.db.users.find_one(filter={ "username": form.username.data })
    if user == None or check_password_hash(user['password'], form.password.data) == False:
        return render_template("login.html", form=form, wrong_credentials=True)

    sessionid = str(random.randint(10**10, 10**20))
    active_sessions[sessionid] = form.username.data
        
    resp = make_response(redirect(url_for('profile')))
    resp.set_cookie('sessionid', sessionid)
    return resp

@app.route("/profile")
def profile():
    sessionid = request.cookies.get('sessionid', "")
    if sessionid not in active_sessions:
        abort(403)

    return render_template("profile.html")

@app.route("/logout")
def logout():
    resp = make_response(redirect("/"))
    resp.set_cookie('sessionid', '', expires=0)
    return resp

@app.route("/upload", methods=["POST","GET"])
def upload():
    sessionid = request.cookies.get('sessionid', "")
    if sessionid not in active_sessions:
        abort(403)

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
            
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
            
        if not allowed_file(file.filename):
            flash('Invalid file extension', 'danger')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            folder = os.path.abspath(app.config['UPLOAD_FOLDER'])
            path = os.path.join(folder, filename)
            os.makedirs(folder, exist_ok=True)
            file.save(path)
            
            flash('Successfully saved', 'success')
            return redirect(url_for('uploaded_file', filename=filename))
            
    return render_template("upload.html")

@app.route('/uploaded/<filename>')
def uploaded_file(filename):
    file_location = os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return send_file(file_location)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == "__main__":
    app.run(host='localhost', port=5000, debug=True)