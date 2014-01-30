from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)

# TODO: put this sensitive information into a new configuration file
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:nova@localhost/rushi'
db = SQLAlchemy(app)
    
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
