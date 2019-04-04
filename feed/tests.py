from django.test import TestCase
from . import nuCypherHelper, nuCypherAlice, nuCypherBob, nuCypherEnrico
import uuid
import os
from umbral.keys import UmbralPublicKey
from nucypher.crypto.kits import UmbralMessageKit
from .models import Feed, Post
from django.contrib.auth.models import User
from nucypher.characters.lawful import Enrico
from nucypher.crypto.kits import UmbralMessageKit
from umbral.signing import Signature


class NucypherTests(TestCase):
    def test_full_encrypt_decrypt(self):
        """Test full process - Alice creates policy, grants a Bob. Bob joins. Enrico encrypts something. Bob decrypts."""
        self.user = User.objects.create_user(username='testuser', password='12345')
        login = self.client.login(username='testuser', password='12345')

        users = User.objects.all()
        passphrase = 'this-is-the-longest-passpheare-ihope' + os.urandom(4).hex()
        labelStr = "TestLabel" + os.urandom(4).hex()
        print(passphrase)
        print(labelStr)
        f = Feed(owner=users[0], alice_passphrase=passphrase, label_string=labelStr, title="Test", description="Descr")
        f.save()

        feed = Feed.objects.all()[0]

        # Create a Policy
        # alice = nuCypherAlice.StartAlice(feed.alice_passphrase)
        alice = nuCypherAlice.StartAlice(passphrase)

        print("!!!!!!!!! ALICE 1:")
        print(bytes(alice.stamp).hex())
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

        print("POLICY CREATED & SAVED TO DB")
        print("ADDING A POST")

        # feed = Feed.objects.all()[0]
        # policy_pubkey_hex = feed.policy_pubkey_hex
        # policy_pubkey = UmbralPublicKey.from_bytes(bytes.fromhex(policy_pubkey_hex))

        print('Encrypting post: ')
        post = "This is a test post"

        enrico = Enrico(policy_encrypting_key=policy_pubkey)
        message_kit, _signature = enrico.encrypt_message(post.encode())

        print("MESSAGE KIT LENGHT: " + str(len(message_kit.to_bytes().hex())))
        print("MESSAGE KIT HEX:")
        print(message_kit.to_bytes().hex())

        enricos_pubkey = enrico.stamp

        p = Post(content=message_kit.to_bytes().hex(), enrico_pubkey_hex=bytes(enricos_pubkey).hex())
        p.save()

        print("POST SAVED TO DB")

        print("!!!!!!! DECRYPTING FEED !!!!!")
        # feed = Feed.objects.all()[0]
        # posts = Post.objects.all()

        alice2 = nuCypherAlice.StartAlice(passphrase)
        print("!!!!!!!!! ALICE 2:")
        print(bytes(alice2.stamp).hex())
        # alice = nuCypherAlice.StartAlice(feed.alice_passphrase)
        labelStr = feed.label_string
        # policy_pubkey_hex = feed.policy_pubkey_hex
        # policy_pubkey = UmbralPublicKey.from_bytes(bytes.fromhex(policy_pubkey_hex))

        bob_one_hex_keys = nuCypherHelper.GenKeys()                         # Dict of hex versions
        bob_one = nuCypherBob.StartBob(bob_one_hex_keys['priv_enc'], bob_one_hex_keys['priv_sig'])

        print('Grant Bob Access To Policy')
        policy_grant = nuCypherAlice.GrantPolicy(alice2, labelStr, bob_one_hex_keys['pub_enc'], bob_one_hex_keys['pub_sig'])

        aliceSigPubkey = alice.stamp
        print("USING ALICE1 PUB KEY: ")
        print(bytes(aliceSigPubkey).hex())
        # aliceSigPubkey = UmbralPublicKey.from_bytes(bytes(alice.stamp))
        joined = nuCypherBob.JoinPolicy(bob_one, alice2.stamp, labelStr)
        print("Bob has joined Policy.")

        alice_pub_key = UmbralPublicKey.from_bytes(bytes(alice.stamp))
        alice2_pub_key = UmbralPublicKey.from_bytes(bytes(alice2.stamp))

        decrypted_posts = []
        # message_kit = UmbralMessageKit.from_bytes(bytes.fromhex(post.content))
        # enricos_pubkey = UmbralPublicKey.from_bytes(bytes.fromhex(post.enrico_pubkey_hex))
        # decrypted = nuCypherBob.DecryptData(bob_one, labelStr, message_kit, enricos_pubkey, policy_pubkey, alice_pub_key)
        decrypted = nuCypherBob.DecryptData(bob_one, labelStr, message_kit, enricos_pubkey, policy_pubkey, alice2_pub_key)
        post_str = decrypted[0].decode()
        print('Decrypted Info:')
        print(post_str)
        # decrypted_posts.append({'date': post_str.date, 'content': post_str})
        """
        for post in posts:
            message_kit = UmbralMessageKit.from_bytes(bytes.fromhex(post.content))
            enricos_pubkey = UmbralPublicKey.from_bytes(bytes.fromhex(post.enrico_pubkey_hex))
            decrypted = nuCypherBob.DecryptData(bob_one, labelStr, message_kit, enricos_pubkey, policy_pubkey, alice_pub_key)
            post_str = decrypted[0].decode()
            print(post.created_date + ": " + post_str)
            decrypted_posts.append({'date': post.created_date, 'content': post_str})
        """

        #print("DECRYPTED MESSAGE")
        #print(decrypted_posts[0].content)

    def test_full_encrypt_decrypt_one_alice(self):
        """Test full process - Alice creates policy, grants a Bob. Bob joins. Enrico encrypts something. Bob decrypts."""
        self.user = User.objects.create_user(username='testuser', password='12345')
        login = self.client.login(username='testuser', password='12345')

        users = User.objects.all()
        passphrase = 'this-is-the-longest-passpheare-ihope' + os.urandom(4).hex()
        labelStr = "TestLabel" + os.urandom(4).hex()
        print(passphrase)
        print(labelStr)
        f = Feed(owner=users[0], alice_passphrase=passphrase, label_string=labelStr, title="Test", description="Descr")
        f.save()

        feed = Feed.objects.all()[0]

        # Create a Policy
        alice = nuCypherAlice.StartAlice(feed.alice_passphrase)
        # alice = nuCypherAlice.StartAlice(passphrase)

        print("ALICE STAMP:")
        print(bytes(alice.stamp).hex())
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

        print("POLICY CREATED & SAVED TO DB")
        print("ADDING A POST")

        feed = Feed.objects.all()[0]
        policy_pubkey_hex = feed.policy_pubkey_hex
        policy_pubkey = UmbralPublicKey.from_bytes(bytes.fromhex(policy_pubkey_hex))

        print('Encrypting post: ')
        post = "This is a test post"

        enrico = Enrico(policy_encrypting_key=policy_pubkey)
        message_kit, _signature = enrico.encrypt_message(post.encode())

        print("MESSAGE KIT LENGHT: " + str(len(message_kit.to_bytes().hex())))
        print("MESSAGE KIT HEX:")
        print(message_kit.to_bytes().hex())

        enricos_pubkey = enrico.stamp

        p = Post(content=message_kit.to_bytes().hex(), enrico_pubkey_hex=bytes(enricos_pubkey).hex())
        p.save()

        print("POST SAVED TO DB")

        print("!!!!!!! DECRYPTING FEED !!!!!")
        feed = Feed.objects.all()[0]
        posts = Post.objects.all()

        labelStr = feed.label_string
        policy_pubkey_hex = feed.policy_pubkey_hex
        policy_pubkey = UmbralPublicKey.from_bytes(bytes.fromhex(policy_pubkey_hex))

        bob_one_hex_keys = nuCypherHelper.GenKeys()                         # Dict of hex versions
        bob_one = nuCypherBob.StartBob(bob_one_hex_keys['priv_enc'], bob_one_hex_keys['priv_sig'])

        print('Grant Bob Access To Policy - Using Original Alice')
        policy_grant = nuCypherAlice.GrantPolicy(alice, labelStr, bob_one_hex_keys['pub_enc'], bob_one_hex_keys['pub_sig'])

        aliceSigPubkey = alice.stamp
        print("USING ALICE1 PUB KEY: ")
        print(bytes(aliceSigPubkey).hex())
        joined = nuCypherBob.JoinPolicy(bob_one, alice.stamp, labelStr)
        print("Bob has joined Policy.")

        alice_pub_key = UmbralPublicKey.from_bytes(bytes(alice.stamp))

        message_kit = UmbralMessageKit.from_bytes(bytes.fromhex(posts[0].content))
        enricos_pubkey = UmbralPublicKey.from_bytes(bytes.fromhex(posts[0].enrico_pubkey_hex))

        decrypted_posts = []
        decrypted = nuCypherBob.DecryptData(bob_one, labelStr, message_kit, enricos_pubkey, policy_pubkey, alice_pub_key)
        post_str = decrypted[0].decode()
        print('Decrypted Info:')
        print(post_str)
        # decrypted_posts.append({'date': post_str.date, 'content': post_str})
        """
        for post in posts:
            message_kit = UmbralMessageKit.from_bytes(bytes.fromhex(post.content))
            enricos_pubkey = UmbralPublicKey.from_bytes(bytes.fromhex(post.enrico_pubkey_hex))
            decrypted = nuCypherBob.DecryptData(bob_one, labelStr, message_kit, enricos_pubkey, policy_pubkey, alice_pub_key)
            post_str = decrypted[0].decode()
            print(post.created_date + ": " + post_str)
            decrypted_posts.append({'date': post.created_date, 'content': post_str})
        """

        #print("DECRYPTED MESSAGE")
        #print(decrypted_posts[0].content)

    def test_full_encrypt_decrypt_old(self):
        # Create a Policy
        passphrase = str(uuid.uuid4())
        alice = nuCypherAlice.StartAlice(passphrase)
        labelStr = "bobtestpolicy" + os.urandom(4).hex()
        policy_pubkey = None
        policy_pubkey = nuCypherAlice.CreatePolicy(alice, labelStr)     # Type: umbral.keys.UmbralPublicKey

        bob_one_hex_keys = nuCypherHelper.GenKeys()                         # Dict of hex versions
        bob_one = None
        bob_one = nuCypherBob.StartBob(bob_one_hex_keys['priv_enc'], bob_one_hex_keys['priv_sig'])

        enrico = nuCypherEnrico.GetEnrico(policy_pubkey)
        # enricos_pubkey = bytes(enrico.stamp)
        enricos_pubkey = enrico.stamp
        test_message = "This is a test"
        encrypted_message = None
        message_kit = nuCypherEnrico.EncryptData(enrico, test_message)
        print("Encrypted message: ")
        print(message_kit)
        message_kit_hex = message_kit.to_bytes().hex()

        print('Grant Bob Access To Policy')
        policy_grant = None
        policy_grant = nuCypherAlice.GrantPolicy(alice, labelStr, bob_one_hex_keys['pub_enc'], bob_one_hex_keys['pub_sig'])
        self.assertIsNot(policy_grant, None)

        aliceSigPubkey = alice.stamp
        print('Alice Sig Pub Key (Hex): ', bytes(aliceSigPubkey).hex())
        joined = nuCypherBob.JoinPolicy(bob_one, aliceSigPubkey, labelStr)
        print("Bob has joined Policy.")

        actual_key = UmbralPublicKey.from_bytes(bytes(alice.stamp))

        decrypted = nuCypherBob.DecryptData(bob_one, labelStr, UmbralMessageKit.from_bytes(bytes.fromhex(message_kit_hex)), enricos_pubkey, policy_pubkey, actual_key)

        print('Decrypted:')
        print(decrypted)
        self.assertIs(decrypted[0].decode(), test_message)

    def test_full_encrypt_decrypt_only_alice(self):
        """Test full process - Alice creates policy, grants a Bob. Bob joins. Enrico encrypts something. Bob decrypts."""
        self.user = User.objects.create_user(username='testuser', password='12345')
        login = self.client.login(username='testuser', password='12345')

        users = User.objects.all()
        passphrase = 'this-is-the-longest-passpheare-ihope' + os.urandom(4).hex()
        labelStr = "TestLabel" + os.urandom(4).hex()
        print(passphrase)
        print(labelStr)
        f = Feed(owner=users[0], alice_passphrase=passphrase, label_string=labelStr, title="Test", description="Descr")
        f.save()

        feed = Feed.objects.all()[0]

        # Create a Policy
        alice = nuCypherAlice.StartAlice(feed.alice_passphrase)
        # alice = nuCypherAlice.StartAlice(passphrase)

        print("ALICE STAMP:")
        print(bytes(alice.stamp).hex())
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

        print("POLICY CREATED & SAVED TO DB")
        print("ADDING A POST")

        feed = Feed.objects.all()[0]
        policy_pubkey_hex = feed.policy_pubkey_hex
        policy_pubkey = UmbralPublicKey.from_bytes(bytes.fromhex(policy_pubkey_hex))

        print('Encrypting post: ')
        post = "This is a test post"

        enrico = Enrico(policy_encrypting_key=policy_pubkey)
        message_kit, _signature = enrico.encrypt_message(post.encode())
        signature_hex = bytes(_signature).hex()

        print("MESSAGE KIT LENGHT: " + str(len(message_kit.to_bytes().hex())))
        print("MESSAGE KIT HEX:")
        print(message_kit.to_bytes().hex())

        print("SIGNATURE")
        print(str(type(_signature)))

        enricos_pubkey = enrico.stamp

        p = Post(content=message_kit.to_bytes().hex(), enrico_pubkey_hex=bytes(enricos_pubkey).hex())
        p.save()

        print("POST SAVED TO DB")

        print("!!!!!!! DECRYPTING FEED !!!!!")
        feed = Feed.objects.all()[0]
        posts = Post.objects.all()

        labelStr = feed.label_string
        policy_pubkey_hex = feed.policy_pubkey_hex
        policy_pubkey = UmbralPublicKey.from_bytes(bytes.fromhex(policy_pubkey_hex))

        aliceSigPubkey = alice.stamp
        print("USING ALICE1 PUB KEY: ")
        print(bytes(aliceSigPubkey).hex())
        alice_pub_key = UmbralPublicKey.from_bytes(bytes(alice.stamp))
        signature = Signature.from_bytes(bytes.fromhex(signature_hex))

        message_kit = UmbralMessageKit.from_bytes(bytes.fromhex(posts[0].content))

        cleartext = alice.verify_from(stranger=enrico,
                                        message_kit=message_kit,
                                        signature=signature,
                                        decrypt=True,
                                        label=labelStr.encode())


        print("DECRYPTED MESSAGE")
        print(cleartext)
