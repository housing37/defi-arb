// house_102523 _ ref: https://docs.balancer.fi/reference/contracts/flash-loans.html#example-code
// SPDX-License-Identifier: GPL-2.0-or-later
// pragma solidity ^0.8.20;
// pragma solidity ^0.7.0;
pragma solidity ^0.8.22;

// import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
// import {IERC20} from "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/IERC20.sol";
//    IERC20(_tokenIn).approve(address(uniswapRouter), _amountIn);

import "@balancer-labs/v2-interfaces/contracts/vault/IVault.sol";
import "@balancer-labs/v2-interfaces/contracts/vault/IFlashLoanRecipient.sol";
// import {IFlashLoanRecipient} from "https://github.com/balancer/balancer-v2-monorepo/blob/master/pkg/interfaces/contracts/vault/IFlashLoanRecipient.sol";
// import {IVault, IFlashLoanRecipient} from "https://github.com/balancer/balancer-v2-monorepo/blob/master/pkg/interfaces/contracts/vault/IVault.sol";
// import {IVault} from "https://github.com/balancer/balancer-v2-monorepo/blob/master/pkg/interfaces/contracts/vault/IVault.sol";
import {ISwapRouter} from "https://github.com/Uniswap/v3-periphery/blob/v1.2.0/contracts/interfaces/ISwapRouter.sol";
// import {IERC20} from "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/IERC20.sol";
// import {IFlashLoanRecipient} from "https://github.com/balancer/balancer-v2-monorepo/blob/master/pkg/interfaces/contracts/vault/IFlashLoanRecipient.sol";
// interface IFlashLoanRecipient {
//     /**
//      * @dev When `flashLoan` is called on the Vault, it invokes the `receiveFlashLoan` hook on the recipient.
//      *
//      * At the time of the call, the Vault will have transferred `amounts` for `tokens` to the recipient. Before this
//      * call returns, the recipient must have transferred `amounts` plus `feeAmounts` for each token back to the
//      * Vault, or else the entire flash loan will revert.
//      *
//      * `userData` is the same value passed in the `IVault.flashLoan` call.
//      */
//     function receiveFlashLoan(
//         IERC20[] memory tokens,
//         uint256[] memory amounts,
//         uint256[] memory feeAmounts,
//         bytes memory userData
//     ) external;
// }
/// @title Router token swapping functionality
/// @notice Functions for swapping tokens via Uniswap V3
//interface ISwapRouter is IUniswapV3SwapCallback {
//    struct ExactInputSingleParams {
//        address tokenIn;
//        address tokenOut;
//        uint24 fee;
//        address recipient;
//        uint256 deadline;
//        uint256 amountIn;
//        uint256 amountOutMinimum;
//        uint160 sqrtPriceLimitX96;
//    }
//
//    /// @notice Swaps `amountIn` of one token for as much as possible of another token
//    /// @param params The parameters necessary for the swap, encoded as `ExactInputSingleParams` in calldata
//    /// @return amountOut The amount of the received token
//    function exactInputSingle(ExactInputSingleParams calldata params) external payable returns (uint256 amountOut);
//
//    struct ExactInputParams {
//        bytes path;
//        address recipient;
//        uint256 deadline;
//        uint256 amountIn;
//        uint256 amountOutMinimum;
//    }
//
//    /// @notice Swaps `amountIn` of one token for as much as possible of another along the specified path
//    /// @param params The parameters necessary for the multi-hop swap, encoded as `ExactInputParams` in calldata
//    /// @return amountOut The amount of the received token
//    function exactInput(ExactInputParams calldata params) external payable returns (uint256 amountOut);
//
//    struct ExactOutputSingleParams {
//        address tokenIn;
//        address tokenOut;
//        uint24 fee;
//        address recipient;
//        uint256 deadline;
//        uint256 amountOut;
//        uint256 amountInMaximum;
//        uint160 sqrtPriceLimitX96;
//    }
//
//    /// @notice Swaps as little as possible of one token for `amountOut` of another token
//    /// @param params The parameters necessary for the swap, encoded as `ExactOutputSingleParams` in calldata
//    /// @return amountIn The amount of the input token
//    function exactOutputSingle(ExactOutputSingleParams calldata params) external payable returns (uint256 amountIn);
//
//    struct ExactOutputParams {
//        bytes path;
//        address recipient;
//        uint256 deadline;
//        uint256 amountOut;
//        uint256 amountInMaximum;
//    }
//
//    /// @notice Swaps as little as possible of one token for `amountOut` of another along the specified path (reversed)
//    /// @param params The parameters necessary for the multi-hop swap, encoded as `ExactOutputParams` in calldata
//    /// @return amountIn The amount of the input token
//    function exactOutput(ExactOutputParams calldata params) external payable returns (uint256 amountIn);
//}

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
    address private constant uniswapRouterV3 = address(0xE592427A0AEce92De3Edee1F18E0157C05861564);
    
    // ref: https://docs.balancer.fi/reference/contracts/flash-loans.html#example-code
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
    // ) external {
        require(msg.sender == address(vault));
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
            uint[] memory amntOut_v2 = swap_v2(router_0, path_0, amntIn_0, 1);
            amntOut = uint256(amntOut_v2[1]); // idx 0=amntIn, 1=amntOut
        }
        
        // check for uniswap v3 integration (requires bytes memory 'path' param)
        if (router_1 == uniswapRouterV3) {
            // convert path to bytes memory
            bytes memory bytes_path = addressesToBytes(path_1);
            amntOut = swap_v3(router_1, bytes_path, amntOut, amntOutMin_1);
        } else {
            // found uniswap v2 protocol integration
            uint[] memory amntOut_v2 = swap_v2(router_1, path_1, amntOut, amntOutMin_1);
            amntOut = uint256(amntOut_v2[1]); // idx 0=amntIn, 1=amntOut
        }
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
    
    function swap_v2(address router, address[] memory path, uint256 amntIn, uint256 amntOutMin) private returns (uint[] memory) {
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

    function convertToUint256(uint[] memory arr, uint index) private pure returns (uint256) {
        require(index < arr.length, "Index out of bounds");
        return uint256(arr[index]);
    }
}
