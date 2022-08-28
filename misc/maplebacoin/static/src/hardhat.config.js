require("@nomiclabs/hardhat-waffle");

// You need to export an object to set up your config
// Go to https://hardhat.org/config/ to learn more

const config = {
  solidity: "0.8.4",
  defaultNetwork: "ganache",
  networks: {
    ganache: {
      url: "http://127.0.0.1:8545",
      chainId: 1337,
      gasPrice: 0,
      gasLimit: 99999999999999,
      mnemonic: 'maple bacon coin test test test test test test test test access',
      hardfork: 'constantinople',
    } 
  }
};

module.exports = config;
