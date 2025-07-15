from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
from flask_login import login_required
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from io import BytesIO
import qrcode
from fpdf import FPDF
import os
from datetime import datetime, timezone
import re

app = Flask(__name__)
app.secret_key = 'exam_secret'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///exam_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def is_valid_usn(usn):
    pattern = r'^1RV\d{2}(CS|EC|ME|CV|BM|BT|AE|EE)\d{2}$'
    return re.match(pattern, usn.upper()) is not None
# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usn = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True, nullable = False)
    # phone = db.Column(db.String(20))
    password = db.Column(db.String(100))
    fee_paid = db.Column(db.Boolean, default=False)
    photo_path = db.Column(db.String(200))  # Add this to User model

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     usn = db.Column(db.String(20), unique=True, nullable=False)
#     name = db.Column(db.String(100), nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     course = db.Column(db.String(100), nullable=False)
#     semester = db.Column(db.Integer, nullable=False)
#     fee_paid = db.Column(db.Boolean, default=False)
#     password = db.Column(db.String(255))  # You can hash later
#     photo_path = db.Column(db.String(200))  # Optional, default=None



class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    signature_path = db.Column(db.String(200))
    photo_path = db.Column(db.String(200))

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    fees_paid = db.Column(db.Boolean, default=False)
    semester = db.Column(db.String(20))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

class HallTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course = db.Column(db.String(100))
    semesters = db.Column(db.String(200))
    subjects = db.Column(db.String(300))
    payment_method = db.Column(db.String(50))
    date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class CollegeFee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='Unpaid')  # 'Paid' or 'Unpaid'
    paid_on = db.Column(db.DateTime)

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        usn = request.form.get('usn')
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        confirm_password = request.form.get("confirm_password")
        # photo = request.files.get('photo')

        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return render_template("register.html")

        if not usn or not email or not name or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(usn=usn).first()

        if not existing_user:
            flash("You are not a verified student. Please contact admin.", "error")
            return redirect(url_for('register'))

        if not existing_user.fee_paid:
            flash("You cannot register for the exam until you pay the fees.", "warning")
            return redirect(url_for('register'))

        if existing_user.password:
            flash("You are already registered. Please login.", "info")
            return redirect(url_for('login'))

        # Save the photo
        # if photo:
        #     ext = os.path.splitext(photo.filename)[1].lower()
        #     if ext not in ['.jpg', '.jpeg', '.png']:
        #         flash("❌ Invalid image format. Only .jpg, .jpeg, or .png are allowed.", "danger")
        #         return redirect(url_for('register'))

        #     photo_filename = f"{usn}_photo{ext}"
        #     photo_folder = os.path.join('static', 'photos')
        #     os.makedirs(photo_folder, exist_ok=True)
        #     photo_path = os.path.join(photo_folder, photo_filename)
        #     photo.seek(0)
        #     photo.save(photo_path)
        #     print(f"✅ Saved photo at: {photo_path}")
        #     # Save relative path to DB
        #     existing_user.photo_path = f"photos/{photo_filename}"
        #     print(f"✅ Saved to DB: {existing_user.photo_path}")

        # Set remaining data
        existing_user.name = name
        existing_user.email = email
        existing_user.password = generate_password_hash(password)

        # ✅ Commit the changes
        db.session.commit()
        print("✅ Changes committed to DB")
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usn = request.form['usn']
        password = request.form['password']

        user = User.query.filter_by(usn=usn).first()
        if user and check_password_hash(user.password, password):
            session['username'] = user.name
            session['usn'] = user.usn
            return redirect(url_for('upload_photo'))
        else:
            flash("❌ Invalid USN or password")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/upload_photo', methods=['GET', 'POST'])
def upload_photo():
    usn = session.get('usn')
    if not usn:
        flash("You must be logged in to upload your photo.", "danger")
        return redirect(url_for('login'))

    user = User.query.filter_by(usn=usn).first()

    if request.method == 'POST':
        photo = request.files.get('photo')
        if not photo:
            flash("Please select a photo to upload.", "danger")
            return redirect(url_for('upload_photo'))

        ext = os.path.splitext(photo.filename)[1].lower()
        if ext not in ['.jpg', '.jpeg', '.png']:
            flash("❌ Invalid image format. Only .jpg, .jpeg, or .png are allowed.", "danger")
            return redirect(url_for('upload_photo'))

        photo_filename = f"{usn}_photo{ext}"
        photo_folder = os.path.join('static', 'photos')
        os.makedirs(photo_folder, exist_ok=True)
        photo_path = os.path.join(photo_folder, photo_filename)

        photo.save(photo_path)
        user.photo_path = f"photos/{photo_filename}"

        db.session.commit()
        flash("✅ Photo uploaded successfully.")
        return redirect(url_for('select_course'))

    return render_template('upload_photo.html')


