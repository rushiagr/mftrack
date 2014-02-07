from app import db

import datetime

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
    status = db.Column(db.String(20)) #TODO: remove this field
    remarks = db.Column(db.String(60))

    def __init__(self, txn_dict):
        self.fund_name = txn_dict.get('fund_name')
        self.amc = txn_dict.get('amc')
        self.units = txn_dict.get('units')
        self.amount = txn_dict.get('amount')
        self.date = txn_dict.get('date')
        self.txn_type = txn_dict.get('txn_type')
        self.user_id = txn_dict.get('user_id')
        self.fund_id = txn_dict.get('fund_id')
        self.nav = txn_dict.get('nav')
        self.status = txn_dict.get('status')
        self.remarks = txn_dict.get('remarks')

class Nav(db.Model):
    fund_id = db.Column(db.String(10), primary_key=True)
    date = db.Column(db.Integer, primary_key=True, autoincrement=False)
    nav = db.Column(db.Float)
    last_updated = db.Column(db.DateTime)
    
    def __init__(self, fund_id, date, nav):
        self.fund_id = fund_id
        self.date = date
        self.nav = nav
        self.last_updated = datetime.datetime.utcnow()

class Fund(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100))   # Fund name as on transaction statement
    updated = db.Column(db.DateTime)
    family = db.Column(db.String(100))
    Class = db.Column(db.String(100))
    url = db.Column(db.String(200))
    
    def __init__(self, fund_id, fund_name, fund_family, fund_class, fund_url):
        self.id = fund_id
        self.name = fund_name
        self.family = fund_family
        self.Class = fund_class
        self.url = fund_url
        self.updated = datetime.datetime.utcnow()

class Keyword(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    keyword = db.Column(db.String(30), primary_key=True)
    
    def __init__(self, id, keyword):
        self.id = id
        self.keyword = keyword

#db.create_all() # Make a create_all() call here (after importing this file 
# to app.py) to create all tables
        