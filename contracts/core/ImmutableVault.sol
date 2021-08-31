//SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract ImmutableVault is ERC20 {
    using SafeERC20 for ERC20;

    address private factory;
    ERC20[] public assets;
    uint256[] public weights;
    uint256[] public reserves;
    ERC20 public trackingToken;
    string private _name;
    string private _symbol;

    constructor(address[] memory _assets, uint256[] memory _weights, address _trackingToken) ERC20("Vault", "PGV") {
        require(_assets.length > 1, "At least 2 tokens are needed");
        require(_assets.length == _weights.length, "Assets and Weights are not matching");
        bytes memory _bname = "PGVault: ";
        for (uint i; i < _assets.length; i++) {
            assets.push(ERC20(_assets[i]));
            if (i == _assets.length - 1) {
                _bname = abi.encodePacked(_bname, ERC20(_assets[i]).symbol());
            } else {
                _bname = abi.encodePacked(_bname, ERC20(_assets[i]).symbol(), "-");
            }
            reserves.push(0);
        }
        _name = string(_bname);
        _symbol = "PGV";
        weights = _weights;
        trackingToken = ERC20(_trackingToken);
        factory = msg.sender;
    }

    function name() public view virtual override returns (string memory) {
        return _name;
    }

    function symbol() public view virtual override returns (string memory) {
        return _symbol;
    }

    function _deposit(address toAccount, uint256 amount) internal {
        for (uint i; i < assets.length; i++) {
            //we need to figure out a way to make this decimals safe
            uint assetAmount = weights[i]*amount;
            assets[i].safeTransferFrom(msg.sender, address(this), assetAmount);
            reserves[i] += assetAmount;
        }

        _mint(toAccount, amount);
    }

    function _withdraw(address toAccount, uint256 amount) internal {
        uint256 _totalSupply = totalSupply();
        _burn(msg.sender, amount);

        for (uint i; i < assets.length; i++) {
            uint balance = assets[i].balanceOf(address(this));
            uint tokenAmount = amount * balance / _totalSupply;
            require(tokenAmount > 0, "Insufficient token to transfer");
            assets[i].safeTransfer(toAccount, tokenAmount);
            reserves[i] -= tokenAmount;
        }
    }

    function deposit(uint256 amount) external {
        _deposit(msg.sender, amount);
    }

    function depositTo(address toAccount, uint256 amount) external {
        _deposit(toAccount, amount);
    }

    function withdraw(uint256 amount) external {
        _withdraw(msg.sender, amount);
    }

    function withdrawTo(address toAccount, uint256 amount) external {
        _withdraw(toAccount, amount);
    }

    function assetLength() external view returns (uint256) {
        return assets.length;
    }
}