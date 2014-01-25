
# NOTES
# ON PARSING TRANSACTION DATA
#DONE step 1: parse when only the table is provided (strip off table heading if
#                                                exist)
# step 2: parse even when more information is present(e.g. when the user does a 
#                                                     ctrl+A and then pastes)
# step 3: see if some other browser/OS gives different text while copying info
# step 4: only take the transactions whose status is 'processed', and remove everything else
# step 5: see how to handle cases when user pastes second time, which has a transaction which is now in 'processed' state but was in a different state previously


# TODO(rushiagr): get mutual fund IDs from internet, and not from a dict filled
# manually

# TODO: auto-detect the company of transaction pasted

# TODO: Store NAV in Txn object

# TODO: while taking data from moneycontrol, also return the date of NAV


# as on 22 jan wednsday
#367389.77Total
#375042.98Current
#print utimf.txn_str
from examples import utimf
from examples import icicipru


import urllib2
import datetime

fund_ids = {
    'UTI-BOND FUND - GROWTH': 'MUT021',
    'UTI-TREASURY ADVANTAGE FUND - INSTITUTIONAL PLAN - GROWTH': 'MUT119',
    'UTI-NIFTY INDEX FUND - GROWTH': 'MUT029',
    'UTI-NIFTY INDEX FUND - DIVIDEND': 'MUT087',
    'ICICI Prudential US Bluechip Equity Fund - Regular Plan - Growth': 'MPI1065',
    'ICICI Prudential Technology Fund - Direct Plan - Growth': 'MPI1128',
    'ICICI Prudential Technology Fund - Regular Plan - Growth': 'MPI015',
    'ICICI Prudential Export and Other Services Fund - Regular Plan - Growth': 'MPI110',
    }

class Txn(object):
    def __init__(self, fund_name=None, txn_type=None, amount=None, units=None,
                 date=None, status=None, remarks=None):
        self.fund_name = fund_name
        if txn_type.lower() in ['purchase', 'new purchase']:
            self.txn_type = 'NEW_PURCHASE'
        elif txn_type.lower() in ['additional purchase']:
            self.txn_type = 'ADDITIONAL_PURCHASE'
        elif txn_type.lower() in ['redemption']:
            self.txn_type = 'REDEMPTION'
        else:
            print "txn type is", txn_type
            raise BaseException
        
        if type(amount) == float:
            self.amount = amount
        elif type(amount) == int:
            self.amount = float(amount)
        elif type(amount) == str:
            amount = amount.replace(',', '')
            try:
                self.amount = float(amount)
            except ValueError:
                print 'amount format not compatible'
                raise

        if type(units) == float:
            self.units = units
        elif type(units) == int:
            self.units = float(units)
        elif type(units) == str:
            units = units.replace(',', '')
            try:
                self.units = float(units)
            except ValueError:
                print 'units format not compatible'
                raise

        months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug',
                  'sep', 'oct', 'nov', 'dec']
        if type(date) == str:
            # Date format '01/01/2014' (DD/MM/YYYY)
            if len(date) == 10 and date[2] == date[5] == '/':
                self.date = int(date[6:10]+date[3:5]+date[0:2])
            # Date format '01 Jan 2014' or '01-jan-2014'
            elif len(date) == 11 and date[3:6].lower() in months:
                month_int = months.index(date[3:6].lower())+1
                month = ('%2s' % month_int).replace(' ', '0')
                self.date = int(date[7:11]+month+date[0:2])
            else:
                raise
        elif type(date) == int:
            if date < 20300000 and date > 19500000:
                self.date = date
            else:
                raise

        self.status = status
        self.remarks = remarks
        self.fund_id = None
        self.nav = None     # NAV on the day the transaction is performed

def get_transaction_stats(txn_list):
    purchase_txn = [txn for txn in txn_list if txn.txn_type in 
                    ['NEW_PURCHASE', 'ADDITIONAL_PURCHASE']]
    redemption_txn = [txn for txn in txn_list if txn.txn_type == 'REDEMPTION']

    amt_invested = sum([txn.amount for txn in purchase_txn])
    amt_redeemed = sum([txn.amount for txn in redemption_txn])

    purchase_units_dict = {}
    for txn in purchase_txn:
        purchase_units_dict[txn.fund_name] = 0.0
    for txn in purchase_txn:
        purchase_units_dict[txn.fund_name] += txn.units
        
    redemption_units_dict = {}
    for txn in redemption_txn:
        redemption_units_dict[txn.fund_name] = 0.0
    for txn in redemption_txn:
        redemption_units_dict[txn.fund_name] += txn.units

    left_units = {}
    # if someone has bought, only then he can sell it
    # TODO: add a check here if the sold units are more than bought
    for fund, bought_units in purchase_units_dict.iteritems():
        sold_units = redemption_units_dict.get(fund)
        left_units[fund] = bought_units if sold_units is None else (bought_units - sold_units)
        
    curr_val_dict = get_curr_fund_value(left_units.keys())
        
    total_amt_invested = 0.0
    
    for fund in curr_val_dict.keys():
        if left_units[fund] is None:
            continue
        total_amt_invested += curr_val_dict[fund] * left_units[fund]
    
    return amt_invested, amt_redeemed, total_amt_invested

