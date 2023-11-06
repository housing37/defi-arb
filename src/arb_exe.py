__fname = 'arb_exe'
__filename = __fname + '.py'
cStrDivider = '#================================================================#'
print('', cStrDivider, f'GO _ {__filename} -> starting IMPORTs & declaring globals', cStrDivider, sep='\n')
cStrDivider_1 = '#----------------------------------------------------------------#'

#------------------------------------------------------------#
#   IMPORTS                                                  #
#------------------------------------------------------------#
import sys, os, time, traceback, json, pprint
from attributedict.collections import AttributeDict
from datetime import datetime
from web3 import Account, Web3, HTTPProvider
import web3
from ethereum.abi import encode_abi # pip install ethereum
import env
from _constants import *
import eth_abi
#from web3.exceptions import ContractLogicError
#import inspect # this_funcname = inspect.stack()[0].function
#parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#sys.path.append(parent_dir) # import from parent dir of this file

#------------------------------------------------------------#
#   GLOBALS
#------------------------------------------------------------#
sel_chain = input('\nSelect chain:\n  0 = ethereum mainnet\n  1 = pulsechain mainnet\n  > ')
assert 0 <= int(sel_chain) <= 1, 'Invalid entry, abort'
(RPC_URL, CHAIN_ID) = (env.eth_main, env.eth_main_cid) if int(sel_chain) == 0 else (env.pc_main, env.pc_main_cid)
print(f'  selected {(RPC_URL, CHAIN_ID)}')

sel_send = input(f'\nSelect sender: (_event_listener: n/a)\n  0 = {env.sender_address_3}\n  1 = {env.sender_address_1}\n  > ')
assert 0 <= int(sel_send) <= 1, 'Invalid entry, abort'
(SENDER_ADDRESS, SENDER_SECRET) = (env.sender_address_3, env.sender_secret_3) if int(sel_send) == 0 else (env.sender_address_1, env.sender_secret_1)
print(f'  selected {SENDER_ADDRESS}')
#------------------------------------------------------------#
print(f'\nSelect arbitrage contract to use:')
for i, v in enumerate(LST_CONTR_ARB_ADDR): print(' ',i, '=', v)
idx = input('  > ')
assert 0 <= int(idx) < len(LST_CONTR_ARB_ADDR), 'Invalid input, aborting...\n'
CONTR_ARB_ADDR = str(LST_CONTR_ARB_ADDR[int(idx)])
print(f'  selected {CONTR_ARB_ADDR}')
#------------------------------------------------------------#
print(f'''\nINITIALIZING web3 ...
    RPC: {RPC_URL}
    ChainID: {CHAIN_ID}
    SENDER: {SENDER_ADDRESS}
    ARB CONTRACT: {CONTR_ARB_ADDR}''')
W3 = Web3(HTTPProvider(RPC_URL))
ACCOUNT = Account.from_key(SENDER_SECRET) # default
#------------------------------------------------------------#
print(f'\nreading contract abi & bytecode files ...')
with open(bin_file, "r") as file: CONTR_ARB_ABI = '0x'+file.read()
with open(abi_file, "r") as file: CONTR_ARB_ABI = file.read()
#------------------------------------------------------------#
print(f'\ninitializing contract {CONTR_ARB_ADDR} ...')
CONTR_ARB_ADDR = W3.to_checksum_address(CONTR_ARB_ADDR)
CONTR_ARB = W3.eth.contract(address=CONTR_ARB_ADDR, abi=CONTR_ARB_ABI)
#------------------------------------------------------------#
print('calc gas settings...')
if int(sel_chain) == 0:
    # ethereum main net (update_102923)
    GAS_LIMIT = 3_000_000# max gas units to use for tx (required)
    GAS_PRICE = W3.to_wei('10', 'gwei') # price to pay for each unit of gas (optional?)
    MAX_FEE = W3.to_wei('14', 'gwei') # max fee per gas unit to pay (optional?)
    MAX_PRIOR_FEE_RATIO = 1.0 # W3.eth.max_priority_fee * mpf_ratio # max fee per gas unit to pay for priority (faster) (optional)
    MAX_PRIOR_FEE = int(W3.eth.max_priority_fee * MAX_PRIOR_FEE_RATIO) # max fee per gas unit to pay for priority (faster) (optional)
