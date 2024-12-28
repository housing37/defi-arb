from web3 import Web3
import pprint

# Function signatures
function_signatures = [
    # uniswapv2 add/remove liqduity functions
    "addLiquidityETH(address,uint256,uint256,uint256,address,uint256)",
    "addLiquidity(address,address,uint256,uint256,uint256,uint256,address,uint256)",
    "removeLiquidityETH(address,uint256,uint256,uint256,address,uint256)",
    "removeLiquidityETHSupportingFeeOnTransferTokens(address,uint256,uint256,uint256,address,uint256)",
    "removeLiquidityETHWithPermit(address,uint256,uint256,uint256,address,uint256,bool)",
    "removeLiquidityETHWithPermitSupportingFeeOnTransferTokens(address,uint256,uint256,uint256,address,uint256,bool)",
    "removeLiquidity(address,address,uint256,uint256,uint256,address,uint256)",
    "removeLiquidityWithPermit(address,address,uint256,uint256,uint256,address,uint256,bool)",
]

# Compute selectors
# selectors = {sig: Web3.keccak(text=sig).hex()[:10] for sig in function_signatures}
selectors = {Web3.keccak(text=sig).hex()[:10]: sig for sig in function_signatures}
print(selectors)
print()
print()
# Pretty print the dictionary
pp = pprint.PrettyPrinter(indent=4)
pp.pprint(selectors)
