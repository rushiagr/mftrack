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

def parse_uti_txn(txn_string):
    """ Takes transaction status from UTIMF website, and converts
    it to a usable matrix."""
    txn_list = txn_string.strip().split('\n')
    txn_matrix = [line.split('    ') for line in txn_list]
    if txn_matrix[0][0] == 'Scheme':
        txn_matrix = txn_matrix[1:]
    return txn_matrix

#print parse_uti_txn(utimf.txn_str)

