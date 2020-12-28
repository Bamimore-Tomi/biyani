from tronapi import Tron

full_node = "https://api.trongrid.io"
solidity_node = "https://api.trongrid.io"
event_server = "https://api.trongrid.io"

tron = Tron(full_node=full_node, solidity_node=solidity_node,
            event_server=event_server)
tron.private_key = "a026abb9d693ff50765cb1026693f0176dfc3589acf2fe04610071311724d7bd"
#TUvZtUq6XysaSgHVMDKSZzLrXfhnTjM6d8
tron.default_address = tron.address.from_private_key(tron.private_key).base58
print(tron.default_address)
transaction = tron.trx.send("TP1UN7psZZMMoaAn2qGBS5yhjbbiT2jxtP", float(0.1))
print(transaction)

#['415402c6b3b0e86ea916976bbd34f3df2d3a6d57a8', '418f074aa4e11a23e0891f310221ab9dcc07ce467f', 
# '41f31ebc049808a7b8cc151218a33fe304873e92f1', '41ed54faac424b550731e41bd770d30daaeb5d9018']