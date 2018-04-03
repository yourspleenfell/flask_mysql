from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector

import re
import md5

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
NAME_REGEX = re.compile(r'^[a-zA-Z]+$')
PWD_REGEX = re.compile(r'(?=.*[A-Z])(?=.*[0-9])')

app = Flask(__name__)
app.secret_key= "SecretKeyForTheMostSecretCircumstances"
mysql = MySQLConnector(app,'users')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/users')
def users():
    user_query = 'SELECT users.id, users.first_name, users.last_name, users.email, users.created_at, users.updated_at FROM users'
    # user_data = {
    #                 'id': id,
    #             }
    users = mysql.query_db(user_query)
    return render_template('index.html', users=users)

@app.route('/users/new')
def new_user():
    return render_template('new.html')

@app.route('/users/<id>/edit')
def edit_user(id):
    user_query = 'SELECT * FROM users WHERE users.id = :id'
    user_data = {
                    'id': id
                }
    user = mysql.query_db(user_query, user_data)
    return render_template('edit.html', user=user[0])

@app.route('/users/<id>')
def get_user(id):
    id = session['id']
    user_query = 'SELECT * FROM users WHERE users.id = :id'
    user_data = {
                    'id': id
                }
    user = mysql.query_db(user_query, user_data)
    session.clear()
    return render_template('/user.html', user=user[0])

@app.route('/users/create', methods=['POST'])
def create_user():
    user_query = 'INSERT INTO users (first_name, last_name, email, created_at, updated_at) VALUES (:first_name, :last_name, :email, NOW(), NOW())'
    user_data = {
                    'id': id,
                    'first_name': request.form['first_name'],
                    'last_name': request.form['last_name'],
                    'email': request.form['email']
                }
    user = mysql.query_db(user_query, user_data)
    session['id'] = user
    return redirect('/users/<id>')

@app.route('/users/<id>/destroy')
def destroy_user(id):
    print id
    delete_query = 'DELETE FROM users WHERE users.id =:id'
    delete_data = {
                    'id': id
                  }
    mysql.query_db(delete_query, delete_data)
    flash('Successfully removed user ' + str(id), 'success')
    return redirect('/users')

@app.route('/users/<id>', methods=['POST'])
def get_user_post(id):
    session['id'] = id
    update_query = 'UPDATE users SET first_name = :first_name, last_name=:last_name, email=:email, updated_at=NOW() WHERE users.id = :id'
    update_data = {
                    'id': id,
                    'first_name': request.form['first_name'],
                    'last_name': request.form['last_name'],
                    'email': request.form['email']
                }
    mysql.query_db(update_query, update_data)
    print session['id']
    return redirect('/users/<id>')


app.run(debug=True)