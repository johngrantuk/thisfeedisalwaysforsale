$(document).ready(function () {

  console.log('Web3 test')
  var Web3 = require('web3');
  var account;

  if (window.ethereum) { // for modern DApps browser
      window.web3 = new Web3(ethereum);
      try {
          ethereum.enable().then(function (result){
            console.log(web3.version)
            account = web3.eth.accounts[0];
            console.log(account);
          });
      } catch (error) {
          console.error(error);
      }
  }else if (web3) { // for old DApps browser
      window.web3 = new Web3(web3.currentProvider);
  } else {
      console.log('Non-Ethereum browser detected. You should consider trying MetaMask!');
  }

$("#load").click(function() {

  // Need to load a nonce on page load
  signature = web3.personal.sign(
    web3.fromUtf8('This is a signed message used to verify you are from the account you say. It costs nothing to do.'),
      account,
      (err, signature) => {
          console.log('Sig:');
          console.log(signature);
          console.log("Decrypting...");

          $.ajax({
              type: "POST",
              data: {
                'signature': signature
              },
              url: 'decrypt/',
              dataType: 'html',
              success: function (data) {
                $('#posts').html(data);
              }
          })
      }
  )


})

$("#buyfeed").click(function() {
  var priceEth = $('#salePrice').val();
  var depositEth = $('#deposit').val();

  console.log('Buy feed');
  console.log(priceEth)
  console.log(depositEth)

  var steward= web3.eth.contract(artSteward).at('0x13a225FB5533bF144F8c484e0E5eD09A6aaDc45c');
  steward.buy.sendTransaction(web3.toWei(priceEth, 'ether'), {
      from: web3.eth.accounts[0],
      value: web3.toWei(priceEth, 'ether')
    },
  (err, res) => {
    if(err){
      console.log('Error');
      if(err.message.indexOf('revert Not enough') !== -1)
        alert('Not Enough');
      else
        console.log(err)
    }else{
      $('#currentPrice').html('Current Price (ETH): ' + priceEth);
      $('#currentPatron').html('Current Patron: ' + web3.eth.accounts[0]);
    }
  });

})


})
