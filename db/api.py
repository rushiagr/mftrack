from app import db
import models

fund_ids = {
    'UTI-BOND FUND - GROWTH': 'MUT021',
    'UTI-TREASURY ADVANTAGE FUND - INSTITUTIONAL PLAN - GROWTH': 'MUT119',
    'UTI-NIFTY INDEX FUND - GROWTH': 'MUT029',
    'UTI-NIFTY INDEX FUND - DIVIDEND': 'MUT087',
    'ICICI Prudential US Bluechip Equity Fund - Regular Plan - Growth': 'MPI1065',
    'ICICI Prudential Technology Fund - Direct Plan - Growth': 'MPI1128',
    'ICICI Prudential Technology Fund - Regular Plan - Growth': 'MPI015',
    'ICICI Prudential Export and Other Services Fund - Regular Plan - Growth': 'MPI110',
    'blah':'blah',
}

def unpack_transactions(txn_list):
    """Converts list of DB transaction objects to list of dicts."""
    return_list = []
    for txn in txn_list:
        obj = {}
        obj['fund_name'] = txn.fund_name
        obj['txn_type'] = txn.txn_type
        obj['amount'] = txn.amount
        obj['units'] = txn.units
        obj['date'] = txn.date
        obj['status'] = txn.status
        obj['remarks'] = txn.remarks
        obj['txn_id'] = txn.txn_id
        obj['user_id'] = txn.user_id
        obj['amc'] = txn.amc
        obj['nav'] = txn.nav
        obj['fund_id'] = txn.fund_id
        return_list.append(obj)
    return return_list

def store_transactions(txn_list):
    for txn in txn_list:
        db.session.add(models.TxnRaw(txn))
    db.session.commit()
    

def get_fund_id(fund_name):
    # to be replaced with a call to database
    return fund_ids[fund_name]

def get_all_transactions(user_id): # TODO add sorted flag
    txns = models.TxnRaw.query.all()
    return unpack_transactions(txns)

def get_txns_from_db(user_id, amc):
    return models.TxnRaw.query.filter_by(user_id=user_id, amc=amc).all()

def get_last_transaction_date(user_id, amc):
    try:
        return models.TxnRaw.query.filter_by(user_id=user_id, amc=amc).order_by(models.TxnRaw.date.desc()).first().date
    except AttributeError:
        return 00000000

def get_db_objects_from_txn_list(txn_list, user_id):
    """Returns DB objects from txn_objs."""
    db_objs = []
    for txn_obj in txn_list:
        db_obj = models.TxnRaw(txn_obj['fund_name'],
                        txn_obj['amc'],
                        txn_obj['units'],
                        txn_obj['amount'],
                        txn_obj['date'],
                        txn_obj['txn_type'],
                        user_id,
                        txn_obj['fund_id'],
                        txn_obj['nav'],
                        txn_obj['status'],
                        txn_obj['remarks'])
        db_objs.append(db_obj)
    return db_objs
get_last_transaction_date(1, 'uti')