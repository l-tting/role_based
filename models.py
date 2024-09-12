from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///barber.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Client(db.Model):
    __tablename__ = 'clients'
    id = db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String,nullable=False)
    phone_number =db.Column(db.Integer,unique=True,nullable=False)
    password =db.Column(db.String,nullable=False)
    appointment = db.relationship('Appointments',backref='client_appointment')


class Barber(db.Model):
    __tablename__ = 'barbers'
    id = db.Column(db.Integer,primary_key=True)
    first_name = db.Column(db.String,nullable =False)
    last_name=db.Column(db.String,nullable =False)
    email=db.Column(db.String,unique=True,nullable=False)
    phone_number=db.Column(db.Integer,unique=True,nullable=False)
    password =db.Column(db.String,nullable=False)
    appointment = db.relationship('Appointments',backref='barber_appointment')


class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String,unique=True,nullable=False)
    email = db.Column(db.String,unique=True,nullable=False)
    password =db.Column(db.String,nullable=False)

class Appointments(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer,primary_key=True)
    client_id = db.Column(db.Integer,db.ForeignKey('clients.id'))
    barber_id = db.Column(db.Integer,db.ForeignKey('barbers.id'))
    appointment_date = db.Column(db.Date,nullable=False)
    appointment_time = db.Column(db.Time,nullable=False)
    booked_at = db.Column(db.DateTime,server_default=func.now())




with app.app_context():
    db.create_all()


