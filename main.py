import json
import sys
from web3.gas_strategies.rpc import rpc_gas_price_strategy
from web3 import Web3
from eth_account import Account
from web3.eth import Eth
from web3._utils.encoding import Web3JsonEncoder


SEPOLIA_ETH__RPC_NODE = "https://rpc.sepolia.org"
BINANCE_RPC_NODE = "https://data-seed-prebsc-1-s1.binance.org:8545"


RPC_NODE = BINANCE_RPC_NODE

w3 = Web3(Web3.HTTPProvider(RPC_NODE))
eth = Eth(w3)


def create_account():
    account = Account.create()
    print(
        f"Account address: {account.address} with private key: {account.key}")
    with open("accounts.txt", 'a') as f:
        f.write(f"{account.address},{account.key.hex()}\n")


def set_default_account(addr):
    eth.default_account = addr


def get_balance():
    account = eth.default_account
    if not account:
        account = input(
            "No default account found, please provide with an account address:\n")
    print(f"{'Valid' if w3.is_address(account) else 'Not valid'} ethereum address")
    balance_in_wei = eth.get_balance(account=account)
    balance_in_eth = w3.from_wei(balance_in_wei, 'ether')
    print(f"Account has {balance_in_eth} ethers")


def get_block_num():
    block_num = eth.get_block_number()
    print(block_num)


def get_gas_price():
    gas_price_wei = w3.eth.gas_price
    print(f"Gas price is {w3.from_wei(gas_price_wei, 'ether')} ether")


def get_gas_price_strategy():
    gas_price_wei = rpc_gas_price_strategy(w3)
    print(f"Gas price is {w3.from_wei(gas_price_wei, 'ether')} ether")


def send_transaction(recipient, ether):
    sender = eth.default_account
    if not sender:
        sender = str(input(
            "No default account found for sender, please provide with an account sender address:\n"))
    with open("accounts.txt", 'r') as f:
        data = f.readlines()
        for line in data:
            if line.split(',')[0] == sender:
                private_key = str(line.split(',')[1]).strip()
                break
    if not private_key:
        print("No private key found for sender, aborting..")
        return
    signed_txn = eth.account.sign_transaction(dict(
        nonce=w3.eth.get_transaction_count(sender),
        gas=100000,
        gasPrice=w3.eth.gas_price,
        to=recipient,
        value=w3.to_wei(ether, 'ether'),
        data=b'',
        chainId=eth.chain_id
    ),
        private_key
    )
    txn = eth.send_raw_transaction(signed_txn.rawTransaction)
    print(f"Transaction sent with ID {txn.hex()}")


def get_acc_txns_count():
    account = eth.default_account
    if not account:
        account = str(
            input("No default account found, please provide with an account address:\n"))
    txns_count = eth.get_transaction_count(account=account)
    print(f"Account {account} has {txns_count} transactions")


def get_block(block_id, full_transactions):
    block = eth.get_block(block_identifier=block_id,
                          full_transactions=full_transactions)
    print(json.dumps(block, cls=Web3JsonEncoder, indent=2))


def get_block_transactions_count(block_id):
    txns_count = eth.get_block_transaction_count(block_id)
    print(f"Block '{block_id}' includes {txns_count} transactions")


def print_menu():
    print(
        """
Menu selection
    1.  Create account
    2.  Set default account
    3.  Show account balance
    4.  Get block number
    5.  Get gas price
    6.  Get gas price strategy
    7.  Send transaction
    8.  Get account transactions count
    9.  Get block
    10. Get block transactions count
    11. Exit
"""
    )


print(
    f"Client is {'connected' if w3.is_connected() else 'not connected'} to RPC node {RPC_NODE}")
print(f"Current chain ID is: {eth.chain_id}")

print_menu()

selection = int(input())

while True:
    if selection == 1:
        create_account()
        print_menu()
    elif selection == 2:
        addr = str(input("Set default account:\n"))
        set_default_account(addr)
        print_menu()
    elif selection == 3:
        get_balance()
        print_menu()
    elif selection == 4:
        get_block_num()
        print_menu()
    elif selection == 5:
        get_gas_price()
        print_menu()
    elif selection == 6:
        get_gas_price_strategy()
        print_menu()
    elif selection == 7:
        recipient = str(input("Send to address:\n"))
        ether = float(input("Ether to send:\n"))
        send_transaction(recipient, ether)
        print_menu()
    elif selection == 8:
        get_acc_txns_count()
        print_menu()
    elif selection == 9:
        block_id = input(
            "Insert a block by integer or one of keywords latest/earliest/pending/safe/finalized\n")
        try:
            block_id = int(block_id)
        except:
            block_id = str(block_id)
        full_transactions = str(input("Include full transactions? y/n:\n"))
        if full_transactions in ['y', 'Y']:
            full_transactions = True
        else:
            full_transactions = False
        get_block(block_id, full_transactions)
        print_menu()
    elif selection == 10:
        block_id = input(
            "Insert a block by integer or one of keywords latest/earliest/pending/safe/finalized\n")
        try:
            block_id = int(block_id)
        except:
            block_id = str(block_id)
        get_block_transactions_count(block_id)
        print_menu()
    elif selection == 11:
        print("Exiting")
        sys.exit(0)
    else:
        print("Not supported option")
        print_menu()
    selection = int(input())