else:
    # pulsechain main net (update_103123)
    GAS_LIMIT = 20_000_000 # max gas units to use for tx (required)
    GAS_PRICE = W3.to_wei('0.0005', 'ether') # price to pay for each unit of gas ('gasPrice' param fails on PC)
    MAX_FEE = W3.to_wei('0.001', 'ether') # max fee per gas unit to pay (optional?)
    MAX_PRIOR_FEE_RATIO = 1.0
    MAX_PRIOR_FEE = int(W3.eth.max_priority_fee * MAX_PRIOR_FEE_RATIO) # max fee per gas unit to pay for priority (faster) (optional)

print(f'''\nSetting gas params ...
    GAS_LIMIT: {GAS_LIMIT}
    GAS_PRICE: {GAS_PRICE} *'gasPrice' param fails on PC
    MAX_FEE: {MAX_FEE} ({MAX_FEE / 10**18} wei)
    MAX_PRIOR_FEE: {MAX_PRIOR_FEE}''')
#------------------------------------------------------------#
#------------------------------------------------------------#
    
print(f'finalizing arb settings...')
#ADDR_LOAN_TOK = ADDR_USDC # note_110423: USDC failes test balancer loan (pc)
ADDR_LOAN_TOK = ADDR_WETH # note_110423: WETH success test balancer loan (pc)
#AMNT_LOAN_TOK = 114983659 * 10**18 # max pc->balancer loan (114983659 WETH)
AMNT_LOAN_TOK =  14_000_000 * 10**18 # max pc->balancer loan (114983659 WETH)

LST_ARB_KEYS = [    ['ROUTER',          ['PATH_0', 'PATH_n']]]
LST_ARB = [ [ROUTER_pulsex_router02_v2, [ADDR_WETH, ADDR_WPLS]],

            [ROUTER_pulsex_router02_v2, [ADDR_WPLS, ADDR_WHETH]], # map_route
            [ROUTER_pulsex_router02_v2, [ADDR_WHETH, ADDR_ROB]], # arb_search
            [ROUTER_9INCH_PC,           [ADDR_ROB, ADDR_WPLS]], # arb_search
            #[ROUTER_9INCH_PC,           [ADDR_9INCH, ADDR_WPLS]], # map_route
            
            [ROUTER_pulsex_router02_v2, [ADDR_WPLS, ADDR_WETH]]]
LST_ARB_KV = list(zip(LST_ARB_KEYS, LST_ARB))

#------------------------------------------------------------#
#   FUNCTION SUPPORT                                         #
#------------------------------------------------------------#
def tx_sign_send_wait(tx, wait_rec=True):
    global ACCOUNT
    signed_tx = W3.eth.account.sign_transaction(tx, ACCOUNT.key)
    tx_hash = W3.eth.send_raw_transaction(signed_tx.rawTransaction)

    # print outgoing tx (required json print)
    pjson = json.dumps(tx, indent=4)
    print(cStrDivider_1, f'[{get_time_now()}] _ TX sent\n tx_hash: {tx_hash.hex()}\n wait_receipt={wait_rec}', f' tx_params:\n  {pjson}', cStrDivider_1,sep='\n')

    if wait_rec:
        print(f'[{get_time_now()}] _ WAITING for mined tx receipt\n tx_hash: {tx_hash.hex()} ...') # wait for receipt
        tx_receipt = W3.eth.wait_for_transaction_receipt(tx_hash)
        if not tx_receipt: tx_receipt = {'status':-37}

        # print incoming tx receipt (requires pprint & AttributeDict)
        tx_receipt = AttributeDict(tx_receipt) # import required
        tx_rc_print = pprint.PrettyPrinter().pformat(tx_receipt)

        if tx_receipt['status'] == 1:
            print(f"[{get_time_now()}] _ SUCCESS! tx mined\n tx_hash: {tx_hash.hex()}", cStrDivider_1, sep='\n')
            print(cStrDivider_1, f'TRANSACTION RECEIPT:\n  {tx_rc_print}', cStrDivider_1, sep='\n')
        else:
            print(cStrDivider, cStrDivider, f"\n[{get_time_now()}] _ *ERROR* _ status = {tx_receipt['status']} _ 'tx_sign_send_wait' execution FAILED...\n tx_hash: {tx_hash.hex()}\n TRANSACTION RECEIPT:\n  {tx_rc_print}\n", cStrDivider, cStrDivider, sep='\n')
        return tx_hash, tx_receipt, wait_rec
    return tx_hash, {}, wait_rec
    # Once the transaction is mined, you have successfully called the `makeFlashLoan` function with the `userData` parameter in your Solidity contract

