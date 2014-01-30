import utils

import unittest
from datetime import date

class UtilsTestCase(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
    
    def test_get_float(self):
        valid_inputs = [1, 1.2, '1', '1.2', '1,22.22', '1,23']
        valid_outputs = [1.0, 1.2, 1.0, 1.2, 122.22, 123]
        for inp, out in zip(valid_inputs, valid_outputs):
            self.assertEqual(utils.get_float(inp), out)
        self.assertRaises(BaseException, utils.get_float, 'blah')
        
    def test_int_date(self):
        valid_inp = ['22 feb 2014',
                     '22 sep 2000',
                     '01-oct-2012',
                     '22/22/1222',
                     '11-11-1111',
                     '11.11.1111',
                     date(2001, 12, 31)]
        valid_out = [20140222, 20000922, 20121001, 12222222, 11111111,
                    11111111, 20011231]
        for inp, out in zip(valid_inp, valid_out):
            self.assertEqual(utils.int_date(inp), out)
        
        self.assertRaises(BaseException, utils.int_date, 99999999)
        self.assertRaises(BaseException, utils.int_date, '1/1/2001')
        