import os
import chess
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, session
from flask_assets import Environment, Bundle
from database import *
import requests

        
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


@app.route('/standings/all')
@check_login
def all_standings(user):
    return render_template('standings.html', type='all', user=user)
    
    
@app.route('/standings/my')
@check_login
def my_standings(user):
    return render_template('standings.html', type='my', user=user,
                           standings=Standings.select().where(Standings.creator == user))


@app.route('/standings/create')
@check_login
def create_standings(user):
    return render_template('create_standings.html', type='my', user=user)
    
    
@app.route('/users')
@check_login
def users(user):
    return render_template('users.html', user=user, users=User.select())


@app.route('/users/<int:user_id>')
@check_login
def view_user(user, user_id):
    return render_template('user.html', user=user)
    
    
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
    
    
@app.route('/api/standings/create', methods=['POST'])
@check_login
def api_create_standings(user):
    data = request.form
    try:
        result = requests.get(data['link'])
        print(result.status_code)
        if str(result.status_code)[0] not in '23':
            res = {
                'status': 'invalid URL'
            }
        else:
            standings = Standings.create(creator=user,
                                         season=data['season'],
                                         date=data['date'],
                                         title=data['title'],
                                         venue=data['venue'],
                                         link=data['link'],
                                         identification=data['identification'])
            if len(request.files) > 0 and request.files['logo'].content_type[:6] == 'image/':
                logo_url = f'static/images/logos/{standings.id}.{request.files["logo"].content_type[6:]}'
                request.files['logo'].save(logo_url)
                standings.logo = '/' + logo_url
                standings.save()
            res = {
                    'status': 'ok'
            }
    except Exception as e:
        from traceback import format_exc
        print(format_exc())
        res = {
            'status': 'invalid URL'
        }
    return jsonify(res)
    
    
@app.route('/logout')
@check_login
def logout(user):
    session.pop('flask_user_id')
    return redirect('/login', code=302)

    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
