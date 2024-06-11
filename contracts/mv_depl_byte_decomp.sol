// Decompiled by library.dedaub.com
// 2023.09.03 18:36 UTC
// Compiled using the solidity compiler version 0.8.21


// Data structures and variables inferred from the use of storage instructions
mapping (uint256 => uint256) _balanceOf; // STORAGE[0x0]
mapping (uint256 => mapping (uint256 => uint256)) _allowance; // STORAGE[0x1]
uint256 _totalSupply; // STORAGE[0x2]
uint256[] array_3; // STORAGE[0x3]
uint256[] array_4; // STORAGE[0x4]
uint256 _owner; // STORAGE[0x5] bytes 0 to 19


// Events
Approval(address, address, uint256);
Transfer(address, address, uint256);
OwnershipTransferred(address, address);

function name() public payable {
    v0 = 0x35b();
    v1 = new bytes[](v0.length);
    v2 = v3 = 0;
    while (v2 < v0.length) {
        v1[v2] = v0[v2];
        v2 = v2 + 32;
    }
    v1[v0.length] = 0;
    return v1;
}

// house_090923:
//  - set global _totalSupply = _totalSupply + varg0
//  - set global _balanceOf[address(varg1)] = address(varg1) balance + varg0
//  - mint 'varg0' token count to 'address(varg1)'
function 0x11ca(uint256 varg0, uint256 varg1) private {
    require(address(varg1) - address(0x0), Error('ERC20: mint to the zero address'));
    v0 = _SafeAdd(_totalSupply, varg0);
    _totalSupply = v0;
    v1 = _SafeAdd(_balanceOf[address(varg1)], varg0);
    _balanceOf[address(varg1)] = v1;
    emit Transfer(address(0x0), address(varg1), varg0);
    return ;
}

function approve(address varg0, uint256 varg1) public payable {
    require(4 + (msg.data.length - 4) - 4 >= 64);
    require(varg0 == varg0);
    require(varg1 == varg1);
    0xa78(varg1, varg0, msg.sender);
    return bool(1);
}

function totalSupply() public payable {
    return _totalSupply;
}

function 0x166c(uint256 varg0) private {
    v0 = v1 = varg0 >> 1;
    if (!(varg0 & 0x1)) {
        v0 = v2 = v1 & 0x7f;
    }
    require((varg0 & 0x1) - (v0 < 32), Panic(34)); // access to incorrectly encoded storage byte array
    return v0;
}

function _SafeAdd(uint256 varg0, uint256 varg1) private {
    require(varg0 <= varg0 + varg1, Panic(17)); // arithmetic overflow or underflow
    return varg0 + varg1;
}

function transferFrom(address varg0, address varg1, uint256 varg2) public payable {
    require(4 + (msg.data.length - 4) - 4 >= 96);
    require(varg0 == varg0);
    require(varg1 == varg1);
    require(varg2 == varg2);
    0xc3b(varg2, msg.sender, varg0);
    0xcc6(varg2, varg1, varg0);
    return bool(1);
}

function _SafeExp(uint256 varg0, uint256 varg1, uint256 varg2) private {
    if (varg1) {
        if (varg0) {
            if (varg0 == 1) {
                return 1;
            } else if (varg0 == 2) {
                require(varg1 <= uint8.max, Panic(17)); // arithmetic overflow or underflow
                require(2 ** varg1 <= varg2, Panic(17)); // arithmetic overflow or underflow
                return 2 ** varg1;
            } else if (!((varg0 < 11) & (varg1 < 78) | (varg0 < 307) & (varg1 < 32))) {
                v0 = v1 = 1;
                while (varg1 > 1) {
                    require(varg0 <= varg2 / varg0, Panic(17)); // arithmetic overflow or underflow
                    if (varg1 & 0x1) {
                        v0 = v0 * varg0;
                    }
                    varg0 *= varg0;
                    varg1 = varg1 >> 1;
                }
                require(v0 <= varg2 / varg0, Panic(17)); // arithmetic overflow or underflow
                return v0 * varg0;
            } else {
                require(varg0 ** varg1 <= varg2, Panic(17)); // arithmetic overflow or underflow
                return varg0 ** varg1;
            }
        } else {
            return 0;
        }
    } else {
        return 1;
    }
}

// house_090923: calc raise varg0 to the power of varg1
function 0x1893(uint256 varg0, uint8 varg1) private {
    v0 = _SafeExp(varg0, varg1, uint256.max);
    return v0;
}

function _SafeMul(uint256 varg0, uint256 varg1) private {
    require(!varg0 | (varg1 == varg0 * varg1 / varg0), Panic(17)); // arithmetic overflow or underflow
    return varg0 * varg1;
}

function decimals() public payable {
    return uint8(18);
}

