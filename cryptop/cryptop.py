import curses
import os
import sys
import re
import shutil
import configparser
import json
import pkg_resources
import locale

import requests
import requests_cache

from forex_python.converter import CurrencyRates

# GLOBALS!
BASEDIR = os.path.join(os.path.expanduser('~'), '.cryptop')
CONFFILE = os.path.join(BASEDIR, 'config.ini')
CONFIG = configparser.ConfigParser()
DATAFILE = os.path.join(BASEDIR, 'wallet.json')

COIN_FORMAT = re.compile('[A-Z]{2,5},\d{0,}\.?\d{0,}')

SORT_FNS = {
    'coin' : lambda item: item[0],
    'price': lambda item: float(item[1][0]),
    'held' : lambda item: float(item[2]),
    'val'  : lambda item: float(item[1][0]) * float(item[2])
}
SORTS = list(SORT_FNS.keys())
COLUMN = SORTS.index('val')
ORDER = True

KEY_ESCAPE = 27
KEY_ZERO = 48
KEY_A = 65
KEY_Q = 81
KEY_R = 82
KEY_S = 83
KEY_C = 67
KEY_a = 97
KEY_q = 113
KEY_r = 114
KEY_s = 115
KEY_c = 99

def read_configuration(confpath):
    """Read the configuration file at given path."""
    # copy our default config file
    if not os.path.isfile(confpath):
        defaultconf = pkg_resources.resource_filename(__name__, 'config.ini')
        shutil.copyfile(defaultconf, CONFFILE)

    CONFIG.read(confpath)
    return CONFIG


def if_coin(coin, url='https://api.coinmarketcap.com/v1/ticker/'):
    '''Check if coin exists'''
    data = requests.get(url).json()
    return coin in [x['symbol'] for x in data]


def get_price(coins, curr=None, url='https://api.coinmarketcap.com/v1/ticker/'):
    """
    get the price data

    api returns list of dicts for all coins like

    [
        {
            "id": "bitcoin",
            "name": "Bitcoin",
            "symbol": "BTC",
            "rank": "1",
            "price_usd": "14751.6",
            "price_btc": "1.0",
            "24h_volume_usd": "21974500000.0",
            "market_cap_usd": "246760708110",
            "available_supply": "16727725.0",
            "total_supply": "16727725.0",
            "max_supply": "21000000.0",
            "percent_change_1h": "-6.49",
            "percent_change_24h": "-3.45",
            "percent_change_7d": "43.54",
            "last_updated": "1512733154"
        },

        {...},

    ]


    :param coins: str, len 3 ISO symbol ie. 'BTC'
    :param curr: str, len 3 ISO symbol ie. 'USD'
    :param url: str, API request url
    :return: list of price in curr, hi, lo for coin in coins

    """
    try:
        r = requests.get(url)
        data = r.json()
    except requests.exceptions.RequestException:
        sys.exit('Could not complete request')

    curr = curr or CONFIG['api'].get('currency', 'USD').upper()

    coin_data = []
    for coin in coins:
        for dic in data:
            if dic['symbol'] == coin:
                dic = build_currency(dic, curr)
                coin_data.append(dic)

    coin_data_list = [
        (
            coin['price'][curr],
            float(coin['percent_change_1h']),
            float(coin['percent_change_24h']),
        ) for coin in coin_data
    ]

    return coin_data_list



def build_currency(dic, curr):
    """make a sub-dict with price conversions"""
    usd = float(dic.pop('price_usd'))
    dic['price'] = {
        'USD': usd,
        curr: convert_currency(usd, curr),
    }
    return dic

def convert_currency(usd, curr):
    if curr == 'USD':
        return usd
    return usd * CurrencyRates().get_rates('USD')[curr]


def get_theme_colors():
    ''' Returns curses colors according to the config'''
    def get_curses_color(name_or_value):
        try:
            return getattr(curses, 'COLOR_' + name_or_value.upper())
        except AttributeError:
            return int(name_or_value)

    theme_config = CONFIG['theme']
    return (get_curses_color(theme_config.get('text', 'yellow')),
        get_curses_color(theme_config.get('banner', 'yellow')),
        get_curses_color(theme_config.get('banner_text', 'black')),
        get_curses_color(theme_config.get('background', -1)))


def conf_scr():
    '''Configure the screen and colors/etc'''
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    text, banner, banner_text, background = get_theme_colors()
    curses.init_pair(2, text, background)
    curses.init_pair(3, banner_text, banner)
    curses.halfdelay(10)

def str_formatter(coin, val, held):
    '''Prepare the coin strings as per ini length/decimal place values'''
    max_length = CONFIG['theme'].getint('field_length', 13)
    dec_place = CONFIG['theme'].getint('dec_places', 2)
    avg_length = CONFIG['theme'].getint('dec_places', 2) + 10
    held_str = '{:>{},.8f}'.format(float(held), max_length)
    val_str = '{:>{},.{}f}'.format(float(held) * val[0], max_length, dec_place)
    return '  {:<5} {:>{}}  {} {:>{}} {:>{}} {:>{}}'.format(coin,
        locale.currency(val[0], grouping=True)[:max_length], avg_length,
        held_str[:max_length],
        locale.currency(float(held) * val[0], grouping=True)[:max_length], avg_length,
        # locale.currency(val[1], grouping=True)[:max_length], avg_length,
        # locale.currency(val[2], grouping=True)[:max_length], avg_length,
        str(val[1])+'%', avg_length,
        str(val[2]) + '%', avg_length,
    )

