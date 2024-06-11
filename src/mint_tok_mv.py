# house_091423
'''
    HOW-TO use this code from CLI (command line interface)
        1) install python3 on your system
            ref: https://letmegooglethat.com/?q=how+to+install+python3+on+my+system
        2) open up the CLI and install web3.py
            $ python3 -m pip install web3
        3) set variables below
            'sender_address' = the address of the wallet you are using (like in MM)
            'sender_secret'  = the private key of the wallet you are using (like in MM)
        4) run the script from CLI
            $ python3 mint_tok_mv.py
            
        short-hand:
            $ python3 -m pip install web3
            $ python3 mint_tok_mv.py
'''

__fname = 'mint_tok_mv'
__filename = __fname + '.py'
cStrDivider = '#================================================================#'
print('', cStrDivider, f'START _ {__filename}', cStrDivider, sep='\n')
print(f'GO {__filename} -> starting IMPORTs and globals decleration')

#------------------------------------------------------------#
#   IMPORTS                                                  #
#------------------------------------------------------------#
import sys
from datetime import datetime
from web3 import Web3
#import inspect # this_funcname = inspect.stack()[0].function

# support import from parent dir
#parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#sys.path.append(parent_dir) # add parent dir of this file to sys.path

#------------------------------------------------------------#
#   GLOBALS
#------------------------------------------------------------#
# contract address & sender keys
contract_address = '0xA1BEe1daE9Af77dAC73aA0459eD63b4D93fC6d29' # ᨓᨆ (ᨓᨆ)
sender_address = "0xYourSenderAddress"
sender_secret = "sender_address_private_key"

# function hex (decompiled) & contract ABI (re-compiled) from contract_address
#   byte-code: https://scan.pulsechain.com/address/0xA1BEe1daE9Af77dAC73aA0459eD63b4D93fC6d29/contracts#address-tabs
#   decompile: https://library.dedaub.com/decompile
#   recompile: https://remix.ethereum.org/
func_hex = "0xa4566950"
contract_abi = [{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"owner","type":"address"},{"indexed":True,"internalType":"address","name":"spender","type":"address"},{"indexed":False,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":True,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"from","type":"address"},{"indexed":True,"internalType":"address","name":"to","type":"address"},{"indexed":False,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"subtractedValue","type":"uint256"}],"name":"decreaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"addedValue","type":"uint256"}],"name":"increaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"pure","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"pure","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"}]

#------------------------------------------------------------#
#   FUNCTION SUPPORT
#------------------------------------------------------------#
def mint_mv():
    print('ENTER - mint_mv')
    try:
        print('# connect to pulse chain')
        #w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID'))
        w3 = Web3(Web3.HTTPProvider('https://rpc.pulsechain.com'))

        print('# Check if connected')
        if w3.isConnected(): print(" Connected to PulseChain mainnet")
        else: print(" Failed to connect to PulseChain mainnet")

        print('# get the contract w/ address & abi')
        contract = w3.eth.contract(address=contract_address, abi=contract_abi)
        
        print('# Prepare the transaction data')
        tx_data = {
            #"value": w3.toWei(1, "ether"),  # Specify the value you want to send with the transaction
            "to": contract_address,
            "chainId": 369, # 369 = pulsechain Mainnet... required for replay-protection (EIP-155)
            "data": func_hex, # Call the custom function hex value on the contract
            "gas": 20000000,  # Adjust the gas limit as needed
            "gasPrice": w3.toWei("4000000", "gwei"),  # Adjust the gas price as needed
            "nonce": w3.eth.getTransactionCount(sender_address)
        }

        print(f'# Create a signed transaction _ tx_data: {tx_data}')
        signed_tx = w3.eth.account.signTransaction(tx_data, private_key=sender_secret)

        print('# Send the transaction')
        tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        
        print(f'# wait for mined receipt _ tx_hash: {tx_hash.hex()}')
        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        
        print(cStrDivider, f'Function "{func_hex}" executed successfully...\n tx_hash: {tx_hash.hex()}\n Transaction receipt: {tx_receipt}', cStrDivider, sep='\n')
        
    except Exception as e:
        print(cStrDivider, f'\n*Exception Caught*\n _ Error: {e}\n', cStrDivider, sep='\n')

#------------------------------------------------------------#
#   DEFAULT SUPPORT                                          #
#------------------------------------------------------------#
READ_ME = f'''
    *EXAMPLE EXECUTION*
        $ python3 {__filename} -<nil> <nil>
        $ python3 {__filename}
        
    *NOTE* INPUT PARAMS...
        nil
'''
def wait_sleep(wait_sec : int, b_print=True): # sleep 'wait_sec'
    print(f'waiting... {wait_sec} sec')
    for s in range(wait_sec, 0, -1):
        if b_print: print('wait ', s, sep='', end='\n')
        time.sleep(1)
    print(f'waited... {wait_sec} sec')
        
def get_time_now():
    return datetime.now().strftime("%H:%M:%S.%f")[0:-4]
    
def read_cli_args():
    print(f'\nread_cli_args...\n # of args: {len(sys.argv)}\n argv lst: {str(sys.argv)}')
    for idx, val in enumerate(sys.argv): print(f' argv[{idx}]: {val}')
    print('read_cli_args _ DONE\n')
    return sys.argv

def go_main():
    run_time_start = get_time_now()
    print(f'\n\nRUN_TIME_START: {run_time_start}\n'+READ_ME)
    lst_argv = read_cli_args()

    # validate args
    if len(lst_argv) > 1:
        print('', cStrDivider, f'# *** ERROR *** _ {__filename} _ invalid args\n ... exiting   {get_time_now()}', cStrDivider, sep='\n')
        exit(1)

    # execute procedural support
    mint_mv()

    # end
    print(f'\n\nRUN_TIME_START: {run_time_start}\nRUN_TIME_END:   {get_time_now()}\n')
    
if __name__ == "__main__":
    go_main()

print('', cStrDivider, f'# END _ {__filename}', cStrDivider, sep='\n')

'''
    known addresses minting MV

    - 0x55115786b6e8Dadd7417c1975314edfCFb86B8e3
    - 0x845f9ba19E7eAB5e57081194557795634FF9b0ff
    - 0x9978b32A2fa90Df78C8B5Fb27d1b91d64Ef45399
    - 0xcA2D833d7777186dB7457C10f07602104C2c97be
    - 0x8B7369921D672f1b26Cd58674e3a434899A73816
    - 0x90AC232c9d55dF367b66A33aBE3aE3534AbD8F0d

    - 0x9abf7504162e5ca517d504a16e8addcb10115aab
'''
