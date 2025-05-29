from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = "strata-secret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///participants.db'
db = SQLAlchemy(app)
# ✅ Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# Models
class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    college = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(10))
    events = db.Column(db.String(300))
    username = db.Column(db.String(100))
    password = db.Column(db.String(300))

# Create DB
with app.app_context():
    db.create_all()

# Send Email Function
def send_email(to_email, subject, body):
    sender = "asanth2712@gmail.com"
    password = "odyz nzjq ahbp wosy"  # replace with your app password

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to_email

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender, password)
        server.sendmail(sender, [to_email], msg.as_string())

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        college = request.form['college']
        email = request.form['email']
        phone = request.form['phone']
        events = ', '.join(request.form.getlist('events'))

        username = email.split('@')[0]
        password = generate_password_hash(phone)
        body = f"""
        🎉 Thank you for registering for *STRATA Intercollege Meet!* 🎉

         Hey {name},

        Your participation is officially confirmed! Here are your login credentials to access the STRATA portal:

        🆔 Username: {username}
        🔐 Password: {phone}

        ✨ You can now log in and check:
        • Your registered events 📋
        • Event venues 🏛️
        • Event timings ⏰

        👉 Login here: http://127.0.0.1:5000/login

        If you have any queries, feel free to contact our team. We’re excited to have you on board and can't wait to see you shine on event day! 🌟

        Best Wishes,  
        STRATA Organizing Team 🎊
        """



        participant = Participant(name=name, college=college, email=email,
                                  phone=phone, events=events,
                                  username=username, password=password)
        db.session.add(participant)
        db.session.commit()

        # Send email
       
        send_email(email, "🎉 STRATA Registration Successful!", body)

        return render_template("success.html", username=username)

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_input = request.form['password']

        if username == ADMIN_USERNAME and password_input == ADMIN_PASSWORD:
            session['user'] = 'admin'
            return redirect(url_for('admin_dashboard'))

        participant = Participant.query.filter_by(username=username).first()
        if participant and check_password_hash(participant.password, password_input):
            session['user'] = participant.username
            return redirect(url_for('participant_dashboard'))
        else:
            return render_template('login.html', error="Invalid Credentials.")
    return render_template('login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user' in session and session['user'] == 'admin':
        participants = Participant.query.all()
        return render_template('admin_dashboard.html', participants=participants)
    else:
        return redirect(url_for('login'))


@app.route('/participant/dashboard')
def participant_dashboard():
    if 'user' in session and session['user'] != 'admin':
        participant = Participant.query.filter_by(username=session['user']).first()
        return render_template('participant_dashboard.html', participant=participant)
    else:
        return redirect(url_for('login'))

    
@app.route('/dashboard')
def dashboard():
    if 'admin' in session:
        participants = Participant.query.all()
        return render_template('dashboard.html', participants=participants)
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('admin', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True,port = 5001)
