from app import db

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

