import os
from flask import Flask, render_template, redirect, url_for, send_from_directory
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import Length, Email
from flask import send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import UserMixin, LoginManager, current_user, login_user, logout_user
from flask_migrate import Migrate, upgrade
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap

#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'campuspass'
Bootstrap(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.init_app(app)

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:campuspassdb@/User?unix_socket=/cloudsql/campuspass:europe-west1:campuspassdb2/campuspass"
#USER = 'root'
#PASSWORD = 'campuspassdb'
#DATABASE = 'campuspassdb2'
## connection_name is of the format `project:region:your-cloudsql-instance`
#CONNECTION_NAME = 'campuspass:europe-west1:campuspassdb2' 
#
#LIVE_SQLALCHEMY_DATABASE_URI = (
#    'mysql+pymysql://{user}:{password}@localhost/{database}'
#    '?unix_socket=/cloudsql/{connection_name}').format(
#        user=USER, password=PASSWORD,
#        database=DATABASE, connection_name=CONNECTION_NAME)
#
#LOCAL_SQLALCHEMY_DATABASE_URI = 'sqlite:///db.db'
#
#if os.environ.get ('GAE_INSTANCE'):
#    app.config['SQLALCHEMY_DATABASE_URI'] = LIVE_SQLALCHEMY_DATABASE_URI
#else:
#    app.config['SQLALCHEMY_DATABASE_URI'] = LOCAL_SQLALCHEMY_DATABASE_URI

@login.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(20))
    surname = db.Column(db.String(30))
    major = db.Column(db.String(10))
    intake = db.Column(db.Integer)

class LoginForm(FlaskForm):
    email = StringField("email", validators=[Email()])
    password = PasswordField("password", validators=[Length(min=5)])

class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated

class LoginForm(FlaskForm):
    email = StringField("email", validators=[Email()])
    password = PasswordField("password", validators=[Length(min=5)])

class RegisterForm(FlaskForm):
    email = StringField("email", validators=[Email()])
    password = PasswordField("password", validators=[Length(min=5)])
    repeat_password = PasswordField("repated_password", validators=[Length(min=5)])
    name = StringField("name", validators=[Length(min=1)])
    surname = StringField("surname", validators=[Length(min=1)])
    major = StringField("major", validators=[Length(min=1)])
    intake = StringField("intake", validators=[Length(min=1)])

admin = Admin(app, index_view=MyAdminIndexView())
admin.add_view(MyModelView(User, db.session))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit() and form.password.data == form.repeat_password.data:
        user = User(
            email=form.email.data, password=generate_password_hash(form.password.data),
            name=form.name.data, surname=form.surname.data, major=form.major.data, intake=form.intake.data
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("index"))

    return render_template("index_register.html", form=form)


#@app.route("/login")
#def login():
#    user = User.query.get(1)
#    login_user(user)
#    return 'It\'s working mf, you are logged in'

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if check_password_hash(user.password, form.password.data):
            login_user(user)

            return redirect(url_for("index"))

    return render_template("index_login.html", form=form)

# Fix logout
@app.route("/logout")
def logout():
    logout_user()
    return 'You are out mothafucka'

@app.route('/database/dbupgrade')    ##Consider replacing; not very secure
def dbupgrade():

    migrate = Migrate(app, db)
    upgrade(directory=migrate.directory)
    return 'migrated'

@app.route("/ad")
def ad():
    return render_template("admin.html")

@app.route("/id")
def id():
    return render_template("id.html")

@app.route("/database")
def database():
    return render_template("admin_database.html")

@app.route("/emergency")
def emergency():
    return render_template("admin_emergency.html")

@app.route("/map_agent")
def map_agent():
    return render_template("admin_mapAgent.html")

@app.route("/ml")
def ml():
    return render_template("admin_ML.html")

@app.route("/room_access")
def room_access():
    return render_template("admin_roomAccess.html")

@app.route("/safety")
def safety():
    return render_template("admin_safety.html")

@app.route("/wallet")
def wallet():
    return render_template("admin_wallet.html")

if __name__ == "__main__":
    app.run(debug=True)