from django.test import TestCase
import time
from web3.auto import w3
from web3 import Web3, HTTPProvider
from eth_account.messages import defunct_hash_message
from . import contracts_abi

ERC721FullAddress = '0xe5560289be2a80826ea72dB95e0b14379A7C4d3E'
ArtStewardAddress = '0x13a225FB5533bF144F8c484e0E5eD09A6aaDc45c'


class Web3Tests(TestCase):
    def test_query_feed_owner(self):
        # contract="ERC721Full" method="ownerOf"
        account = '0x13a225FB5533bF144F8c484e0E5eD09A6aaDc45c'              # ArtSteward

        w3t = Web3(HTTPProvider("http://127.0.0.1:8545"))
        # w3.eth.enable_unaudited_features()

        contract = w3t.eth.contract(address=ERC721FullAddress, abi=contracts_abi.erc721)
        owner = contract.functions.ownerOf(42).call()
        print(owner)
        print(str(type(owner)))
        self.assertEquals(owner, account)

    def test_signature_recover(self):
        # contract="ERC721Full" method="ownerOf"
        signature = '0xce652dc6b3f68823ea16886db657b5d57b6d285d7b70ac6e6b3b98a85e74369c6215d25e584789398afede48fa565450c639a971a8c8a22cef65b184397206e51c'
        account = '0xeE398666cA860DFb7390b5D73EE927e9Fb41a60A'

        message_hash = defunct_hash_message(text='I am signing this nonce')
        recovered_account = w3.eth.account.recoverHash(message_hash, signature=signature)

        print(account)
        self.assertEquals(recovered_account, account)


    def test_buy(self):
        buyer_account = '0x0e626b761fef2092f26cf431b1f8840c19a85bb4'
        buyer_account_pk = '0xa885d56d1ce4cb666454ac296a3429735c3a887750211a4bc9545531d6a228d6'

        w3t = Web3(HTTPProvider("http://127.0.0.1:8545"))

        buyer_account = w3t.toChecksumAddress(buyer_account)

        nonce = w3t.eth.getTransactionCount(buyer_account)

        contract = w3t.eth.contract(address=ArtStewardAddress, abi=contracts_abi.artSteward)

        print("Nonce:")
        print(nonce)

        txn_dict = contract.functions.buy(Web3.toWei('1.1', 'ether')).buildTransaction({
            'chainId': None,
            'gas': 2000000,
            'gasPrice': Web3.toWei('40', 'gwei'),
            'nonce': nonce,
            'value': Web3.toWei('1.1', 'ether')
        })

        signed_txn = w3t.eth.account.signTransaction(txn_dict, private_key=buyer_account_pk)

        result = w3t.eth.sendRawTransaction(signed_txn.rawTransaction)

        tx_receipt = w3t.eth.getTransactionReceipt(result)

        count = 0
        while tx_receipt is None and (count < 30):
            time.sleep(1)
            tx_receipt = w3t.eth.getTransactionReceipt(result)
            print(tx_receipt)

        if tx_receipt is None:
            print("TX FAILED")

        print("CHecking NEW owner")
        erc721_contract = w3t.eth.contract(address=ERC721FullAddress, abi=contracts_abi.erc721)
        owner = erc721_contract.functions.ownerOf(42).call()
        deposit = contract.functions.deposit().call()
        price = contract.functions.price().call()
        state = contract.functions.state().call()
        print(owner)
        print(deposit)
        print(price)
        print(state)
        self.assertEquals(owner, buyer_account)

    """
  it('steward: init: buy with 2 ether, price of 1 success [price = 1 eth, deposit = 1 eth]', async () => {
    const { logs } = await steward.buy(web3.utils.toWei('1', 'ether'), { from: accounts[2], value: web3.utils.toWei('1', 'ether') });
    expectEvent.inLogs(logs, 'LogBuy', { owner: accounts[2], price: ether('1')});
    const deposit = await steward.deposit.call();
    const price = await steward.price.call();
    const state = await steward.state.call();
    assert.equal(deposit, web3.utils.toWei('1', 'ether'));
    assert.equal(price, web3.utils.toWei('1', 'ether'));
    assert.equal(state, 1);
  });
    """
