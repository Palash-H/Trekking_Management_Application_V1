from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime

db = SQLAlchemy()

class Admin(db.Model):
    __tablename__='admin'
    id = db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(20),nullable= False)
    email = db.Column(db.String(64),unique=True,nullable=False)
    passhash = db.Column(db.String(200),nullable=False)

class Staff(db.Model):
    __tablename__ = 'staff'
    id = db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(20),nullable= False)
    email = db.Column(db.String(64),unique=True,nullable=False)
    passhash = db.Column(db.String(200),nullable=False)
    contact = db.Column(db.String(20),nullable = False)
    approval_status = db.Column(db.String(20),default="Pending")

    treks = db.relationship('Trek',backref='staff',lazy=True)

class Trekker(db.Model):
    __tablename__ = 'trekker'
    id = db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(20),nullable= False)
    email = db.Column(db.String(64),unique=True,nullable=False)
    passhash = db.Column(db.String(200),nullable=False)
    phone = db.Column(db.String(20),nullable =False)
    is_active = db.Column(db.Boolean,default= True)

    bookings= db.relationship('Booking',backref='trekker',lazy=True)

class Trek(db.Model):
    __tablename__ = 'trek'
    id = db.Column(db.Integer,primary_key=True)
    trek_name=db.Column(db.String(20),nullable= False)
    location = db.Column(db.String(100),nullable=False)
    difficulty = db.Column(db.String(20),nullable=False)
    duration = db.Column(db.Integer,nullable = False)
    available_slots = db.Column(db.Integer,nullable= False)
    staff_id = db.Column(db.Integer,db.ForeignKey('staff.id'),nullable=False)
    start_date=db.Column(db.Date,nullable=False)
    end_date=db.Column(db.Date,nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='Open')

    booking = db.relationship('Booking',backref='trek',lazy=True)


class Booking(db.Model):
    __tablename__ = 'booking'

    id = db.Column(db.Integer,primary_key =True)
    trekker_id = db.Column(db.Integer,db.ForeignKey('trekker.id'),nullable=False)
    trek_id = db.Column(db.Integer,db.ForeignKey('trek.id'),nullable=False)
    booking_slot = db.Column(db.DateTime,default=datetime.utcnow)
    status =db.Column(db.String(20),default = "Booked")


    __table_args__ = (
    db.UniqueConstraint('trekker_id', 'trek_id', name='uix_trekker_trek'),
)