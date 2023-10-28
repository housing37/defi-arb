from web3 import Web3, HTTPProvider
from web3.middleware import construct_sign_and_send_raw_middleware
from web3.gas_strategies.time_based import fast_gas_price_strategy
import env

print('getting keys and intializing web3...')
SENDER_ADDRESS = env.sender_address_1 # deploy from
SENDER_SECRET = env.sender_secret_1 # deploy from
#SENDER_ADDRESS = env.sender_address_2 # deploy from
#SENDER_SECRET = env.sender_secret_2 # deploy from

# Connect to a local Ethereum node or a remote one
local_test = 'http://localhost:8545'
eth_main = f'https://mainnet.infura.io/v3/{env.ETH_MAIN_RPC_KEY}'
eth_test = f'https://goerli.infura.io/v3/'
pc_main = f'https://rpc.pulsechain.com'
eth_main_cid=1
pc_main_cid=369
#NET_URL = eth_main
#CHAIN_ID = eth_main_cid
NET_URL = pc_main
CHAIN_ID = pc_main_cid

print(f'DEPLOYING to: {NET_URL}')
W3 = Web3(HTTPProvider(NET_URL))

abi_file = "../contracts/BalancerFLR.json"
bin_file = "../contracts/BalancerFLR.bin"

print('reading abi file... '+abi_file)
with open(abi_file, "r") as file:
    CONTR_ABI = file.read()

print('reading bytecode file... '+bin_file)
with open(bin_file, "r") as file:
    CONTR_BYTES = file.read()
    CONTR_BYTES = '0x'+CONTR_BYTES

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

    print(f"Estimated gas cost: {gas_estimate}")

    # Optionally, you can also estimate the gas price (in Gwei) using a gas price strategy
    # Replace 'fast' with other strategies like 'medium' or 'slow' as needed
#    gas_price = W3.eth.generateGasPrice(fast_gas_price_strategy)
#
#    print(f"Estimated gas price (Gwei): {W3.fromWei(gas_price, 'gwei')}")
    
    proc = input('\n procced? [y/n]\n > ')
    return proc == 'y'

# note: params checked/set in priority order; 'def|max_params' uses 'mpf_ratio'
#   if all params == False, falls back to 'min_params=True' (ie. just use 'gas_limit')
def get_gas_params_lst(min_params=False, max_params=False, def_params=True, mpf_ratio=1.0):
    global NET_URL
    
    # Estimate the gas cost for the transaction
    #gas_estimate = buy_tx.estimate_gas()
    if NET_URL == pc_main:
        gas_limit = 20_000_000 # max gas units to use for tx (required)
        gas_price = W3.to_wei('0.0009', 'ether') # price to pay for each unit of gas (optional)
        max_fee = W3.to_wei('0.002', 'ether') # max fee per gas unit to pay (optional)
        max_prior_fee = int(W3.eth.max_priority_fee * mpf_ratio) # max fee per gas unit to pay for priority (faster) (optional)
        #max_priority_fee = W3.to_wei('0.000000003', 'ether')
    
    if NET_URL == eth_main:
        # 102823
        #   -1327: eth main -> FAIELD - $9 and ran out of gass
        #gas_limit = 60_000 # max gas units to use for tx (required)
        gas_limit = 2_000_000 # max gas units to use for tx (required)
        gas_price = W3.to_wei('13', 'gwei') # price to pay for each unit of gas (optional?)
        max_fee = W3.to_wei('18', 'gwei') # max fee per gas unit to pay (optional?)
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
        
proceed = estimate_gas()
assert proceed, "\ndeployment canceled after gas estimate\n"

print('reading abi file... '+abi_file)
with open(abi_file, "r") as file:
    CONTR_ABI = file.read()

print('reading bytecode file... '+bin_file)
with open(bin_file, "r") as file:
    CONTR_BYTES = file.read()

print('intializing contract...')
balancer_flr = W3.eth.contract(
    abi=CONTR_ABI,
    bytecode=CONTR_BYTES
)

print('calculating gas...')
tx_params = {
    'chainId': CHAIN_ID,
    'nonce': W3.eth.getTransactionCount(SENDER_ADDRESS),
}
lst_gas_params = get_gas_params_lst(min_params=False, max_params=True, def_params=True, mpf_ratio=1.0)
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
