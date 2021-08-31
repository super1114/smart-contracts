//SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract SlashingERC20 is ERC20 {

    constructor(uint amount) ERC20("Vault", "PGLV") public {
        _mint(msg.sender, amount);
    }


    function slash(address account) external {
        _burn(account, balanceOf(account));
    }

}