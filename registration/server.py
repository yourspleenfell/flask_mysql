from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector

import re
import md5

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
NAME_REGEX = re.compile(r'^[a-zA-Z]+$')
PWD_REGEX = re.compile(r'(?=.*[A-Z])(?=.*[0-9])')

app = Flask(__name__)
app.secret_key= "SecretKeyForTheMostSecretCircumstances"
mysql = MySQLConnector(app,'register')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    error = False
    email = request.form['email']
    password = request.form['password']
    user_query = 'SELECT * FROM users WHERE users.email =:email LIMIT 1'
    query_data = {
             'id': id,
             'email': email,
             'password': password
           }
    user = mysql.query_db(user_query, query_data)
    if len(request.form['email']) is 0:
        error = True
        flash('You must enter an email to login', 'error')
    if len(request.form['password']) is 0:
        error = True
        flash('You must enter a password to login', 'error')
    if error:
        return redirect('/')
    if user[0]['email'] != request.form['email']:
        error = True
        flash('You have entered an incorrect email', 'error')
    if user[0]['password'] != md5.new(password).hexdigest():
        error = True
        flash('You have entered an incorrect password', 'error')
    if error:
        return redirect('/')
    if len(user) != 0:
        encrypted_password = md5.new(password).hexdigest()
    if user[0]['password'] == encrypted_password:
        session['user'] = user[0]['user_id']
        session['name'] = user[0]['first_name']
        flash('Successfully logged in ' + user[0]['first_name'], 'success')
        return redirect('/user')

@app.route('/register')
def register():
    return render_template('/register.html')

@app.route('/submit', methods=['POST'])
def submit():
    error = False
    if len(request.form['first_name']) is 0:
        error = True
        flash('You must enter a first name', 'error')
    elif not NAME_REGEX.match(request.form['first_name']):
        error = True
        flash('First name can contain only letters', 'error')
    if len(request.form['last_name']) is 0:
        error = True
        flash('You must enter a last name', 'error')
    elif not NAME_REGEX.match(request.form['last_name']):
        error = True
        flash('First name can contain only letters', 'error')
    if len(request.form['email']) is 0:
        error = True
        flash('You must enter an email address', 'error')
    elif not EMAIL_REGEX.match(request.form['email']):
        error = True
        flash('Invalid email address entered', 'error')
    if len(request.form['password']) < 8:
        error = True
        flash('Password must be at least 8 digits', 'error')
    elif not PWD_REGEX.match(request.form['password']):
        error = True
        flash('Password must contain one capital letter and one number', 'error')
    elif request.form['password'] != request.form['password_confirm']:
        error = True
        flash('Passwords must match', 'error')
    if error:
        return redirect('/register')
    else:
        query = 'INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (:first_name, :last_name, :email, :password, NOW(), NOW())'
        password = request.form['password']
        hashed_pw = md5.new(password).hexdigest()
        data = {
             'first_name': request.form['first_name'],
             'last_name': request.form['last_name'],
             'email': request.form['email'],
             'password': hashed_pw,
            }
        mysql.query_db(query, data)
        session['email'] = request.form['email']
        flash('Thank you for registering an account ' + request.form['first_name'] + ' ' + request.form['last_name'], 'success')
        return redirect('/user')

@app.route('/user')
def user():
    if 'user' not in session:
        email = session['email']
        user_query = 'SELECT * FROM users WHERE users.email =:email LIMIT 1'
        query_data = {
                'email': email,
            }
        user = mysql.query_db(user_query, query_data)
        session['user'] = user[0]['user_id']
    return render_template('user.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/wall')
def wall():
    if 'user' not in session:
        flash('You must log in to view the wall', 'error')
        return redirect('/')
    else:
        message_query = 'SELECT * FROM messages JOIN users ON users.user_id = messages.user_id'
        messages = mysql.query_db(message_query)
        comment_query = 'SELECT * FROM comments JOIN messages on messages.message_id = comments.message_id JOIN users ON users.user_id = comments.user_id'
        comments = mysql.query_db(comment_query)
        return render_template('/wall.html', all_messages = messages, all_comments = comments)

@app.route('/post', methods=['POST'])
def post():
    if len(request.form['message']) is 0:
        flash('Cannot post a blank message', 'error')
        return redirect('/wall')
    else:
        message_query = 'INSERT INTO messages (user_id, message, created_at, updated_at) VALUES (:user_id, :message, NOW(), NOW())'
        message_data = {
                'user_id': session['user'],
                'message': request.form['message']
                }
        mysql.query_db(message_query, message_data)
        flash('Message successfully posted', 'success')
        return redirect('/wall')

@app.route('/comment', methods=['POST'])
def comment():
    if len(request.form['comment']) is 0:
        flash('Cannot post a blank comment', 'error')
        return redirect('/wall')
    else:
        comment_query = 'INSERT INTO comments (user_id, message_id, comment, created_at, updated_at) VALUES (:user_id, :message_id, :comment, NOW(), NOW())'
        comment_data = {
                'user_id': session['user'],
                'message_id': int(request.form['message_id']),
                'comment': request.form['comment']
                }
        mysql.query_db(comment_query, comment_data)
        flash('Comment successfully posted', 'success')    
        return redirect('/wall')

app.run(debug=True)