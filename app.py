from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

from models import db, User, Department, DepartmentMember, Event, Meeting, Attendance, GalleryImage, WelfareContribution, PrayerRequest

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-this-to-a-random-secret-key-later'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///church.db'  # we'll switch to Postgres later
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.context_processor
def inject_year():
    return {'current_year': datetime.now().year}

# ---------- HOME ----------
@app.route('/')
def home():
    return render_template('home.html')


# ---------- GENERAL MEMBER REGISTRATION ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        password = request.form.get('password')
        cell_group = request.form.get('cell_group')

        existing_user = User.query.filter(
            (User.email == email) | (User.phone_number == phone_number)
        ).first()
        if existing_user:
            flash('An account with this email or phone number already exists.', 'danger')
            return redirect(url_for('register'))

        new_user = User(
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            password_hash=generate_password_hash(password),
            cell_group=cell_group,
            role='member',
            is_approved=False
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please wait for admin approval before logging in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


# ---------- MEN'S DEPARTMENT REGISTRATION ----------
@app.route('/mens-department/register', methods=['GET', 'POST'])
def mens_register():
    mens_dept = Department.query.filter_by(name='Men').first()

    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        password = request.form.get('password')
        occupation = request.form.get('occupation')
        skills = request.form.get('skills')
        marital_status = request.form.get('marital_status')
        sub_committee = request.form.get('sub_committee')

        existing_user = User.query.filter(
            (User.email == email) | (User.phone_number == phone_number)
        ).first()
        if existing_user:
            flash('An account with this email or phone number already exists.', 'danger')
            return redirect(url_for('mens_register'))

        new_user = User(
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            password_hash=generate_password_hash(password),
            role='member',
            department_id=mens_dept.id if mens_dept else None,
            is_approved=False
        )
        db.session.add(new_user)
        db.session.commit()

        dept_member = DepartmentMember(
            user_id=new_user.id,
            department_id=mens_dept.id if mens_dept else None,
            occupation=occupation,
            skills=skills,
            marital_status=marital_status,
            sub_committee=sub_committee
        )
        db.session.add(dept_member)
        db.session.commit()

        flash('Men\'s Department registration successful! Please wait for admin approval.', 'success')
        return redirect(url_for('login'))

    return render_template('mens_register.html')


# ---------- LOGIN ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('login'))

        if not user.is_approved:
            flash('Your account is pending admin approval.', 'warning')
            return redirect(url_for('login'))

        login_user(user)
        flash(f'Welcome back, {user.full_name}!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('login.html')


# ---------- LOGOUT ----------
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))


# ---------- DASHBOARD ----------
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)