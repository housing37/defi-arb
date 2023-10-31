from web3 import Web3, HTTPProvider
from web3.middleware import construct_sign_and_send_raw_middleware
from web3.gas_strategies.time_based import fast_gas_price_strategy
import env

print('getting keys and setting globals ...')
## SETTINGS ##
abi_file = "../contracts/BalancerFLR.json"
bin_file = "../contracts/BalancerFLR.bin"

sel = input('\nSelect chain:\n  0 = ethereum mainnet\n  1 = pulsechain mainnet\n  > ')
assert int(sel) == 0 or int(sel) == 1, 'Invalid entry, abort'
(RPC_URL, CHAIN_ID) = (env.eth_main, env.eth_main_cid) if int(sel) == 0 else (env.pc_main, env.pc_main_cid)

sel = input(f'\nSelect sender:\n  0 = {env.sender_address_3}\n  1 = {env.sender_address_1}\n  > ')
assert int(sel) == 0 or int(sel) == 1, 'Invalid entry, abort'
(SENDER_ADDRESS, SENDER_SECRET) = (env.sender_address_3, env.sender_secret_3) if int(sel) == 0 else (env.sender_address_1, env.sender_secret_1)

print(f'''\nINITIALIZING web3 ...
    RPC: {RPC_URL}
    ChainID: {CHAIN_ID}
    SENDER: {SENDER_ADDRESS}''')
W3 = Web3(HTTPProvider(RPC_URL))
    
print(f'\nDEPLOYING bytecode: {bin_file}')
print(f'DEPLOYING abi: {abi_file}')

if int(sel) == 0:
    # ethereum main net
    GAS_LIMIT = 3_000_000# max gas units to use for tx (required)
    GAS_PRICE = W3.to_wei('10', 'gwei') # price to pay for each unit of gas (optional?)
    MAX_FEE = W3.to_wei('14', 'gwei') # max fee per gas unit to pay (optional?)
    MAX_PRIOR_FEE_RATIO = 1.0 # W3.eth.max_priority_fee * mpf_ratio # max fee per gas unit to pay for priority (faster) (optional)
    MAX_PRIOR_FEE = int(W3.eth.max_priority_fee * MAX_PRIOR_FEE_RATIO) # max fee per gas unit to pay for priority (faster) (optional)
else:
    # pulsechain main net
    GAS_LIMIT = 20_000_000 # max gas units to use for tx (required)
    GAS_PRICE = W3.to_wei('0.0009', 'ether') # price to pay for each unit of gas (optional?)
    MAX_FEE = W3.to_wei('0.002', 'ether') # max fee per gas unit to pay (optional?)
    MAX_PRIOR_FEE_RATIO = 1.0
    MAX_PRIOR_FEE = int(W3.eth.max_priority_fee * MAX_PRIOR_FEE_RATIO) # max fee per gas unit to pay for priority (faster) (optional)
print(f'''\nSetting gas params ...
    GAS_LIMIT: {GAS_LIMIT}
    GAS_PRICE: {GAS_PRICE}
    MAX_FEE: {MAX_FEE}
    MAX_PRIOR_FEE: {MAX_PRIOR_FEE}''')

assert input('\n procced? [y/n]\n > ') == 'y', "aborted...\n"

print('\nreading bytecode file... '+bin_file)
with open(bin_file, "r") as file:
    CONTR_BYTES = file.read()
    CONTR_BYTES = '0x'+CONTR_BYTES
    
print('reading abi file... '+abi_file)
with open(abi_file, "r") as file:
    CONTR_ABI = file.read()

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

    print(f"\nEstimated gas cost: {gas_estimate}")

    # Optionally, you can also estimate the gas price (in Gwei) using a gas price strategy
    # Replace 'fast' with other strategies like 'medium' or 'slow' as needed
    #gas_price = W3.eth.generateGasPrice(fast_gas_price_strategy)
    #print(f"Estimated gas price (Gwei): {W3.fromWei(gas_price, 'gwei')}")
    
    proc = input('\n procced? [y/n]\n > ')
    return proc == 'y'

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

#print('reading abi file... '+abi_file)
#with open(abi_file, "r") as file:
#    CONTR_ABI = file.read()
#
#print('reading bytecode file... '+bin_file)
#with open(bin_file, "r") as file:
#    CONTR_BYTES = file.read()

print('intializing contract to deploy...')
balancer_flr = W3.eth.contract(
    abi=CONTR_ABI,
    bytecode=CONTR_BYTES
)

print('calculating gas...')
tx_params = {
    'chainId': CHAIN_ID,
    'nonce': W3.eth.getTransactionCount(SENDER_ADDRESS),
}
lst_gas_params = get_gas_params_lst(RPC_URL, min_params=False, max_params=True, def_params=True)
for d in lst_gas_params: tx_params.update(d) # append gas params

print('building tx...')
constructor_tx = balancer_flr.constructor().buildTransaction(tx_params)

print('signing and sending tx...')
# Sign and send the transaction # Deploy the contract
tx_signed = W3.eth.account.signTransaction(constructor_tx, private_key=SENDER_SECRET)
tx_hash = W3.eth.sendRawTransaction(tx_signed.rawTransaction)

print('waiting for receipt...')
print(f'tx_hash: {tx_hash.hex()}')
# Wait for the transaction to be mined
receipt = W3.eth.waitForTransactionReceipt(tx_hash)
print(f'RECEIPT:\n {receipt}')
contract_address = receipt['contractAddress']
print(f'\n\n Contract deployed at address: {contract_address}\n\n')
