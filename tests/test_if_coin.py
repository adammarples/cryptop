from unittest import TestCase
from unittest.mock import MagicMock, Mock

import cryptop.cryptop as cryptop

class TestIf_coin(TestCase):

    def setUp(self):
        side_effect = lambda x, y: {'dec_places': 2, 'field_length': 13}[x]
        theme = Mock()
        theme.getint = MagicMock(side_effect=side_effect)
        self.CONFIG = {'theme': theme, 'api': {
            'currency': 'USD'}}
            
    def test_if_coin(self):
        assert cryptop.if_coin('BTC', url='https://api.coinmarketcap.com/v1/ticker/')

    def test_get_price(self):
        cryptop.CURRENCY = 'USD'
        coins = ['BTC', 'ETHOS', 'ETH', 'NEO']
        data = cryptop.get_price(coins)
        print (data)
        cryptop.CURRENCY = 'GBP'
        coins = ['BTC', 'ETHOS', 'ETH', 'NEO']
        data = cryptop.get_price(coins)
        print(data)

    def test_write(self):
        cryptop.CONFIG = self.CONFIG
        curses = Mock()
        curses.color_pair = MagicMock(return_value=None)
        cryptop.curses = curses
        stdscr = Mock()
        stdscr.addnstr = MagicMock(return_value=None)
        wallet = {'BTC': '100'}
        cryptop.write_scr(stdscr, wallet, 1920, 1080)

    def test_str_formatter(self):
        cryptop.CONFIG = self.CONFIG
        cryptop.XE = '#'
        out = cryptop.str_formatter('BTC', [1, 3.2, 2.3], 6)
        print (out)
