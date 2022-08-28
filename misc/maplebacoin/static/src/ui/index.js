const express = require('express')
const fs = require('fs')
const { spawn } = require('node:child_process');
const getRawBody = require('raw-body')
const hre = require('hardhat')
const app = express()
const port = 3000

app.use(express.static('./ui/static'))

app.use(function (req, res, next) {
    getRawBody(req, {
      length: req.headers['content-length'],
      limit: '50kb',
      encoding: "utf8"
    }, function (err, string) {
      if (err) return next(err)
      req.text = string
      next()
    })
  })

app.post('/deploy', (req, res) => {
    try {
        if (req.text.length < 5) {
            throw error
        }
        const solcSrc = req.text.slice(5)
        console.log(solcSrc)
        const tempName = Math.random().toString(36).replace(/[^a-z]+/g, '')

        fs.writeFileSync(`./contracts/${tempName}.sol`, solcSrc)
        
        const ls = spawn('npx', ['hardhat', 'run', './scripts/solve.js', `contracts/${tempName}.sol:Solve`])
        let response = ""

        ls.stdout.on('data', (data) => {
            console.log(`stdout: ${data}`)
            response = response + "<br>" + data
        });
        
        ls.stderr.on('data', (data) => {
            console.error(`stderr: ${data}`)
            response = response + "<br>" + data
        });
        
        ls.on('close', (code) => {
            console.log(`test exited with code ${code}`)
            fs.unlinkSync(`./contracts/${tempName}.sol`)
            res.send(`Contract Tested: \n${response}`)
        });    
    }
    catch (e) { 
        res.send("Challenge borked :C")
    }
})

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`)
})