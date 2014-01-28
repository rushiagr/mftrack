import unittest.TestCase
#from parse_txn_history import fill_redemption_stats
 
class TestParseTxnHistory(unittest.TestCase):

    def setUp(self):
        super(TestParseTxnHistory, self).setUp()
#        t1 = Txn(fund_name='blah', txn_type='purchase', amount=1000, units=100)
#        t2 = Txn(fund_name='blah', txn_type='redemption', amount=880, units=80)
#        t3 = Txn(fund_name='blah', txn_type='purchase', amount=600, units=50)
#        t4 = Txn(fund_name='blah', txn_type='redemption', amount=650, units=60)
#        self.fake_txns = [t1, t2, t3, t4]
        
    def test_user_id_only(self):
        self.request.headers['X_USER'] = 'testuser'
        response = self.request.get_response(self.middleware)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(self.context.user_id, 'testuser')
    
    def test_fill_redemption_stats(self):
        a = 1
        b = '1'
        self.assertEqual(a, int(b))

    def test_fill_redemption_stats2(self):
        self.assertEqual(1, int('12'))
    
