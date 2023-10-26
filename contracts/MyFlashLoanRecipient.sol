// house_102523 _ ref: https://docs.balancer.fi/reference/contracts/flash-loans.html#example-code
// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity ^0.7.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
//    IERC20(_tokenIn).approve(address(uniswapRouter), _amountIn);

import "@balancer-labs/v2-interfaces/contracts/vault/IVault.sol";
import "@balancer-labs/v2-interfaces/contracts/vault/IFlashLoanRecipient.sol";

// house_102423 (not tested)
interface IPulseXRouter {
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
        (address tokenA, address tokenB, uint256 amountToSwap) = abi.decode(userData, (address, address, uint256));

        // approve for payback when execution finished
        //  init testing: return immediately (payback right away; req funds in this contract)
        uint256 amountOwed = amounts[0] + feeAmounts[0];
        IERC20(asset).approve(address(vault), amountOwed);
        
        // ...
        
        // house_102423 swap logic
        IPulseXRouter router_v1 = IPulseXRouter(0x98bf93ebf5c380C0e6Ae8e192A7e2AE08edAcc02);
        IPulseXRouter router_v2 = IPulseXRouter(0x165C3410fC91EF562C50559f7d2289fEbed552d9);
        
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
        
        // solidlycom (ref: https://docs.solidly.com/resources/contract-addresses)
        //  ref: https://etherscan.io/address/0x77784f96C936042A3ADB1dD29C91a55EB2A4219f#writeProxyContract
        0x77784f96C936042A3ADB1dD29C91a55EB2A4219f // Router ('v2 contracts')
        
        // kyberswap (ref: https://docs.kyberswap.com/liquidity-solutions/kyberswap-classic/contracts/classic-contract-addresses)
        //  ref: https://etherscan.io/address/0x1c87257F5e8609940Bc751a07BB085Bb7f8cDBE6#writeContract
        //  ref: https://etherscan.io/address/0x5649B4DD00780e99Bab7Abb4A3d581Ea1aEB23D0#code
        //  found discord and asked for support: forward me to ask Q -> https://support.kyberswap.com/hc/en-us/requests/new
        0x1c87257F5e8609940Bc751a07BB085Bb7f8cDBE6 // DMMRouter ('Dynamic Fee')
        0x5649B4DD00780e99Bab7Abb4A3d581Ea1aEB23D0 // KSRouter ('Static Fee')
        
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
