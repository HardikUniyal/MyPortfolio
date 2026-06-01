import os
from threading import Thread
from dotenv import load_dotenv
from flask_mail import Mail, Message
from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
load_dotenv
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)
app.secret_key = "hardik_super_secret_key"


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

def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            print("Background Email Error:", e)

@app.route("/", methods =['GET','POST'])
def home():
    if request.method == 'POST':
        user_name = request.form.get('name')
        user_email = request.form.get('email')
        user_message = request.form.get('message')

        new_entry = Contact(name=user_name, email=user_email, message=user_message)
        db.session.add(new_entry)
        db.session.commit()
        try:
            msg = Message('New Portfolio Alert!',
            sender = os.environ.get('MAIL_USERNAME'),
            recipients = [os.environ.get('MAIL_USERNAME')])

            msg.body = f"Hello Hardik,\n\n Someone send you a mail:\n\nName: {user_name}\nEmail: {user_email}\nMessage:{user_message}"
            Thread(target=send_async_email, args=(app, msg)).start()
        except Exception as e:
            print("Email setup error!:",e)
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