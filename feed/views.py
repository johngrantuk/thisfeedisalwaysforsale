from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .models import Feed, Post
from . import nuCypherHelper, nuCypherAlice, nuCypherBob, nuCypherEnrico
from django.views.decorators.csrf import csrf_exempt
from umbral.keys import UmbralPublicKey
from nucypher.characters.lawful import Enrico
from nucypher.crypto.kits import UmbralMessageKit
import os
from umbral.signing import Signature

from web3.auto import w3
from web3 import Web3, HTTPProvider
from eth_account.messages import defunct_hash_message
from . import contracts_abi


alice = None
enrico = None   # Enrcio needs to be consistent

def feed_admin(request):

    feed = Feed.objects.all()[0]
    posts = Post.objects.all()
    return render(request, 'feed_admin.html', {'feed': feed, 'posts': posts})


def create_policy(request):
    global alice, enrico

    if request.is_ajax():
        feed = Feed.objects.all()[0]

        feed.alice_passphrase = 'this_has_to_be_a_long_password_ok' + os.urandom(4).hex()
        feed.label_string = 'greatest_feed_in_the_world_' + os.urandom(4).hex()
        feed.save()
        print(feed.label_string)
        # Create a Policy
        alice = nuCypherAlice.StartAlice(feed.alice_passphrase)
        labelStr = feed.label_string
        policy_pubkey = nuCypherAlice.CreatePolicy(alice, labelStr)     # Type: umbral.keys.UmbralPublicKey
        enrico = nuCypherEnrico.GetEnrico(policy_pubkey)
        enricos_pubkey = enrico.stamp
        enrico_pubkey_hex = bytes(enricos_pubkey).hex()

        policy_pubkey_hex = policy_pubkey.to_bytes().hex()
        # print(str(type(policy_pubkey)))                 # <class 'umbral.keys.UmbralPublicKey'>
        # print(str(type(policy_pubkey_hex)))             # <class 'str'>
        feed.policy_pubkey_hex = policy_pubkey_hex
        feed.enrico_pubkey_hex = enrico_pubkey_hex
        feed.save()

        # delete all old posts
        posts = Post.objects.all()
        if posts.exists():
            posts.delete()

        # encrypt and save new posts
        policy_pubkey = UmbralPublicKey.from_bytes(bytes.fromhex(policy_pubkey_hex))
        # enrico_pubkey = UmbralPublicKey.from_bytes(bytes.fromhex(enrico_pubkey_hex))
        post = "Me and Kyle on holiday."
        print('Encrypting post: ')
        print(post)

        message_kit, _signature = enrico.encrypt_message(post.encode())
        p = Post(content=message_kit.to_bytes().hex(), enrico_pubkey_hex=bytes(enricos_pubkey).hex(), signature=bytes(_signature).hex())
        p.save()

        post = "Me and Kyle walking down a long and lonesome road."
        print('Encrypting post: ')
        print(post)

        message_kit, _signature = enrico.encrypt_message(post.encode())
        p = Post(content=message_kit.to_bytes().hex(), enrico_pubkey_hex=bytes(enricos_pubkey).hex(), signature=bytes(_signature).hex())
        p.save()

        data = {
            'policy_pubkey_hex': policy_pubkey_hex,
            'enrico_pubkey_hex': enrico_pubkey_hex
        }
        return JsonResponse(data)


@csrf_exempt
def add_post(request):

    global enrico

    if request.is_ajax():
        print(request.POST)
        post = request.POST.get('post')
        policy_pubkey_hex = request.POST.get('policy_pubkey_hex')
        # enrico_pubkey_hex = request.POST.get('enrico_pubkey_hex')

        policy_pubkey = UmbralPublicKey.from_bytes(bytes.fromhex(policy_pubkey_hex))
        # enrico_pubkey = UmbralPublicKey.from_bytes(bytes.fromhex(enrico_pubkey_hex))
        print('Encrypting post: ')
        print(post)

        # enrico = nuCypherEnrico.GetEnrico(policy_pubkey)
        # enrico = Enrico(policy_encrypting_key=policy_pubkey)
        enricos_pubkey = enrico.stamp
        # print("!!! Enricos Pub Key: ")
        # print(bytes(enricos_pubkey).hex())
        # print(enrico_pubkey_hex)
        # message_kit = nuCypherEnrico.EncryptData(enrico, post)
        message_kit, _signature = enrico.encrypt_message(post.encode())

        print("MESSAGE KIT LENGHT: " + str(len(message_kit.to_bytes().hex())))
        print(message_kit.to_bytes().hex())
        # print("Encrypted message: ")
        # print(message_kit)
        # message_kit.to_bytes()
        p = Post(content=message_kit.to_bytes().hex(), enrico_pubkey_hex=bytes(enricos_pubkey).hex(), signature=bytes(_signature).hex())
        p.save()

        return render(request, 'post.html', {'post': p})


