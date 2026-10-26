"""Z0 roles: test issuer, wallet, relying party for the Vault ID layer.

Credential messages (indices matter; disclosed selectively):

    0: adult boolean            (disclosed on request)
    1: resident-EU boolean     (disclosed on request)
    2: vault holder pseudonym  (never disclosed in Z0)
    3: wallet secret           (never disclosed; possession proof)

Holder binding: the wallet secret is a hidden signed message, so only the
holder can produce a valid presentation. Per-verifier pseudonym
lambda_v = HMAC-SHA256(wallet_secret, verifier_id) is folded into the
presentation header, so the proof's challenge commits to it: it cannot be
swapped, it is stable for one site and unlinkable across sites.
"""

import hashlib
import hmac
import os

from . import bbs


class Issuer:
    """The test issuer (the hub's BBS key in the real design)."""

    def __init__(self):
        self.sk, self.pk = bbs.keygen()
        self.header = b"vault-z0-test-issuer/v1"

    def issue(self, adult: bool, resident_eu: bool, vault_pseudonym: bytes,
             wallet_secret: bytes) -> bytes:
        messages = [
            b"adult: " + str(adult).encode(),
            b"resident-EU: " + str(resident_eu).encode(),
            b"vault-id: " + vault_pseudonym.hex().encode(),
            wallet_secret,
        ]
        return bbs.sign(self.sk, self.pk, self.header, messages)


class Wallet:
    """The holder's phone: carries the credential, presents, never mints."""

    def __init__(self):
        self.wallet_secret = os.urandom(32)
        self.vault_pseudonym = os.urandom(16)
        self.credential = None
        self.issuer_pk = None
        self.issuer_header = None

    def receive(self, issuer: "Issuer", credential: bytes):
        self.credential = credential
        self.issuer_pk = issuer.pk
        self.issuer_header = issuer.header

    def pseudonym_for(self, verifier_id: bytes) -> bytes:
        return hmac.new(self.wallet_secret, b"z0-pseudonym:" + verifier_id,
                        hashlib.sha256).digest()

    def present(self, verifier_id: bytes, nonce: bytes,
                disclosed_indexes=(0,)) -> dict:
        if self.credential is None:
            raise ValueError("no credential")
        # The wallet knows adult/resident are True for the Z0 demo holder.
        messages = [
            b"adult: True",
            b"resident-EU: True",
            b"vault-id: " + self.vault_pseudonym.hex().encode(),
            self.wallet_secret,
        ]
        pseudonym = self.pseudonym_for(verifier_id)
        ph = nonce + verifier_id + pseudonym
        proof = bbs.proof_gen(self.credential, self.issuer_pk,
                              self.issuer_header, ph, messages,
                              list(disclosed_indexes))
        disclosed = [messages[i] for i in disclosed_indexes]
        return {
            "proof": proof,
            "disclosed": disclosed,
            "disclosed_indexes": list(disclosed_indexes),
            "pseudonym": pseudonym,
            "ph": ph,
            "message_count": len(messages),
        }


class RelyingParty:
    """A demo verifier: checks the proof, the nonce binding and the pseudonym."""

    def __init__(self, issuer_pk, issuer_header, verifier_id: bytes):
        self.issuer_pk = issuer_pk
        self.issuer_header = issuer_header
        self.verifier_id = verifier_id

    def verify(self, presentation: dict, nonce: bytes) -> bool:
        expected_ph = nonce + self.verifier_id + presentation["pseudonym"]
        if presentation["ph"] != expected_ph:
            return False  # wrong nonce or audience: replay or misbinding
        return bbs.proof_verify(
            self.issuer_pk,
            presentation["proof"],
            self.issuer_header,
            presentation["ph"],
            presentation["disclosed"],
            presentation["disclosed_indexes"],
            presentation["message_count"],
        )
