

# NOTES
# step 1: parse when only the table is provided (strip off table heading if
#                                                exist)
# step 2: parse even when more information is present(e.g. when the user does a 
#                                                     ctrl+A and then pastes)
# step 3: see if some other browser/OS gives different text while copying info
# step 4: only take the transactions whose status is 'processed', and remove everything else
# step 5: see how to handle cases when user pastes second time, which has a transaction which is now in 'processed' state but was in a different state previously


query_string = example_uti.strip()
query_list = query_string.split('\n')
query_matrix = [line.split('    ') for line in query_list]
if query_matrix[0][0] == 'Scheme':
    query_matrix = query_matrix[1:]
print query_matrix