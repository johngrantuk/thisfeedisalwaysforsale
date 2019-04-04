from django.shortcuts import render
from django.http import JsonResponse
from .models import Feed, Post
from . import nuCypherHelper, nuCypherAlice, nuCypherBob, nuCypherEnrico
from django.views.decorators.csrf import csrf_exempt
from umbral.keys import UmbralPublicKey
from nucypher.characters.lawful import Enrico
from nucypher.crypto.kits import UmbralMessageKit

def feed_admin(request):

    feed = Feed.objects.all()[0]
    posts = Post.objects.all()
    return render(request, 'feed_admin.html', {'feed': feed, 'posts': posts})


def create_policy(request):
    if request.is_ajax():
        feed = Feed.objects.all()[0]

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

        data = {
            'policy_pubkey_hex': policy_pubkey_hex,
            'enrico_pubkey_hex': enrico_pubkey_hex
        }
        return JsonResponse(data)


@csrf_exempt
def add_post(request):
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
        enrico = Enrico(policy_encrypting_key=policy_pubkey)
        enricos_pubkey = enrico.stamp
        print("!!! Enricos Pub Key: ")
        print(bytes(enricos_pubkey).hex())
        # print(enrico_pubkey_hex)
        # message_kit = nuCypherEnrico.EncryptData(enrico, post)
        message_kit, _signature = enrico.encrypt_message(post.encode())

        print("MESSAGE KIT LENGHT: " + str(len(message_kit.to_bytes().hex())))
        print(message_kit.to_bytes().hex())
        # print("Encrypted message: ")
        # print(message_kit)
        # message_kit.to_bytes()
        p = Post(content=message_kit.to_bytes().hex(), enrico_pubkey_hex=bytes(enricos_pubkey).hex())
        p.save()

        return render(request, 'post.html', {'post': p})


def feed(request):

    feed = Feed.objects.all()[0]
    posts = Post.objects.all()
    return render(request, 'feed.html', {'feed': feed, 'posts': posts})


def decrypt(request):
    print("!!!!!!! DECRYPTING FEED !!!!!")
    feed = Feed.objects.all()[0]
    posts = Post.objects.all()

    alice = nuCypherAlice.StartAlice(feed.alice_passphrase)
    labelStr = feed.label_string
    policy_pubkey_hex = feed.policy_pubkey_hex
    policy_pubkey = UmbralPublicKey.from_bytes(bytes.fromhex(policy_pubkey_hex))

    bob_one_hex_keys = nuCypherHelper.GenKeys()                         # Dict of hex versions
    bob_one = nuCypherBob.StartBob(bob_one_hex_keys['priv_enc'], bob_one_hex_keys['priv_sig'])

    print('Grant Bob Access To Policy')
    policy_grant = nuCypherAlice.GrantPolicy(alice, labelStr, bob_one_hex_keys['pub_enc'], bob_one_hex_keys['pub_sig'])

    # aliceSigPubkey = alice.stamp
    aliceSigPubkey = UmbralPublicKey.from_bytes(bytes(alice.stamp))
    joined = nuCypherBob.JoinPolicy(bob_one, aliceSigPubkey, labelStr)
    print("Bob has joined Policy.")

    alice_pub_key = UmbralPublicKey.from_bytes(bytes(alice.stamp))

    decrypted_posts = []

    for post in posts:
        message_kit = UmbralMessageKit.from_bytes(bytes.fromhex(post.content))
        enricos_pubkey = UmbralPublicKey.from_bytes(bytes.fromhex(post.enrico_pubkey_hex))
        decrypted = nuCypherBob.DecryptData(bob_one, labelStr, message_kit, enricos_pubkey, policy_pubkey, alice_pub_key)
        post_str = decrypted[0].decode()
        print(post.created_date + ": " + post_str)
        decrypted_posts.append({'date': post.created_date, 'content': post_str})

    return render(request, 'posts.html', {'posts': decrypted_posts})
