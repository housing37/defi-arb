# Certainly! Here's the complete example with the corrected MyContract constructor 
#  included and the deployment script using the buildTransaction approach in Python:
from web3 import Web3
from solcx import compile_standard

# Define the contract source code
mathlib_source = '''
// MathLib.sol
pragma solidity ^0.8.0;

library MathLib {
    function add(uint256 a, uint256 b) external pure returns (uint256) {
        return a + b;
    }
}
'''

mycontract_source = '''
// MyContract.sol
pragma solidity ^0.8.0;

import "./MathLib.sol";

contract MyContract {
    MathLib public mathLibInstance;

    constructor(address mathLibAddress) {
        // Link to the deployed MathLib
        mathLibInstance = MathLib(mathLibAddress);
    }

    function addNumbers(uint256 a, uint256 b) external view returns (uint256) {
        // Use the library function
        return mathLibInstance.add(a, b);
    }
}
'''

# Compile the contracts
compiled_mathlib = compile_standard({
    "language": "Solidity",
    "sources": {"MathLib.sol": {"content": mathlib_source}},
    "settings": {"outputSelection": {"*": {"*": ["abi", "evm.bytecode"]}}},
})

compiled_mycontract = compile_standard({
    "language": "Solidity",
    "sources": {"MyContract.sol": {"content": mycontract_source}},
    "settings": {"outputSelection": {"*": {"*": ["abi", "evm.bytecode"]}}},
})

# Connect to a local Ethereum node (change the URL accordingly)
w3 = Web3(Web3.HTTPProvider("http://localhost:8545"))

# Deploy both contracts together
mathlib_contract = w3.eth.contract(abi=compiled_mathlib["contracts"]["MathLib.sol:MathLib"]["abi"], bytecode=compiled_mathlib["contracts"]["MathLib.sol:MathLib"]["evm"]["bytecode"]["object"])
mycontract_contract = w3.eth.contract(abi=compiled_mycontract["contracts"]["MyContract.sol:MyContract"]["abi"], bytecode=compiled_mycontract["contracts"]["MyContract.sol:MyContract"]["evm"]["bytecode"]["object"])

# Build transaction for MathLib deployment
mathlib_txn = mathlib_contract.constructor().buildTransaction({
    'from': w3.eth.accounts[0],
    'gas': 2000000,
    'gasPrice': w3.toWei('50', 'gwei'),
    'nonce': w3.eth.getTransactionCount(w3.eth.accounts[0]),
})

# Sign and send MathLib deployment transaction
mathlib_signed_txn = w3.eth.account.sign_transaction(mathlib_txn, private_key='your_private_key')
mathlib_tx_hash = w3.eth.sendRawTransaction(mathlib_signed_txn.rawTransaction)
mathlib_tx_receipt = w3.eth.waitForTransactionReceipt(mathlib_tx_hash)
mathlib_address = mathlib_tx_receipt["contractAddress"]

# Build transaction for MyContract deployment and link to MathLib
mycontract_txn = mycontract_contract.constructor(mathlib_address).buildTransaction({
    'from': w3.eth.accounts[0],
    'gas': 2000000,
    'gasPrice': w3.toWei('50', 'gwei'),
    'nonce': w3.eth.getTransactionCount(w3.eth.accounts[0]),
})

# Sign and send MyContract deployment transaction
mycontract_signed_txn = w3.eth.account.sign_transaction(mycontract_txn, private_key='your_private_key')
mycontract_tx_hash = w3.eth.sendRawTransaction(mycontract_signed_txn.rawTransaction)
mycontract_tx_receipt = w3.eth.waitForTransactionReceipt(mycontract_tx_hash)
mycontract_address = mycontract_tx_receipt["contractAddress"]

print(f"MathLib deployed at address: {mathlib_address}")
print(f"MyContract deployed at address: {mycontract_address}")
