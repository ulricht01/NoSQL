from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, logout_user, UserMixin, LoginManager, login_user, current_user
import pymysql
from flask_mongoengine import MongoEngine
from redis import Redis
from datetime import datetime
import time
import pickle
from sqlalchemy import create_engine
import hashlib
from neo4j import GraphDatabase, basic_auth

pymysql.install_as_MySQLdb()

app  = Flask(__name__)

redis = Redis(host='localhost', port=6379)

app.config['MONGODB_SETTINGS'] = {
    'db': 'kontakt',
    'host': 'localhost',
    'port': 27017
}
app.config['SECRET_KEY'] = 'hardsecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqldb://root@127.0.0.1:3308/registration"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db_mongo = MongoEngine()
db_mongo.init_app(app)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message = "Prosím přihlaste se pro zobrazení této stránky!"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class Kontakt(db_mongo.Document):
    username = db_mongo.StringField()
    telefon = db_mongo.StringField()
    mesto = db_mongo.StringField()
    ulice = db_mongo.StringField()
    cislo_popisne = db_mongo.StringField()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100), unique = True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    surname = db.Column(db.String(100))

    def __init__(self, username, password, name, surname):
        self.username = username
        self.password = password
        self.name = name
        self.surname = surname

@login_required
@app.route("/mysql_redis")
def cache_redis():
    if redis.exists("user"):
        textData = redis.get("user")
        data = pickle.loads(textData)
        x = data["usr"]
        mess = "Zobrazeno z Redisu!"
        return render_template("mysql_redis.html", x=x, mess=mess)
    else:
        data = {}
        userList = []
        users = db.session.execute(db.select(User.username, User.name)).scalars()
        for user in users:
            userList.append(str(user))
        data["usr"] = userList
        textData = pickle.dumps(data)
        redis.set("user", textData)
        x = data["usr"]
        redis.expire("user", 5)
        mess = "Uloženo do Redisu!"
        return render_template("mysql_redis.html", x=x, mess=mess)
 


@app.route("/")
@login_required
def html():
    return render_template('template.html')

@app.route("/login")
def login(): 
    if current_user.is_authenticated:   
        return render_template("profil.html")
    else:
        return render_template("login.html")



@app.route("/login", methods=["GET", "POST"])
def login_post():
    if request.method == "POST":
        user = request.form["username"]
        passw = request.form["password"]
        user_info = User.query.filter_by(username=user).first()
        if user not in db.session.execute(db.select(User.username)).scalars():
            flash("Neexistující uživatel!")
        elif passw != user_info.password:
            flash("Existující uživatel ale chybné heslo!")
        else:
            login_user(user_info)
            return render_template("profil.html")
            
            
    return render_template("login.html")

@app.route('/register' , methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return render_template("profil.html")   
    else:
        if request.method == "POST":
            user = request.form["username"]
            passw = request.form["password"]
            rep_passw = request.form["rep_password"]
            name = request.form["name"]
            surname = request.form["surname"]
            if user not in db.session.execute(db.select(User.username)).scalars() and passw == rep_passw:
                register =User(user, passw, name, surname)

                db.session.add(register)
                db.session.commit()

                flash("Registrace byla úspěšná!")
                return redirect(url_for('login'))
            elif user not in db.session.execute(db.select(User.username)).scalars() and passw != rep_passw:
                flash("Hesla se neshodují!")
            else:
                flash("Jméno už existuje!")
            
    db.create_all()
    return render_template('register.html')

@app.route("/profil")
@login_required
def profil(): 
    return render_template("profil.html")

@app.route("/mysql")
@login_required
def mysql_db():
    users = User.query.all()
    return render_template("mysql.html", users=users)

@app.route('/mongo_db', methods=['GET','POST'])
@login_required
def mongo_db():
    if request.method == "POST":
        username = current_user.username
        telefon = request.form["telefon"]
        mesto = request.form["mesto"]
        ulice = request.form["ulice"]
        cislo_popisne = request.form["cislo_popisne"] 
        user = Kontakt.objects(username__in=[username]).first()
        if user:
            flash("Už máš zadaný kontakt!")
        else:
            kontakt = Kontakt(username=username,telefon=telefon, mesto=mesto, ulice=ulice, cislo_popisne=cislo_popisne)
            kontakt.save()
            return redirect(url_for('mongo_data'))
    
    return render_template("mongo_db.html")

@app.route('/mongo_data', methods=['GET','POST'])
@login_required
def mongo_data():
    kontakt = Kontakt.objects()
    if request.method == "POST":
        username = current_user.username
        telefon = request.form["telefon"]
        mesto = request.form["mesto"]
        ulice = request.form["ulice"]
        cislo_popisne = request.form["cislo_popisne"] 
        user = Kontakt.objects(username__in=[username]).first()
        if user:
            Kontakt.delete(user)
            kontakt = Kontakt(username=username,telefon=telefon, mesto=mesto, ulice=ulice, cislo_popisne=cislo_popisne)
            kontakt.save()
            flash("Úspěšná změna!")
            return redirect(url_for('mongo_data'))
        else:
            kontakt = Kontakt(username=username,telefon=telefon, mesto=mesto, ulice=ulice, cislo_popisne=cislo_popisne)
            kontakt.save()
            flash("Úspěšné zadání kontaktu!")
            return redirect(url_for('mongo_data'))
    return render_template("mongo_DATA.html", kontakt=kontakt)

@app.route('/neo4j', methods=['GET','POST'])
def neo_data():
    return render_template('neo.html')



@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

