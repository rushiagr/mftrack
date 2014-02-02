
# NOTES
# ON PARSING TRANSACTION DATA
#DONE step 1: parse when only the table is provided (strip off table heading if
#                                                exist)
# step 2: parse even when more information is present(e.g. when the user does a 
#                                                     ctrl+A and then pastes)
# step 3: see if some other browser/OS gives different text while copying info
# step 4: only take the transactions whose status is 'processed', and remove everything else
# step 5: see how to handle cases when user pastes second time, which has a transaction which is now in 'processed' state but was in a different state previously

#NOTE: we are using NAV values from only moneycontrol site, and not from amount/units. This should change in future

# TODO(rushiagr): get mutual fund IDs from internet, and not from a dict filled
# manually

# TODO(rushiagr): Use database's transaction object, and remove Txn

# TODO: auto-detect the company of transaction pasted

# TODO: Store NAV in Txn object

# TODO: while taking data from moneycontrol, also return the date of NAV

# TODO: show the users the profit they're earning on each of the fund

# TODO: when a user redeems some units, show how much profit he earned 
# (assuming he is redeeming the units which were purchased first)

# TODO: give the user a choice to redeem units which were bought 'later', and 
# not the ones he purchased first.

# Note : do not use NAV value from icici bank at all. it is usually outdated,
# and doesnt match with amount divided by units

# TODO: get value of NAV from 'units' and 'amount', and not from moneycontrol

# TODO: add these defects to github issues for this project

# fill al these information into database tables

# NOTE: for now, ignore that moneycontrol can have old values for today

# TODO check if deriving nav values from units and amount give more accurate final values

# TODOadd mechanism for giving the users updates regarding moneycontrol data (e.g.
# the data was last modified on moneycontrol server on yesterday, and generally
# it gets updated at so and so time so you can expect it to become updated again
# in blah hours

from examples import utimf
from examples import icicipru

#from db import models
from db import api as db
import utils

import urllib2
import datetime

# Constants
NEW_PURCHASE = 1
ADDITIONAL_PURCHASE = 2
REDEMPTION = 3

PURCHASE = 101

def get_txns():
    return db.get_all_transactions(1)

class Txn(object):
    def __init__(self, fund_name=None, txn_type=None, amount=None, units=None,
                 date=None, status=None, remarks=None):
        self.fund_name = fund_name
        if txn_type.lower() in ['purchase', 'new purchase',
                                'additional purchase']:
            self.txn_type = PURCHASE
        elif txn_type.lower() in ['redemption']:
            self.txn_type = REDEMPTION
        else:
            raise BaseException
        
        self.amount = utils.get_float(amount)
        self.units = utils.get_float(units)
        self.date = utils.int_date(date)
        self.status = status
        self.remarks = remarks
        self.fund_id = db.get_fund_id(fund_name)
        self.nav = None     # NAV on the day the transaction is performed
        self.amc = None
        # NOTE: The Txn object will also possess a list 'sold_units_nav_tuple_list' 
        # later in the processing, which will contain the sold units and the
        # buying price of them


def get_detailed_stats(txn_list):
    mf_dict = {}
    # TODO: values of mf_dict should be objects, and not list. For those objects
    # we will add additional attributes like total redemption, total profit in 
    # redemption, total units still held, total profit in current scenario, etc
    # BUT make sure you study the implications of having all this information
    # stored and retrieved from database

    for txn in txn_list:
        mf_dict[txn['fund_name']] = {}
        mf_dict[txn['fund_name']]['txns'] = []
    for txn in txn_list:
        mf_dict[txn['fund_name']]['txns'].append(txn)

    for mf in mf_dict:
        mf_dict[mf]['txns'].sort(key=lambda x: x['date'])
    for mf in mf_dict:
        no_nav_txn = [txn for txn in mf_dict[mf]['txns'] if txn['nav'] is None]
        if len(no_nav_txn) != 0:
            # TODO: optimize here too
            fill_all_navs_for_fund(mf_dict[mf]['txns'])

    for mf in mf_dict:
        fill_redemption_stats(mf_dict[mf]['txns'])

    mf_curr_value_dict = get_curr_fund_value(mf_dict.keys())


    for mf in mf_dict:
        mf_dict[mf]['total_units'] = sum([txn['units'] for txn in mf_dict[mf]['txns'] if txn['txn_type'] == PURCHASE])
        mf_dict[mf]['total_units'] -= sum([txn['units'] for txn in mf_dict[mf]['txns'] if txn['txn_type'] == REDEMPTION])
        mf_dict[mf]['total_amount_invested'] = sum([txn['left_units'] * txn['nav'] for txn in mf_dict[mf]['txns']])
        mf_dict[mf]['total_amount_now'] = mf_curr_value_dict[mf] * mf_dict[mf]['total_units']
        mf_dict[mf]['percentage_gains'] = mf_dict[mf]['total_amount_now']/mf_dict[mf]['total_amount_invested']*100.0 if mf_dict[mf]['total_amount_invested'] != 0.0 else 0.0
    stats = {}
    stats['total_amount_invested'] = sum([mf_dict[mf]['total_amount_invested'] for mf in mf_dict])
    stats['total_amount_now'] = sum([mf_dict[mf]['total_amount_now'] for mf in mf_dict])
    stats['percentage_gains'] = stats['total_amount_now']/stats['total_amount_invested']*100.0 - 100.0 if stats['total_amount_invested'] != 0.0 else 0.0
    return mf_dict, stats


