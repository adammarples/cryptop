from unittest import TestCase
from unittest.mock import MagicMock, Mock
import locale

import cryptop.cryptop as cryptop

class TestIf_coin(TestCase):

    def test_if_coin(self):
        assert cryptop.if_coin('BTC', url='https://api.coinmarketcap.com/v1/ticker/')

    def test_get_price(self):
        coins = ['BTC', 'ETH', 'XRB']
        data = cryptop.get_price(coins, curr='USD')
        print (data)

    def test_write(self):
        side_effect = lambda x, y: {'dec_places': 2, 'field_length': 13}[x]
        theme = Mock()
        theme.getint = MagicMock(side_effect=side_effect)
        CONFIG = {'theme': theme, 'api': {'currency': 'USD'}}
        cryptop.CONFIG = CONFIG
        curses = Mock()
        curses.color_pair = MagicMock(return_value=None)
        cryptop.curses = curses
        stdscr = Mock()
        stdscr.addnstr = MagicMock(return_value=None)
        wallet = Mock()
        wallet.keys = MagicMock(return_value=['BTC', 'ETH', 'XRB'])
        wallet.values = MagicMock(return_value=[100, 200, 300])
        locale.setlocale(locale.LC_MONETARY, 'en_CA.UTF-8')
        cryptop.locale = locale
        cryptop.write_scr(stdscr, wallet, 1920, 1080)
