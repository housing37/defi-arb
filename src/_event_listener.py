
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
eth_main = f'https://mainnet.infura.io/v3/{env.ETH_MAIN_RPC_KEY}'
RPC_URL = eth_main
W3 = Web3(HTTPProvider(RPC_URL))
#CONTR_ARB_ADDR = "0x59012124c297757639e4ab9b9e875ec80a5c51da" # deployed eth main 102823_1550
CONTR_ARB_ADDR = "0x48af7d501bca526171b322ac2d8387a8cf085850" # deployed eth main 102823_2140
print(f'reading contract abi file: {CONTR_ARB_ADDR} ...')
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
print(f'waiting for events from contract: {CONTR_ARB_ADDR} ...')
while True:
    time.sleep(5) # wait 1 sec
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
