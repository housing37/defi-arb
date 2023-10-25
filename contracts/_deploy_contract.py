from web3 import Web3, HTTPProvider
from solc import compile_source

# Connect to a local Ethereum node or a remote one
w3 = Web3(HTTPProvider('http://localhost:8545'))

# Read the Solidity contract source code from a .sol file
#with open("HelloWorld.sol", "r") as file:
with open("MyFlashLoanRecipient.sol", "r") as file:
    contract_source_code = file.read()

compiled_sol = compile_source(contract_source_code)
#contract_interface = compiled_sol['<stdin>:HelloWorld']
contract_interface = compiled_sol['<stdin>:FlashLoanRecipient']

# Set the default account to your Ethereum address
w3.eth.default_account = w3.eth.accounts[0]

# Deploy the contract
HelloWorld = w3.eth.contract(
    abi=contract_interface['abi'],
    bytecode=contract_interface['bin']
)

# Transaction data
constructor_tx = HelloWorld.constructor().buildTransaction({
    'chainId': 1,  # Mainnet
    'gas': 2000000,  # You may need to adjust the gas limit
    'gasPrice': w3.toWei('20', 'gwei'),
    'nonce': w3.eth.getTransactionCount(w3.eth.default_account),
})

# Sign and send the transaction
constructor_tx_signed = w3.eth.account.signTransaction(constructor_tx, private_key='YOUR_PRIVATE_KEY')
tx_hash = w3.eth.sendRawTransaction(constructor_tx_signed.rawTransaction)

# Wait for the transaction to be mined
receipt = w3.eth.waitForTransactionReceipt(tx_hash)
contract_address = receipt['contractAddress']
print(f'Contract deployed at address: {contract_address}')
