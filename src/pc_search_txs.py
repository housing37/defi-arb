from web3 import Web3
import json, os, pprint
from attributedict.collections import AttributeDict # tx_receipt requirement
from read_env import read_env
try:
    #ref: https://github.com/sloria/read_env
    #ref: https://github.com/sloria/read_env/blob/master/read_env.py
    read_env() # recursively traverses up dir tree looking for '.env' file
except:
    print("#==========================#")
    print(" ERROR: no .env files found ")
    print("#==========================#")

# infura support
#ETH_MAIN_RPC_KEY = os.environ['ETH_MAIN_INFURA_KEY_0']
ETH_MAIN_RPC_KEY = os.environ['ETH_MAIN_INFURA_KEY_1']
local_test = 'http://localhost:8545'
eth_main = f'https://mainnet.infura.io/v3/{ETH_MAIN_RPC_KEY}'
eth_test = f'https://goerli.infura.io/v3/'
pc_main = f'https://rpc.pulsechain.com'
eth_main_cid=1
pc_main_cid=369

# Global parameters
RPC_URL = pc_main
# START_BLOCK = 15_537_393  # pc system state snapshot blocknumber
START_BLOCK = 15_596_290  # pc system state snapshot blocknumber
# START_BLOCK = 19_836_385  # pc system state snapshot blocknumber
# START_BLOCK = 19_836_380  # pc system state snapshot blocknumber
# START_BLOCK = 17_238_152  # pc system state snapshot blocknumber

OA_addies = ["0x9Cd83BE15a79646A3D22B81fc8dDf7B7240a62cB", "0x075e72a5edf65f0a5f44699c7654c1a76941ddc8"]  # $PLS sac, $PLSX sac
SECOND_CONTRACT = "0x6B175474E89094C44Da98b954EedeAC495271d0F"  # Set to None if not filtering by a second contract
CHAIN_ID = pc_main_cid

# Initialize Web3
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Verify the chain ID
node_chain_id = w3.eth.chain_id
if node_chain_id != CHAIN_ID:
    print(f"Warning: Connected to chain ID {node_chain_id}, but expected {CHAIN_ID}.")
    exit(1)

if not w3.is_connected():
    print("Failed to connect to the Ethereum node.")
    exit(1)

# Function to fetch and filter transactions
def fetch_transactions():
    current_block = w3.eth.block_number
    print(f'\nSearching: {OA_addies}')
    print(f"\nProcessing block ...")
    for block_number in range(START_BLOCK, current_block + 1):
        # print_log += f'{block_number} '
        # print(f"Processing block {block_number}...")
        print(f'{block_number if block_number == START_BLOCK or block_number % 100 == 0 else "."}', end=' ', flush=True)

        block = w3.eth.get_block(block_number, full_transactions=True)

        found_tx = False
        for tx in block.transactions:
            # Check if OA_addies is involved
            if tx['from'] in OA_addies or (tx['to'] and tx['to'] in OA_addies):
                found_tx = True
                print(f"\n\nFOUND from: {tx['from']}")
                if tx['to']: print(f"        to: {tx['to']}")
                
                if tx['from'] == SECOND_CONTRACT or (tx['to'] and tx['to'] in SECOND_CONTRACT):
                    print(f"**FOUND from pDAI**: {tx['from']}")
                    if tx['to']: print(f"**        to pDAI**: {tx['to']}")
                # If SECOND_CONTRACT is specified, further filter
                # if SECOND_CONTRACT:
                #     receipt = w3.eth.get_transaction_receipt(tx['hash'])
                #     if SECOND_CONTRACT.lower() not in [log['address'].lower() for log in receipt['logs']]:
                #         continue

                # Print raw transaction in JSON format
                tx_receipt = AttributeDict(tx) # import required
                tx_json = json.loads(Web3.to_json(tx_receipt))
                tx_rc_print = pprint.PrettyPrinter(indent=4).pformat(tx_json)
                print(tx_rc_print + '\n')
        
        if found_tx:
            print(f"\nProcessing block ...")
            found_tx = False

if __name__ == "__main__":
    fetch_transactions()
