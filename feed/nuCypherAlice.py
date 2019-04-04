import datetime
import json
import os
import shutil

import maya
from twisted.logger import globalLogPublisher

from nucypher.characters.lawful import Bob, Ursula
from nucypher.config.characters import AliceConfiguration
from nucypher.crypto.powers import DecryptingPower, SigningPower
from nucypher.network.middleware import RestMiddleware
from nucypher.utilities.logging import SimpleObserver
import uuid

from umbral.keys import UmbralPublicKey


def StartAlice(Passphrase):
    """Start an Alice. The Authority."""
    print("Starting A New Alice...")

    # Twisted Logger
    globalLogPublisher.addObserver(SimpleObserver())

    TEMP_ALICE_DIR = os.path.join('/', 'tmp', 'alices', str(uuid.uuid4()))
    print('Alice Temp Dir: ' + TEMP_ALICE_DIR)

    # We expect the url of the seednode as the first argument.
    SEEDNODE_URL = 'localhost:11500'
    SEEDNODE_URL = '18.222.119.242:9151'

    ursula = Ursula.from_seed_and_stake_info(seed_uri=SEEDNODE_URL,
                                             federated_only=True,
                                             minimum_stake=0)

    alice_config = AliceConfiguration(
        config_root=os.path.join(TEMP_ALICE_DIR),
        is_me=True,
        known_nodes={ursula},
        start_learning_now=False,
        federated_only=True,
        learn_on_same_thread=True,
    )

    alice_config.initialize(password=Passphrase)
    alice_config.keyring.unlock(password=Passphrase)
    alicia = alice_config.produce()

    # We will save Alicia's config to a file for later use
    alice_config_file = alice_config.to_configuration_file()

    # Let's get to learn about the NuCypher network
    alicia.start_learning_loop(now=True)

    return alicia


def CreatePolicy(Alice, LabelStr):
    """Create A Policy. Returns umbral.keys.UmbralPublicKey"""
    # The Policy Label is a bytestring that categorizes the data that Alicia wants to share.
    label = LabelStr.encode()

    # Alicia can create the public key associated to the policy label,
    # even before creating any associated policy.
    policy_pubkey = Alice.get_policy_pubkey_from_label(label)

    print("The policy public key for "
          "label '{}' is {}".format(label.decode("utf-8"), policy_pubkey.to_bytes().hex()))

    return policy_pubkey


def GrantPolicy(Alice, Label, BobPublicKeyEnc, BobPublicKeySig):
    """Grant access to a Bob."""
    # Alicia now wants to share data associated with this label.
    # To do so, she needs the public key of the recipient.
    # In this example, we generate it on the fly (for demonstration purposes)

    Pub_Enc = UmbralPublicKey.from_bytes(bytes.fromhex(BobPublicKeyEnc))
    Pub_Sig = UmbralPublicKey.from_bytes(bytes.fromhex(BobPublicKeySig))

    powers_and_material = {
        DecryptingPower: Pub_Enc,
        SigningPower: Pub_Sig
    }

    # We create a view of the Bob who's going to be granted access.
    bob_view = Bob.from_public_keys(powers_and_material=powers_and_material, federated_only=True)

    # Here are our remaining Policy details, such as:
    # - Policy duration
    policy_end_datetime = maya.now() + datetime.timedelta(days=5)
    # - m-out-of-n: This means Alicia splits the re-encryption key in 5 pieces and
    #               she requires Bob to seek collaboration of at least 3 Ursulas
    m, n = 1, 1

    Label = Label.encode()
    # With this information, Alicia creates a policy granting access to Bob.
    # The policy is sent to the NuCypher network.
    print("Creating access policy for the Bob...")
    policy = Alice.grant(bob=bob_view,
                          label=Label,
                          m=m,
                          n=n,
                          expiration=policy_end_datetime)
    print("Policy Granted")
    return policy

    """
    # For the demo, we need a way to share with Bob some additional info
    # about the policy, so we store it in a JSON file
    policy_info = {
        "policy_pubkey": policy.public_key.to_bytes().hex(),
        "alice_sig_pubkey": bytes(alicia.stamp).hex(),
        "label": label.decode("utf-8"),
    }

    filename = POLICY_FILENAME
    with open(filename, 'w') as f:
        json.dump(policy_info, f)
    """