@app.route('/select_course', methods=['GET', 'POST'])
def select_course():
    usn = session.get('usn')
    user = User.query.filter_by(usn=usn).first()

    # Check fee status
    fee_status = CollegeFee.query.filter_by(user_id=user.id).first()
    if not fee_status or fee_status.status != 'Paid':
        flash("❌ You cannot register for exams until you pay the college fees.")
        return redirect(url_for('home'))
    if not user.photo_path:
        flash("⚠️ Please upload your photo before proceeding.")
        return redirect(url_for('upload_photo'))


    all_courses = Course.query.all()
    if request.method == 'POST':
        course_id = request.form['course_id']
        course = Course.query.get(course_id)
        session['course_id'] = course.id
        session['course'] = course.name
        return redirect(url_for('select_semester'))

    return render_template('select_course.html', courses=all_courses)


@app.route('/select_semester', methods=['GET', 'POST'])
def select_semester():
    course_id = session.get('course_id')
    semesters = db.session.query(Subject.semester).filter_by(course_id=course_id).distinct().all()
    semester_list = sorted({s[0] for s in semesters})

    if request.method == 'POST':
        selected = request.form.getlist('semesters')
        if not selected:
            flash("⚠️ Please select at least one semester.")
            return redirect(url_for('select_semester'))
        session['semesters'] = selected
        return redirect(url_for('select_subjects'))

    return render_template('select_semester.html', semesters=semester_list)

@app.route('/select_subjects', methods=['GET', 'POST'])
def select_subjects():
    selected_semesters = session.get('semesters', [])
    course_id = session.get('course_id')
    subjects = Subject.query.filter(Subject.course_id == course_id, Subject.semester.in_(selected_semesters)).all()

    if request.method == 'POST':
        selected_subjects = request.form.getlist('subjects')
        if not selected_subjects:
            flash("⚠️ Please select at least one subject.")
            return redirect(url_for('select_subjects'))
        session['subjects'] = selected_subjects
        return redirect(url_for('payment'))

    return render_template('select_subjects.html', subjects=subjects)

# @app.route('/payment', methods=['GET', 'POST'])
# def payment():
#     if request.method == 'POST':
#         session['payment_method'] = request.form.get('method')
#         return render_template('payment_confirm.html', method=session['payment_method'])
#     return render_template('payment.html')

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    # Calculate total amount
    selected_subjects = session.get('subjects', [])
    amount = 300 * len(selected_subjects)
    if request.method == 'POST':
        method = request.form.get('method')
        session['payment_method'] = method
        # For Card: collect card details
        if method == 'Card':
            card_number = request.form.get('card_number')
            expiry = request.form.get('expiry')
            cvv = request.form.get('cvv')
            # You can validate/store card details as needed
            return render_template('payment_confirm.html', method=method, amount=amount)
        # For QR: show QR code
        elif method == 'QR Code':
            # Generate QR code for payment
            qr_data = f"Pay Rs.{amount} to ABC College"
            qr_img = qrcode.make(qr_data)
            qr_filename = f"static/payment_qr_{session['usn']}.png"
            qr_img.save(qr_filename)
            return render_template('payment_confirm.html', method=method, amount=amount, qr_filename=qr_filename)
        # For UPI: collect UPI ID or show instructions
        elif method == 'UPI':
            upi_id = request.form.get('upi_id')
            return render_template('payment_confirm.html', method=method, amount=amount, upi_id=upi_id)
    return render_template('payment.html', amount=amount)


@app.route('/payment_confirm', methods=['POST'])
def payment_confirm():
    username = session['username']
    usn = session.get('usn')
    user = User.query.filter_by(usn=usn).first()

    new_ticket = HallTicket(
        user_id=user.id,
        course=session.get('course'),
        semesters=','.join(session.get('semesters', [])),
        subjects=','.join(session.get('subjects', [])),
        payment_method=session.get('payment_method')
    )
    db.session.add(new_ticket)
    db.session.commit()

    flash("✅ Payment successful!!")
    return redirect(url_for('profile'))

# @app.route('/profile')
# def profile():
#     usn = session.get('usn')
#     ticket = HallTicket.query.join(User).filter(User.usn == usn).order_by(HallTicket.id.desc()).first()

#     if not ticket:
#         return redirect(url_for('payment'))
    
#     qr_filename = f"{usn}_qr.png"

#     return render_template('profile.html',
#                            username=session.get('username'),
#                            course=ticket.course,
#                            subjects=ticket.subjects.split(','),
#                            qr_filename=qr_filename)


