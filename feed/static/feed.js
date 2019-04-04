$(document).ready(function () {

console.log('Web3 test')
var Web3 = require('web3');
var web3 = window.web3;

if(typeof web3 !== 'undefined') {
    console.log("Using web3 detected from external source like Metamask");
    web3 = new Web3(web3.currentProvider);
} else {
    console.log("Using localhost");
    web3 = new Web3(new Web3.providers.HttpProvider("http://localhost:8545"));
}

var account = web3.eth.accounts[0];
console.log(account);


$("#load").click(function() {


  if($('#ownerCheck').is(':checked')){
    // Need to load a nonce on page load
    signature = web3.personal.sign(
      web3.fromUtf8('I am signing this nonce'),
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
  }else{
    console.log("Not Owner");
  }

})


})
