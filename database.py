from hashlib import sha1
from random import random
from datetime import datetime
from peewee import *


db = SqliteDatabase('data/contest_standings.db')


def get_hexdigest(salt, raw_password):
    data = salt + raw_password
    return sha1(data.encode('utf8')).hexdigest()

@db.func()
def make_password(raw_password):
    salt = get_hexdigest(str(random()), str(random()))[:5]
    hsh = get_hexdigest(salt, raw_password)
    return '%s$%s' % (salt, hsh)

@db.func()
def check_password(raw_password, enc_password):
    salt, hsh = enc_password.split('$', 1)
    return hsh == get_hexdigest(salt, raw_password)
    
    
class BaseModel(Model):
    class Meta:
        database = db

    
class User(BaseModel):
    username = CharField(unique=True)
    firstname = CharField()
    secondname = CharField()
    registration_date = DateTimeField(default=datetime.now)
    photo = CharField(default='/static/images/user.png')
    password_hash = CharField()
            
    def get_full_name(self):
        return f'{self.secondname} {self.firstname}'
        
    def get_created_standings_count(self):
        return 0
        
    def get_registration_date(self):
        return str(self.registration_date)[:10]
        
  
class Standings(BaseModel):
    creator = ForeignKeyField(User, backref='created_standings')
    season = CharField()
    date = DateTimeField()
    creation_date = DateTimeField(default=datetime.now)
    title = CharField()
    venue = CharField()
    link = CharField()
    identification = CharField()
    logo = CharField(default='/static/images/logo.png')
    
    duration = IntegerField()
    n_problems = IntegerField()
    team_column = IntegerField(default=2)
    region_column = IntegerField(default=-1)
    first_problem_column = IntegerField(default=3)
    time_format = CharField()
    
    def get_short_link(self):
        start = self.link.find('://') + 3
        return self.link[start:self.link.find('/', start)]
    
    def get_date(self):
        return str(self.date)[:10]


User.create_table()
Standings.create_table()
