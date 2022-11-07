from flask import Flask, render_template, redirect, url_for, flash, abort
from functools import wraps
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import  RegisterForm, LoginForm
import smtplib

mail_id = "mailforpythoncodetesting@gmail.com"
passwd = "?yth0^(0d!^&"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
bootstrap = Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travel_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

##CONFIGURE TABLES

# creating table for Users
class Users(UserMixin, db.Model):
    __tablename__ = "Users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)
    shop_name = db.Column(db.String(250), nullable=False)


    # Relating User with their own booking details
    # Booking = relationship("User_Booking_Details", back_populates='name_of_booker')

db.create_all()

# Creating table for booking
# class Shop_Details(db.Model):
#     __tablename__ = "Shop_details"
#     id = db.Column(db.Integer, primary_key=True)

    # Creating Foreign Key , "Users.id" the users refers to tablename of User
    # booking_id = db.Column(db.Integer, db.ForeignKey('Users.id'))

    # Creating reference to  User obj , the "Booking" refers to booking property in the user class
    # name_of_booker = relationship('Users', back_populates='Booking')

    # shop_name = db.Column(db.String(250), nullable=False)
    # Email = db.Column(db.String(250), nullable=False)
    # ph_no = db.Column(db.String(250), nullable=False)
    # location = db.Column(db.String(250), nullable=False)
    # description = db.Column(db.String(500), nullable= False)

    # To = db.Column(db.String(250), nullable=False)
    # Date = db.Column(db.String(250), nullable=False)
    # Time = db.Column(db.String(250), nullable=False)

# db.create_all()

#Create admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            print(current_user.id)
            return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template("register.html")

# @app.route('/home')
# def home():
#     return render_template("home.html")

@app.route('/register', methods =['GET', 'POST'])
def register():
    register_form = RegisterForm()

    if register_form.validate_on_submit():

        if Users.query.filter_by(email=register_form.email.data).first():
            flash("You've already signed in with the email, login instead!")
            return redirect(url_for('login'))

        # hashing and salting password
        hashed_password = generate_password_hash(
            register_form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        # creating new_user entry in Users table
        new_user = Users(
            name=register_form.name.data,
            email=register_form.email.data,
            password=hashed_password,
            shop_name=register_form.shop_name.data,
        )
        db.session.add(new_user)
        db.session.commit()

        # Log in and authenticate user after adding details to database.
        login_user(new_user)
        print(current_user.id)
        return redirect(url_for('home'))

    return render_template("register.html", form=register_form, current_user=current_user)


@app.route('/login', methods=['GET','POST'])
def login():
    login_form = LoginForm()

    if login_form.validate_on_submit():
        email = login_form.email.data
        password = login_form.password.data

        # find user by email
        user_need_to_login = Users.query.filter_by(email=email).first()
        print(user_need_to_login)

        # if user is not exist then show a message
        if not user_need_to_login:
            flash('That email does not exist. please try again')
            return redirect(url_for('login'))

        # check stored password hash against entered password hashed
        elif not check_password_hash(pwhash=user_need_to_login.password, password=password):
            flash('Password incorrect,please try again')
            return redirect(url_for('login'))

        # if every thing is false then the user need to be loged in
        else:
            login_user(user_need_to_login)
            return redirect(url_for('home', current_user=current_user))

    return render_template("login.html", form=login_form, current_user=current_user)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# @app.route('/forget_password')
# def forget_password():
#     return render_template("forget_password.html")


# @app.route('/booking',methods=['GET','POST'])
# @login_required
# def booking():
#     booking_form = BookingForm()
#     if booking_form.validate_on_submit():
#         new_booking = User_Booking_Details(
#             name=booking_form.name.data,
#             no_of_psngr=booking_form.nopsngr.data,
#             Email=booking_form.email.data,
#             ph_no=booking_form.phonenum.data,
#             From=(booking_form.fplace.data).lower(),
#             To=(booking_form.tplace.data).lower(),
#             Date=booking_form.date.data,
#             Time=booking_form.time.data,
#       )
#         db.session.add(new_booking)
#         db.session.commit()
#
#         if Users.query.filter_by(email=booking_form.email.data).first():
#             return redirect(url_for('payment'))
#
#     return render_template("booking_form.html", form=booking_form)
#


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)

