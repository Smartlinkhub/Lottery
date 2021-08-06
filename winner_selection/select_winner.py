from pytezos import *
from time import sleep
import requests
from hashlib import blake2b
import argparse
import json
from os import urandom

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--private-key', help="Admin's private key")
parser.add_argument('-a', '--api-key', help="Kaiko api key")
args = parser.parse_args()

admin = pytezos.using(shell='https://rpc.mainnet.tzstats.com',
                      key=args.private_key)
contract = admin.contract("KT192nuuX8TLqsBK8XQo5e5uB2GLjLwNkoNy") #contract address
salt = urandom(5)
tx3 = admin.bulk(contract.save_hashed_salt(blake2b(salt).digest())).autofill().sign().inject(_async=False)

while True:
    try:
        if int(contract.storage['id']()) == 500:
            try:
                res = requests.get(
                    url="https://us.market-api.kaiko.io/v2/data/trades.v1/spot_direct_exchange_rate/xtz/usd?include_exchanges=*&sources=true",
                    headers={
                        "X-Api-Key": args.api_key
                    }).json()
                res['timestamp'] /= 1000
                vol, timestamp = int(float(res['data'][0]['volume']) * 10 ** 8).to_bytes(byteorder="big", length=10), int(
                    res['timestamp']).to_bytes(length=10, byteorder="big")
                winner = int(blake2b(salt + timestamp + vol).hexdigest(), 16)
                tx = admin.bulk(contract.selectWinner(winner)).autofill().sign().inject(_async=False)
                tx["salt"] = int.from_bytes(salt, byteorder="big")
                with open("../history/winner_history.json", "a") as f:
                    json.dump(tx, f)
                    f.close()
                winner_data = {
                                'time': timestamp,
                                'volume': vol,
                                'salt': salt
                            }
                sleep(60)
                tx2 = admin.bulk(contract.save_data(winner_data)).autofill().sign().inject(_async=False)
                sleep(60)
                salt = urandom(5)
                tx3 = admin.bulk(contract.save_hashed_salt(blake2b(salt).digest())).autofill().sign().inject(_async=False)
                sleep(120)
            except Exception as e:
                print(str(e))
    except Exception as e:
                print(str(e))
    sleep(1)
