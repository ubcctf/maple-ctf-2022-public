const hre =  require("hardhat");
const ethers = hre.ethers;
const BigNumber = ethers.BigNumber;

async function main() {

  const wellKnownSigners = await ethers.getSigners();

  const mpWallet = ethers.Wallet.fromMnemonic("maple bacon coin test test test test test test test test access").connect(ethers.provider);
  console.log("Created MapleWallet", mpWallet.address);

  const MapleBaCoin =  await ethers.getContractFactory("MapleBaCoin");
  const mpbc = await MapleBaCoin.connect(mpWallet).deploy();
  await mpbc.deployed().then(()=>console.log("MapleBaCoin deployed to", mpbc.address));

  const MapleBankon = await ethers.getContractFactory("MapleBankon");
  const mpbnk = await MapleBankon.connect(mpWallet).deploy(mpbc.address);
  await mpbnk.deployed().then(()=>console.log("MapleBankon deployed to", mpbnk.address));
  await mpbc.connect(mpWallet).setBank(mpbnk.address);
  await mpbc.connect(mpWallet).transfer(mpbnk.address, BigNumber.from(10).pow(18));


}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
