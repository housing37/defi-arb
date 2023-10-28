// house_102523 _ ref: https://docs.balancer.fi/reference/contracts/flash-loans.html#example-code
// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity ^0.8.22;

import "@balancer-labs/v2-interfaces/contracts/vault/IVault.sol";
import "@balancer-labs/v2-interfaces/contracts/vault/IFlashLoanRecipient.sol";
import {ISwapRouter} from "https://github.com/Uniswap/v3-periphery/blob/v1.2.0/contracts/interfaces/ISwapRouter.sol";

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

contract BalancerFLR is IFlashLoanRecipient {
    // ref: https://docs.balancer.fi/reference/contracts/flash-loans.html#example-code
    IVault private constant vault = IVault(0xBA12222222228d8Ba445958a75a0704d566BF2C8);
    address private constant uniswapRouterV3 = address(0xE592427A0AEce92De3Edee1F18E0157C05861564);
    address private _owner;
    
    constructor() {
        _owner = msg.sender;
    }

    function makeFlashLoan(
        IERC20[] memory tokens,
        uint256[] memory amounts,
        bytes memory userData
    ) external {
        require(msg.sender == _owner, "loan to owner only");
        vault.flashLoan(this, tokens, amounts, userData);
    }
    
    function receiveFlashLoan(
        IERC20[] memory tokens,
        uint256[] memory amounts,
        uint256[] memory feeAmounts,
        bytes memory userData
    ) external override {
        require(msg.sender == address(vault), "loan from vault only");
        (address router_0, address router_1, address[] memory path_0, address[] memory path_1, uint256 amntIn_0, uint256 amntOutMin_1) = abi.decode(userData, (address, address, address[], address[], uint256, uint256));
        
        // approve for payback when execution finished
        //  init testing: return immediately (payback right away; req funds in this contract)
        uint256 amountOwed = amounts[0] + feeAmounts[0];
        // IERC20(asset).approve(address(vault), amountOwed);
        tokens[0].approve(address(vault), amountOwed);
        
        // uint[] memory amntOut_v2;
        uint256 amntOut;
        
        // check for uniswap v3 integration (requires bytes memory 'path' param)
        if (router_0 == uniswapRouterV3) {
            // convert path to bytes memory
            bytes memory bytes_path = addressesToBytes(path_0);
            amntOut = swap_v3(router_0, bytes_path, amntIn_0, 1);
        } else {
            // found uniswap v2 protocol integration
            amntOut = swap_v2(router_0, path_0, amntIn_0, 1);
        }
        
        // check for uniswap v3 integration (requires bytes memory 'path' param)
        if (router_1 == uniswapRouterV3) {
            // convert path to bytes memory
            bytes memory bytes_path = addressesToBytes(path_1);
            amntOut = swap_v3(router_1, bytes_path, amntOut, amntOutMin_1);
        } else {
            // found uniswap v2 protocol integration
            amntOut = swap_v2(router_1, path_1, amntOut, amntOutMin_1);
        }
    }
    
    receive() external payable {}
    
    // Function to transfer ERC20 tokens to a target address
    function transferTokens(address token, address to, uint256 amount) external {
        // Check that the caller is the owner or has the appropriate permissions
        require(msg.sender == _owner, "only owner");
        
        // Create an instance of the ERC20 token
        IERC20 tok = IERC20(token);

        // Check the contract's balance of the token
        uint256 contractBalance = tok.balanceOf(address(this));
        require(contractBalance >= amount, "Insufficient balance in the contract");

        // Transfer tokens to the target address
        tok.transfer(to, amount);
    }
    
    function swap_v3(address router, bytes memory path, uint256 amntIn, uint256 amntOutMin) private returns (uint256) {
        // v3: uniswap v3
        // ISwapRouter constant swapRouter = ISwapRouter(router);
        ISwapRouter swapRouter = ISwapRouter(router);
        IERC20(address(this)).approve(address(swapRouter), amntIn);
        uint deadline = block.timestamp + 300;
        ISwapRouter.ExactInputParams memory params = ISwapRouter.ExactInputParams({
            path: path,
            recipient: address(this),
            deadline: deadline,
            amountIn: amntIn,
            amountOutMinimum: amntOutMin
        });
        uint256 amntOut = swapRouter.exactInput(params);
        return amntOut;
    }
    
    function swap_v2(address router, address[] memory path, uint256 amntIn, uint256 amntOutMin) private returns (uint256) {
        // v2: solidlycom, kyberswap, pancakeswap, sushiswap, uniswap v2, pulsex v1|v2
        // IUniswapV2 constant swapRouter = IUniswapV2(router);
        IUniswapV2 swapRouter = IUniswapV2(router);
        IERC20(address(this)).approve(address(swapRouter), amntIn);
        uint deadline = block.timestamp + 300;
        uint[] memory amntOut = swapRouter.swapExactTokensForTokens(
                        amntIn,
                        amntOutMin,
                        path, //address[] calldata path,
                        address(this),
                        deadline
                    );
        return uint256(amntOut[1]); // idx 0=amntIn, 1=amntOut
    }
    
    function addressesToBytes(address[] memory addresses) private pure returns (bytes memory) {
        bytes memory result = new bytes(addresses.length * 20); // Each address is 20 bytes long

        for (uint256 i = 0; i < addresses.length; i++) {
            // Convert each address to bytes and copy it into the result
            bytes20 addressBytes = bytes20(addresses[i]);
            for (uint256 j = 0; j < 20; j++) {
                result[i * 20 + j] = addressBytes[j];
            }
        }

        return result;
    }
}
