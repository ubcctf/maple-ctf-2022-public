const hre =  require("hardhat");
const ethers = hre.ethers;

async function main() {
  // We get the contract to deploy
  
  const solveScript = process.argv[2];

  const wellKnownSigners = await ethers.getSigners();

  const MapleBaCoin =  await ethers.getContractFactory("MapleBaCoin");
  const mpbc = await MapleBaCoin.attach("0xb538Caf4B3f86726e69DC6Be0AFfB8547575658C");

  const MapleBankon = await ethers.getContractFactory("MapleBankon");
  const mpbnk = await MapleBankon.attach("0xAA05378869fF467B0ab91a87d994E71067712629");

  const solveWallet = wellKnownSigners[1];
  const Solve = await ethers.getContractFactory(solveScript);
  const solve = await Solve.connect(solveWallet).deploy(mpbnk.address, mpbc.address);
  await solve.deployed();
  await solve.connect(solveWallet).attack();
  const endBalance = await mpbc.balanceOf(solve.address);
  console.log(`Your contract ended up with ${endBalance} MapleBaCoins. You need at least 100`);
  if (endBalance.gte(100)) {
    console.log("maple{FAKEFLAG}");
  }
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