def get_curr_fund_value(fund_name_list):
    unit_values = {}
    for fund in fund_name_list:
        fund_id = fund_ids[fund]
        data_list = extract_moneycontrol_data(get_mf_data(fund_id, 
                    intdate_last_month(), intdate_today()))
        unit_values[fund] = data_list[-1][1]
    return unit_values

def txn_to_obj_list(txn_string, amc):
    txn_matrix = parse_txn(txn_string)
    txn_obj_list = []
    if amc.lower() == 'uti':
        positions = [0, 1, 2, 3, 4]
    elif amc.lower() == 'icici':
        positions = [0, 1, 5, 3, 2]
    else:
        raise

    for txn in txn_matrix:
        obj = Txn(fund_name=txn[positions[0]],
                  txn_type=txn[positions[1]],
                  amount=txn[positions[2]],
                  units=txn[positions[3]],
                  date=txn[positions[4]]
                  )
        txn_obj_list.append(obj)
    
    # Additional details contained in transactions
    if amc.lower() == 'uti':
        for obj in txn_obj_list:
            obj.remarks = txn[6] if len(txn) >= 7 else None
    elif amc.lower() == 'icici':
        for obj in txn_obj_list:
            obj.nav = float(txn[4])
    
    return txn_obj_list


def parse_txn(txn_string):
    """ Takes transaction status from UTIMF or ICICI website, and converts
    it to a usable matrix."""
    txn_list = txn_string.strip().split('\n')
    txn_matrix = [line.split('    ') for line in txn_list]
    if txn_matrix[0][0].lower() in ['scheme', 'fund name']:
        txn_matrix = txn_matrix[1:]
    return txn_matrix

def get_mf_data(mf_code, from_ddmmyyyy_str, to_ddmmyyyy_str):
    query_url = get_url(mf_code, from_ddmmyyyy_str, to_ddmmyyyy_str)
    resp = urllib2.urlopen(query_url)
    return resp.read()

def get_url(mf_code, from_date, to_date):
    from_date = str(from_date)
    to_date = str(to_date)
    url_str = ('http://moneycontrol.com/mf/mf_info/hist_tech_chart.php?'
               'im_id=%(mf_id)s'
               '&dd=%(from_dd)s'
               '&mm=%(from_mm)s'
               '&yy=%(from_yyyy)s'
               '&t_dd=%(to_dd)s'
               '&t_mm=%(to_mm)s'
               '&t_yy=%(to_yyyy)s'
               '&range=max' % 
               
        {'mf_id': mf_code,
         'from_dd': from_date[0:2],
         'from_mm': from_date[2:4],
         'from_yyyy': from_date[4:],
         'to_dd': to_date[0:2],
         'to_mm': to_date[2:4],
         'to_yyyy': to_date[4:],
         })
    return url_str

def get_date_int(date_str, date_ref=None):
    """ Returns date in integer form (YYYYMMDD, e.g. 20141231). If the 
    date_ref is provided, it will use that as a guide for conversion.
    Example of date_ref: '01 Jan 2014'"""
    months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep',
              'oct', 'nov', 'dec']
    if date_ref.lower() == '01 jan 2014':
        date = date_str[7:]
        month_int = months.index(date_str[3:6].lower())+1
        date += str(month_int) if month_int > 10 else '0'+str(month_int)
        date += date_str[0:2]
        return int(date)
    elif date_ref.lower() == '01/01/2014':
        date = date_str[6:] + date_str[3:5] + date_str[0:2] 
        return int(date)
    else:
        raise
    # TODO(rushiagr): implement all other types, including pattern matching

def intdate_from_datetime(date):
    return (date.day*1000000 + date.month*10000 + date.year)

def intdate_today():
    return intdate_from_datetime(datetime.date.today())

def intdate_last_month():
    return intdate_from_datetime(datetime.date.today() - datetime.timedelta(days=30))

def extract_moneycontrol_data(data_str):
    lines = data_str.split('\n')
    date_value_list = []
    for line in lines:
        l = line.split(',')
        date_value_list.append((get_date_int(l[0], '01 jan 2014'), float(l[1])))
    return date_value_list

#print extract_moneycontrol_data(get_mf_data('MPI110', intdate_last_month(), intdate_today()))
#print get_mf_data('MPI110', intdate_last_month(), intdate_today())

print get_transaction_stats(txn_to_obj_list(utimf.txn_str, 'uti'))
print get_transaction_stats(txn_to_obj_list(icicipru.txn_str, 'icici'))



