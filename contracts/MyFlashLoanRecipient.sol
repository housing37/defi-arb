// house_102523 _ ref: https://docs.balancer.fi/reference/contracts/flash-loans.html#example-code
// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity ^0.7.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
//    IERC20(_tokenIn).approve(address(uniswapRouter), _amountIn);

import "@balancer-labs/v2-interfaces/contracts/vault/IVault.sol";
import "@balancer-labs/v2-interfaces/contracts/vault/IFlashLoanRecipient.sol";

/// @title Router token swapping functionality
/// @notice Functions for swapping tokens via Uniswap V3
interface ISwapRouter is IUniswapV3SwapCallback {
    struct ExactInputSingleParams {
        address tokenIn;
        address tokenOut;
        uint24 fee;
        address recipient;
        uint256 deadline;
        uint256 amountIn;
        uint256 amountOutMinimum;
        uint160 sqrtPriceLimitX96;
    }

    /// @notice Swaps `amountIn` of one token for as much as possible of another token
    /// @param params The parameters necessary for the swap, encoded as `ExactInputSingleParams` in calldata
    /// @return amountOut The amount of the received token
    function exactInputSingle(ExactInputSingleParams calldata params) external payable returns (uint256 amountOut);

    struct ExactInputParams {
        bytes path;
        address recipient;
        uint256 deadline;
        uint256 amountIn;
        uint256 amountOutMinimum;
    }

    /// @notice Swaps `amountIn` of one token for as much as possible of another along the specified path
    /// @param params The parameters necessary for the multi-hop swap, encoded as `ExactInputParams` in calldata
    /// @return amountOut The amount of the received token
    function exactInput(ExactInputParams calldata params) external payable returns (uint256 amountOut);

    struct ExactOutputSingleParams {
        address tokenIn;
        address tokenOut;
        uint24 fee;
        address recipient;
        uint256 deadline;
        uint256 amountOut;
        uint256 amountInMaximum;
        uint160 sqrtPriceLimitX96;
    }

    /// @notice Swaps as little as possible of one token for `amountOut` of another token
    /// @param params The parameters necessary for the swap, encoded as `ExactOutputSingleParams` in calldata
    /// @return amountIn The amount of the input token
    function exactOutputSingle(ExactOutputSingleParams calldata params) external payable returns (uint256 amountIn);

    struct ExactOutputParams {
        bytes path;
        address recipient;
        uint256 deadline;
        uint256 amountOut;
        uint256 amountInMaximum;
    }

    /// @notice Swaps as little as possible of one token for `amountOut` of another along the specified path (reversed)
    /// @param params The parameters necessary for the multi-hop swap, encoded as `ExactOutputParams` in calldata
    /// @return amountIn The amount of the input token
    function exactOutput(ExactOutputParams calldata params) external payable returns (uint256 amountIn);
}

// house_102423 (not tested)
interface IUniswapV2 {
    function swapExactTokensForTokens(
        uint amountIn,
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    ) external returns (uint[] memory amounts);
    function swapTokensForExactTokens(
        uint amountOut,
        uint amountInMax,
        address[] calldata path,
        address to,
        uint deadline
    ) external returns (uint[] memory amounts);
}

