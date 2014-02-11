from app import db
import models

from sqlalchemy import or_, text
from sqlalchemy.sql import func
import datetime

# fund_ids = {
#     'UTI-BOND FUND - GROWTH': 'MUT021',
#     'UTI-TREASURY ADVANTAGE FUND - INSTITUTIONAL PLAN - GROWTH': 'MUT119',
#     'UTI-NIFTY INDEX FUND - GROWTH': 'MUT029',
#     'UTI-NIFTY INDEX FUND - DIVIDEND': 'MUT087',
#     'ICICI Prudential US Bluechip Equity Fund - Regular Plan - Growth': 'MPI1065',
#     'ICICI Prudential Technology Fund - Direct Plan - Growth': 'MPI1128',
#     'ICICI Prudential Technology Fund - Regular Plan - Growth': 'MPI015',
#     'ICICI Prudential Export and Other Services Fund - Regular Plan - Growth': 'MPI110',
#     'blah':'blah',
# }

# def get_fund_name(fund_id):
#     for k, v in fund_ids.iteritems():
#         if v == fund_id:
#             return k
#     raise BaseException
    
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
    

# def get_fund_id(fund_name):
#     # to be replaced with a call to database
#     return fund_ids[fund_name]

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

def get_last_nav_date(fund_id):
    last_date = models.Nav.query.filter_by(fund_id=fund_id).order_by(models.Nav.date.desc()).first()
    if last_date:
        return last_date.date
    else:
        return 0

def get_navs(fund_id, from_date, to_date):
    data =  models.Nav.query.filter(models.Nav.fund_id==fund_id, models.Nav.date >= str(from_date), models.Nav.date <= str(to_date))
    date_value_dict = {}
    for datum in data:
        date_value_dict[datum.date] = datum.nav
    return date_value_dict

def store_navs(fund_id, date_value_dict):
    for date in date_value_dict:
        db.session.add(models.Nav(fund_id, date, date_value_dict[date]))
    fund = models.Fund.query.filter_by(id=fund_id).first()
    if fund:
        fund.updated = datetime.datetime.utcnow()
        db.session.commit()
        return True
    else:
        return False

def last_updated(fund_id):
#    return models.Fund.query.filter_by(fund_id=fund_id).first().last_updated
    fund = models.Fund.query.filter_by(id=fund_id).first()
    if not fund:
        store_navs(fund_id, {})
        return datetime.datetime.utcnow()
    else:
        return fund.updated

def fund_id_from_keywords(keywords):
#    keywords_OR_arg = (models.Keyword.keyword == kw for kw in keywords)
#    print keywords_OR_arg
#    models.Keyword.query(models.Keyword.id,
#                         db.count(models.Keyword.keyword).label("kw_count"))\
#                 .filter(or_(keywords_OR_arg)).order_by("kw_count")
    keywords = [keywords]
    query_str = ('SELECT keyword.id, count(*) as count_col '
                'from keyword '
                'where ')

    param_dict = {}
    for kw in keywords:
        param_dict['id'+str(keywords.index(kw)+1)] = kw

    ls = []
    for i in range(len(keywords)):
        ls.append('keyword.keyword = :id' + str(i+1) + ' ')

    query_str += ' or '.join(ls)
    query_str += ' group by keyword.id order by count_col desc'
    return db.engine.execute(text(query_str), **param_dict).first().id

def get_all_fund_families():
    return [row['family'] for row in db.engine.execute('SELECT DISTINCT family FROM fund ORDER BY family;')]

#store_navs('MPI015', {})
