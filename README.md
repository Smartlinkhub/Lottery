[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Discord][discord-shield]][discord-url]
[![Telegram][telegram-shield]][telegram-url]
[![LinkedIn][linkedin-shield]][linkedin-url]
[![Twitter][twitter-shield]][twitter-url]
[![Reddit][reddit-shield]][reddit-url]
<img width="700" alt="portfolio_view" src="https://gateway.pinata.cloud/ipfs/QmPUSnYbmWqueYbwaVdhgyim9Kfsq2MjwE7hNqdzq6RR2v">

# Smartlink <a name="Smartlink"></a>
Smartlink addresses one of the biggest challenges in the global marketplace: ‘Need to Trust,’ by introducing decentralized escrow services and payments processing based on Tezos' institutional-grade smart contracts that suppress the need for buyers and sellers to trust each other.

Smartlink aims to provide a user-centered escrow solution to secure online and face-to-face transactions while broadening payments acceptance options through integrated cryptocurrencies.

Smartlink proposes a new method to initiate commercial transactions by offering Trust-As-A-Service to incentivize commitment and eliminate the trust deficit in the global marketplace.

# 🎱 Lottery

This lottery contract is quite simple and can be modified easily to change the lottery parameters (ticket price, winning prize and number of tickets / round).
- [Smartlink <a name="Smartlink"></a>](#smartlink-)
- [🎱 Lottery](#-lottery)
  - [Variables <a name="VariablesLottery"></a>](#variables-)
    - [buyTicket: <a name="buyTicket"></a>](#buyticket-)
    - [selectWinner: <a name="selectWinner"></a>](#selectwinner-)
    - [resetLottery: <a name="resetLottery"></a>](#resetlottery-)
    - [save_data: <a name="save_data"></a>](#save_data-)
    - [save_hashed_salt: <a name="save_hashed_salt"></a>](#save_hashed_salt-)
    - [pause: <a name="pause"></a>](#pause-)

## Variables <a name="VariablesLottery"></a>
|              Name |                                       Type                                        | Description                                                                              |
| ----------------: | :-------------------------------------------------------------------------------: | :--------------------------------------------------------------------------------------- |
|             admin |                                     TAddress                                      | Address of the admin                                                                     |
| FA12TokenContract |                                     TAddress                                      | Address of the token contract                                                            |
|      hashed_salts |                              TBig_map(TNat, TBytes)                               | Mapping of the round number to the hashed salt used to compute the random winning number |
|                id |                                       TNat                                        | Number of the current ticket to be sold                                                  |
|             limit |                                       TNat                                        | Maximum number of tickets sold before picking a winner                                   |
|  previous_winners |             TBig_map(TNat, TRecord(winner : TAddress, ticket : TNat))             | Mapping of the round to the winner and his ticket number                                 |
|            paused |                                       TBool                                       | Bool to pause the contract                                                               |
|             price |                                       TNat                                        | Price of a ticket                                                                        |
|           reserve |                                     TAddress                                      | Address of the token reserve to pay the lottery winners                                  |
|         round_num |                                       TNat                                        | Current round number                                                                     |
|           tickets |                             TBig_map(TNat, TAddress)                              | Mapping of the ticket number to the address of its owner                                 |
|          user_map |                          TMap(TAddress, TList(sp.TNat))                           | Mapping of every user for this round and all his tickets                                 |
|      winning_data | TBig_map(TNat,sp.TRecord(time = sp.TBytes, volume = sp.TBytes, salt = sp.TBytes)) | Mapping of the round number and the data used to compute the random winning number       |
|     winning_price |                                       TNat                                        | Amount of SMAK to be won                                                                 |


### buyTicket: <a name="buyTicket"></a>
```python
@sp.entry_point
def buyTicket(self, params):
    sp.set_type(params, sp.TNat)
```
Function that will sell the number of tickets entered as a parameter to a user.

### selectWinner: <a name="selectWinner"></a>
```python
@sp.entry_point
def selectWinner(self, params):
    sp.verify(~self.data.paused, Error.Paused)
    sp.verify(sp.sender == self.data.admin, Error.AccessDenied)
    sp.verify(self.data.id == self.data.limit, Error.TicketsRemaining)
    sp.set_type(params, sp.TNat)
```
Function that will select a winner with the number given by the admin. Only the admin can call this function and this function can only be called when all tickets are sold. More information  is provided on the random number selection.

### resetLottery: <a name="resetLottery"></a>
```python
def resetLottery(self):
    self.data.id = sp.nat(0)
    sp.for i in sp.range(0, self.data.limit):
        del self.data.tickets[i]
```
Function that will delete all the tickets.

### save_data: <a name="save_data"></a>
```python
@sp.entry_point
def save_data(self, params):
    sp.verify(~self.data.paused, Error.Paused)
    sp.verify(sp.sender == self.data.admin, Error.AccessDenied)
    sp.set_type(params, win_data)
```
Function that will save the data used for computing the random number. Only the admin can call this function and this function.

### save_hashed_salt: <a name="save_hashed_salt"></a>
```python
@sp.entry_point
def save_hashed_salt(self, params):
    sp.verify(~self.data.paused, Error.Paused)
    sp.verify(sp.sender == self.data.admin, Error.AccessDenied)
    sp.set_type(params, sp.TBytes)
    self.data.hashed_salts[self.data.round_num] = params
```
Function that will save the hashed salt that will be used to compute the random number. Only the admin can call this function.

### pause: <a name="pause"></a>
```python
@sp.entry_point
def pause(self, params):
    sp.set_type(params, sp.TUnit)
    sp.verify(sp.sender == self.data.admin, Error.AccessDenied)
    self.data.paused = sp.bool(True) 
```
Function that will pause the contract. Only the admin can call this function.


[contributors-shield]: https://img.shields.io/github/contributors/Smartlinkhub/SMAK-Staking.svg?style=for-the-badge
[contributors-url]: https://github.com/Smartlinkhub/SMAK-Staking/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/Smartlinkhub/SMAK-Staking.svg?style=for-the-badge
[forks-url]: https://github.com/Smartlinkhub/SMAK-Staking/network/members
[telegram-url]: https://t.me/smartlinkofficial
[telegram-shield]: https://img.shields.io/badge/-Telegram-black.svg?style=for-the-badge&logo=Telegram&colorB=555
[linkedin-url]: https://www.linkedin.com/company/smartlinkso
[linkedin-shield]: https://img.shields.io/badge/-Linkedin-black.svg?style=for-the-badge&logo=Linkedin&colorB=555
[discord-shield]: https://img.shields.io/badge/-Discord-black.svg?style=for-the-badge&logo=discord&colorB=555
[discord-url]:https://discord.gg/Rut5xxqGWQ
[twitter-shield]: https://img.shields.io/badge/-Twitter-black.svg?style=for-the-badge&logo=twitter&colorB=555
[twitter-url]:https://twitter.com/smartlinkHQ
[reddit-shield]: https://img.shields.io/badge/-reddit-black.svg?style=for-the-badge&logo=reddit&colorB=555
[reddit-url]:https://www.reddit.com/user/Teamsmartlink/
