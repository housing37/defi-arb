__fname = 'arb_exe'
__filename = __fname + '.py'
cStrDivider = '#================================================================#'
print('', cStrDivider, f'START _ {__filename}', cStrDivider, sep='\n')
print(f'GO {__filename} -> starting IMPORTs and globals decleration')
cStrDivider_1 = '#----------------------------------------------------------------#'

#------------------------------------------------------------#
#   IMPORTS                                                  #
#------------------------------------------------------------#
import sys, os, time, traceback
from datetime import datetime
from web3 import Account, Web3
from ethereum.abi import encode_abi # pip install ethereum
import env
#import inspect # this_funcname = inspect.stack()[0].function
#parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#sys.path.append(parent_dir) # import from parent dir of this file

#------------------------------------------------------------#
#   GLOBALS
#------------------------------------------------------------#
# STATIC CONSTANTS
SENDER_ADDRESS = env.sender_address_1 # default
SENDER_SECRET = env.sender_secret_1 # default
AMNT_MAX = 115792089237316195423570985008687907853269984665640564039457584007913129639935 # uint256.max
RPC_URL = 'https://rpc.pulsechain.com'
#RPC_URL = 'https://mainnet.infura.io/v3/{env.ETH_MAIN_RPC_KEY}'

CONTR_ARB_ADDR = "0x904f51cab7CBF3251D2E5D20831F9E31FA11E4E1" # deployed 102823
print(f'reading abi file for contract: {CONTR_ARB_ADDR}...')
with open("../contracts/BalancerFLR.json", "r") as file: CONTR_ARB_ABI = file.read()

print('connecting to pulsechain ... (getting account for secret)')
W3 = Web3(Web3.HTTPProvider(RPC_URL))
ACCOUNT = Account.from_key(SENDER_SECRET) # default
CONTR_ARB = W3.eth.contract(address=CONTR_ARB_ADDR, abi=CONTR_ARB_ABI)
#account = Web3.toChecksumAddress("0xYourSenderAddress")

ROUTER_UNISWAP_V3 = '0xE592427A0AEce92De3Edee1F18E0157C05861564'
ROUTER_PANCAKESWAP_V3 = '0x13f4EA83D0bd40E75C8222255bc855a974568Dd4'

ADDR_rETH = '0xae78736Cd615f374D3085123A210448E74Fc6393'
ADDR_DAI = '0x6B175474E89094C44Da98b954EedeAC495271d0F'

ADDR_WETH = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
ADDR_WBTC = '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599'
ADDR_USDT = '0xdAC17F958D2ee523a2206206994597C13D831ec7'
ADDR_USDC = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'

ROUTER_0 = ROUTER_UNISWAP_V3
ROUTER_1 = ROUTER_UNISWAP_V3

ADDR_IN_0 = ADDR_WETH
ADDR_OUT_MIN_0 = ADDR_WBTC
ADDR_IN_1 = ADDR_WBTC
ADDR_OUT_MIN_1 = ADDR_USDC

AMNT_IN_0 = '34041.08509'
AMNT_OUT_MIN_1 = '19.02837'
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
    print(cStrDivider_1, f'[{get_time_now()}] _ TX sent\n tx_hash: {tx_hash.hex()}\n tx_params: {tx}\n wait_rec={wait_rec}', cStrDivider_1, sep='\n')
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
def go_loan():
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

    # NOTE: if receive runtime error w/ encode_abi
    #   pointing to: /Library/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages/ethereum/abi.py
    #   then check the len of list of types vs len of data_to_encode
    data_to_encode = (router_0, router_1, addr_path_0, addr_path_1, amntIn_0, amntOutMin_1)
    encoded_data = encode_abi(['address', 'address', 'address[]', 'address[]', 'uint256', 'uint256'], data_to_encode)

    # Define the array of IERC20 tokens for loan (w/ amounts)
    lst_tok_addr = [addr_path_0[0]]
    lst_tok_amnt = [amntIn_0]

    print('preparing tx...')
    tx_params = {
        'chainId':369, # required
        'from': ACCOUNT.address,
        'to': CONTR_ARB_ADDR,
        #'gas': 2000000,  # Adjust gas limit as needed
        #'gasPrice': W3.toWei('20', 'gwei'),  # Adjust gas price as needed
        "gas": 20_000_000,  # Adjust the gas limit as needed
        'nonce': W3.eth.getTransactionCount(ACCOUNT.address),
        'data': CONTR_ARB.encodeABI(fn_name='makeFlashLoan', args=[lst_tok_addr, lst_tok_amnt, encoded_data]),
        
    }
    print('calculating gas...')
    lst_gas_params = get_gas_params_lst(min_params=False, max_params=True, def_params=True, mpf_ratio=1.0)
    for d in lst_gas_params: tx_params.update(d) # append gas params

    print('sing, send, and wait for receipt...')
    tx_hash, tx_receipt, wait_rec = tx_sign_send_wait(tx_params, wait_rec=True)

#------------------------------------------------------------#
#   DEFAULT SUPPORT                                          #
#------------------------------------------------------------#
READ_ME = f'''
    *DESCRIPTION*
        execute arbitrage opportunity

    *NOTE* INPUT PARAMS...
        nil
        
    *EXAMPLE EXECUTION*
        $ python3 {__filename} -<nil> <nil>
        $ python3 {__filename}
'''
# note: params checked/set in priority order; 'def|max_params' uses 'mpf_ratio'
#   if all params == False, falls back to 'min_params=True' (ie. just use 'gas_limit')
def get_gas_params_lst(min_params=False, max_params=False, def_params=True, mpf_ratio=1.0):
    global W3
    # Estimate the gas cost for the transaction
    #gas_estimate = buy_tx.estimate_gas()
    gas_limit = 20_000_000 # max gas units to use for tx (required)
    gas_price = W3.to_wei('0.0009', 'ether') # price to pay for each unit of gas (optional)
    max_fee = W3.to_wei('0.002', 'ether') # max fee per gas unit to pay (optional)
    max_prior_fee = int(W3.eth.max_priority_fee * mpf_ratio) # max fee per gas unit to pay for priority (faster) (optional)
    #max_priority_fee = W3.to_wei('0.000000003', 'ether')

    if min_params:
        return [{'gas':gas_limit}]
    elif max_params:
        #return [{'gas':gas_limit}, {'gasPrice': gas_price}, {'maxFeePerGas': max_fee}, {'maxPriorityFeePerGas': max_prior_fee}]
        return [{'gas':gas_limit}, {'maxFeePerGas': max_fee}, {'maxPriorityFeePerGas': max_prior_fee}]
    elif def_params:
        return [{'gas':gas_limit}, {'maxPriorityFeePerGas': max_prior_fee}]
    else:
        return [{'gas':gas_limit}]

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

if __name__ == "__main__":
    ## start ##
    RUN_TIME_START = get_time_now()
    print(f'\n\nRUN_TIME_START: {RUN_TIME_START}\n'+READ_ME)
    lst_argv_OG, argv_cnt = read_cli_args()
    
    ## exe ##
    try:
        go_loan()
    except Exception as e:
        print_except(e, debugLvl=0)
    
    ## end ##
    print(f'\n\nRUN_TIME_START: {RUN_TIME_START}\nRUN_TIME_END:   {get_time_now()}\n')

print('', cStrDivider, f'# END _ {__filename}', cStrDivider, sep='\n')