function increaseAllowance(address varg0, uint256 varg1) public payable {
    require(4 + (msg.data.length - 4) - 4 >= 64);
    require(varg0 == varg0);
    require(varg1 == varg1);
    v0 = _SafeAdd(_allowance[msg.sender][varg0], varg1);
    0xa78(v0, varg0, msg.sender);
    return bool(1);
}

function burn(uint256 varg0) public payable {
    require(4 + (msg.data.length - 4) - 4 >= 32);
    require(varg0 == varg0);
    0xf3b(varg0, msg.sender);
}

function () public payable {
    revert();
}

function balanceOf(address varg0) public payable {
    require(4 + (msg.data.length - 4) - 4 >= 32);
    require(varg0 == varg0);
    return _balanceOf[varg0];
}

function renounceOwnership() public payable {
    require(_owner == msg.sender, Error('Ownable: caller is not the owner'));
    _owner = 0;
    emit OwnershipTransferred(_owner, address(0x0));
}

function burnFrom(address varg0, uint256 varg1) public payable {
    require(4 + (msg.data.length - 4) - 4 >= 64);
    require(varg0 == varg0);
    require(varg1 == varg1);
    0xc3b(varg1, msg.sender, varg0);
    0xf3b(varg1, varg0);
}

function owner() public payable {
    return _owner;
}

function symbol() public payable {
    v0 = 0x619();
    v1 = new bytes[](v0.length);
    v2 = v3 = 0;
    while (v2 < v0.length) {
        v1[v2] = v0[v2];
        v2 = v2 + 32;
    }
    v1[v0.length] = 0;
    return v1;
}

// house: mint more MV
//  calcs 4 specific amounts to mint to 4 static addresses
//  calcs a 5th specific amount to mint to function caller address
function 0xa4566950() public payable {
    v0 = 0x1893(10, 18); // house: raise varg0 to the power of varg1
    v1 = _SafeMul(4, v0); // house: total amnt to mint
    0x11ca(v1, 57005); // house: mint 'v' token count to static 'address'
    
    // house: mint 'v' token count to static 'address'
    v2 = 0x1893(10, 18);
    v3 = _SafeMul(1, v2);
    0x11ca(v3, 0x7a20189b297343cf26d8548764b04891f37f3414);
    
    // house: mint 'v' token count to static 'address'
    v4 = 0x1893(8, 18);
    v5 = _SafeMul(1, v4);
    0x11ca(v5, 0x46eb71eb92e3ed2534d005ab4436b4b8db24dfa);
    
    // house: mint 'v' token count to static 'address'
    v6 = 0x1893(7, 18);
    v7 = _SafeMul(1, v6);
    0x11ca(v7, 0x9abf7504162e5ca517d504a16e8addcb10115aab);
    
    // house: mint 'v' token count to static 'address'
    v8 = 0x1893(5, 18);
    v9 = _SafeMul(1, v8);
    0x11ca(v9, 0x7ae04ed7f1082d8aa1c19893e9ec4039a666c02c);
    
    // house: mint 'v' token count to 'address' of function caller
    v10 = 0x1893(10, 18);
    v11 = _SafeMul(1, v10);
    0x11ca(v11, msg.sender);
}

function decreaseAllowance(address varg0, uint256 varg1) public payable {
    require(4 + (msg.data.length - 4) - 4 >= 64);
    require(varg0 == varg0);
    require(varg1 == varg1);
    require(_allowance[msg.sender][varg0] >= varg1, Error('ERC20: decreased allowance below zero'));
    0xa78(_allowance[msg.sender][varg0] - varg1, varg0, msg.sender);
    return bool(1);
}

function transfer(address varg0, uint256 varg1) public payable {
    require(4 + (msg.data.length - 4) - 4 >= 64);
    require(varg0 == varg0);
    require(varg1 == varg1);
    0xcc6(varg1, varg0, msg.sender);
    return bool(1);
}

function allowance(address varg0, address varg1) public payable {
    require(4 + (msg.data.length - 4) - 4 >= 64);
    require(varg0 == varg0);
    require(varg1 == varg1);
    return _allowance[varg0][varg1];
}

function transferOwnership(address varg0) public payable {
    require(4 + (msg.data.length - 4) - 4 >= 32);
    require(varg0 == varg0);
    require(_owner == msg.sender, Error('Ownable: caller is not the owner'));
    require(varg0 - address(0x0), Error('Ownable: new owner is the zero address'));
    _owner = varg0;
    emit OwnershipTransferred(_owner, varg0);
}

function 0x35b() private {
    v0 = 0x166c(array_3.length);
    v1 = new bytes[](v0);
    v2 = v3 = v1.data;
    v4 = 0x166c(array_3.length);
    if (!v4) {
        return v1;
    } else if (31 < v4) {
        v5 = v6 = array_3.data;
        do {
            MEM[v2] = STORAGE[v5];
            v5 += 1;
            v2 += 32;
        } while (v3 + v4 <= v2);
        return v1;
    } else {
        MEM[v3] = array_3.length >> 8 << 8;
        return v1;
    }
}

