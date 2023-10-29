// house_102523 _ ref: https://docs.balancer.fi/reference/contracts/flash-loans.html#example-code
// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity ^0.8.22;

import "@balancer-labs/v2-interfaces/contracts/vault/IVault.sol";
import "@balancer-labs/v2-interfaces/contracts/vault/IFlashLoanRecipient.sol";
import {ISwapRouter} from "https://github.com/Uniswap/v3-periphery/blob/v1.2.0/contracts/interfaces/ISwapRouter.sol";

// house_102823 (testing...)
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
    address public _owner;
    
    event logX(address indexed contr, address sender, string message);
    event logRFL(address indexed contr, address sender, string message);
    event logMFL(address indexed contr, address sender, string message);

    constructor() {
        emit logX(address(this), msg.sender, "logX 0");
        _owner = msg.sender;
    }

    function makeFlashLoan(
        IERC20[] memory tokens,
        uint256[] memory amounts,
        bytes memory userData
    ) external {
        emit logMFL(address(this), msg.sender, "logMFL 0");
        require(msg.sender == _owner, "loan to owner only");
        emit logMFL(address(this), msg.sender, "logMFL 1");
        vault.flashLoan(this, tokens, amounts, userData);
        emit logMFL(address(this), msg.sender, "logMFL -1");
    }
    
    function receiveFlashLoan(
        IERC20[] memory tokens,
        uint256[] memory amounts,
        uint256[] memory feeAmounts,
        bytes memory userData
    ) external override {
        emit logRFL(address(this), msg.sender, "logRFL 0");
        require(msg.sender == address(vault), "loan from vault only");
        
        emit logRFL(address(this), msg.sender, "logRFL 1");
        (address router_0, address router_1, address[] memory path_0, address[] memory path_1, uint256 amntIn_0, uint256 amntOutMin_1) = abi.decode(userData, (address, address, address[], address[], uint256, uint256));
        
        emit logRFL(address(this), msg.sender, "logRFL 2");
        // approve for payback when execution finished
        //  init testing: return immediately (payback right away; req funds in this contract)
        uint256 amountOwed = amounts[0] + feeAmounts[0];
        // IERC20(asset).approve(address(vault), amountOwed);
        tokens[0].approve(address(vault), amountOwed);
        
        // uint[] memory amntOut_v2;
        uint256 amntOut;
        
        // check for uniswap v3 integration (requires bytes memory 'path' param)
        if (router_0 == uniswapRouterV3) {
            emit logRFL(address(this), msg.sender, "logRFL 3a");
            // convert path to bytes memory
            bytes memory bytes_path = addressesToBytes(path_0);
            amntOut = swap_v3(router_0, bytes_path, amntIn_0, 1);
        } else {
            emit logRFL(address(this), msg.sender, "logRFL 3b");
            // found uniswap v2 protocol integration
            amntOut = swap_v2(router_0, path_0, amntIn_0, 1);
        }
        
        // check for uniswap v3 integration (requires bytes memory 'path' param)
        if (router_1 == uniswapRouterV3) {
            emit logRFL(address(this), msg.sender, "logRFL 4a");
            // convert path to bytes memory
            bytes memory bytes_path = addressesToBytes(path_1);
            amntOut = swap_v3(router_1, bytes_path, amntOut, amntOutMin_1);
        } else {
            emit logRFL(address(this), msg.sender, "logRFL 4b");
            // found uniswap v2 protocol integration
            amntOut = swap_v2(router_1, path_1, amntOut, amntOutMin_1);
        }
        emit logRFL(address(this), msg.sender, "logRFL -1");
    }
    
    modifier onlyOwner() {
        // Check that the caller is the owner or has the appropriate permissions
        require(msg.sender == _owner, "Only owner");
        _;
    }

    function withdraw(uint256 amount) external onlyOwner {
        require(address(this).balance >= amount, "Insufficient native token balance");
        
        // cast owner address to a 'payable' address so it can receive ETH
        payable(_owner).transfer(amount);
    }
    
    receive() external payable {}
    
    // Function to transfer ERC20 tokens to a target address
    function transferTokens(address token, address to, uint256 amount) external onlyOwner {
        // Create an instance of the ERC20 token
        IERC20 tok = IERC20(token);

        // Check the contract's balance of the token
        uint256 contractBalance = tok.balanceOf(address(this));
        require(contractBalance >= amount, "Insufficient balance in the contract");

        // Transfer tokens to the target address
        tok.transfer(to, amount);
    }
    
    function swap_v3(address router, bytes memory path, uint256 amntIn, uint256 amntOutMin) private returns (uint256) {
        emit logRFL(address(this), msg.sender, "logRFL 5a");
        
        // v3: uniswap v3
        ISwapRouter swapRouter = ISwapRouter(router);
        
        emit logRFL(address(this), msg.sender, "logRFL 5b");
        IERC20(address(this)).approve(address(swapRouter), amntIn);
        uint deadline = block.timestamp + 300;
        
        emit logRFL(address(this), msg.sender, "logRFL 5c");
        ISwapRouter.ExactInputParams memory params = ISwapRouter.ExactInputParams({
            path: path,
            recipient: address(this),
            deadline: deadline,
            amountIn: amntIn,
            amountOutMinimum: amntOutMin
        });
        
        emit logRFL(address(this), msg.sender, "logRFL 5d");
        uint256 amntOut = swapRouter.exactInput(params);
        return amntOut;
    }
    
    function swap_v2(address router, address[] memory path, uint256 amntIn, uint256 amntOutMin) private returns (uint256) {
        emit logRFL(address(this), msg.sender, "logRFL 6a");
        // v2: solidlycom, kyberswap, pancakeswap, sushiswap, uniswap v2, pulsex v1|v2
        IUniswapV2 swapRouter = IUniswapV2(router);
        
        emit logRFL(address(this), msg.sender, "logRFL 6b");
        IERC20(address(this)).approve(address(swapRouter), amntIn);
        uint deadline = block.timestamp + 300;
        
        emit logRFL(address(this), msg.sender, "logRFL 6c");
        uint[] memory amntOut = swapRouter.swapExactTokensForTokens(
                        amntIn,
                        amntOutMin,
                        path, //address[] calldata path,
                        address(this),
                        deadline
                    );

        emit logRFL(address(this), msg.sender, "logRFL 6d");
        return uint256(amntOut[1]); // idx 0=amntIn, 1=amntOut
    }
    
    function addressesToBytes(address[] memory addresses) private returns (bytes memory) {
        bytes memory result = new bytes(addresses.length * 20); // Each address is 20 bytes long

        emit logX(address(this), msg.sender, "logX 1a");
        for (uint256 i = 0; i < addresses.length; i++) {
            // Convert each address to bytes and copy it into the result
            bytes20 addressBytes = bytes20(addresses[i]);
            for (uint256 j = 0; j < 20; j++) {
                result[i * 20 + j] = addressBytes[j];
            }
        }
        
        emit logX(address(this), msg.sender, "logX 1b");
        return result;
    }
}
