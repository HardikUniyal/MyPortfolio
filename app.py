from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
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

@app.route("/", methods =['GET','POST'])
def home():
    if request.method == 'POST':
        user_name = request.form.get('name')
        user_email = request.form.get('email')
        user_message = request.form.get('message')

        new_entry = Contact(name=user_name, email=user_email, message=user_message)
        db.session.add(new_entry)
        db.session.commit()
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