contract FlashLoanRecipient is IFlashLoanRecipient {
    IVault private constant vault = IVault(0xBA12222222228d8Ba445958a75a0704d566BF2C8);

    function makeFlashLoan(
        IERC20[] memory tokens,
        uint256[] memory amounts,
        bytes memory userData
    ) external {
      vault.flashLoan(this, tokens, amounts, userData);
    }

    function receiveFlashLoan(
        IERC20[] memory tokens,
        uint256[] memory amounts,
        uint256[] memory feeAmounts,
        bytes memory userData
    ) external override {
        require(msg.sender == address(vault));
        (address router, address tokenA, address tokenB, uint256 amountToSwap) = abi.decode(userData, (address, address, address, uint256));
        
        // check for uniswap v2|v3
        if (router == address(0xE592427A0AEce92De3Edee1F18E0157C05861564)) {
            // v3: uniswap v3
            ISwapRouter swapRouter = ISwapRouter(router)
        } else {
            // v2: solidlycom, kyberswap, pancakeswap, sushiswap, uniswap v2, pulsex v1|v2
            IUniswapV2 swapRouter = IUniswapV2(router)
        }
            
        // approve for payback when execution finished
        //  init testing: return immediately (payback right away; req funds in this contract)
        uint256 amountOwed = amounts[0] + feeAmounts[0];
        IERC20(asset).approve(address(vault), amountOwed);
        
        // ...
        
        // house_102423 swap logic
        IPulseXRouter router_v1 = IPulseXRouter(0x98bf93ebf5c380C0e6Ae8e192A7e2AE08edAcc02);
        IPulseXRouter router_v2 = IPulseXRouter(0x165C3410fC91EF562C50559f7d2289fEbed552d9);
        
        // fraxswap
        
        // radioshack
        
        // found in logs
        //  0xcBAE5C3f8259181EB7E2309BC4c72fDF02dD56D8
        //  0x03407772F5EBFB9B10Df007A2DD6FFf4EdE47B53
        //  0x564C4529E12FB5a48AD609820D37D15800c1f539
        // 	0x696708Db871B77355d6C2bE7290B27CF0Bb9B24b
        
        // balancer (ref: https://docs.balancer.fi/reference/contracts/deployment-addresses/mainnet.html)
        //  don't see 'router' address anywhere
        //  found discord and asked for support
        
        // defiswap (ref: https://docs.defiswap.io/developer/smart-contracts)
        //  can only find BSC: https://bscscan.com/address/0xeb33cbbe6f1e699574f10606ed9a495a196476df#writeContract
        //  found discord and asked for support (https://discord.com/invite/UjTUyN6qhx)
        
        // shibaswap
        //  found: https://docs.shibatoken.com/shibaswap and https://shibaswap.com/#/
        //      not sure which one is right
        //  found discord and opened support request
        //  found pdf on one of the sites above with 'MULTISIGADDRESSES' (i dunno)
        //      ref: https://github.com/shytoshikusama/woofwoofpaper/raw/main/SHIBA_INU_WOOF_WOOF.pdf
        
        // verse (ref: https://docs.swapverse.exchange/ & https://twitter.com/Swapverse_)
        //  can't find discord or list of contract addresses
        
        // uniswap v3
        //  ref: https://docs.uniswap.org/contracts/v3/reference/deployments
        //  ref: https://github.com/Uniswap/v3-periphery/blob/v1.0.0/contracts/SwapRouter.sol
        0xE592427A0AEce92De3Edee1F18E0157C05861564 // SwapRouter
        
        // uniswap v2
        //  ref: https://docs.uniswap.org/contracts/v2/reference/smart-contracts/router-02
        0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D // 'UniswapV2Router02'
        
        // solidlycom (ref: https://docs.solidly.com/resources/contract-addresses)
        //  ref: https://etherscan.io/address/0x77784f96C936042A3ADB1dD29C91a55EB2A4219f#writeProxyContract
        0x77784f96C936042A3ADB1dD29C91a55EB2A4219f // Router ('v2 contracts')
        
        // kyberswap (ref: https://docs.kyberswap.com/liquidity-solutions/kyberswap-classic/contracts/classic-contract-addresses)
        //  ref: https://etherscan.io/address/0x1c87257F5e8609940Bc751a07BB085Bb7f8cDBE6#writeContract
        //  ref: https://etherscan.io/address/0x5649B4DD00780e99Bab7Abb4A3d581Ea1aEB23D0#code
        //  found discord and asked for support: forward me to ask Q -> https://support.kyberswap.com/hc/en-us/requests/new
        0x1c87257F5e8609940Bc751a07BB085Bb7f8cDBE6 // DMMRouter ('Dynamic Fee')
        0x5649B4DD00780e99Bab7Abb4A3d581Ea1aEB23D0 // KSRouter ('Static Fee')
        0x5F1dddbf348aC2fbe22a163e30F99F9ECE3DD50a // found in logs (etherscan.io say kyberswap)
        
        // pancakeswap (verified on discord)
        //  ref: https://etherscan.io/address/0x13f4EA83D0bd40E75C8222255bc855a974568Dd4#writeContract
        //  ref: https://etherscan.io/address/0x10ed43c718714eb63d5aa57b78b54704e256024e
        0x13f4EA83D0bd40E75C8222255bc855a974568Dd4 // ethereum: v3
        0x10ED43C718714eb63d5aA57B78B54704E256024E // ethereum: v2
        
        // sushiswap (verified on discord)
        //  ref: https://docs.sushi.com/docs/Developers/Deployment%20Addresses
        //  ref: https://etherscan.io/address/0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F#writeContract
        //  found V2Router02, and asked support for v3 in discord
        0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F // ethereum: V2Router02 'specifically for v2 pools'
        //0x02a480a258361c9bc3eaacbd6473364c67adcd3a // sushiswap AxelarAdapter has swap function _ ref: https://github.com/sushiswap
        //0x580ED43F3BBa06555785C81c2957efCCa71f7483 // sushiswap StargateAdapter has swap function _ ref: https://github.com/sushiswap
        //0x804b526e5bF4349819fe2Db65349d0825870F8Ee // sushiswap SushiXSwapV2 has swap function _ ref: https://github.com/sushiswap
        //0xc5578194D457dcce3f272538D1ad52c68d1CE849 // sushiswap i dunno
        //0x827179dD56d07A7eeA32e3873493835da2866976 // sushiswap 'RouteProcessor3'
        //0x011E52E4E40CF9498c79273329E8827b21E2e581 // sushiswap 'SushiXSwap'
        
        // TODO: integrate swap logic
        //  swap token A for token B, on router 1
        //  swap token B for token A, on router 2
        // 	pay back loan + interest
        

    }
}
