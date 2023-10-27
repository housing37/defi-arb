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

contract BalancerFlashLoanRecipient is IFlashLoanRecipient {
    IVault private constant vault = IVault(0xBA12222222228d8Ba445958a75a0704d566BF2C8);
    address private constant uniswapRouterV3 = address(0xE592427A0AEce92De3Edee1F18E0157C05861564)
    
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
        (address router_0, address router_1, address[] path_0, address[] path_1, uint256 amntOutMin_0, uint256 amntOutMin_1) = abi.decode(userData, (address, address, address[], address[], uint256, uint256));
        
        // approve for payback when execution finished
        //  init testing: return immediately (payback right away; req funds in this contract)
        uint256 amountOwed = amounts[0] + feeAmounts[0];
        IERC20(asset).approve(address(vault), amountOwed);
        
        uint256 amntOut = 0
        
        
        // check for uniswap v3 integration (requires bytes memory 'path' param)
        if (router_0 == uniswapRouterV3) {
            // convert path to bytes memory
            bytes memory bytes_path = addressesToBytes(path_0)
            amntOut = swap_v3(router_0, bytes_path, 1, uint256 amntOutMin_0)
        } else {
            // found uniswap v2 protocol integration
            amntOut = swap_v2(router_0, path_0, 1, amntOutMin_0)
        }
        
        // check for uniswap v3 integration (requires bytes memory 'path' param)
        if (router_1 == uniswapRouterV3) {
            // convert path to bytes memory
            bytes_path = addressesToBytes(path_1)
            amntOut = swap_v3(router_1, bytes_path, amntOut, amntOutMin_1)
        } else {
            // found uniswap v2 protocol integration
            amntOut = swap_v2(router_1, path_1, amntOut, amntOutMin_1)
        }
    }
    
    function swap_v3(address router, bytes memory path, uint256 amntIn, uint256 amntOutMin) private returns (uint256) {
        // v3: uniswap v3
        ISwapRouter constant swapRouter = ISwapRouter(router)
        IERC20(address(this)).approve(address(swapRouter), amntIn);
        deadline = block.timestamp + 300;
        ISwapRouter.ExactInputParams memory params = ISwapRouter.ExactInputParams({
            path: path,
            recipient: address(this),
            deadline: deadline,
            amountIn: amntIn,
            amountOutMinimum: amntOutMin
        });
        amntOut = swapRouter.exactInput(params);
        return amntOut;
    }
    
    function swap_v2(address router, address[] path, uint256 amntIn, uint256 amntOutMin) private returns (uint256) {
        // v2: solidlycom, kyberswap, pancakeswap, sushiswap, uniswap v2, pulsex v1|v2
        IUniswapV2 constant swapRouter = IUniswapV2(router)
        IERC20(address(this)).approve(address(swapRouter), amntIn);
        deadline = block.timestamp + 300;
        amntOut = swapExactTokensForTokens(
                        amntIn,
                        amntOutMin,
                        path, //address[] calldata path,
                        address(this),
                        deadline
                    );
        return amntOut;
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
//struct ExactOutputParams {
//    bytes path;
//    address recipient;
//    uint256 deadline;
//    uint256 amountOut;
//    uint256 amountInMaximum;
//}
//
//struct ExactInputParams {
//    bytes path;
//    address recipient;
//    uint256 deadline;
//    uint256 amountIn;
//    uint256 amountOutMinimum;
//}


        
// TODO: integrate swap logic
//  swap token A for token B, on router 1
//  swap token B for token A, on router 2
// 	pay back loan + interest

