# Winner selection
The concept of blockchain is that everything can be verified by anyone, therefore we can't introduce any randomness in the blockchain. It's then common to use an oracle to provide random data but it's not yet implemented on Tezos so we had to solve the problem ourselves and came to this solution:
* A random integer of 5 bytes.
* Timestamp of Kaiko API request
* 24-hour XTZ/USDT volume of all exchanges tracked by Kaiko, including BeQuant + Bitfinex + BinanceUS + Bittrex + Coinbase + CEX.IO + Ethfinex + Gatecoin + Kraken
The salt is computed and hashed at the begining of each lottery round and is saved on the contract so everyone can verify that SmartLink didn't modify it to cheat. The timestamp of the API request is added with the XTZ-USD volume so that everyone can verify that the data used by SmartLink is legitimate.
Those 3 numbers are converted to bytes and concatenated in this order [Salt Timestamp Volume] and are then hashed with Blake2b hash function. This function is used a lot in the Tezos ecosystem (that's why we used this one). The hash gives us an hexadecimal number (base 16) so we convert it to decimal (base 10) and we apply it a modulo 500 so it gives us a number between 0 and 499 to select a winning ticket.

This script is used to compute the winning number. As soon as all the tickets are sold it will execute a transaction to select a winner and save the data used to select the winner on the contract.

# How to use the script
## Install python:
Set up a [python](https://www.python.org/downloads/) environment.

## Install the packages:
```bash
pip install pytezos requests hashlib
```
If you have errors when installing pytezos check their [quick start](https://pytezos.org/quick_start.html) page.

## Run the script:
```bash
python3 select_winner.py --api-key $KAIKO_API_KEY --private-key $PRIVATE_KEY
```
