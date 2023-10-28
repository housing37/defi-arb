from web3 import Web3, HTTPProvider
import env

print('getting keys and intializing web3...')
SENDER_ADDRESS = env.sender_address_1 # default
SENDER_SECRET = env.sender_secret_1 # default

# Connect to a local Ethereum node or a remote one
#w3 = Web3(HTTPProvider('http://localhost:8545'))
#w3 = Web3(HTTPProvider(f'https://mainnet.infura.io/v3/{env.ETH_MAIN_RPC_KEY}'))
#w3 = Web3(HTTPProvider(f'https://goerli.infura.io/v3/'))
W3 = Web3(HTTPProvider(f'https://rpc.pulsechain.com'))

# note: params checked/set in priority order; 'def|max_params' uses 'mpf_ratio'
#   if all params == False, falls back to 'min_params=True' (ie. just use 'gas_limit')
def get_gas_params_lst(min_params=False, max_params=False, def_params=True, mpf_ratio=1.0):
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
        

abi_file = "../contracts/BalancerFLR.json"
print('reading abi file... '+abi_file)
with open(abi_file, "r") as file:
    CONTR_ABI = file.read()
    
bin_file = "../contracts/BalancerFLR.bin"
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
    #'chainId': 1,  # ethereum Mainnet
    #'chainId': 5,  # goerli ethereum testnet
    #'gasPrice': w3.toWei('20', 'gwei'),
    
    'chainId': 369,  # pulsechain Mainnet
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
