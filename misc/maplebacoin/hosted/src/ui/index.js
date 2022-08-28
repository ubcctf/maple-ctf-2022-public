const express = require('express')
const fs = require('fs')
const getRawBody = require('raw-body')
const { v4: uuidv4 } = require('uuid');
const app = express()
const port = 3000
const { createClient } = require('redis');
const solc = require('solc');
const { ethers } = require("ethers");
const ganache = require("ganache");
const options = {
  chain: {
    hardfork: "constantinople"
  },
  miner: {
    defaultGasPrice: "0x0",
    blockTime: 0,
    instamine: "eager",
    //blockGasLimit: "0xffffffff",
  },
  logging: {
    quiet: true,
  //  verbose: true,
  },
  wallet: {
    mnemonic: "maple bacon coin test test test test test test test test access",
  },
};


const COIN = fs.readFileSync(`./contracts/MapleBaCoin.sol`, 'utf8');
const BANK = fs.readFileSync(`./contracts/MapleBankon.sol`, 'utf8');
const CONTEXT = fs.readFileSync(`./contracts/Context.sol`, 'utf8');
const OWNABLE = fs.readFileSync(`./contracts/Ownable.sol`, 'utf8');
const ERC20 = fs.readFileSync(`./contracts/ERC20.sol`, 'utf8');
const IERC20 = fs.readFileSync(`./contracts/IERC20.sol`, 'utf8');
const IERC20META = fs.readFileSync(`./contracts/IERC20Metadata.sol`, 'utf8');

const db = createClient({
  url: 'redis://:'
});
/* const db = createClient() */

db.on('error', (err) => console.log('Redis Client Error', err));

db.connect().then(()=>{
  app.use(express.static('./ui/static'))

  app.use(function (req, res, next) {
      getRawBody(req, {
        length: req.headers['content-length'],
        limit: '1kb',
        encoding: "utf8"
      }, function (err, string) {
        if (err) return next(err)
        req.text = string
        next()
      })
    })

  app.post('/deploy', (req, res) => {
    if (req.text.length < 5) {
      res.send("Malformed Submission")
    }
    let ip = req.header("X-Forwarded-For") || " "
    console.log(`Request from ${ip}`);

    db.get(ip).then((timestamp)=>{
      if (timestamp && Date.now() - timestamp < 20000){
        console.log("Rate-Limited")
        res.send(`You need to wait ${(20000 - (Date.now() - timestamp))/1000} more seconds before submitting.`)
      } else {
        db.set(ip, Date.now()).then(()=>{
          console.log(req.text);
          const uuid = uuidv4();
          db.set(uuid, "Processing...Please refresh the page occasionally. If no results show for 1 minute, try again.").then(()=>{
            testContract(req.text, uuid)
            res.send(`Your output will be updated after a while: <a href="/results/${uuid}">Here<a\\>`)
          })
        })
      }
    })

    
  })

  app.get('/results/:uuid', (req, res) => {
    db.get(req.params.uuid).then((x)=>{res.send(x)});
  })

  async function testContract(text, uuid) {
    try {
      const solcSrc = text.slice(5)
      const input = {
        language: 'Solidity',
        sources: {
          'MapleBaCoin.sol': {
            content: COIN,
          },
          'MapleBankon.sol': {
            content: BANK,
          },
          'Context.sol': {
            content: CONTEXT,
          },
          'Ownable.sol': {
            content: OWNABLE,
          },
          'IERC20Metadata.sol': {
            content: IERC20META,
          },
          'IERC20.sol': {
            content: IERC20,
          },
          'ERC20.sol': {
            content: ERC20,
          },
        },
        settings: {
          outputSelection: {
            '*': {
              '*': ['*']
            }
          },
          evmVersion: "constantinople",
        }
      };
      input.sources[`${uuid}.sol`] = {
        content: solcSrc,
      }
      const output = JSON.parse(solc.compile(JSON.stringify(input)));
      const provider = new ethers.providers.Web3Provider(ganache.provider(options));

      const solveWallet = provider.getSigner(2);
      const mpWallet = ethers.Wallet.fromMnemonic("maple bacon coin test test test test test test test test access").connect(provider);
      const MapleBaCoin =  ethers.ContractFactory.fromSolidity(output.contracts[`MapleBaCoin.sol`].MapleBaCoin);
      const mpbc = await MapleBaCoin.connect(mpWallet).deploy();
      await mpbc.deployed().then(()=>console.log("MapleBaCoin deployed to", mpbc.address));
    
      const MapleBankon = ethers.ContractFactory.fromSolidity(output.contracts[`MapleBankon.sol`].MapleBankon);
      const mpbnk = await MapleBankon.connect(mpWallet).deploy(mpbc.address);
      await mpbnk.deployed().then(()=>console.log("MapleBankon deployed to", mpbnk.address));
      await mpbc.connect(mpWallet).setBank(mpbnk.address);
      await mpbc.connect(mpWallet).transfer(mpbnk.address, ethers.BigNumber.from(10).pow(18));

      const Solve = ethers.ContractFactory.fromSolidity(output.contracts[`${uuid}.sol`].Solve);
      const solve = await Solve.connect(solveWallet).deploy(mpbnk.address, mpbc.address);
      await solve.deployed();
      await solve.connect(solveWallet).attack();
      const endBalance = await mpbc.balanceOf(solve.address);
      let result = `Your contract ended up with ${endBalance} MapleBaCoins. You need at least 100.<br>`;
      if (endBalance.gte(100)) {
        result = result + "maple{code_quality_on_par_with_scam_tokens}";
      }
      db.set(uuid, result);
    }
    catch (e) { 
      console.log(e)
      db.set(uuid, "Either your file did not compile correctly, or a transaction was reverted.");
    }
  }

  app.listen(port, () => {
    console.log(`Example app listening on port ${port}`)
  })

});
