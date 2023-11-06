// house_102523 _ ref: https://docs.balancer.fi/reference/contracts/flash-loans.html#example-code
// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity ^0.8.22;

import "@balancer-labs/v2-interfaces/contracts/vault/IVault.sol";
import "@balancer-labs/v2-interfaces/contracts/vault/IFlashLoanRecipient.sol";
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

contract BalancerFLR_pc is IFlashLoanRecipient {
    // ref: https://docs.balancer.fi/reference/contracts/flash-loans.html#example-code
    IVault private constant vault = IVault(0xBA12222222228d8Ba445958a75a0704d566BF2C8);
    
    address private constant weth = address(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2);
    address private constant atropa = address(0xCc78A0acDF847A2C1714D2A925bB4477df5d48a6);
    address private constant wpls = address(0xA1077a294dDE1B09bB078844df40758a5D0f9a27);
    address private constant rob = address(0x1c2766F5949A4aA5d4cf0439067051135ffc1b28);
    
    // uniswap v2 protocol based
    address private constant plsx_rtr_v1 = address(0x98bf93ebf5c380C0e6Ae8e192A7e2AE08edAcc02);
    address private constant plsx_rtr_v2 = address(0x165C3410fC91EF562C50559f7d2289fEbed552d9);
    address private constant 9inch_rtr = address(0xeB45a3c4aedd0F47F345fB4c8A1802BB5740d725);

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
    
    // note_110523: only uniswap v2 protocol support for _pc
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
        
        // quote-to-execute slippage %
        uint256 quote_exe_slip_perc = 2;
        
        // (1) get loan in WETH (0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2)
        uint256 weth_bal = tokens[0].balanceOf(address(this)) // max 114983659 WETH from pc->balancer-vault
        require(weth_bal >= amounts[0], "err: loan transfer failed")
        
        
        // (2) arb setup (WETH -> WPLS) _ note: plsx_rtr_v2 w/ 1000x more liq than plsx_rtr_v1
        // weth -> wpls (on pulsex_v2)
        amntOut = swap_v2_wrap([weth, wpls], plsx_rtr_v2, amounts[0], quote_exe_slip_perc);
        
        
        // (3) arb swap (WPLS -> ... -> WPLS)
        // wpls -> rob (on 9inch)
        amntOut = swap_v2_wrap([wpls, rob], 9inch_rtr, amntOut, quote_exe_slip_perc);
            
        // rob -> wpls (on pulsex_v2)
        amntOut = swap_v2_wrap([rob, wpls], plsx_rtr_v2, amntOut, quote_exe_slip_perc);
        
        
        // (4) arb tear-down (WPLS -> WETH) _ note: plsx_rtr_v2 w/ 1000x more liq than plsx_rtr_v1
        amntOut = swap_v2_wrap([wpls, weth], plsx_rtr_v2, amntOut, quote_exe_slip_perc);
        
        
        // (5) payback WETH (0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2)
        //  note: no 'token.approve(,)' needed since this contract is transfering its own tokens
        uint256 amountOwed = amounts[0] + feeAmounts[0]; // house_110523: on fee on pc
        IERC20(tokens[0]).transfer(address(vault), amountOwed);
    }
    
    // uniwswap v2 protocol based: get quote and execute swap w/ quote-to-exe slippage check
    function swap_v2_wrap(address[] memory path, address router, uint256 amntIn, uint256 slip_perc) private returns (uint256) {
        //address[] memory path = [weth, wpls];
        uint256[] memory amountsOut = IUniswapV2(router).getAmountsOut(amntIn, path); // quote swap
        uint256 amntOut = swap_v2(router, path, amntIn, amountsOut[amountsOut.length -1]); // execute swap
        
        // verifiy quote-to-exe slippage & balance of token received (reverts)
        verifyRequirements(amountsOut[amountsOut.length -1], slip_perc, amntOut, path);
        
        return amntOut;
    }
    
    // v2: solidlycom, kyberswap, pancakeswap, sushiswap, uniswap v2, pulsex v1|v2, 9inch
    function swap_v2(address router, address[] memory path, uint256 amntIn, uint256 amntOutMin) private returns (uint256) {
        emit logRFL(address(this), msg.sender, "logRFL 6a");
        IUniswapV2 swapRouter = IUniswapV2(router);
        
        emit logRFL(address(this), msg.sender, "logRFL 6b");
        IERC20(address(path[0])).approve(address(swapRouter), amntIn);
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
        return uint256(amntOut[amntOut.length - 1]); // idx 0=path[0].amntOut, 1=path[1].amntOut, etc.
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
    
    function verifyRequirements(amountsOut, quote_exe_slip_perc, uint256 amntOut, path) private {
        // verify slippage from quote-to-execute (amntOut is within quote_exe_slip_perc of amountsOut[1])
        (lower_bound, upper_bound) = getSlippageForPerc(amountsOut[amountsOut.length -1], quote_exe_slip_perc);
        require(lower_bound <= amntOut && amntOut <= upper_bound, string(abi.encodePacked("err: quote-to-execute slippage > ", quote_exe_slip_perc, "%")));

        // verifiy balance of token received
        uint256 wpls_bal = IERC20(path[path.length -1]).balanceOf(address(this));
        require(wpls_bal >= amntOut, "err: balance low");
    }
    
    function getSlippageForPerc(uint256 amnt, uint256 perc) private returns (uint256, uint256) {
        uint256 amnt_slip = (amnt * perc) / 100;
        uint256 lower_bound = amnt - amnt_slip;
        uint256 upper_bound = amnt + amnt_slip;
        return (lower_bound, upper_bound);
    }
}