function 0x619() private {
    v0 = 0x166c(array_4.length);
    v1 = new bytes[](v0);
    v2 = v3 = v1.data;
    v4 = 0x166c(array_4.length);
    if (!v4) {
        return v1;
    } else if (31 < v4) {
        v5 = v6 = array_4.data;
        do {
            MEM[v2] = STORAGE[v5];
            v5 += 1;
            v2 += 32;
        } while (v3 + v4 <= v2);
        return v1;
    } else {
        MEM[v3] = array_4.length >> 8 << 8;
        return v1;
    }
}

function 0xa78(uint256 varg0, address varg1, address varg2) private {
    require(varg2 - address(0x0), Error('ERC20: approve from the zero address'));
    require(varg1 - address(0x0), Error('ERC20: approve to the zero address'));
    _allowance[varg2][varg1] = varg0;
    emit Approval(varg2, varg1, varg0);
    return ;
}

function 0xc3b(uint256 varg0, uint256 varg1, uint256 varg2) private {
    v0 = _allowance[address(varg2)][address(varg1)];
    if (v0 != uint256.max) {
        require(v0 >= varg0, Error('ERC20: insufficient allowance'));
        0xa78(v0 - varg0, varg1, varg2);
    }
    return ;
}

function 0xcc6(uint256 varg0, uint256 varg1, uint256 varg2) private {
    require(address(varg2) - address(0x0), Error('ERC20: transfer from the zero address'));
    require(address(varg1) - address(0x0), Error('ERC20: transfer to the zero address'));
    require(_balanceOf[address(varg2)] >= varg0, Error('ERC20: transfer amount exceeds balance'));
    _balanceOf[address(varg2)] = _balanceOf[address(varg2)] - varg0;
    v0 = _SafeAdd(_balanceOf[address(varg1)], varg0);
    _balanceOf[address(varg1)] = v0;
    emit Transfer(address(varg2), address(varg1), varg0);
    return ;
}

function 0xf3b(uint256 varg0, uint256 varg1) private {
    require(address(varg1) - address(0x0), Error('ERC20: burn from the zero address'));
    require(_balanceOf[address(varg1)] >= varg0, Error('ERC20: burn amount exceeds balance'));
    _balanceOf[address(varg1)] = _balanceOf[address(varg1)] - varg0;
    require(_totalSupply - varg0 <= _totalSupply, Panic(17)); // arithmetic overflow or underflow
    _totalSupply = _totalSupply - varg0;
    emit Transfer(address(varg1), address(0x0), varg0);
    return ;
}

// Note: The function selector is not present in the original solidity code.
// However, we display it for the sake of completeness.

function __function_selector__(bytes4 function_selector) public payable {
    MEM[64] = 128;
    require(!msg.value);
    if (msg.data.length < 4) {
        ();
    } else if (0x715018a6 > function_selector >> 224) {
        if (0x313ce567 > function_selector >> 224) {
            if (0x6fdde03 == function_selector >> 224) {
                name();
            } else if (0x95ea7b3 == function_selector >> 224) {
                approve(address,uint256);
            } else if (0x18160ddd == function_selector >> 224) {
                totalSupply();
            } else {
                require(0x23b872dd == function_selector >> 224);
                transferFrom(address,address,uint256);
            }
        } else if (0x313ce567 == function_selector >> 224) {
            decimals();
        } else if (0x39509351 == function_selector >> 224) {
            increaseAllowance(address,uint256);
        } else if (0x42966c68 == function_selector >> 224) {
            burn(uint256);
        } else {
            require(0x70a08231 == function_selector >> 224);
            balanceOf(address);
        }
    } else if (0xa4566950 > function_selector >> 224) {
        if (0x715018a6 == function_selector >> 224) {
            renounceOwnership();
        } else if (0x79cc6790 == function_selector >> 224) {
            burnFrom(address,uint256);
        } else if (0x8da5cb5b == function_selector >> 224) {
            owner();
        } else {
            require(0x95d89b41 == function_selector >> 224);
            symbol();
        }
    } else if (0xa4566950 == function_selector >> 224) {
        0xa4566950();
    } else if (0xa457c2d7 == function_selector >> 224) {
        decreaseAllowance(address,uint256);
    } else if (0xa9059cbb == function_selector >> 224) {
        transfer(address,uint256);
    } else if (0xdd62ed3e == function_selector >> 224) {
        allowance(address,address);
    } else {
        require(0xf2fde38b == function_selector >> 224);
        transferOwnership(address);
    }
}

