from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
import re
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://get-it-done:get-it-done@localhost:8889/get-it-done'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "p64bdyS33spMgNMS"

class Task(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    completed = db.Column(db.Boolean)

    def __init__(self, name):
        self.name = name
        self.completed = False

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))

    def __init__(self, email, password):
        self.email = email
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and "email" not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            return redirect('/')
        else:
            # TODO - login failed
            return "<h1>failed</h1>"
    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        emailErr = ''
        passwordErr = ''
        verifyErr = ''
        valid = True
        validString = re.compile(r'^(?=\S{3,120}$)')
        validEmail = re.compile(r'^(?=\S{5,120}$)(?=[^@]*[@][^@]*$)(?=[^\.].*[^\.]@[^\.].*\.[^\.]+$)(?!.*\.\..*$)')
        if not validEmail.match(email):
            emailErr = "Invalid Email"
            valid = False
        if not validString.match(password):
            passwordErr = "Password must be 3-120 characters with no spaces"
            valid = False
        if password != verify:
            verifyErr = "Password does not match"
            valid = False
        if not valid:
            return render_template("register.html", email=email, emailErr=emailErr,
                passwordErr = passwordErr, verifyErr=verifyErr)
        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/')
        else:
            #TODO - better message
            return "<h1>user exists</h1>"
    return render_template('register.html')

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')

@app.route('/', methods=['POST', 'GET'])
def index():

    if request.method == 'POST':
        task_name = request.form['task']
        new_task = Task(task_name)
        db.session.add(new_task)
        db.session.commit()

    tasks = Task.query.filter_by(completed=False).all()
    completed_tasks = Task.query.filter_by(completed=True).all()

    return render_template('todos.html', title="Get It Done",
        tasks=tasks, completed_tasks=completed_tasks)

@app.route('/delete-task', methods=['POST'])
def delete_task():

    task_id = int(request.form['task-id'])
    task = Task.query.get(task_id)
    task.completed = True
    db.session.add(task)
    db.session.commit()

    return redirect('/')

if __name__ == "__main__":
    app.run()
