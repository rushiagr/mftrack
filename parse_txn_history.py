from examples import utimf

# NOTES
# step 1: parse when only the table is provided (strip off table heading if
#                                                exist)
# step 2: parse even when more information is present(e.g. when the user does a 
#                                                     ctrl+A and then pastes)
# step 3: see if some other browser/OS gives different text while copying info
# step 4: only take the transactions whose status is 'processed', and remove everything else
# step 5: see how to handle cases when user pastes second time, which has a transaction which is now in 'processed' state but was in a different state previously

#print utimf.txn_str
import httplib

def parse_uti_txn(txn_string):
    """ Takes transaction status from UTIMF website, and converts
    it to a usable matrix."""
    txn_list = txn_string.strip().split('\n')
    txn_matrix = [line.split('    ') for line in txn_list]
    if txn_matrix[0][0] == 'Scheme':
        txn_matrix = txn_matrix[1:]
    return txn_matrix

#print parse_uti_txn(utimf.txn_str)

import urllib2

def get_mf_data(mf_code, from_ddmmyyyy_str, to_ddmmyyyy_str):
    query_url = get_url(mf_code, from_ddmmyyyy_str, to_ddmmyyyy_str)
    resp = urllib2.urlopen(query_url)
#    print resp
#    print resp.read()
    return resp.read()

def get_url(mf_code, from_ddmmyyyy_str, to_ddmmyyyy_str):
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
         'from_dd': from_ddmmyyyy_str[0:2],
         'from_mm': from_ddmmyyyy_str[2:4],
         'from_yyyy': from_ddmmyyyy_str[4:],
         'to_dd': to_ddmmyyyy_str[0:2],
         'to_mm': to_ddmmyyyy_str[2:4],
         'to_yyyy': to_ddmmyyyy_str[4:],
         })
    return url_str

print get_mf_data('MUT119', '08082008', '11082008')
print get_url('MUT119', '08082008', '08082012')