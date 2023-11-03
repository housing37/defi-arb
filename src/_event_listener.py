''' house_102823
    ref: https://docs.balancer.fi/reference/contracts/apis/vault.html#flashloan
        flashLoan(
            IFlashLoanRecipient recipient,
            IERC20[] tokens,
            uint256[] amounts,
            bytes userData)

        emits FlashLoan(IFlashLoanRecipient indexed recipient,
                        IERC20 indexed token,
                        uint256 amount,
                        uint256 feeAmount)
'''
from web3 import Web3, HTTPProvider
from web3.contract import ConciseContract
import time
import env
#------------------------------------------------------------#
print('getting keys and setting globals ...')
## SETTINGS ##
abi_file = "../contracts/BalancerFLR.json"
bin_file = "../contracts/BalancerFLR.bin"

sel_chain = input('\nSelect chain:\n  0 = ethereum mainnet\n  1 = pulsechain mainnet\n  > ')
assert 0 <= int(sel_chain) <= 1, 'Invalid entry, abort'
(RPC_URL, CHAIN_ID) = (env.eth_main, env.eth_main_cid) if int(sel_chain) == 0 else (env.pc_main, env.pc_main_cid)

sel_send = input(f'\nSelect sender: (_event_listener: n/a)\n  0 = {env.sender_address_3}\n  1 = {env.sender_address_1}\n  > ')
assert 0 <= int(sel_send) <= 1, 'Invalid entry, abort'
(SENDER_ADDRESS, SENDER_SECRET) = (env.sender_address_3, env.sender_secret_3) if int(sel_send) == 0 else (env.sender_address_1, env.sender_secret_1)
#------------------------------------------------------------#
LST_CONTR_ARB_ADDR = [
    "0x59012124c297757639e4ab9b9e875ec80a5c51da", # deployed eth main 102823_1550
    "0x48af7d501bca526171b322ac2d8387a8cf085850", # deployed eth main 102823_2140
    "0x0B3f73687A5F78ACbdEccF860cEd0d8A5630F806", # deployed pc main 103023_2128
    "0xc2fa6dF341b18AE3c283CE3E7C0f1b4F5F6cabBb", # deployed pc main 110123_1953
    "0x42b2dDF6cd1C4c269785a228D40307a1e0441c77", # deployed pc main 110323_1649
    "0xF02e6E28E250073583766D77e161f67C21aEe388", # deployed pc main 110323_1715
]
print(f'\nSelect arbitrage contract to use:')
for i, v in enumerate(LST_CONTR_ARB_ADDR): print(' ',i, '=', v)
idx = input('  > ')
assert 0 <= int(idx) < len(LST_CONTR_ARB_ADDR), 'Invalid input, aborting...\n'
CONTR_ARB_ADDR = str(LST_CONTR_ARB_ADDR[int(idx)])
#------------------------------------------------------------#
print(f'''\nINITIALIZING web3 ...
    RPC: {RPC_URL}
    ChainID: {CHAIN_ID}
    SENDER: {SENDER_ADDRESS}
    ARB CONTRACT: {CONTR_ARB_ADDR}''')
W3 = Web3(HTTPProvider(RPC_URL))

print(f'\nreading abi file from contract {CONTR_ARB_ADDR} ...')
with open("../contracts/BalancerFLR.json", "r") as file: CONTR_ARB_ABI = file.read()
#------------------------------------------------------------#

# Create a contract instance
CONTR_ARB_ADDR = W3.to_checksum_address(CONTR_ARB_ADDR)
contract = W3.eth.contract(address=CONTR_ARB_ADDR, abi=CONTR_ARB_ABI)

def handle_event(event):
    c = event["args"]["contr"]
    s = event["args"]["sender"]
    m = event["args"]["message"]
    bnum = event["blockNumber"]
    print(f'\n[EVT] _ b|{bnum} _ ',"Contract: ", c, "Sender: ", s, "Msg: ", m)
#    print("Event received:")
#    print("Contract:", event["args"]["contr"])
#    print("Sender:", event["args"]["sender"])
#    print("Message:", event["args"]["message"])
#    print("Block Number:", event["blockNumber"])

# Set up an event filter
event_filter_0 = contract.events.logX.createFilter(fromBlock="latest")
event_filter_1 = contract.events.logMFL.createFilter(fromBlock="latest")
event_filter_2 = contract.events.logRFL.createFilter(fromBlock="latest")

# Listen for events
print(f'waiting for events from contract {CONTR_ARB_ADDR} ...')
while True:
    time.sleep(5) # wait 5 sec
    print('.', end=' ', flush=True)
    for event in event_filter_0.get_new_entries():
        handle_event(event)
    for event in event_filter_1.get_new_entries():
        handle_event(event)
    for event in event_filter_2.get_new_entries():
        handle_event(event)
#########

## Replace with the event signature (topic) of the event you want to listen for
#event_signature = W3.keccak(text="FlashLoan(IFlashLoanRecipient,IERC20,uint256,uint256)").hex()
#
## Create a function to handle the event
#def handle_event(event):
#    print("FlashLoan event received:")
#    print("Recipient:", event['args']['recipient'])
#    print("Token:", event['args']['token'])
#    print("Amount:", event['args']['amount'])
#    print("Fee Amount:", event['args']['feeAmount'])
#
## Set up the event filter
#event_filter = W3.eth.filter({'address': CONTR_ARB_ADDR, 'topics': [event_signature]})
#
#print('Started listening for events ... ')
#while True:
#    for event in event_filter.get_new_entries():
#        handle_event(event)


####

## Create a contract object
#contract = W3.eth.contract(address=CONTR_ARB_ADDR, abi=CONTR_ARB_ABI)
#
#def handle_event(event):
#    print("FlashLoan event received:")
#    print("Recipient:", event['args']['recipient'])
#    print("Token:", event['args']['token'])
#    print("Amount:", event['args']['amount'])
#    print("Fee Amount:", event['args']['feeAmount'])
#
## Define the event filter
#event_filter = contract.events.FlashLoan.createFilter(fromBlock="latest")
#
## Start listening for events
#while True:
#    for event in event_filter.get_new_entries():
#        handle_event(event)
