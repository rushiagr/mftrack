from examples import utimf

# NOTES
# ON PARSING TRANSACTION DATA
#DONE step 1: parse when only the table is provided (strip off table heading if
#                                                exist)
# step 2: parse even when more information is present(e.g. when the user does a 
#                                                     ctrl+A and then pastes)
# step 3: see if some other browser/OS gives different text while copying info
# step 4: only take the transactions whose status is 'processed', and remove everything else
# step 5: see how to handle cases when user pastes second time, which has a transaction which is now in 'processed' state but was in a different state previously

# as on 22 jan wednsday
#367389.77Total
#375042.98Current
#print utimf.txn_str
import urllib2
import datetime

fund_ids = {
    'UTI-BOND FUND - GROWTH': 'MUT021',
    'UTI-TREASURY ADVANTAGE FUND - INSTITUTIONAL PLAN - GROWTH': 'MUT119',
    'UTI-NIFTY INDEX FUND - GROWTH': 'MUT029',
    'UTI-NIFTY INDEX FUND - DIVIDEND': 'MUT087',
    }

NEW_PURCHASE = 1
ADDITIONAL_PURCHASE = 2
REDEMPTION = 3

PROCESSED = 101
NOT_PROCESSED = 102

class Txn(object):
    def __init__(self, fund_name=None, txn_type=None, amount=None, units=None,
                 date=None, status=None, remarks=None):
        self.fund_name = fund_name
        self.txn_type = txn_type
        self.amount = amount
        self.units = units
        self.date = date
        self.status = status
        self.remarks = remarks

def get_transaction_stats(txn_list):
    purchase_txn = [txn for txn in txn_list if txn.txn_type == 'New Purchase' or txn.txn_type == 'Additional Purchase']
#    import pdb;pdb.set_trace()
    redemption_txn = [txn for txn in txn_list if txn.txn_type == 'Redemption']
    amt_invested = sum([float(txn.amount) for txn in purchase_txn])
    amt_redeemed = sum([float(txn.amount) for txn in redemption_txn])
    purchase_units_dict = {}
    for txn in purchase_txn:
        purchase_units_dict[txn.fund_name] = 0
    for txn in purchase_txn:
        purchase_units_dict[txn.fund_name] += float(txn.units)

    redemption_units_dict = {}
    for txn in redemption_txn:
        redemption_units_dict[txn.fund_name] = 0
    for txn in redemption_txn:
        redemption_units_dict[txn.fund_name] += float(txn.units)

    left_units = {}
    # if someone has bought, only then he can sell it
    for fund, bought_units in purchase_units_dict.iteritems():
        sold_units = redemption_units_dict.get(fund)
        left_units[fund] = bought_units if sold_units is None else (bought_units - sold_units)
        
    curr_val_dict = get_curr_fund_value(left_units.keys()) # returns a dict #TODO
    
    total_amt_invested = 0.0
    
    for fund in curr_val_dict.keys():
        if left_units[fund] is None:
            continue
        total_amt_invested += curr_val_dict[fund] * left_units[fund]
    
    return amt_invested, amt_redeemed, total_amt_invested

#    amt_invested = get_amt_invested()
#     units_still_invested = get_units(purchase_list)
#     units_redeemed = get_units(redemption_list)
#     pass


def get_curr_fund_value(fund_name_list):
    unit_values = {}
    for fund in fund_name_list:
        fund_id = fund_ids[fund]
        unit_values[fund] = (get_curr_fund_value_from_fund_id(fund_id))
#        fund_value_list = extract_moneycontrol_data(get_mf_data('MUT119', intdate_last_month(), intdate_today()))
    return unit_values

def get_curr_fund_value_from_fund_id(fund_id):
    data_list = extract_moneycontrol_data(get_mf_data(fund_id, 
                                                 intdate_last_month(), 
                                                 intdate_today()))
    return data_list[-1][1]

def txn_matrix_to_obj_list(txn_matrix):
    txn_obj_list = []
    for txn in txn_matrix:
        print 'txxxn', txn
        obj = Txn(txn[0],
                  txn[1],
                  float(txn[2]),
                  float(txn[3]),
                  get_date_int(txn[4], '01/01/2014'),
                  txn[5],
                  txn[6] if len(txn) >= 7 else '')
        txn_obj_list.append(obj)
    return txn_obj_list


def parse_uti_txn(txn_string):
    """ Takes transaction status from UTIMF website, and converts
    it to a usable matrix."""
    txn_list = txn_string.strip().split('\n')
    txn_matrix = [line.split('    ') for line in txn_list]
    if txn_matrix[0][0] == 'Scheme':
        txn_matrix = txn_matrix[1:]
    return txn_matrix

print parse_uti_txn(utimf.txn_str)

def get_mf_data(mf_code, from_ddmmyyyy_str, to_ddmmyyyy_str):
    query_url = get_url(mf_code, from_ddmmyyyy_str, to_ddmmyyyy_str)
    resp = urllib2.urlopen(query_url)
#    print resp
#    print resp.read()
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
#        print date
        return int(date)
    elif date_ref.lower() == '01/01/2014':
        date = date_str[6:] + date_str[3:5] + date_str[0:2] 
        return int(date)
    else:
        raise
    # TODO(rushiagr): implement all other types
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

print extract_moneycontrol_data(get_mf_data('MUT119', intdate_last_month(), intdate_today()))
#print get_url('MUT119', '08082008', '08082012')
print get_date_int('04 Feb 2015', '01 Jan 2014')
print get_date_int('04/02/2015', '01/01/2014')

print get_transaction_stats(txn_matrix_to_obj_list(parse_uti_txn(utimf.txn_str)))



