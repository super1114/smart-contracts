//SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "./ImmutableVault.sol";

contract VaultFactory {

    mapping(address => address[]) public getVault;
    address[] public allVaults;

    event VaultCreated(address[] addresses, uint256[] weights, address trackingToken, address vault, uint);

    function createVault(address[] memory addresses, uint256[] memory weights, address trackingToken) external returns (address vault) {
        for (uint i; i < addresses.length; i++) {
            for (uint j = i + 1; j < addresses.length; j++) {
                require(addresses[i] != addresses[j], "Repeating token not supported");
            }
        }

        bytes memory bytecode = type(ImmutableVault).creationCode;
        // TODO: revisit the salt, it's using the args to create the salt, but the args is
        // already part of the creation code to generate the address, so we could just do
        // something else for the salt, perhaps use a nonce
        bytes32 salt = keccak256(abi.encodePacked(addresses, weights, trackingToken));
        // this is using the new create2 syntax
        vault = address(new ImmutableVault{salt: salt}(addresses, weights, trackingToken));
        getVault[trackingToken].push(vault);
        allVaults.push(vault);
        emit VaultCreated(addresses, weights, trackingToken, vault, allVaults.length);
    }

    function allVaultsLength() external view returns (uint256) {
        return allVaults.length;
    }

    function getVaultAddress(address[] memory addresses, uint256[] memory weights, address trackingToken) external view returns (address) {
        // TODO: update the init code hash with the latest version of ImmutableVault before releasing
        // this can make the method even more gas efficient
        return address(uint160(uint256(keccak256(abi.encodePacked(
            hex'ff',
            address(this),
            keccak256(abi.encodePacked(addresses, weights, trackingToken)),
            getInitHash(abi.encode(addresses, weights, trackingToken)) // init code hash
        )))));
    }

    // Debug function that can be used to find the init code hash of the ImmutableVault contract
    function getInitHash(bytes memory encodedArgs) public pure returns(bytes32){
        
        return keccak256(abi.encodePacked(type(ImmutableVault).creationCode, encodedArgs));
    }

}