# Hash verification:
This script can be used by anyone to verify that the hash sent to the selectWinner entrypoint corresponds to the data provided to the save_data entrypoint.
# How to use the script
## Install python:
Set up a [python](https://www.python.org/downloads/) environment.

## Install the packages:
```bash
pip install hashlib
```
## Run the script:
```bash
python3 select_winner.py -s $SALT -t $TIMESTAMP -v $VOLUME
```
You can find those values in the contract's [storage](https://tzkt.io/KT192nuuX8TLqsBK8XQo5e5uB2GLjLwNkoNy/storage/9315). <br></br>
Now just apply a modulo and you will have the winning ticket number.