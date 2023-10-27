__fname = 'arb_exe'
__filename = __fname + '.py'
cStrDivider = '#================================================================#'
print('', cStrDivider, f'START _ {__filename}', cStrDivider, sep='\n')
print(f'GO {__filename} -> starting IMPORTs and globals decleration')
cStrDivider_1 = '#----------------------------------------------------------------#'

#------------------------------------------------------------#
#   IMPORTS                                                  #
#------------------------------------------------------------#
import sys, os, time
from datetime import datetime
from web3 import Account, Web3
from ethereum.abi import encode_abi
import env
#import inspect # this_funcname = inspect.stack()[0].function
#parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#sys.path.append(parent_dir) # import from parent dir of this file

#------------------------------------------------------------#
#   GLOBALS
#------------------------------------------------------------#
# STATIC CONSTANTS
SENDER_ADDRESS = env.sender_address_0 # default
SENDER_SECRET = env.sender_secret_0 # default
AMNT_MAX = 115792089237316195423570985008687907853269984665640564039457584007913129639935 # uint256.max
#RPC_URL = 'https://rpc.pulsechain.com'
RPC_URL = 'https://mainnet.infura.io/v3/{env.ETH_MAIN_RPC_KEY}'
#SWAP_TYPE_ET_FOR_T = 0
#SWAP_TYPE_T_FOR_ET = 1
CONTR_ARB_ADDR = "0xYourContractAddress"
CONTR_ARB_ABI = []  # Define your contract's ABI

print('connecting to pulsechain ... (getting account for secret)')
W3 = Web3(Web3.HTTPProvider(RPC_URL))
ACCOUNT = Account.from_key(SENDER_SECRET) # default
CONTR_ARB = W3.eth.contract(address=CONTR_ARB_ADDR, abi=CONTR_ARB_ABI)
#account = Web3.toChecksumAddress("0xYourSenderAddress")

ROUTER_UNISWAP_V3 = '0xE592427A0AEce92De3Edee1F18E0157C05861564'
ROUTER_PANCAKESWAP_V3 = '0x13f4EA83D0bd40E75C8222255bc855a974568Dd4'

ADDR_WBTC = '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599'
ADDR_WETH = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
ADDR_rETH = '0xae78736Cd615f374D3085123A210448E74Fc6393'
ADDR_DAI = '0x6B175474E89094C44Da98b954EedeAC495271d0F'

ROUTER_0 = ROUTER_UNISWAP_V3
ROUTER_1 = ROUTER_UNISWAP_V3

ADDR_IN_0 = ADDR_DAI
ADDR_OUT_MIN_0 = ADDR_WBTC
ADDR_IN_1 = ADDR_WBTC
ADDR_OUT_MIN_1 = ADDR_rETH

AMNT_IN_0 = '33680.246'
AMNT_OUT_MIN_1 = '17.4821'
LST_ARB = [
        [ROUTER_0, ROUTER_1],
        [[ADDR_IN_0, ADDR_OUT_MIN_0], [ADDR_IN_1, ADDR_OUT_MIN_1]],
        [AMNT_IN_0, AMNT_OUT_MIN_1]
    ]

#------------------------------------------------------------#
#   FUNCTION SUPPORT                                         #
#------------------------------------------------------------#
# allowance for 'contract_a' to spend 'accnt' tokens, inside 'contract_b'
def get_allowance(contract_a, accnt, contract_b, go_print=True):
    allow_num = contract_b.functions.allowance(accnt.address, contract_a.address).call()
    if go_print:
        print(f'Function "allowance" executed successfully...\n contract_b: {contract_b.address}\n shows allowance for contract_a: {contract_a.address}\n to spend tokens from sender_address: {accnt.address}\n token amnt allowed: {allow_num}')
    return allow_num

# contract_a approves (grants allowance for) contract_b to spend SENDER_ADDRESS tokens
def set_approval(contract_a, contract_b, amnt=-1):
    global W3, ACCOUNT
    #bal_eth = get_sender_pls_bal(go_print=True)
    
    print('set_approval _ build, sign, & send tx ...')
    d_tx_data = {
            'chainId': 369,  # Replace with the appropriate chain ID (Mainnet)
            'gas': 20000000,  # Adjust the gas limit as needed
            'gasPrice': W3.to_wei('4000000', 'gwei'),  # Set the gas price in Gwei
            'nonce': W3.eth.getTransactionCount(ACCOUNT.address),
        }
    tx_data = contract_a.functions.approve(contract_b.address, amnt).buildTransaction(d_tx_data) # build tx
    signed_tx = W3.eth.account.signTransaction(tx_data, private_key=ACCOUNT.key) # sign tx
    tx_hash = W3.eth.sendRawTransaction(signed_tx.rawTransaction) # send tx
    
    print(f'[{get_time_now()}] _ WAITING for mined receipt _ tx_hash: {tx_hash.hex()} ...') # wait for receipt
    tx_receipt = W3.eth.waitForTransactionReceipt(tx_hash)
    if tx_receipt and tx_receipt['status'] == 1:
        print(f"[{get_time_now()}] _ 'approve' SUCCESS:\n contract_a: {contract_a.address}\n approved contract_b: {contract_b.address}\n to spend SENDER_ADDRESS: {ACCOUNT.address} tokens\n amnt allowed: {amnt}\n tx_hash: {tx_hash.hex()}\n Transaction receipt: {tx_receipt}")
    else:
        print(f'*ERROR* Function "approve" execution failed...\n tx_hash: {tx_hash.hex()}\n Transaction receipt: {tx_receipt}')

