import smartpy as sp

class Error:
    NotEnoughTickets    = "Not enough remaining ticket. Please check the number of remaining tickets"
    Paused              = "Contract is paused please use the new contract"
    Null                = "You must buy at least 1 ticket"
    AccessDenied        = "You must be admin"
    TicketsRemaining    = "Not all tickets are sold"



def call(c, x):
    sp.transfer(x, sp.mutez(0), c)

win_data = sp.TRecord(time = sp.TBytes, volume = sp.TBytes, salt = sp.TBytes)

class Lottery(sp.Contract):
    def __init__(self,contract, reserve, admin, metadata_url):
            self.init(
            FA12TokenContract = contract,
            reserve = reserve,
            limit = sp.nat(500),
            tickets = sp.map(tkey = sp.TNat, tvalue = sp.TAddress),
            id = sp.nat(0),
            previous_winners = sp.big_map(tkey = sp.TNat, tvalue = sp.TRecord(winner = sp.TAddress, ticket = sp.TNat, users = sp.TNat)),
            price = sp.nat(1_000_000),
            winning_price = sp.nat(490_000_000),
            user_map = sp.map(tkey = sp.TAddress, tvalue = sp.TList(sp.TNat)),
            round_num = sp.nat(1),
            winning_data = sp.big_map(tkey = sp.TNat, tvalue = win_data),
            hashed_salts = sp.big_map(tkey = sp.TNat, tvalue = sp.TBytes),
            admin = admin,
            paused = sp.bool(False),
            metadata = sp.big_map({"":metadata_url})
        )

    # The function will enable users to buy tickets for the lottery
    # The function takes as parameters:
    # - the number of tickets the user wants to buy
    @sp.entry_point
    def buyTicket(self, params):
        sp.set_type(params, sp.TNat)
        sp.verify(~self.data.paused, Error.Paused)
        sp.verify(params != 0, Error.Null)
        sp.verify(params + self.data.id <= self.data.limit, Error.NotEnoughTickets)
        
        sp.for i in sp.range(0, params):
            self.data.tickets[self.data.id] = sp.sender
            sp.if ~self.data.user_map.contains(sp.sender):
                self.data.user_map[sp.sender] = sp.list([self.data.id])
            sp.else:
                self.data.user_map[sp.sender].push(self.data.id)
            self.data.id += 1

        price = params * self.data.price
        
        paramTrans = sp.TRecord(from_ = sp.TAddress, to_ = sp.TAddress, value = sp.TNat).layout(("from_ as from", ("to_ as to", "value")))
        paramCall = sp.record(from_=sp.sender, to_=self.data.reserve, value = price)
        call(sp.contract(paramTrans, self.data.FA12TokenContract, entry_point = "transfer").open_some(), paramCall)        
    
    # The function will enable the admin to select a winner
    # The function takes as parameters:
    # - the random winning number
    @sp.entry_point
    def selectWinner(self, params):
        sp.verify(~self.data.paused, Error.Paused)
        sp.verify(sp.sender == self.data.admin, Error.AccessDenied)
        sp.verify(self.data.id == self.data.limit, Error.TicketsRemaining)
        sp.set_type(params, sp.TNat)

        params = params % self.data.limit
        winner = self.data.tickets[params]
        self.data.previous_winners[self.data.round_num] = sp.record(winner = winner, ticket = params, users = sp.len(self.data.user_map))
        self.data.round_num += 1

        paramTrans = sp.TRecord(from_ = sp.TAddress, to_ = sp.TAddress, value = sp.TNat).layout(("from_ as from", ("to_ as to", "value")))
        paramCall = sp.record(from_=self.data.reserve, to_ = winner, value = self.data.winning_price)
        call(sp.contract(paramTrans, self.data.FA12TokenContract, entry_point="transfer").open_some(), paramCall)

        self.resetLottery()

    # The function will reset the lottery
    def resetLottery(self):
        self.data.id = sp.nat(0)
        sp.for i in sp.range(0, self.data.limit):
            del self.data.user_map[self.data.tickets[i]]
            del self.data.tickets[i]

    # The function will enable the admin to save the data used to select a winner
    # The function takes as parameters:
    # - the volume of XTZ/USD on BeQuant + Bitfinex + BinanceUS + Bittrex + Coinbase + CEX.IO + Ethfinex + Gatecoin + Kraken
    @sp.entry_point
    def save_data(self, params):
        sp.verify(~self.data.paused, Error.Paused)
        sp.verify(sp.sender == self.data.admin, Error.AccessDenied)
        sp.set_type(params, win_data)
        self.data.winning_data[sp.as_nat(self.data.round_num - 1)] = params

    # The function will enable the admin to save the hashed salt at the begining of the lottery round
    # The function takes as parameters:
    # - the hashed salt the will be used to get the random number
    @sp.entry_point
    def save_hashed_salt(self, params):
        sp.verify(~self.data.paused, Error.Paused)
        sp.verify(sp.sender == self.data.admin, Error.AccessDenied)
        sp.set_type(params, sp.TBytes)
        self.data.hashed_salts[self.data.round_num] = params


    # The function will pause the contract
    @sp.entry_point
    def pause(self, params):
        sp.verify(~self.data.paused, Error.Paused)
        sp.set_type(params, sp.TUnit)
        sp.verify(sp.sender == self.data.admin, Error.AccessDenied)
        self.data.paused = sp.bool(True)  
            
