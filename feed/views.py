from django.shortcuts import render
from django.http import JsonResponse
from .models import Feed, Post
from . import nuCypherHelper, nuCypherAlice, nuCypherEnrico
from django.views.decorators.csrf import csrf_exempt
from umbral.keys import UmbralPublicKey
from nucypher.characters.lawful import Enrico

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
        # print("Encrypted message: ")
        # print(message_kit)
        # message_kit.to_bytes()
        p = Post(content=message_kit.to_bytes(), enrico_pubkey_hex=bytes(enricos_pubkey).hex())
        p.save()

        return render(request, 'post.html', {'post': p})
