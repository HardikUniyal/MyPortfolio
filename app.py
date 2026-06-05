import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import socket
import requests
def send_telegram_msg (user_name, user_email, user_msg):
    TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
    message = f"New Portfolio Lead!\nName: {user_name}\nEmail: {user_email}\nMsg: {user_msg}"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    try:
        requests.get(url)
    except Exception as e:
        print("Telegram request error", e)

old_getaddrinfo = socket.getaddrinfo
def new_getaddrinfo(*args, **kwargs):
    responses = old_getaddrinfo(*args, **kwargs)
    return [r for r in responses if r[0] == socket.AF_INET]
socket.getaddrinfo = new_getaddrinfo
app = Flask(__name__)
load_dotenv
app.secret_key = "hardik_super_secret_key"
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'None'


#Database comfig (ENgine Setup)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#Database model
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100),nullable=False)
    email = db.Column(db.String(100),nullable=False)
    message = db.Column(db.Text, nullable=False)
#Routes (webpages)
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == 'admin123':
            session['is_admin'] = True
            return redirect(url_for('admin'))
        else:
            return "Wrong Password! Hacker banne ki koshish naa karo."
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('is_admin', None)
    return redirect(url_for('login'))
@app.route('/delete/<int:id>')
def delete_msg(id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    msg_to_delete = Contact.query.get_or_404(id)

    try:
        db.session.delete(msg_to_delete)
        db.session.commit()
        return redirect(url_for('admin'))
    except:
        return "Message cannot be deleted. "

@app.route("/", methods =['GET','POST'])
def home():
    if request.method == 'POST':
        import time
        current_time = time.time()
        last_submit_time = session.get('last_submit_time')

        if last_submit_time and (current_time - float(last_submit_time) < 60):
            remaining_time = int(60 - (current_time - float(last_submit_time)))
            flash(f"please wait {remaining_time}seconds before sending another message.", "danger")
            return redirect(url_for('home', _anchor='contact'))
        
        user_name = request.form.get('name')
        user_email = request.form.get('email')
        user_message = request.form.get('message')

        new_entry = Contact(name=user_name, email=user_email, message=user_message)
        db.session.add(new_entry)
        db.session.commit()
        try:
            session['last_submit_time'] = current_time
            send_telegram_msg(user_name, user_email, user_message)
        except Exception as e:
            print("TELEGRAM/SESSION ERROR!:",e)
        flash("Thank you! Your message has been sent successfully,", "success")
        return redirect(url_for('home', _anchor='contact'))

    return render_template("index.html")
@app.route("/admin")
def admin():
    if not session.get('is_admin'):
        return redirect(url_for('login'))

    all_messages = Contact.query.all()

    return render_template("admin.html", messages=all_messages)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)