cryptop
=======
cryptop is a lightweight command line based cryptocurrency portfolio.
Built on Python 3 and ncurses with simplicity in mind, cryptop updates in realtime.

.. image:: img\cryptop.png

I forked this repo from https://github.com/huwwp/cryptop in order to change a few things.

The cryptocompare api was not updating the price of the most superior of all cryptocurrencies, Raiblocks (XRB)
so i have changed the API to coinmarketcap.

This API doesn't provide price HI/LOW so I have also changed the outputs to 1HR change and 24HR, which I prefer.

I have also added the functionality to read your wallet.json from a github gist (or any enpoint which delivers json)
by updating the wallet > web setting in the config.ini.

A note: github gists send text, save your gist without an extension and with no spaces in the raw text, an example gist
is provided with 1 BTC as an example.

Installation
------------

cryptop requires Python 3 to run, and has only been tested in Python 3.6 so far.

This fork of cryptop is not on pip yet, it can be installed manually, download the repo and run

.. code:: bash

    sudo python setup.py install

or

.. code:: bash

    pip install git+https://github.com/adammarples/cryptop.git


pip and setup.py can be run with a --user flag if you would prefer not to sudo. Both require setuptools which is included in most python installs and many distros by default

Windows doesn't have curses installed so download the .whl for your version and install it with pip

https://www.lfd.uci.edu/~gohlke/pythonlibs/#curses

Usage
-----

Start from a terminal.

.. code:: bash

    cryptop

Follow the on screen instructions to add/remove cryptocurrencies from your portfolio.

Customisation
-------------

Cryptop creates two config files in a .cryptop folder in your home directory.

.crypto/config.ini contains theme configuration (text/background colors) and
options to change the output currency (default USD), update frequency, number of decimal places to display and maximum width for float values.

.cryptop/wallet.json contains the coins and amounts you hold, you shouldn't need to edit it manually

adding a github gist json file under [wallet] web= in the config will allow you to read your wallet from a gist json
now you can update your wallet.json without the application!

This gist will not be possible to update however in the cryptop terminal.

Credits
-------

Uses the coinmarketcap.com API

Tipjar
------

BTC: 15wNW29q7XAEbC8yus49CWvt91JkhcdkoW  <- original dev's wallet

XRB: xrb_1pgig4p4wp9ykuz3soxnarfzpjardpampjb3ihrsrftumfmfbiwiuxkhzm59 <- my raiblocks wallet

Disclaimer
----------

I am not liable for the accuracy of this program’s output nor actions
performed based upon it.
