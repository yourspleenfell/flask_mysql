from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector

import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

app = Flask(__name__)
app.secret_key= "ThisIsMySecretKey"
mysql = MySQLConnector(app,'email_valid')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    query = 'INSERT INTO emails (email, created_at, updated_at) VALUES (:email, NOW(), NOW())'
    data = {
             'email': request.form['email'],
           }
    mysql.query_db(query, data)
    error = False
    if len(request.form['email']) is 0:
        error = True
        flash('You must enter an email address', 'error')
    elif not EMAIL_REGEX.match(request.form['email']):
        error = True
        flash('Invalid email address entered', 'error')
    if error:
        return redirect('/')
    else:
        flash('Successfully added your email ' + request.form['email'], 'success')
        return redirect('/success')

@app.route('/success')
def success():
    query = 'SELECT * FROM emails'
    emails = mysql.query_db(query)
    return render_template('success.html', emails=emails)

@app.route('/delete/<email_id>', methods=['POST'])
def delete(email_id):
    email_id = request.form['email_id']
    query = 'DELETE FROM emails WHERE id = :id'
    data = {'id': email_id}
    mysql.query_db(query, data)
    flash('Successfully removed ' + request.form['email'])
    return redirect('/success')

app.run(debug=True)