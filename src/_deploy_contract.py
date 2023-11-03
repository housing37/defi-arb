from web3 import Web3, HTTPProvider
from web3.middleware import construct_sign_and_send_raw_middleware
from web3.gas_strategies.time_based import fast_gas_price_strategy
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
print(f'''\nINITIALIZING web3 ...
    RPC: {RPC_URL}
    ChainID: {CHAIN_ID}
    SENDER: {SENDER_ADDRESS}''')
W3 = Web3(HTTPProvider(RPC_URL))
#------------------------------------------------------------#
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
    GAS_PRICE = W3.to_wei('0.0005', 'ether') # price to pay for each unit of gas (optional?)
    MAX_FEE = W3.to_wei('0.001', 'ether') # max fee per gas unit to pay (optional?)
    MAX_PRIOR_FEE_RATIO = 1.0
    MAX_PRIOR_FEE = int(W3.eth.max_priority_fee * MAX_PRIOR_FEE_RATIO) # max fee per gas unit to pay for priority (faster) (optional)

print(f'''\nSetting gas params ...
    GAS_LIMIT: {GAS_LIMIT}
    GAS_PRICE: {GAS_PRICE}
    MAX_FEE: {MAX_FEE}
    MAX_PRIOR_FEE: {MAX_PRIOR_FEE}''')
#------------------------------------------------------------#
print(f'\nreading contract abi & bytecode files ...')
with open(abi_file, "r") as file: CONTR_ABI = file.read()
with open(bin_file, "r") as file: CONTR_BYTES = '0x'+file.read()
#------------------------------------------------------------#

print(f'\nDEPLOYING bytecode: {bin_file}')
print(f'DEPLOYING abi: {abi_file}')

assert input('\n procced? [y/n]\n > ') == 'y', "aborted...\n"

def estimate_gas():
    # Replace with your contract's ABI and bytecode
    contract_abi = CONTR_ABI
    contract_bytecode = CONTR_BYTES
    
    # Replace with your wallet's private key
    private_key = SENDER_SECRET

    # Create a web3.py contract object
    contract = W3.eth.contract(abi=contract_abi, bytecode=contract_bytecode)

    # Set the sender's address from the private key
    sender_address = W3.eth.account.from_key(private_key).address

    # Estimate gas for contract deployment
    gas_estimate = contract.constructor().estimateGas({'from': sender_address})

    print(f"\nEstimated gas cost _ 0: {gas_estimate}")

    import statistics
    block = W3.eth.get_block("latest", full_transactions=True)
    gas_estimate = int(statistics.median(t.gas for t in block.transactions))
    gas_price = W3.eth.gas_price
    gas_price_1018 = gas_price * 10**18
    gas_price_eth = W3.fromWei(gas_price, 'ether')
    print(f"\nEstimated gas cost _ 1: {gas_estimate}")
    print(f"\nCurrent gas price: {gas_price} W3.eth.gas_price")
    print(f"\nCurrent gas price: {gas_price_eth} PLS")
    print(f"\nCurrent gas price: {gas_price_1018} maybe")
    # Optionally, you can also estimate the gas price (in Gwei) using a gas price strategy
    # Replace 'fast' with other strategies like 'medium' or 'slow' as needed
    #gas_price = W3.eth.generateGasPrice(fast_gas_price_strategy)
    #print(f"Estimated gas price (Gwei): {W3.fromWei(gas_price, 'gwei')}")
    
    return input('\n procced? [y/n]\n > ') == 'y'

# note: params checked/set in priority order; 'def|max_params' uses 'mpf_ratio'
#   if all params == False, falls back to 'min_params=True' (ie. just use 'gas_limit')
def get_gas_params_lst(rpc_url, min_params=False, max_params=False, def_params=True):
    # Estimate the gas cost for the transaction
    #gas_estimate = buy_tx.estimate_gas()
    gas_limit = GAS_LIMIT # max gas units to use for tx (required)
    gas_price = GAS_PRICE # price to pay for each unit of gas (optional?)
    max_fee = MAX_FEE # max fee per gas unit to pay (optional?)
    max_prior_fee = MAX_PRIOR_FEE # max fee per gas unit to pay for priority (faster) (optional)
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
        
proceed = estimate_gas()
assert proceed, "\ndeployment canceled after gas estimate\n"

print('\nintializing contract to deploy ...')
balancer_flr = W3.eth.contract(
    abi=CONTR_ABI,
    bytecode=CONTR_BYTES
)

print('calculating gas ...')
tx_nonce = W3.eth.getTransactionCount(SENDER_ADDRESS)
tx_params = {
    'chainId': CHAIN_ID,
    'nonce': tx_nonce,
}
lst_gas_params = get_gas_params_lst(RPC_URL, min_params=False, max_params=True, def_params=True)
for d in lst_gas_params: tx_params.update(d) # append gas params

print(f'building tx w/ NONCE: {tx_nonce} ...')
constructor_tx = balancer_flr.constructor().buildTransaction(tx_params)

print('signing and sending tx ...')
# Sign and send the transaction # Deploy the contract
tx_signed = W3.eth.account.signTransaction(constructor_tx, private_key=SENDER_SECRET)
tx_hash = W3.eth.sendRawTransaction(tx_signed.rawTransaction)

print('waiting for receipt ...')
print(f'    tx_hash: {tx_hash.hex()}')
# Wait for the transaction to be mined
receipt = W3.eth.waitForTransactionReceipt(tx_hash)
#print(f'RECEIPT:\n {receipt}')
# Pretty print the dictionary
import pprint
pp = pprint.PrettyPrinter(indent=4)
pp.pprint(f'RECEIPT:\n {receipt}')
contract_address = receipt['contractAddress']
print(f'\n\n Contract deployed at address: {contract_address}\n\n')