def tx_sign_send_wait(tx, wait_rec=True):
    global ACCOUNT
    signed_tx = W3.eth.account.sign_transaction(tx, ACCOUNT.key)
    tx_hash = W3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(cStrDivider_1, f'[{get_time_now()}] _ TX sent\n tx_hash: {tx_hash.hex()}\n tx_params: {tx_params}\n wait_rec={wait_rec}', cStrDivider_1, sep='\n')
    if wait_rec:
        print(f'[{get_time_now()}] _ WAITING for mined tx receipt _ tx_hash: {tx_hash.hex()} ...') # wait for receipt
        tx_receipt = W3.eth.wait_for_transaction_receipt(tx_hash)
        if tx_receipt and tx_receipt['status'] == 1:
            print(f"[{get_time_now()}] _ SUCCESS! tx mined _ tx_hash: {tx_hash.hex()}", cStrDivider_1, sep='\n')
            print(cStrDivider_1, f'TRANSACTION RECEIPT:\n {tx_receipt}', cStrDivider_1, sep='\n')
        else:
            print(cStrDivider, cStrDivider, f'\n[{get_time_now()}] _ *ERROR* _ "build_sign_send_tx" execution failed...\n tx_hash: {tx_hash.hex()}\n TRANSACTION RECEIPT: {tx_receipt}\n', cStrDivider, cStrDivider, sep='\n')
        return tx_hash, tx_receipt, wait_rec
    return tx_hash, {}, wait_rec
    # Once the transaction is mined, you have successfully called the `makeFlashLoan` function with the `userData` parameter in your Solidity contract

# router contract, tok_contr (in), amount_exact (in_ET-T|out_T-ET), swap_path, swap_type (ET-T|T-ET)
def go_swap(rout_contr, tok_contr, amount_exact, swap_path=[], swap_type=1, slip_perc=0, time_out_sec=180):
    global W3, ACCOUNT, LST_ARB
    
    # check tok_contr allowance for swap, and approve if needed, then check again
    #print('\nSTART - validate allowance ...', cStrDivider_1, sep='\n')
    #allow_num = get_allowance(rout_contr, ACCOUNT, tok_contr, go_print=True) # rout_contr can spend in tok_contr
    #if allow_num == 0:
    #    set_approval(tok_contr, rout_contr, AMNT_MAX) # tok_contr approves rout_contr to spend
    #    allow_num = get_allowance(rout_contr, ACCOUNT, tok_contr, go_print=True) # rout_contr can spend in tok_contr
    #print(cStrDivider_1, 'DONE - validate allowance', sep='\n')
    
    router_0 = LST_ARB[0][0]
    router_1 = LST_ARB[0][1]

    addr_path_0 = LST_ARB[1][0] # [ADDR_DAI, ADDR_WBTC]
    addr_path_1 = LST_ARB[1][1] # [ADDR_WBTC, ADDR_rETH]

    amntIn_0 = W3.toWei(LST_ARB[2][0], 'ether')
    amntOutMin_1 = W3.toWei(LST_ARB[2][1], 'ether')
    
    data_to_encode = (router_0, router_1, addr_path_0, addr_path_1, amntIn_0, amntOutMin_1)
    encoded_data = encode_abi(['address', 'address[]', 'address[]', 'uint256', 'uint256'], data_to_encode)

    # Define the array of IERC20 tokens for loan (w/ amounts)
    lst_tok_addr = [addr_path_0[0]]
    lst_tok_amnt = [amntIn_0]

    # Prepare the transaction
    tx = {
        'from': ACCOUNT.address,
        'to': ARB_CONTR_ADDR,
        'gas': 2000000,  # Adjust gas limit as needed
        'gasPrice': W3.toWei('20', 'gwei'),  # Adjust gas price as needed
        'nonce': W3.eth.getTransactionCount(ACCOUNT.address),
        'data': CONTR_ARB.encodeABI(fn_name='makeFlashLoan', args=[lst_tok_addr, lst_tok_amnt, encoded_data]),
    }

    tx_hash, tx_receipt, wait_rec = tx_sign_send_wait(tx, wait_rec=True)
    # Encode the `userData` using the ABI
    #bytes_path_0 = bytes(int(value, 16) for value in addr_path_0)
    #bytes_path_1 = bytes(int(value, 16) for value in addr_path_1)
    #data_to_encode = (router_addr_0, router_addr_1, bytes_path_0, bytes_path_1, amntIn_0, amntOutMin_1)
    #encoded_data = encode_abi(['address', 'bytes', 'bytes', 'uint256', 'uint256'], data_to_encode)