@app.route('/profile')
def profile():
    usn = session.get('usn')
    username = session.get('username')

    user = User.query.filter_by(usn=usn).first()
    ticket = HallTicket.query.filter_by(user_id=user.id).order_by(HallTicket.id.desc()).first()

    if not ticket:
        return redirect(url_for('payment'))

    # ✅ Generate QR code if it doesn't exist or always overwrite
    # qr_data = f"Name: {username}\nCourse: {ticket.course}\nSubjects: {ticket.subjects}"
    qr_data = f"""Name: {user.name}
    USN: {user.usn}
    Course: {ticket.course}
    Semesters: {ticket.semesters}
    Subjects: {ticket.subjects}
    Amount Paid: ₹{300 * len(ticket.subjects.split(','))}
    """


    qr_img = qrcode.make(qr_data)

    qr_filename = f"{usn}_qr.png"
    qr_path = os.path.join("static", qr_filename)
    qr_img.save(qr_path)

    return render_template('profile.html',
                           username=username,
                           course=ticket.course,
                           subjects=ticket.subjects.split(','),
                           qr_filename=qr_filename,
                           photo_filename=os.path.basename(user.photo_path) if user.photo_path else None)

@app.route('/transaction_history')
def transaction_history():
    usn = session.get('usn')
    user = User.query.filter_by(usn=usn).first()
    tickets = HallTicket.query.filter_by(user_id=user.id).order_by(HallTicket.id.desc()).all()

    return render_template('transaction_history.html', tickets=tickets, username=user.name)

# @app.route('/transaction_history')
# @login_required
# def transaction_history():
#     user_id = session['user_id']
#     user = User.query.get(user_id)
#     tickets = HallTicket.query.filter_by(user_id=user_id).order_by(HallTicket.date.desc()).all()
#     return render_template('transaction_history.html', tickets=tickets, username=user.name)

@app.route('/download_hall_ticket')
def download_hall_ticket():
    username = session.get('username')
    usn = session.get('usn')
    user = User.query.filter_by(usn=usn).first()

    ticket = HallTicket.query.filter_by(user_id=user.id).order_by(HallTicket.id.desc()).first()
    if not ticket:
        return redirect(url_for('profile'))

    course = Course.query.filter_by(name=ticket.course).first()
    if not course:
        return "Course not found", 404

    # Generate QR
    qr_data = f"Name: {username}\nCourse: {course.name}\nSubjects: {ticket.subjects}"
    qr_img = qrcode.make(qr_data)
    qr_path = os.path.join("static", f"{usn}_qr.png")
    qr_img.save(qr_path)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "ABC College of Science & Technology", ln=True, align='C')

    current_y = pdf.get_y()
    pdf.image(qr_path, x=10, y=current_y, w=40)
    if user.photo_path:
        photo_path = os.path.join('static/photos', os.path.basename(user.photo_path))
        if os.path.exists(photo_path):
            pdf.image(photo_path, x=160, y=20, w=30)
        else:
            print(f"⚠️ Photo file not found at {photo_path}")

    pdf.set_y(current_y + 60)

    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Name: {username}", ln=True)
    pdf.cell(0, 10, f"USN: {usn}", ln=True)
    pdf.cell(0, 10, f"Course: {course.name}", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(50, 10, "Subject", 1)
    pdf.cell(40, 10, "Date", 1)
    pdf.cell(40, 10, "Time", 1)
    pdf.cell(60, 10, "Invigilator", 1)
    pdf.ln()

    pdf.set_font("Arial", size=12)
    for i, sub in enumerate(ticket.subjects.split(',')):
        date = f"2025-07-{10 + i}"
        time = f"{9 + i}:00 AM"
        invigilator = ""
        pdf.cell(50, 10, sub.strip(), 1)
        pdf.cell(40, 10, date, 1)
        pdf.cell(40, 10, time, 1)
        pdf.cell(60, 10, invigilator, 1)
        pdf.ln()

    pdf.ln(15)

    # Signature Labels
    sig_y = pdf.get_y()
    pdf.set_font("Arial", size=12)
    pdf.cell(80, 10, "Student Signature", ln=0)
    pdf.set_xy(130, sig_y)
    pdf.cell(60, 10, "Principal Signature", ln=1)

    # Student Signature Image
    if course.signature_path and os.path.exists(course.signature_path):
        if course.signature_path.lower().endswith(('.jpg', '.jpeg', '.png')):
            pdf.image(course.signature_path.replace("\\", "/"), x=10, y=sig_y + 10, w=40)
        else:
            print("⚠️ Unsupported image file type:", course.signature_path)
    # else:
        # print("❌ Signature file not found or path is empty:", course.signature_path)

    # Principal Signature Image
    principal_signature_path = "static/sign_engineering.png"
    if os.path.exists(principal_signature_path):
        pdf.image(principal_signature_path, x=150, y=sig_y + 10, w=40)
    else:
        print("❌ Principal signature not found at:", principal_signature_path)

    pdf_output = pdf.output(dest='S').encode('latin1')
    pdf_buffer = BytesIO(pdf_output)

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"{username}_hall_ticket.pdf",
        mimetype='application/pdf'
    )

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Tables created successfully.")
    app.run(debug=True)
