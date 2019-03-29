from umbral.keys import UmbralPrivateKey


def GenKeys():
    """Create new Private and Public keys."""
    enc_privkey = UmbralPrivateKey.gen_key()
    sig_privkey = UmbralPrivateKey.gen_key()
    enc_pubkey = enc_privkey.get_pubkey()
    sig_pubkey = sig_privkey.get_pubkey()

    keys = {
        'priv_enc': enc_privkey.to_bytes().hex(),
        'priv_sig': sig_privkey.to_bytes().hex(),
        'pub_enc': enc_pubkey.to_bytes().hex(),
        'pub_sig': sig_pubkey.to_bytes().hex()
    }

    return keys