# router contract, tok_contr (in), amount_exact (in_ET-T|out_T-ET), swap_path, swap_type (ET-T|T-ET)
def go_loan():
    global W3, ACCOUNT, LST_ARB, LST_ARB_KV, CHAIN_ID, RPC_URL, CONTR_ARB
    print(f'setting arb tx params data... [{get_time_now()}]')
    print(f' LST_ARB_KV:\n {json.dumps(LST_ARB_KV, indent=4)}')

    # Define the array of IERC20 tokens for loan (w/ amounts)
    lst_tok_addr = [ADDR_LOAN_TOK] # tokens to receive loan
    lst_tok_amnt = [AMNT_LOAN_TOK] # amnt to receive
    
    routers = [l[0] for l in LST_ARB]
    paths = [l[1] for l in LST_ARB]
    data_to_encode = [routers, paths]
    encoded_data = eth_abi.encode_abi(('address[]', 'address[][]'), data_to_encode)

    print(f'setting function call...\n loan tokens: {lst_tok_addr}\n loan amounts: {[f"{(x / 10**18):,}" for x in lst_tok_amnt]} ({AMNT_LOAN_TOK})\n encoded_data: {encoded_data.hex()}\n')
    flash_loan_function = CONTR_ARB.functions.makeFlashLoan(
        lst_tok_addr,
        lst_tok_amnt,
        encoded_data
    )

    # FAILES because 'from' is not set yet (.sol checks for owner)
    try:
        gas_estimate = flash_loan_function.estimateGas()
        print(f'gas_estimate... {gas_estimate}')
    except Exception as e:
        gas_estimate = 200000
        print(e) # failed solidity "require(...,'')"
        print("Failed to estimate gas, attempting to send with", gas_estimate, "gas limit...")
        
    print('preparing tx...')
    tx_params = {
        'chainId':CHAIN_ID, # required
        'from': ACCOUNT.address,
        'nonce': W3.eth.getTransactionCount(ACCOUNT.address),
    }
    
    print('setting gas params...')
    lst_gas_params = get_gas_params_lst(RPC_URL, min_params=False, max_params=True, def_params=True, mpf_ratio=1.0)
    for d in lst_gas_params: tx_params.update(d) # append gas params
    data = flash_loan_function.buildTransaction(tx_params)
    assert input('\n procced? [y/n]\n > ') == 'y', '...aborted'
    
    print(f'\nsign, send, and wait for receipt... [{get_time_now()}]')
    tx_hash, tx_receipt, wait_rec = tx_sign_send_wait(data, wait_rec=True)
        
    # Retrieve the event logs
    logs = contract.events.ErrorOccurred().processReceipt(txn_receipt)
    if logs:
        error_message = logs[0].args.errorMessage
        print("\n\nTransaction failed with custom error message:", error_message, "\n\n")
        
#    try:
#        print(f'\nsign, send, and wait for receipt... [{get_time_now()}]')
#        tx_hash, tx_receipt, wait_rec = tx_sign_send_wait(data, wait_rec=True)
#    except ContractLogicError as e:
#        error_message = str(e)
#        print("\n\nTransaction failed with error message:", error_message, "\n\n")

