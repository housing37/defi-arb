// SPDX-License-Identifier: UNLICENSED
// ref: https://ethereum.org/en/history
//  code size limit = 24576 bytes (a limit introduced in Spurious Dragon _ 2016)
//  code size limit = 49152 bytes (a limit introduced in Shanghai _ 2023)
pragma solidity ^0.8.24;        

// inherited contracts
// import "@openzeppelin/contracts/token/ERC20/IERC20.sol"; // deploy

// local _ $ npm install @openzeppelin/contracts
import "./node_modules/@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract AtropaMV {
    address public constant TOK_WPLS = address(0xA1077a294dDE1B09bB078844df40758a5D0f9a27);
    address public constant BURN_ADDR = address(0x0000000000000000000000000000000000000369);
    address public constant TOK_MV = address(0xA1BEe1daE9Af77dAC73aA0459eD63b4D93fC6d29);
    bytes4 public constant HASH_MV_MINT = 0xa4566950;

    /* -------------------------------------------------------- */
    /* GLOBALS                                                  */
    /* -------------------------------------------------------- */
    /* _ TOKEN INIT SUPPORT _ */
    string public tVERSION = '0.2';

    /* _ ADMIN SUPPORT _ */
    address public KEEPER;
    // address[] private WHITELIST_ADDRS;
    // mapping(address => bool) public WHITELIST_ADDR_MAP;

    /* -------------------------------------------------------- */
    /* STRUCTS                                        
    /* -------------------------------------------------------- */

    /* -------------------------------------------------------- */
    /* EVENTS                                        
    /* -------------------------------------------------------- */
    event KeeperTransfer(address _prev, address _new);
    event InvokedMintMV(address _target, bytes4 _selector, uint32 _loopCnt);
    // event WhitelistAddressUpdated(address _address, bool _add);

    /* -------------------------------------------------------- */
    /* CONSTRUCTOR                                              */
    /* -------------------------------------------------------- */
    // NOTE: sets msg.sender to '_owner' ('Ownable' maintained)
    constructor() {

        // add default keeper and whitelist (for whatever may be needed)
        KEEPER = msg.sender;
        // _editWhitelistAddress(KEEPER, true); // true = _add
    }

    /* -------------------------------------------------------- */
    /* MODIFIERS                                                
    /* -------------------------------------------------------- */
    modifier onlyKeeper() {
        require(msg.sender == KEEPER, "!keeper :p");
        _;
    }

    /* -------------------------------------------------------- */
    /* PUBLIC - KEEPER SUPPORT            
    /* -------------------------------------------------------- */
    //  NOTE: _tokAmnt must be in uint precision to _tokAddr.decimals()
    function KEEPER_maintenance(address _tokAddr, uint256 _tokAmnt) external onlyKeeper() {
        require(IERC20(_tokAddr).balanceOf(address(this)) >= _tokAmnt, ' not enough amount for token :O ');
        IERC20(_tokAddr).transfer(KEEPER, _tokAmnt);
        // emit KeeperMaintenance(_tokAddr, _tokAmnt);
    }
    function KEEPER_withdraw(uint256 _natAmnt) external onlyKeeper {
        require(address(this).balance >= _natAmnt, " Insufficient native PLS balance :[ ");
        payable(KEEPER).transfer(_natAmnt); // cast to a 'payable' address to receive ETH
        // emit KeeperWithdrawel(_natAmnt);
    }
    function KEEPER_setKeeper(address _newKeeper) external onlyKeeper {
        require(_newKeeper != address(0), ' 0 address :/ ');
        address prev = address(KEEPER);
        KEEPER = _newKeeper;
        emit KeeperTransfer(prev, KEEPER);
    }
    function KEEPER_tokenBalance(address _token) external view onlyKeeper() returns (uint256) {
        require(_token != address(0), ' 0 address _token :/ ');
        return IERC20(_token).balanceOf(address(this));
    }
    // function KEEPER_editWhitelistAddress(address _address, bool _add) external onlyKeeper() {
    //     require(_address != address(0), ' 0 address :/ ');
    //     _editWhitelistAddress(_address, _add);
    // }
    // function KEEPER_editWhitelistAddressMulti(bool _add, address[] memory _addresses) external onlyKeeper() {
    //     require(_addresses.length > 0, ' 0 addresses found :/ ');
    //     for (uint8 i=0; i < _addresses.length;) {
    //         _editWhitelistAddress(_addresses[i], _add);
    //         unchecked { i++; }
    //     }
    // }

    /* -------------------------------------------------------- */
    /* PUBLIC - ACCESSORS
    /* -------------------------------------------------------- */
    // function getWhitelistAddresses() external view returns (address[] memory) {
    //     return WHITELIST_ADDRS;
    // }

    /* -------------------------------------------------------- */
    /* PUBLIC - KEEPER - USER INTERFACE
    /* -------------------------------------------------------- */
    function KEEPER_invokeMintMV(uint32 _loopCnt) external onlyKeeper() {
        address target = TOK_MV; // atropa MV token contract address
        bytes4 selector = HASH_MV_MINT; // atropa MV token mint function hash '0xa4566950()'
        bytes memory params = ""; // params: func()
        // bytes memory params = abi.encode(42, address(0x00..369)); // params: func(uint,address)

        for (uint32 i=0; i<_loopCnt;) {
            bytes memory result = _callFunction(target, selector, params);
            unchecked { i++; }
        }
        emit InvokedMintMV(target, selector, _loopCnt);
    }

    /* -------------------------------------------------------- */
    /* PUBLIC - USER INTERFACE
    /* -------------------------------------------------------- */
    // handle contract USD value deposits (convert PLS to USD stable)
    receive() external payable {
        // extract PLS value sent
        // uint256 amntIn = msg.value;
        // address from = msg.sender;
    }

    /* -------------------------------------------------------- */
    /* PRIVATE - SUPPORTING                                     */
    /* -------------------------------------------------------- */
    function _callFunction(address target, bytes4 selector, bytes memory params) private returns (bytes memory) {
        (bool success, bytes memory result) = target.call(abi.encodePacked(selector, params));
        require(success, "Call failed");
        return result;
    }
    // function _editWhitelistAddress(address _address, bool _add) private { // does not allow duplicates
    //     WHITELIST_ADDR_MAP[_address] = _add;
    //     if (_add) {
    //         WHITELIST_ADDRS = _addAddressToArraySafe(_address, WHITELIST_ADDRS, true); // true = no dups            
    //     } else {
    //         WHITELIST_ADDRS = _remAddressFromArray(_address, WHITELIST_ADDRS);
    //     }
    //     emit WhitelistAddressUpdated(_address, _add);
    // }
    // function _addAddressToArraySafe(address _addr, address[] memory _arr, bool _safe) private pure returns (address[] memory) {
    //     if (_addr == address(0)) { return _arr; }

    //     // safe = remove first (no duplicates)
    //     if (_safe) { _arr = _remAddressFromArray(_addr, _arr); }

    //     // perform add to memory array type w/ static size
    //     address[] memory _ret = new address[](_arr.length+1);
    //     for (uint i=0; i < _arr.length;) { _ret[i] = _arr[i]; unchecked {i++;}}
    //     _ret[_ret.length-1] = _addr;
    //     return _ret;
    // }
    // function _remAddressFromArray(address _addr, address[] memory _arr) private pure returns (address[] memory) {
    //     if (_addr == address(0) || _arr.length == 0) { return _arr; }
        
    //     // NOTE: remove algorithm does NOT maintain order & only removes first occurance
    //     for (uint i = 0; i < _arr.length;) {
    //         if (_addr == _arr[i]) {
    //             _arr[i] = _arr[_arr.length - 1];
    //             assembly { // reduce memory _arr length by 1 (simulate pop)
    //                 mstore(_arr, sub(mload(_arr), 1))
    //             }
    //             return _arr;
    //         }

    //         unchecked {i++;}
    //     }
    //     return _arr;
    // }
}


