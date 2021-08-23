from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask(__name__)
app.secret_key = 'bank-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:@localhost/banking_system"

db = SQLAlchemy(app)


class Users(db.Model):
    uname = db.Column(db.String(80), nullable=False, primary_key=True)
    password = db.Column(db.Integer, nullable=False)
    balance = db.Column(db.Integer, nullable=False)


@app.route("/")
def login():
    return render_template("login.html")


username = []
database = Users.query.all()
for name in database:
    username.append(name.uname)


@app.route("/home", methods=["GET", "POST"])
def loginform():
    if(request.method == 'POST'):
        name = request.form['username']
        password = request.form['password']

        if name not in username:
            return render_template("login.html", info="Invalid User")
        else:
            user = Users.query.filter_by(uname=name)[0]
            if password != str(user.password):
                return render_template("login.html", info="Invalid Password")
            else:
                session['user'] = name
                return render_template("feature.html", user=user)
    if 'user' in session:
        user = Users.query.filter_by(uname=session['user'])[0]
        return render_template("feature.html", user=user)
    else:
        return render_template("login.html")


@ app.route("/withdrawcover", methods=['GET', 'POST'])
def withdrawcover():
    try:
        user = Users.query.filter_by(uname=session['user'])[0]
        amount = int(request.form['w_amount'])
        if(user.balance - amount <= 100):
            return render_template("cover.html", info="not withdrawn due to low balance", user=user)
        else:
            user.balance = user.balance - amount
            db.session.commit()
    except:
        return "Something Went Wrong"
    return render_template("cover.html", info="withdrawn", user=user)


@ app.route("/depositecover", methods=['GET', 'POST'])
def depoitecover():
    try:
        user = Users.query.filter_by(uname=session['user'])[0]
        user.balance = user.balance + int(request.form['d_amount'])
        db.session.commit()
    except:
        return "Something Went Wrong"
    return render_template("cover.html", info="deposited", user=user)


@ app.route("/transfercover", methods=['GET', 'POST'])
def transfercover():
    try:
        user = Users.query.filter_by(uname=session['user'])[0]
        receiver = request.form['r_name']
        if(receiver == session['user']):
            return render_template("cover.html", info="can't be transferred because both are same account", user=user)
        else:
            amount = int(request.form['t_amount'])
            if(user.balance-amount <= 100):
                return render_template("cover.html", info="can't be transferred due to low balance", user=user)
            else:
                r_user = Users.query.filter_by(uname=receiver)[0]
                r_user.balance = r_user.balance + amount
                user.balance = user.balance - amount
                db.session.commit()
                return render_template("cover.html", info="transferred", user=user)
    except:
        return render_template("cover.html", info="can't be transferred Check receiver's name", user=user)


@ app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/')


@ app.route('/about')
def about():
    user = Users.query.filter_by(uname=session['user'])[0]
    return render_template('about.html', user=user)


app.run(debug=True)
