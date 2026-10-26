"""Z0 pass-mark tests: correctness, selective disclosure, unlinkability,
replay resistance, and timings. Run: python3 -m unittest discover -s z0"""

import statistics
import time
import unittest

from z0 import bbs
from z0.roles import Issuer, Wallet, RelyingParty


class TestBBS(unittest.TestCase):
    def test_pairing_bilinearity(self):
        # Anchors the group-equation orientation used in core_verify.
        lhs = bbs.pairing(bbs.multiply(bbs.G2, 7), bbs.multiply(bbs.G1, 5))
        rhs = bbs.pairing(bbs.G2, bbs.multiply(bbs.G1, 35))
        self.assertEqual(lhs, rhs)

    def test_sign_verify_roundtrip(self):
        sk, pk = bbs.keygen()
        msgs = [b"adult: True", b"resident-EU: True", b"secret-3", b"secret-4"]
        sig = bbs.sign(sk, pk, b"h", msgs)
        self.assertEqual(len(sig), 80)  # 48-byte point + 32-byte scalar
        self.assertTrue(bbs.verify(pk, sig, b"h", msgs))

    def test_tampered_message_rejected(self):
        sk, pk = bbs.keygen()
        msgs = [b"adult: True", b"resident-EU: True"]
        sig = bbs.sign(sk, pk, b"h", msgs)
        self.assertFalse(bbs.verify(pk, sig, b"h", [b"adult: False", b"resident-EU: True"]))

    def test_selective_disclosure(self):
        sk, pk = bbs.keygen()
        msgs = [b"adult: True", b"resident-EU: True", b"hidden-2", b"hidden-3"]
        sig = bbs.sign(sk, pk, b"h", msgs)
        ph = b"nonce" + b"site-a" + b"pseud"
        proof = bbs.proof_gen(sig, pk, b"h", ph, msgs, [0])
        # Verifier sees only message 0 and cannot learn the hidden ones.
        self.assertTrue(bbs.proof_verify(pk, proof, b"h", ph,
                                        [b"adult: True"], [0], 4))
        # Wrong disclosed claim fails.
        self.assertFalse(bbs.proof_verify(pk, proof, b"h", ph,
                                          [b"adult: False"], [0], 4))
        # Wrong presentation header (nonce/audience) fails: replay binding.
        self.assertFalse(bbs.proof_verify(pk, proof, b"h", b"other" + b"site-a" + b"pseud",
                                          [b"adult: True"], [0], 4))
        # Wrong message count fails.
        self.assertFalse(bbs.proof_verify(pk, proof, b"h", ph,
                                          [b"adult: True"], [0], 3))

    def test_proofs_are_randomized(self):
        sk, pk = bbs.keygen()
        msgs = [b"adult: True", b"resident-EU: True", b"h2", b"h3"]
        sig = bbs.sign(sk, pk, b"h", msgs)
        proofs = [bbs.proof_gen(sig, pk, b"h", b"ph", msgs, [0]) for _ in range(8)]
        self.assertEqual(len(set(proofs)), 8)  # unlinkable: no two alike


class TestZ0PassMarks(unittest.TestCase):
    """The Z0 row of the ID layer build plan."""

    def setUp(self):
        self.issuer = Issuer()
        self.wallet = Wallet()
        cred = self.issuer.issue(True, True, self.wallet.vault_pseudonym,
                                 self.wallet.wallet_secret)
        self.wallet.receive(self.issuer, cred)
        self.site_a = RelyingParty(self.issuer.pk, self.issuer.header, b"site-a.example")
        self.site_b = RelyingParty(self.issuer.pk, self.issuer.header, b"site-b.example")

    def test_two_sites_cannot_correlate_100_presentations(self):
        """Pass mark: two sites cannot correlate 100 presentations from one holder."""
        pseud_a, proofs_a = set(), set()
        for i in range(100):
            pres = self.wallet.present(b"site-a.example", b"na-%d" % i)
            self.assertTrue(self.site_a.verify(pres, b"na-%d" % i))
            pseud_a.add(pres["pseudonym"])
            proofs_a.add(pres["proof"])
        pseud_b, proofs_b = set(), set()
        for i in range(100):
            pres = self.wallet.present(b"site-b.example", b"nb-%d" % i)
            self.assertTrue(self.site_b.verify(pres, b"nb-%d" % i))
            pseud_b.add(pres["pseudonym"])
            proofs_b.add(pres["proof"])
        self.assertEqual(len(pseud_a), 1)          # stable per site
        self.assertEqual(len(pseud_b), 1)
        self.assertNotEqual(pseud_a, pseud_b)       # unlinkable across sites
        self.assertEqual(len(proofs_a | proofs_b), 200)  # no repeated proof

    def test_replay_rejected(self):
        pres = self.wallet.present(b"site-a.example", b"nonce-1")
        self.assertTrue(self.site_a.verify(pres, b"nonce-1"))
        self.assertFalse(self.site_a.verify(pres, b"nonce-2"))
        self.assertFalse(self.site_b.verify(pres, b"nonce-1"))  # wrong audience

    def test_stolen_credential_cannot_present(self):
        """Holder binding: the hidden wallet secret is required to present."""
        thief = Wallet()
        thief.receive(self.issuer, self.wallet.credential)  # credential only
        pres = thief.present(b"site-a.example", b"nonce-x")
        self.assertFalse(self.site_a.verify(pres, b"nonce-x"))

    def test_timings(self):
        """Pass mark: presentation under 1 s; verification recorded against
        the 100 ms production target (pure-Python reference: two pairings)."""
        gen_ms, ver_ms = [], []
        for i in range(5):
            t0 = time.perf_counter()
            pres = self.wallet.present(b"site-a.example", b"t-%d" % i)
            gen_ms.append((time.perf_counter() - t0) * 1000)
            t0 = time.perf_counter()
            ok = self.site_a.verify(pres, b"t-%d" % i)
            ver_ms.append((time.perf_counter() - t0) * 1000)
            self.assertTrue(ok)
        gen, ver = statistics.median(gen_ms), statistics.median(ver_ms)
        print("\n  Z0 timings (pure Python, py_ecc): "
              "ProofGen %.0f ms, ProofVerify %.0f ms "
              "(production target via the Rust reference: 1000 ms / 100 ms)" % (gen, ver))
        self.assertLess(gen, 1000)
        self.assertLess(ver, 3000)  # pure-Python bound; see z0/README.md


if __name__ == "__main__":
    unittest.main(verbosity=2)
