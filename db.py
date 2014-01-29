
'''
table transaction
(will contain the transactions copied from mutual funds 'show all transactions' page)
    user id
    txn date
    fund name
    txn type (redemption/purchase)
    fund id
    units
    nav
    amount
    status
    remarks
    


'''

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)

# TODO: put this sensitive information into a new configuration file
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:nova@localhost/rushi'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.username
        
# @app.route('/')
# def hello():
#     return 'heylow world!ss'


db.create_all()
#Boom, and there is your database. Now to create some users:

admin = User('admin', 'admin@example.com')
guest = User('guest', 'guest@example.com')
#But they are not yet in the database, so lets make sure they are

db.session.add(admin)
db.session.add(guest)
db.session.commit()
#Accessing the data in database is easy as a pie:

users = User.query.all()
#[<User u'admin'>, <User u'guest'>]
admin = User.query.filter_by(username='admin').first()
print users
print admin
print admin.username
print admin.email