from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    members = db.relationship('DepartmentMember', backref='department', lazy=True)
    events = db.relationship('Event', backref='department', lazy=True)
    meetings = db.relationship('Meeting', backref='department', lazy=True)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    photo_url = db.Column(db.String(255))
    cell_group = db.Column(db.String(100))
    role = db.Column(db.String(20), default='member')  # member, dept_admin, super_admin
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=True)
    is_approved = db.Column(db.Boolean, default=False)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)

    dept_member_info = db.relationship('DepartmentMember', backref='user', uselist=False, lazy=True)


class DepartmentMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    occupation = db.Column(db.String(150))
    skills = db.Column(db.Text)
    marital_status = db.Column(db.String(50))
    sub_committee = db.Column(db.String(100))
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=True)
    event_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))


class Meeting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    meeting_date = db.Column(db.DateTime, nullable=False)
    topic = db.Column(db.String(200))
    led_by = db.Column(db.String(150))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    attendance = db.relationship('Attendance', backref='meeting', lazy=True)


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey('meeting.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    present = db.Column(db.Boolean, default=True)


class GalleryImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(200))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=True)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)


class WelfareContribution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    purpose = db.Column(db.String(150))
    date_contributed = db.Column(db.DateTime, default=datetime.utcnow)
    recorded_by = db.Column(db.Integer, db.ForeignKey('user.id'))


class PrayerRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    request_text = db.Column(db.Text, nullable=False)
    is_private = db.Column(db.Boolean, default=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, prayed_for