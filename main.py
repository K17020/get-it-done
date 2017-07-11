from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy 


app = Flask(__name__)
app.config['DEBUG'] = True
# Note: the connection string after :// contains the following info:
# user:password@server:portNumber/databaseName
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://get-it-done:beproductive@localhost:8889/get-it-done'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'rF1iDxY6qlTmvyJl'


# This class creates a table in the database get-it-done
class Task(db.Model):
    
    id = db.Column(db.Integer, primary_key=True) # Creates the primary key in a table
    name = db.Column(db.String(120)) # Creates a name that is a string that can only be 120 characters
    completed = db.Column(db.Boolean) # Creates a bool for if the task has been completed
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id')) # Connects the Task ID to the User ID

    def __init__(self, name, owner):
        self.name = name
        self.completed = False
        self.owner = owner

# The class handles usernames and passwords in a database
class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True) # cable for the email/username and the unique=True looks for a unique email
    password = db.Column(db.String(120))
    tasks = db.relationship('Task', backref='owner') # Populate from from the Task class where the owner property is related

    def __init__(self, email, password):
        self.email = email
        self.password = password

# Checks to see if the user has logged in before displaying the page
@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first() # return username with given email if it exist if not it will return none
        if user and user.password == password: #checks to see if user and passwords match as well as well if the passwords match the user 
            session['email'] = email # remember that user has logged in
            flash('Logged in')
            return redirect('/')
            # TODO - 'why the log in failed'
        else:
            flash('user password incorrect, or user does not exist', 'error')
            
    return render_template('login.html')

@app.route('/register', methods=['POST','GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        
        existing_user = user = User.query.filter_by(email=email).first() # Checks to see if the user exists in the database
        if not existing_user: # if not create a new user with the data provided
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email # remember the user has logged in
            return redirect('/')
        else:
        # TODO tell users that they already exist in the database
        # TODO - very if is the passwords match
            return '<h1>Duplicate User</h1>' # if they do exist return this message


    return render_template('register.html')

# logs the user out of the app
@app.route('/logout', methods=['GET'])
def logout():
    del session['email'] # removes the email from the session to log you out
    return redirect('/login')

@app.route('/', methods=['POST', 'GET'])
def index():
    
    owner = User.query.filter_by(email=session['email']).first()
    
# This takes the users input from the todo.html and adds it to the database. 
    if request.method == 'POST':
        task_name = request.form['task']
        owner = User.query.filter_by(email=session['email']).first() # Checks to see if the owner is logged into the session. 
        new_task = Task(task_name, owner)
        db.session.add(new_task)
        db.session.commit()

    tasks = Task.query.filter_by(completed=False).all() # Checks to see if the task in the database is True or False and removes it from the page
    completed_tasks = Task.query.filter_by(completed=True, owner=owner).all() # See above, Checks to see if the user of the current session is looking at their data
    return render_template('todo.html', title="Get It Done!",  # repost data from the database according to if it has been completed or not
        tasks=tasks, completed_tasks=completed_tasks)

@app.route('/delete-task', methods=['POST'])
def delete_task():

    task_id = int(request.form['task-id'])
    task = Task.query.get(task_id)
    task.completed = True
    db.session.add(task)
    db.session.commit()

    return redirect('/')

if __name__ == '__main__':
    app.run()