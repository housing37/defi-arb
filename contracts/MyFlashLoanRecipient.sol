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
        
        // approve for payback when execution finished
        //  init testing: return immediately (payback right away; req funds in this contract)
        uint256 amountOwed = amounts[0] + feeAmounts[0];
        IERC20(asset).approve(address(vault), amountOwed);
        
        // ...
        
        // house_102423 swap logic
        IPulseXRouter router_v1 = IPulseXRouter(0x98bf93ebf5c380C0e6Ae8e192A7e2AE08edAcc02);
        IPulseXRouter router_v2 = IPulseXRouter(0x165C3410fC91EF562C50559f7d2289fEbed552d9);
        
        // TODO: integrate swap logic
        //  swap token A for token B, on router 1
        //  swap token B for token A, on router 2
        // 	pay back loan + interest
        

    }
}