#------------------------------------------------------------#
#   DEFAULT SUPPORT                                          #
#------------------------------------------------------------#
READ_ME = f'''
    *DESCRIPTION*
        search for arbitrage opportunites via dexscreener
         - loop through each chain ID
         - for each token address,
            log token value diffs between dex routers

    *NOTE* INPUT PARAMS...
        nil
        
    *EXAMPLE EXECUTION*
        $ python3 {__filename} -<nil> <nil>
        $ python3 {__filename}
'''
def exe_GET_request(url='nil_url'):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json() # data
        else:
            print(f"Request failed with status code {response.status_code}\n returning empty list")
            return []
    except requests.exceptions.RequestException as e:
        # Handle request exceptions
        print_except(e, debugLvl=0)
        return -1
        
#ref: https://stackoverflow.com/a/1278740/2298002
def print_except(e, debugLvl=0):
    # prints instance, args, __str__ allows args to be printed directly
    #print(type(e), e.args, e)
    print('', cStrDivider, f' Exception Caught _ e: {e}', cStrDivider, sep='\n')
    if debugLvl > 0:
        print('', cStrDivider, f' Exception Caught _ type(e): {type(e)}', cStrDivider, sep='\n')
    if debugLvl > 1:
        print('', cStrDivider, f' Exception Caught _ e.args: {e.args}', cStrDivider, sep='\n')

    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    strTrace = traceback.format_exc()
    print('', cStrDivider, f' type: {exc_type}', f' file: {fname}', f' line_no: {exc_tb.tb_lineno}', f' traceback: {strTrace}', cStrDivider, sep='\n')
    
def wait_sleep(wait_sec : int, b_print=True, bp_one_line=True): # sleep 'wait_sec'
    print(f'waiting... {wait_sec} sec')
    for s in range(wait_sec, 0, -1):
        if b_print and bp_one_line: print(wait_sec-s+1, end=' ', flush=True)
        if b_print and not bp_one_line: print('wait ', s, sep='', end='\n')
        time.sleep(1)
    if bp_one_line and b_print: print() # line break if needed
    print(f'waiting... {wait_sec} sec _ DONE')
        
def get_time_now(dt=True):
    if dt: return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[0:-4]
    return datetime.now().strftime("%H:%M:%S.%f")[0:-4]
    
def read_cli_args():
    print(f'\nread_cli_args...\n # of args: {len(sys.argv)}\n argv lst: {str(sys.argv)}')
    for idx, val in enumerate(sys.argv): print(f' argv[{idx}]: {val}')
    print('read_cli_args _ DONE\n')
    return sys.argv, len(sys.argv)

def go_main():
    lst_d = []
    addr = symb = chain = 'nil'
    for c in LST_CHAIN_PARAMS:
        addr = c[2]
        symb = c[1]
        chain = c[0]
        d0 = search_for_arb(t_addr=addr,
                            t_symb=symb,
                            chain_id=chain,
                            d_print=True)
        lst_d.append([d0, addr, symb, chain])
                            
    print()
    for v in lst_d:
        d0 = v[0]
        print(f'{v[3]} _ start from token: {v[2]} _ unique tokens found: {len(v[0].keys())} ...')
        [print(k, d0[k][0:5]) for k in d0.keys()]
        print(f'{v[3]} _ start from token: {v[2]} _ unique tokens found: {len(v[0].keys())}\n')

if __name__ == "__main__":
    ## start ##
    RUN_TIME_START = get_time_now()
    print(f'\n\nRUN_TIME_START: {RUN_TIME_START}\n'+READ_ME)
    lst_argv_OG, argv_cnt = read_cli_args()
    
    ## exe ##
    try:
        go_main()
    except Exception as e:
        print_except(e, debugLvl=0)
    
    ## end ##
    print(f'\n\nRUN_TIME_START: {RUN_TIME_START}\nRUN_TIME_END:   {get_time_now()}\n')

print('', cStrDivider, f'# END _ {__filename}', cStrDivider, sep='\n')