def write_scr(stdscr, wallet, y, x):
    '''Write text and formatting to screen'''
    pad1 = '{:>{}}'.format('', CONFIG['theme'].getint('dec_places', 2) + 10 - 3)
    pad2 = ' ' * (CONFIG['theme'].getint('field_length', 13) - 2)
    pad3 =  ' ' * (CONFIG['theme'].getint('field_length', 13) - 3)
    pad4 = ' ' * (CONFIG['theme'].getint('field_length', 13) - 6)
    pad5 = ' ' * (CONFIG['theme'].getint('field_length', 13) - 6)

    if y >= 1:
        stdscr.addnstr(0, 0, 'cryptop v0.2.0', x, curses.color_pair(2))
    if y >= 2:
        header = '  COIN{}PRICE{}HELD {}VAL{}1 HR {}24 HR %  '.format(pad1, pad2, pad3, pad4, pad5)
        stdscr.addnstr(1, 0, header, x, curses.color_pair(3))

    total = 0
    coinl = list(wallet.keys())
    heldl = list(wallet.values())
    if coinl:
        coinvl = get_price(coinl)

        if y > 3:
            s = sorted(list(zip(coinl, coinvl, heldl)), key=SORT_FNS[SORTS[COLUMN]], reverse=ORDER)
            coinl = list(x[0] for x in s)
            coinvl = list(x[1] for x in s)
            heldl = list(x[2] for x in s)
            print (coinl, coinvl, heldl)
            for coin, val, held in zip(coinl, coinvl, heldl):
                print (coin, val, held)
                if coinl.index(coin) + 2 < y:
                    stdscr.addnstr(coinl.index(coin) + 2, 0,
                    str_formatter(coin, val, held), x, curses.color_pair(2))
                total += float(held) * val[0]



    if y > len(coinl) + 3:
        stdscr.addnstr(y - 2, 0, 'Total Holdings: {:10}    '
            .format(locale.currency(total, grouping=True)), x, curses.color_pair(3))
        stdscr.addnstr(y - 1, 0,
            '[A] Add/update coin [R] Remove coin [S] Sort [C] Cycle sort [0\Q]Exit', x,
            curses.color_pair(2))


def read_wallet():
    ''' Reads the wallet data from its json file '''
    if WEBWALLET:
        wallet_json = requests.get(WEBWALLET).json()
        print (wallet_json)

        return wallet_json

    try:
        with open(DATAFILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        # missing or malformed wallet
        write_wallet({})
        return {}


def write_wallet(wallet):
    ''' Write wallet data to its json file '''
    if WEBWALLET:
        return
    with open(DATAFILE, 'w') as f:
        json.dump(wallet, f)


def get_string(stdscr, prompt):
    '''Requests and string from the user'''
    curses.echo()
    stdscr.clear()
    stdscr.addnstr(0, 0, prompt, -1, curses.color_pair(2))
    curses.curs_set(1)
    stdscr.refresh()
    in_str = stdscr.getstr(1, 0, 20).decode()
    curses.noecho()
    curses.curs_set(0)
    stdscr.clear()
    curses.halfdelay(10)
    return in_str


def add_coin(coin_amount, wallet):
    ''' Add a coin and its amount to the wallet '''
    coin_amount = coin_amount.upper()
    if not COIN_FORMAT.match(coin_amount):
        return wallet

    coin, amount = coin_amount.split(',')

    if not if_coin(coin):
        return wallet

    if not amount:
        amount = "0"

    wallet[coin] = amount
    return wallet


def remove_coin(coin, wallet):
    ''' Remove a coin and its amount from the wallet '''
    # coin = '' if window is resized while waiting for string
    if coin:
        coin = coin.upper()
        wallet.pop(coin, None)
    return wallet

def mainc(stdscr):
    inp = 0
    wallet = read_wallet()
    y, x = stdscr.getmaxyx()
    conf_scr()
    stdscr.bkgd(' ', curses.color_pair(2))
    stdscr.clear()
    #stdscr.nodelay(1)
    # while inp != 48 and inp != 27 and inp != 81 and inp != 113:
    while inp not in {KEY_ZERO, KEY_ESCAPE, KEY_Q, KEY_q}:
        while True:
            try:
                write_scr(stdscr, wallet, y, x)
            except curses.error:
                pass

            inp = stdscr.getch()
            if inp != curses.KEY_RESIZE:
                break
            stdscr.erase()
            y, x = stdscr.getmaxyx()

        if inp in {KEY_a, KEY_A}:
            if y > 2:
                data = get_string(stdscr,
                    'Enter in format Symbol,Amount e.g. BTC,10')
                wallet = add_coin(data, wallet)
                write_wallet(wallet)

        if inp in {KEY_r, KEY_R}:
            if y > 2:
                data = get_string(stdscr,
                    'Enter the symbol of coin to be removed, e.g. BTC')
                wallet = remove_coin(data, wallet)
                write_wallet(wallet)

        if inp in {KEY_s, KEY_S}:
            if y > 2:
                global ORDER
                ORDER = not ORDER

        if inp in {KEY_c, KEY_C}:
            if y > 2:
                global COLUMN
                COLUMN = (COLUMN + 1) % len(SORTS)

def main():

    if os.path.isfile(BASEDIR):
        sys.exit('Please remove your old configuration file at {}'.format(BASEDIR))
    os.makedirs(BASEDIR, exist_ok=True)

    global CONFIG
    global WEBWALLET
    CONFIG = read_configuration(CONFFILE)
    WEBWALLET = CONFIG['wallet'].get('web', None)
    locale.setlocale(locale.LC_MONETARY, CONFIG['locale'].get('monetary', ''))

    requests_cache.install_cache(cache_name='api_cache', backend='memory',
        expire_after=int(CONFIG['api'].get('cache', 10)))

    curses.wrapper(mainc)


if __name__ == "__main__":
    main()
