


welcome_page_str='''


'''

def tablify_transactions(txn_list):
    """From transactions list, forms an HTML table."""
    ret = '<table border="1">'    # return value
    for txn in txn_list:
        ret += get_row(txn)
    ret += '</table>'
    return ret


def get_row(txn):
    row = '<tr>'
    for attr in ['fund_name', 'txn_type', 'units', 'amount', 'date']:
        row += '<td>'+str(txn[attr])+'</td>'
    row += '</tr>'
    return row        