// house_102523 _ ref: https://docs.balancer.fi/reference/contracts/flash-loans.html#example-code
// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity ^0.8.22;

import "@balancer-labs/v2-interfaces/contracts/vault/IVault.sol";
import "@balancer-labs/v2-interfaces/contracts/vault/IFlashLoanRecipient.sol";

contract BalancerFLR_test is IFlashLoanRecipient {
    // ref: https://docs.balancer.fi/reference/contracts/flash-loans.html#example-code
    IVault private constant vault = IVault(0xBA12222222228d8Ba445958a75a0704d566BF2C8);
    
    address private constant balancerRouter = address(0x37);
    address public _owner;

    event logX(address indexed contr, address sender, string message);
    event logRFL(address indexed contr, address sender, string message);
    event logMFL(address indexed contr, address sender, string message);

    modifier onlyOwner() {
        require(msg.sender == _owner, "Only owner");
        _;
    }
    
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
        uint256 bal = tokens[0].balanceOf(address(this));
        
        emit logRFL(address(this), msg.sender, "logRFL 3");
        // approve for payback when execution finished
        //  init testing: return immediately (payback right away; req funds in this contract)
        uint256 amountOwed = amounts[0] + feeAmounts[0];
        // IERC20(asset).approve(address(vault), amountOwed);
        tokens[0].approve(address(vault), amountOwed);
        

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
}
