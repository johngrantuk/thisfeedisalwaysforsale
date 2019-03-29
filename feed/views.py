from django.shortcuts import render
from django.http import JsonResponse
from .models import Feed, Post
from . import nuCypherHelper, nuCypherAlice
from django.views.decorators.csrf import csrf_exempt

def feed_admin(request):

    feed = Feed.objects.all()[0]
    return render(request, 'feed_admin.html', {'feed': feed})


def create_policy(request):
    if request.is_ajax():
        feed = Feed.objects.all()[0]

        # Create a Policy
        alice = nuCypherAlice.StartAlice(feed.alice_passphrase)
        labelStr = feed.label_string
        policy_pubkey = nuCypherAlice.CreatePolicy(alice, labelStr)     # Type: umbral.keys.UmbralPublicKey
        policy_pubkey_hex = policy_pubkey.to_bytes().hex()
        # print(str(type(policy_pubkey)))                 # <class 'umbral.keys.UmbralPublicKey'>
        # print(str(type(policy_pubkey_hex)))             # <class 'str'>
        feed.policy_pubkey = policy_pubkey_hex
        feed.save()

        data = {
            'policy_pubkey': policy_pubkey_hex
        }
        return JsonResponse(data)

@csrf_exempt
def add_post(request):
    if request.is_ajax():
        print(request.POST)
        post = request.POST.get('post')

        print('Saving post: ')
        print(post)

        # p = Dodavatel(nazov='Petr', dostupnost=1)
        # p.save()

        posts = Post.objects.all()

        return render(request, 'posts.html', {'posts': posts})