def feed(request):

    feed = Feed.objects.all()[0]
    posts = Post.objects.all()

    w3t = Web3(HTTPProvider(feed.provider))
    erc721_contract = w3t.eth.contract(address=feed.erc721_address, abi=contracts_abi.erc721)
    steward_contract = w3t.eth.contract(address=feed.art_steward_address, abi=contracts_abi.artSteward)

    patron = erc721_contract.functions.ownerOf(42).call()
    price = steward_contract.functions.price().call()
    price_ether = w3t.fromWei(price, 'ether')
    print(price)
    print(price_ether)

    return render(request, 'feed.html', {'feed': feed, 'posts': posts, 'patron': patron, 'price': price_ether})


@csrf_exempt
def decrypt(request):
    global alice, enrico

    signature = request.POST.get('signature')
    print("Signature: " + signature)

    message_hash = defunct_hash_message(text='I am signing this nonce')
    account = w3.eth.account.recoverHash(message_hash, signature=signature)

    print(account)

    print("!!!!!!! DECRYPTING FEED !!!!!")
    feed = Feed.objects.all()[0]

    w3t = Web3(HTTPProvider(feed.provider))
    contract = w3t.eth.contract(address=feed.erc721_address, abi=contracts_abi.erc721)
    owner = contract.functions.ownerOf(42).call()
    print('Owner: ' + owner)
    print('Recovered: ' + account)

    if owner != account:
        print("NOT OWNER")
        return HttpResponse("CHEEKY MONKEY!")

    posts = Post.objects.all()

    labelStr = feed.label_string

    decrypted_posts = []

    for post in posts:
        message_kit = UmbralMessageKit.from_bytes(bytes.fromhex(post.content))
        signature = Signature.from_bytes(bytes.fromhex(post.signature))
        cleartext = alice.verify_from(stranger=enrico,
                                        message_kit=message_kit,
                                        signature=signature,
                                        decrypt=True,
                                        label=labelStr.encode())

        cleartext = cleartext.decode()
        print(str(post.created_date) + ": " + cleartext)
        decrypted_posts.append({'date': str(post.created_date), 'content': cleartext})

    return render(request, 'posts.html', {'posts': decrypted_posts})


def decryptOld(request):
    global alice

    print("!!!!!!! DECRYPTING FEED !!!!!")
    feed = Feed.objects.all()[0]
    posts = Post.objects.all()

    labelStr = feed.label_string
    policy_pubkey_hex = feed.policy_pubkey_hex
    policy_pubkey = UmbralPublicKey.from_bytes(bytes.fromhex(policy_pubkey_hex))

    bob_one_hex_keys = nuCypherHelper.GenKeys()                         # Dict of hex versions
    bob_one = nuCypherBob.StartBob(bob_one_hex_keys['priv_enc'], bob_one_hex_keys['priv_sig'])

    print('Grant Bob Access To Policy')
    policy_grant = nuCypherAlice.GrantPolicy(alice, labelStr, bob_one_hex_keys['pub_enc'], bob_one_hex_keys['pub_sig'])

    joined = nuCypherBob.JoinPolicy(bob_one, alice.stamp, labelStr)
    print("Bob has joined Policy.")

    alice_pub_key = UmbralPublicKey.from_bytes(bytes(alice.stamp))

    decrypted_posts = []

    message_kit = UmbralMessageKit.from_bytes(bytes.fromhex(posts[0].content))
    enricos_pubkey = UmbralPublicKey.from_bytes(bytes.fromhex(posts[0].enrico_pubkey_hex))

    decrypted_posts = []
    print("Alice Pub Key:")
    print(bytes(alice_pub_key).hex())
    decrypted = nuCypherBob.DecryptData(bob_one, labelStr, message_kit, enricos_pubkey, policy_pubkey, alice_pub_key)
    post_str = decrypted[0].decode()
    print('Decrypted Info:')
    print(post_str)

    for post in posts:
        message_kit = UmbralMessageKit.from_bytes(bytes.fromhex(post.content))
        enricos_pubkey = UmbralPublicKey.from_bytes(bytes.fromhex(post.enrico_pubkey_hex))
        decrypted = nuCypherBob.DecryptData(bob_one, labelStr, message_kit, enricos_pubkey, policy_pubkey, alice_pub_key)
        post_str = decrypted[0].decode()
        print(post.created_date + ": " + post_str)
        decrypted_posts.append({'date': post.created_date, 'content': post_str})

    return render(request, 'posts.html', {'posts': decrypted_posts})