@sp.add_test(name = "SMAK Lottery Test")
def test():
    scenario = sp.test_scenario()
    scenario.h1("SMAK Lottery tests")
    scenario.table_of_contents()

    alice = sp.test_account('Alice')
    bob = sp.test_account('Bob')
    charles = sp.test_account('Charles')
    dan = sp.test_account('Danny')
    oscar = sp.test_account('Oscar')
    reserve = sp.test_account("Reserve")
    metadata_url = sp.utils.bytes_of_string("ipfs://Qmd24eKvMaYzBxbKEH6kr6nnnHMCCchntVprK3NJJfVvky")
    contract = sp.address("KT1RneNUEvpwyJoXYKmWPwBzNN1cSujYdgU8")
    scenario.h1("Accounts")
    scenario.show([alice, bob, charles, dan, reserve, oscar])
    
    scenario.h1("Initialize the contract")
    c = Lottery(admin = alice.address, contract = contract, reserve = reserve.address, metadata_url = metadata_url)
    scenario += c

    scenario.h1("Tests")

    scenario.h2("Admin saves the salt that will be used to select the winner")
    scenario += c.save_hashed_salt(sp.bytes("0xAA")).run(sender = alice)

    scenario.h2("Bob tries to save the salt that will be used to select the winner but he is not admin then he fails")
    scenario += c.save_hashed_salt(sp.bytes("0xAA")).run(sender = bob, valid = False, exception = Error.AccessDenied)

    scenario.h2("Several users are buying tickets everything works")
    scenario += c.buyTicket(100).run(sender = alice)
    scenario += c.buyTicket(100).run(sender = bob)
    scenario += c.buyTicket(80).run(sender = charles)
    scenario += c.buyTicket(40).run(sender = dan)
    scenario += c.buyTicket(80).run(sender = oscar)
    scenario += c.buyTicket(50).run(sender = alice)

    scenario.h2("Reserve tries to buy more tickets than remaining so it fails") 
    scenario += c.buyTicket(600).run(sender = reserve, valid = False, exception = Error.NotEnoughTickets)

    scenario.h2("Reserve tries to buy the good amount of tickets ")
    scenario += c.buyTicket(50).run(sender = reserve)

    scenario.h2("Admin picks the winner")
    scenario += c.selectWinner(sp.nat(3290)).run(sender = alice)

    scenario.h2("Admin saves the data used to select winner on chain")
    scenario += c.save_data(sp.record(time = sp.bytes("0xAA"), volume = sp.bytes("0xAA"), salt = sp.bytes("0xAA"))).run(sender = alice)

    scenario.h2("Bob saves the data used to select winner on chain, he is not amdin so it fails")
    scenario += c.save_data(sp.record(time = sp.bytes("0xAA"), volume = sp.bytes("0xAA"), salt = sp.bytes("0xAA"))).run(sender = bob, valid = False, exception = Error.AccessDenied)

    scenario.h2("Alice buys a ticket from the new lottery and it works")
    scenario += c.buyTicket(1).run(sender = alice)

    scenario.h2("Dan tries to buy 0 ticket but fails")
    scenario += c.buyTicket(0).run(sender = dan, valid = False, exception = Error.Null)

    scenario.h2("Oscar tries to buy 11000 tickets but fails")
    scenario += c.buyTicket(11000).run(sender = oscar, valid = False, exception = Error.NotEnoughTickets)

    scenario.h2("Bob tries to pause the contract but he is not admin so it fails")
    scenario += c.pause().run(sender = bob, valid = False, exception = Error.AccessDenied)

    scenario.h2("Alice pauses the contract, she is admin so it works")
    scenario += c.pause().run(sender = alice)

    scenario.h2("Alice tries to buy tickets but the contract is paused so it fails")
    scenario += c.buyTicket(1).run(sender = alice, valid = False, exception = Error.Paused)
    