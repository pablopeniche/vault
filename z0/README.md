# Z0: the ID layer's phone-only phase

A working BBS selective-disclosure credential, wallet and relying party for
the [ID layer](../id.html)'s Z0 row. Pure Python; the only dependency is
`py_ecc`.

```
pip install -r z0/requirements.txt
python3 -m unittest discover -s . -p "tests.py" -t .   # 9 tests, ~5 min
python3 -m z0.demo                                     # end-to-end flow
```

## What it implements

`z0/bbs.py` follows IETF CFRG draft-12 (the BBS Signature Scheme): KeyGen,
Sign, Verify, ProofGen, ProofVerify with selective disclosure, the
serialize/proof octet formats (80-byte signatures, 376-byte proofs for the
4-message demo credential) and the SHAKE-256 ciphersuite's constants.

`z0/roles.py` implements the three roles of the ID layer spec:

- **Issuer** — the hub's BBS key for the demo. Signs four messages: the
  `adult` and `resident-EU` booleans (issuer-signed predicates, so no range
  proofs), the holder's vault pseudonym, and the wallet secret.
- **Wallet** — the phone. Holds the credential and presents; it can prove
  and never mint. The wallet secret is a hidden signed message, so a stolen
  credential file cannot present (holder binding). The per-verifier
  pseudonym is `HMAC(wallet_secret, verifier_id)`, folded into the
  presentation header so the Fiat-Shamir challenge commits to it.
- **RelyingParty** — checks the proof, the nonce and audience binding
  (replay defense), and sees only the disclosed claims.

## Pass marks (Z0 row of the ID layer build plan)

| Mark | Result |
|---|---|
| Presentation generates under 1 s | **191 ms** (pure Python) |
| Verifies under 100 ms | **1185 ms** in pure Python; the mark targets the Rust reference stack, where the same two pairings are ~1 ms. Recorded, not met, in this reference implementation |
| Two sites cannot correlate 100 presentations | **Pass**: pseudonym stable per site, distinct across sites, all 200 proofs unique |
| Replay / misbound audience rejected | **Pass** |
| Stolen credential cannot present | **Pass** |

## Deviations from draft-12 (documented, deliberate)

- Message generators and P1 are `G1 * hash_to_scalar(seed)` instead of the
  ciphersuite's RFC 9380 SSWU hash-to-curve. Sound for a self-consistent
  prototype; not interoperable with other draft-12 stacks yet.
- `expand_message` is a SHAKE-256 XOF close to RFC 9380's
  `expand_message_xof`, not byte-exact.
- Deserialized points are checked on-curve but not subgroup-checked; every
  point this code produces is in the subgroup by construction.

Moving Z0 to the Rust reference implementation (github.com/
decentralized-identity/bbs-signature) is the path to the 100 ms verify
mark and interop; this Python stack stays as the readable reference and test
oracle.