def go_transfer():
    global CHAIN_ID, RPC_URL
    
    print('getting keys and intializing web3...')
    SENDER_ADDRESS = env.sender_address_0 # default
    SENDER_SECRET = env.sender_secret_0 # default

    addr_arb_contr = CONTR_ARB_ADDR
    with open("../contracts/BalancerFLR.json", "r") as file: abi_arb_contr = file.read()
    addr_pdai = "0x6B175474E89094C44Da98b954EedeAC495271d0F" # pDAI token
    abi_pdai = [
        {
            "constant": True,
            "inputs": [{"name": "_owner", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "balance", "type": "uint256"}],
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],  # No inputs required
            "name": "symbol",
            "outputs": [{"name": "", "type": "string"}],
            "type": "function"
        }
    ]
    W3 = Web3(HTTPProvider(f'https://rpc.pulsechain.com'))
    pdai_contr = W3.eth.contract(address=addr_pdai, abi=abi_pdai)
    arb_contr = W3.eth.contract(address=addr_arb_contr, abi=abi_arb_contr)

    # check pdai balance
    pdai_bal = pdai_contr.functions.balanceOf(addr_arb_contr).call()
    print(f'pdai balance: {pdai_bal}\n for contr: {addr_arb_contr}')

    # transfer pdai out (102823: doesn't seem to work)
    #print('attempting "transferTokens"...')
    #arb_contr.functions.transferTokens(addr_pdai, SENDER_ADDRESS, 1)
    print('preparing tx...')
    tx_params = {
        'chainId':CHAIN_ID, # required
        'from': ACCOUNT.address,
        'to': addr_arb_contr,
        #'gas': 2000000,  # Adjust gas limit as needed
        #'gasPrice': W3.toWei('20', 'gwei'),  # Adjust gas price as needed
        "gas": 20_000_000,  # Adjust the gas limit as needed
        'nonce': W3.eth.getTransactionCount(ACCOUNT.address),
        'data': CONTR_ARB.encodeABI(fn_name='transferTokens', args=[addr_pdai, SENDER_ADDRESS, 1 * 10**18]),
        
    }
    print('calculating gas...')
    lst_gas_params = get_gas_params_lst(RPC_URL, min_params=False, max_params=True, def_params=True, mpf_ratio=1.0)
    for d in lst_gas_params: tx_params.update(d) # append gas params

    print('sing, send, and wait for receipt...')
    tx_hash, tx_receipt, wait_rec = tx_sign_send_wait(tx_params, wait_rec=True)

    # check pdai balance again
    pdai_bal = pdai_contr.functions.balanceOf(addr_arb_contr).call()
    print(f'pdai balance: {pdai_bal}\n for contr: {addr_arb_contr}')

    # check PLS balance
    wei_bal = W3.eth.getBalance(addr_arb_contr)
    eth_bal = W3.fromWei(wei_bal, 'ether')
    print(f'PLS balance: {eth_bal}\n for contr: {addr_arb_contr}')

