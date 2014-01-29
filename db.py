
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
    
class TxnRaw(db.Model):
    """Contains raw transactions from copied files."""
    txn_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)  # 1 for now
    fund_name = db.Column(db.String(100))
    amc = db.Column(db.String(20))
    fund_id = db.Column(db.String(10))
    txn_type = db.Column(db.Integer)
    units = db.Column(db.Float)
    nav = db.Column(db.Float)
    date = db.Column(db.Integer)
    amount = db.Column(db.Float)
    status = db.Column(db.String(20))
    remarks = db.Column(db.String(60))

    def __init__(self, fund_name, amc, units, amount, date, txn_type, user_id=None,
                 fund_id=None, nav=None, status=None, remarks=None):
        self.fund_name = fund_name
        self.amc = amc
        self.units = units
        self.amount = amount
        self.date = date
        self.txn_type = txn_type
        self.user_id = user_id
        self.fund_id = fund_id
        self.nav = nav
        self.status = status
        self.remarks = remarks

# @app.route('/')
# def hello():
#     return 'heylow world!ss'


db.create_all()
#Boom, and there is your database. Now to create some users:

admin = User('admin', 'admin@example.com')
guest = User('guest', 'guest@example.com')
txn = TxnRaw('blah', 'fake_house', 11.1, 1.1, 20141122, 12, 31)
#But they are not yet in the database, so lets make sure they are

#db.session.add(admin)

#db.session.add(guest)
#db.session.add(txn)
#db.session.commit()
#Accessing the data in database is easy as a pie:

users = User.query.all()
#[<User u'admin'>, <User u'guest'>]
admin = User.query.filter_by(username='admin').first()
print users
print admin
print admin.username
print admin.email

txns = TxnRaw.query.filter_by(user_id=31).all()
print [txn.txn_id for txn in txns]