def fill_redemption_stats(txn_list):
    # Assumption: txn list is sane, i.e. a guy is not redeeming more units than he
    # has purchased
    # Assumption: list is sorted in order of date
    txn_units = list([txn['units'] for txn in txn_list])
    dup_list = list(txn_list)
    for t in dup_list:
        t['sold_units_nav_tuple_list'] = []
    
    for i in range(len(dup_list)):
        if dup_list[i]['txn_type'] in [REDEMPTION]:
            units_left = dup_list[i]['units']
            for j in range(i):
                if units_left > 0.0:
                    if dup_list[j]['txn_type'] == PURCHASE:
                        if units_left < dup_list[j]['units']:
                            units_to_deduct = units_left
                        else:
                            units_to_deduct = dup_list[j]['units']
                        if units_to_deduct > 0.001:
                            dup_list[i]['sold_units_nav_tuple_list'].append(
                                 (units_to_deduct, dup_list[j]['nav'], ))
                        dup_list[j]['units'] = dup_list[j]['units'] - units_to_deduct
                        units_left -= units_to_deduct
                else:
                    break
    for txn, units in zip(txn_list, txn_units):
        txn['left_units'] = txn['units'] if txn['txn_type'] == PURCHASE else 0.0
        txn['units'] = units

    
def fill_all_navs_for_fund(txn_list):
    """ For the given list of Txn object, fetch the NAVs of all the
    transactions for which this value is not present. All the transactions in txn_list
    are of same fund"""
    # Assumption: list is already sorted
    max_date = txn_list[-1]['date']
    min_date = txn_list[0]['date']
    date_nav_dict = get_mf_data(txn_list[0]['fund_id'], min_date, max_date)
    for txn in txn_list:
        txn['nav'] = date_nav_dict[txn['date']]



def get_curr_fund_value(fund_name_list):
    unit_values = {}
    for fund in fund_name_list:
        fund_id = db.get_fund_id(fund)
        data_dict = get_mf_data(fund_id, utils.last_month(), utils.today())
        unit_values[fund] = data_dict[max(data_dict)]
    return unit_values

def txn_to_obj_list(txn_string, amc=None, user_id=None):
    # TODO: in future, if amc is none, detect it from txn_string
    
    txn_matrix = parse_txn(txn_string)
    txn_obj_list = []
    if amc.lower() == 'uti':
        positions = [0, 1, 2, 3, 4]
    elif amc.lower() == 'icici':
        positions = [0, 1, 5, 3, 2]
    else:
        raise

    for txn in txn_matrix:
        obj = dict(fund_name=txn[positions[0]],
                  txn_type=txn[positions[1]],
                  amount=utils.get_float(txn[positions[2]]),
                  units=utils.get_float(txn[positions[3]]),
                  date=utils.int_date(txn[positions[4]]))
        txn_obj_list.append(obj)
    
    for txn in txn_obj_list:        
        if txn['txn_type'].lower() in ['purchase', 'new purchase',
                                'additional purchase']:
            txn['txn_type'] = PURCHASE
        elif txn['txn_type'].lower() in ['redemption']:
            txn['txn_type'] = REDEMPTION
        else:
            raise BaseException


    
    # Additional details contained in transactions
    if amc.lower() == 'uti':
        for obj, txn in zip(txn_obj_list, txn_matrix):
            obj['remarks'] = txn[6].strip() if len(txn) >= 7 else ''

# DO NOT STORE ICICI NAV. IT IS SoMETIMES AN OLD VALUE
#     elif amc.lower() == 'icici':
#         for obj, txn in zip(txn_obj_list, txn_matrix):
#             obj['nav'] = float(txn[4])

    for obj in txn_obj_list:
        obj['amc'] = amc.lower() if amc.lower() in ['icici', 'uti'] else ''
    
    for obj in txn_obj_list:
        obj['user_id'] = user_id
        
    # TODO Do not make this much api calls to db!!
    for obj in txn_obj_list:
        obj['fund_id'] = db.get_fund_id(obj['fund_name'])

    return txn_obj_list


def parse_txn(txn_string):
    """ Takes transaction status from UTIMF or ICICI website, and converts
    it to a usable matrix."""
    txn_list = txn_string.strip().split('\n')
    txn_matrix = [line.split('    ') if len(line.split('    ')) > 3 else line.split('\t') for line in txn_list ]
    if txn_matrix[0][0].lower() in ['scheme', 'fund name']:
        txn_matrix = txn_matrix[1:]
    return txn_matrix