def go_withdraw():
    global CHAIN_ID, RPC_URL
    
    print('getting keys and intializing web3...')
    SENDER_ADDRESS = env.sender_address_1 # default
    SENDER_SECRET = env.sender_secret_1 # default

    addr_arb_contr = CONTR_ARB_ADDR
    with open("../contracts/BalancerFLR.json", "r") as file: abi_arb_contr = file.read()

    W3 = Web3(HTTPProvider(f'https://rpc.pulsechain.com'))
    arb_contr = W3.eth.contract(address=addr_arb_contr, abi=abi_arb_contr)

    # check PLS balances
    wei_bal = W3.eth.getBalance(addr_arb_contr)
    eth_bal = W3.fromWei(wei_bal, 'ether')
    print(f'PLS balance: {eth_bal}\n for contr: {addr_arb_contr}')
    
    wei_bal = W3.eth.getBalance(SENDER_ADDRESS)
    eth_bal = W3.fromWei(wei_bal, 'ether')
    print(f'PLS balance: {eth_bal}\n for contr: {SENDER_ADDRESS}')

    # transfer pdai out (102823: doesn't seem to work)
    #print('attempting "transferTokens"...')
    #arb_contr.functions.transferTokens(addr_pdai, SENDER_ADDRESS, 1)
    print('preparing tx...')
    tx_params = {
        'chainId':CHAIN_ID, # required
        'from': ACCOUNT.address,
        'to': addr_arb_contr,
        #'gas': 2000000,  # Adjust gas limit as needed
        #'gasPrice': W3.toWei('20', 'gwei'),  # Adjust gas price as needed
        "gas": 20_000_000,  # Adjust the gas limit as needed
        'nonce': W3.eth.getTransactionCount(ACCOUNT.address),
        'data': CONTR_ARB.encodeABI(fn_name='withdraw', args=[10 * 10**18]),
        
    }
    print('calculating gas...')
    lst_gas_params = get_gas_params_lst(RPC_URL, min_params=False, max_params=True, def_params=True, mpf_ratio=1.0)
    for d in lst_gas_params: tx_params.update(d) # append gas params

    print('sing, send, and wait for receipt...')
    tx_hash, tx_receipt, wait_rec = tx_sign_send_wait(tx_params, wait_rec=True)

    # check PLS balances again
    wei_bal = W3.eth.getBalance(addr_arb_contr)
    eth_bal = W3.fromWei(wei_bal, 'ether')
    print(f'PLS balance: {eth_bal}\n for contr: {addr_arb_contr}')
    
    wei_bal = W3.eth.getBalance(SENDER_ADDRESS)
    eth_bal = W3.fromWei(wei_bal, 'ether')
    print(f'PLS balance: {eth_bal}\n for contr: {SENDER_ADDRESS}')

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
def get_gas_params_lst(rpc_url, min_params=False, max_params=False, def_params=True, mpf_ratio=1.0):
    # Estimate the gas cost for the transaction
    #gas_estimate = buy_tx.estimate_gas()
    gas_limit = GAS_LIMIT # max gas units to use for tx (required)
    gas_price = GAS_PRICE # price to pay for each unit of gas (optional?) # 'gasPrice' fails on PC w/ unknown args error
    max_fee = MAX_FEE # max fee per gas unit to pay (optional?)
    max_prior_fee = MAX_PRIOR_FEE # max fee per gas unit to pay for priority (faster) (optional)
    #max_prior_fee = int(W3.eth.max_priority_fee * mpf_ratio) # max fee per gas unit to pay for priority (faster) (optional)
    #max_priority_fee = W3.to_wei('0.000000003', 'ether')

    if min_params:
        return [{'gas':gas_limit}]
    elif max_params:
        # note_110423: 'gasPrice' fails on PC w/ unknown args error
        #return [{'gas':gas_limit}, {'gasPrice': gas_price}, {'maxFeePerGas': max_fee}, {'maxPriorityFeePerGas': max_prior_fee}]
        return [{'gas':gas_limit}, {'maxFeePerGas': max_fee}, {'maxPriorityFeePerGas': max_prior_fee}]
    elif def_params:
        return [{'gas':gas_limit}, {'maxPriorityFeePerGas': max_prior_fee}]
    else:
        return [{'gas':gas_limit}]

#def exe_GET_request(url='nil_url'):
#    try:
#        response = requests.get(url)
#        if response.status_code == 200:
#            return response.json() # data
#        else:
#            print(f"Request failed with status code {response.status_code}\n returning empty list")
#            return []
#    except requests.exceptions.RequestException as e:
#        # Handle request exceptions
#        print_except(e, debugLvl=0)
#        return -1
        
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
        if sys.argv[-1] == '-loan': go_loan()
        if sys.argv[-1] == '-trans': go_transfer()
        if sys.argv[-1] == '-withdraw': go_withdraw()
        
    except Exception as e:
        print_except(e, debugLvl=0)
    
    ## end ##
    print(f'\n\nRUN_TIME_START: {RUN_TIME_START}\nRUN_TIME_END:   {get_time_now()}\n')

print('', cStrDivider, f'# END _ {__filename}', cStrDivider, sep='\n')
