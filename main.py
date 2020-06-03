import os
import chess
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, session
from flask_assets import Environment, Bundle
from database import *

        
app = Flask(__name__)
app.secret_key = open('data/secret_key.txt', 'r').read()
assets = Environment()
assets.init_app(app)


def check_login(route):
    def wrapper(*args, **kwargs):
        if 'flask_user_id' not in session:
            return redirect('/login', code=302)
        return route(user=User.get(session['flask_user_id']), *args, **kwargs)
    wrapper.__name__ = route.__name__ + '_wrapper'
    return wrapper
    

@app.route('/')
def hello():
    return redirect('/home', code=302)
    
    
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/gen/img'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
                               
                               
@app.route('/login')
def login():
    return render_template('login.html')
    

@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/contests/all')
@check_login
def all_contests(user):
    return render_template('contests.html', type='all', user=user)
    
    
@app.route('/contests/my')
@check_login
def my_contests(user):
    return render_template('contests.html', type='my', user=user)


@app.route('/users')
@check_login
def users(user):
    return render_template('users.html', user=user, users=User.select())


@app.route('/home')
@check_login
def home(user):
    return render_template('home.html', user=user)


@app.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.json
    user = User.get_or_none(User.username == data['username'])
    if user is not None:
        res = {
            'status': 'username is taken'
        }
    else:
        res = {
            'status': 'ok'
        }
        user = User.create(username = data['username'],
                    firstname = data['firstname'],
                    secondname = data['secondname'],
                    password_hash = fn.make_password(data['password']))
        session['flask_user_id'] = user.id
    return jsonify(res)
    
    
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    user = User.get_or_none(User.username == data['username'])
    if user is None:
        res = {
            'status': 'invalid username or password'
        }
    elif check_password(data['password'], user.password_hash):
        res = {
            'status': 'ok'
        }
        session['flask_user_id'] = user.id
    else:
        res = {
            'status': 'invalid username or password'
        }
    return jsonify(res)
    
    
@app.route('/logout')
@check_login
def logout(user):
    session.pop('flask_user_id')
    return redirect('/login', code=302)

    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