def get_mf_data(mf_code, from_date, to_date):
    """ Returns a tuple of date and mutual fund NAV for the given mutual fund,
    between the given dates"""
    from_date = str(from_date)
    to_date = str(to_date)
    query_url = ('http://moneycontrol.com/mf/mf_info/hist_tech_chart.php?'
               'im_id=%(mf_id)s'
               '&dd=%(from_dd)s'
               '&mm=%(from_mm)s'
               '&yy=%(from_yyyy)s'
               '&t_dd=%(to_dd)s'
               '&t_mm=%(to_mm)s'
               '&t_yy=%(to_yyyy)s'
               '&range=max' % 
               
        {'mf_id': mf_code,
         'from_dd': from_date[6:],
         'from_mm': from_date[4:6],
         'from_yyyy': from_date[0:4],
         'to_dd': to_date[6:],
         'to_mm': to_date[4:6],
         'to_yyyy': to_date[0:4],
         })
    resp_str = urllib2.urlopen(query_url).read()
    return extract_moneycontrol_data(resp_str)


def extract_moneycontrol_data(data_str):
    """Takes moneycontrol data and converts it in slightly more usable form.
    
    Converts '<date>,<value>,<value>,<value>,<value>' string returned by
    the website into dict with date as key and value is value."""
    # TODO: add check here if moneycontrol returns no data or bad data
    lines = data_str.split('\n')
    date_value_dict = {}
    for line in lines:
        l = line.split(',')
        date_value_dict[utils.int_date(l[0])] = float(l[1])
    return date_value_dict

#print extract_moneycontrol_data(get_mf_data('MPI110', intdate_last_month(), intdate_today()))
#print get_mf_data('MPI110', intdate_last_month(), intdate_today())

#print get_transaction_stats(txn_to_obj_list(utimf.txn_str, 'uti'))
#print get_transaction_stats(txn_to_obj_list(icicipru.txn_str, 'icici'))

# txns = txn_to_obj_list(utimf.txn_str, 'uti')
# mf_dict = get_detailed_stats(txns)


def amount_invested_from_list(txn_list):
    """Returns total amount invested for list of transactions of _same_ mutual
    fund."""
    curr_value = get_curr_fund_value([txn_list[0].fund_name]).values()[0]
    invested_units = 0.0
    for txn in txn_list:
        if txn.txn_type == REDEMPTION:
            invested_units -= txn.units
        elif txn.txn_type == PURCHASE:
            invested_units += txn.units
    return invested_units * curr_value




################################################
#### All the user-related functions  ###########
################################################


def store_transactions(txtbox_data, amc, user_id):
    last_date = db.get_last_transaction_date(user_id, amc)
    txns = txn_to_obj_list(txtbox_data, amc, user_id)
    txns = [txn for txn in txns if txn['date'] > last_date]
    db.store_transactions(txns)

def get_summary(user_id):
    """Get all the important data for the user"""
    txns = db.get_all_transactions(user_id)
    mf_dict, stats = get_detailed_stats(txns)
    return mf_dict, stats


################################################
################################################
################################################



def store_textbox_data_in_db(txtbox_data, amc=None, user_id=None):
    """Takes the transaction information pasted by user into textbox and
    put it into DB. The AMC (Asset Management Company) might or might not be
    provided by the user.
    """
    txns = txn_to_obj_list(txtbox_data, amc)
    user_id = 1  # For now, there is only one user
    to_db_obj_list = db.get_db_objects_from_txn_list(txns, user_id)
    # get transactions from database for that user
    from_db_obj_list = db.get_txns_from_db(user_id, amc)    
    # validate if the data is correct. do all validation checks here
    validate_existing_and_new_txn_data(to_db_obj_list,
                                       from_db_obj_list)
    # get only the new objects to be inserted in db
    new_db_objs = get_new_db_objects(to_db_obj_list, from_db_obj_list)
#    insert_objects_into_db(new_db_objs)





#def insert_objects_into_db(new_db_objs):
#    for obj in new_db_objs:
#        models.db.session.add(obj)
#    models.db.session.commit()

def get_new_db_objects(to_db_obj_list, from_db_obj_list):
    # NOTE(rushiagr): Assumption: when 2 transactions for say 14th Jan are 
    # stored into database, and if three transactions are found for 14th jan,
    # reject the third one, or raise an exception. This is sane, as AMC
    # websites generally update this information at once, for a day.
    if not from_db_obj_list:
        return to_db_obj_list
    to_db_obj_list.sort(key=lambda x: x.date)
    from_db_obj_list.sort(key=lambda x: x.date)
    max_date_from_db = from_db_obj_list[-1]
    to_db_obj_list = [obj for obj in to_db_obj_list if obj.date > max_date_from_db]
    return to_db_obj_list

def validate_existing_and_new_txn_data(to_db_obj_list,
                                       from_db_obj_list):
    return





#store_textbox_data_in_db(utimf.txn_str, amc='uti', user_id=7777)
#store_textbox_data_in_db(icicipru.txn_str, amc='icici', user_id=6666)

# for fund in mf_dict:
#     # not so good way of calculating this information, as it makes a lot of
#     # calls to moneycontrol website
#     print 'fund: %s value: %s' % (fund, amount_invested_from_list(mf_dict[fund]))
# print sum([amount_invested_from_list(mf_dict[fund]) for fund in mf_dict])


