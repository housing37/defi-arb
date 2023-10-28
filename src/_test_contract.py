## house_102823: test 'transferTokens' from deployed BalancerFLR.sol ##
from web3 import Web3, HTTPProvider
import env

print('getting keys and intializing web3...')
SENDER_ADDRESS = env.sender_address_1 # default
SENDER_SECRET = env.sender_secret_1 # default

addr_arb_contr = '0xFD2AaD9Ef84C001a3622188493A8AFd9436892c8'
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

# transfer pdai out
arb_contr.functions().transferTokens(addr_pdai, SENDER_ADDRESS, 1)

# check pdai balance again
pdai_bal = pdai_contr.functions.balanceOf(addr_arb_contr).call()
print(f'pdai balance: {pdai_bal}\n for contr: {addr_arb_contr}')

# check PLS balance
wei_bal = W3.eth.getBalance(addr_arb_contr)
eth_bal = W3.fromWei(wei_bal, 'ether')
print(f'PLS balance: {eth_bal}\n for contr: {addr_arb_contr')
