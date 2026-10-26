"""Z0 demo: issue a credential, present to two sites, verify both.

Run:  python3 -m z0.demo
"""

import time

from . import bbs
from .roles import Issuer, Wallet, RelyingParty


def timed(fn, *a, **k):
    t0 = time.perf_counter()
    out = fn(*a, **k)
    return out, (time.perf_counter() - t0) * 1000


def main():
    issuer = Issuer()
    wallet = Wallet()

    cred, ms = timed(issuer.issue, True, True, wallet.vault_pseudonym,
                     wallet.wallet_secret)
    print("issuer  : credential issued, %d bytes, %.0f ms" % (len(cred), ms))

    wallet.receive(issuer, cred)

    site_a = RelyingParty(issuer.pk, issuer.header, b"site-a.example")
    site_b = RelyingParty(issuer.pk, issuer.header, b"site-b.example")

    nonce_a1, nonce_a2 = b"nonce-a-1", b"nonce-a-2"

    pres, ms = timed(wallet.present, b"site-a.example", nonce_a1)
    ok, ms_v = timed(site_a.verify, pres, nonce_a1)
    print("wallet  : presentation to site-a, proof %d bytes, %.0f ms"
          % (len(pres["proof"]), ms))
    print("site-a  : verified=%s in %.0f ms, saw claims %s, pseudonym %s..."
          % (ok, ms_v, pres["disclosed"], pres["pseudonym"].hex()[:16]))

    # Same site, second presentation: stable pseudonym, different proof bytes.
    pres2, _ = timed(wallet.present, b"site-a.example", nonce_a2)
    ok2, _ = timed(site_a.verify, pres2, nonce_a2)
    print("site-a  : verified=%s, same pseudonym=%s, proof bytes differ=%s"
          % (ok2, pres2["pseudonym"] == pres["pseudonym"],
             pres2["proof"] != pres["proof"]))

    # Second site: unrelated pseudonym, still verifies.
    pres_b, _ = timed(wallet.present, b"site-b.example", b"nonce-b-1")
    ok_b, _ = timed(site_b.verify, pres_b, b"nonce-b-1")
    print("site-b  : verified=%s, pseudonym differs from site-a=%s"
          % (ok_b, pres_b["pseudonym"] != pres["pseudonym"]))

    # Replay: old presentation against a fresh nonce must fail.
    replay_ok = site_a.verify(pres, b"nonce-a-2")
    print("site-a  : replay of old presentation accepted=%s (must be False)"
          % replay_ok)

    print("\nbilinear sanity: pairing(multiply(G2,k), G1) == pairing(G2, G1)^k:",
          bbs.pairing(bbs.multiply(bbs.G2, 7), bbs.multiply(bbs.G1, 5))
          == bbs.pairing(bbs.G2, bbs.multiply(bbs.G1, 35)))


if __name__ == "__main__":
    main()
