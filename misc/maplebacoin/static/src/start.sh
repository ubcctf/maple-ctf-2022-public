npx ganache --chain.chainId="1337" \
        --gasPrice="0" \
        --logging.quiet="true" \
        --miner.blockTime="0" \
        --miner.instamine="eager" \
        --gasLimit="99999999999999" \
        --mnemonic='maple bacon coin test test test test test test test test access' \
        --hardfork='constantinople' &
npx hardhat run scripts/deploy.js "nothing";
npm run start ; kill $1
