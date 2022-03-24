import random
from flask import Flask, abort, make_response, redirect, render_template, request, url_for
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from LoginForm import LoginForm
from SignUpForm import SignUpForm

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/hw2"
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
    if user == None and check_password_hash(user.password, form.password.data):
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

if __name__ == "__main__":
    app.run(host='localhost', port=5000, debug=True)