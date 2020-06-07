import os
import chess
from flask import Flask, render_template, render_template_string, request, jsonify, send_from_directory, redirect, session
from flask_assets import Environment, Bundle
from database import *
import requests
from contest_parsing import parse_standings, team_identifier
from io import StringIO

        
app = Flask(__name__)
app.secret_key = open('data/secret_key.txt', 'r').read()
assets = Environment()
assets.init_app(app)


def get_logged_in_user():
    if 'flask_user_id' not in session:
        return None
    return User.get_or_none(session['flask_user_id'])
    
        
def check_login(route):
    def wrapper(*args, **kwargs):
        if 'flask_user_id' not in session:
            return redirect('/login', code=302)
        user = User.get_or_none(session['flask_user_id'])
        if user is None:
            return redirect('/login', code=302)
        return route(user=user, *args, **kwargs)
    wrapper.__name__ = route.__name__ + '_wrapper'
    return wrapper
    

@app.route('/')
def hello():
    return redirect('/home', code=302)
    
    
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/images'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
                               
                               
@app.route('/login')
def login():
    return render_template('login.html')
    

@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/standings/all')
def all_standings():
    return render_template('standings.html', type='all', user=get_logged_in_user(),
                           standings=Standings.select().order_by(-Standings.id))
    
    
@app.route('/standings/my')
@check_login
def my_standings(user):
    return render_template('standings.html', type='my', user=user,
                           standings=Standings.select().where(Standings.creator == user).order_by(-Standings.id))


@app.route('/users/<int:user_id>/standings')
def user_standings(user_id):
    return render_template('standings.html', type='all', user=get_logged_in_user(),
                           standings=Standings.select().where(Standings.creator == user_id).order_by(-Standings.id))
                           
                           
@app.route('/standings/<int:standings_id>')
def view_standings(standings_id):
    standings = Standings.get_or_none(Standings.id == standings_id)
    if standings is None:
        return "Standings doesn't exist"
    status, created_standings = parse_standings(standings.link, 
                                                standings.n_problems,
                                                standings.team_column, 
                                                standings.region_column, 
                                                standings.first_problem_column, 
                                                standings.time_format)
    if status != 'ok':
        return status
    path_to_scripts = 'interactive_standings/'
    title = '''<p align="center" style="font-family: times-new-roman">
    <a style="float: left; margin: 13px; padding-left: 7px" href="../../"> 
        <img width="30px" src="/static/images/back_arrow.png">
    </a>
    <font size="7"> {} </font> </p> 
    <p align="center" style="font-family: times-new-roman"> <font size="7"> {}, {} </font> </p>'''.format(standings.title, 
                                                                                                          standings.venue,
                                                                                                          standings.get_named_date())
    created_standings.set_meta_information(title, standings.duration, standings.n_problems, path_to_scripts, standings.identification)
    html = StringIO()
    created_standings.write(html)
    return render_template_string(html.getvalue())
    
    
@app.route('/standings/create')
@check_login
def create_standings(user):
    return render_template('create_standings.html', type='create', user=user)
    
    
@app.route('/standings/<int:standings_id>/edit')
@check_login
def edit_standings(user, standings_id):
    standings = Standings.get_or_none(Standings.id == standings_id)
    if standings is None or standings.creator.id != user.id:
        return redirect('/standings/my', code=302)
    return render_template('create_standings.html', type='edit', user=user, standings=standings)
    
    
@app.route('/users')
def users():
    return render_template('users.html', user=get_logged_in_user(), users=User.select())


@app.route('/teams')
def teams():
    return render_template('teams.html', user=get_logged_in_user(), team_identifier=team_identifier)
    
    
@app.route('/users/<int:user_id>')
def view_user(user_id):
    return render_template('user.html', user=get_logged_in_user(), view_user=User.get_or_none(User.id == user_id))
    
    
@app.route('/home')
def home():
    return render_template('home.html', user=get_logged_in_user())


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
        if str(result.status_code)[0] not in '23':
            res = {
                'status': 'invalid URL'
            }
        else:
            duration = int(data['duration'][0]) * 60 + int(data['duration'][2:4])
            standings = Standings.create(creator=user,
                                         season=data['season'],
                                         date=data['date'],
                                         title=data['title'],
                                         venue=data['venue'],
                                         link=data['link'],
                                         identification=data['identification'],
                                         duration=duration,
                                         n_problems=data['n_problems'],
                                         team_column=data['team_column'],
                                         region_column=data['region_column'],
                                         first_problem_column=data['first_problem_column'],
                                         time_format=data['time_format'])
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
    
    
@app.route('/api/standings/<int:standings_id>/edit', methods=['POST'])
@check_login
def api_edit_standings(user, standings_id):
    standings = Standings.get_or_none(Standings.id == standings_id)
    if standings is None:
        res = {
            'status': 'such standings doesn\'t exist'
        }
    elif standings.creator.id != user.id:
        res = {
            'status': 'you have no access to this standings'
        }
    else:
        data = request.form
        try:
            result = requests.get(data['link'])
            if str(result.status_code)[0] not in '23':
                res = {
                    'status': 'invalid URL'
                }
            else:
                duration = int(data['duration'][0]) * 60 + int(data['duration'][2:4])
                standings.season = data['season']
                standings.date = data['date']
                standings.title = data['title']
                standings.venue = data['venue']
                standings.link = data['link']
                standings.identification = data['identification']
                standings.duration = duration
                standings.n_problems = data['n_problems']
                standings.team_column = data['team_column']
                standings.region_column = data['region_column']
                standings.first_problem_column = data['first_problem_column']
                standings.time_format = data['time_format']
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
