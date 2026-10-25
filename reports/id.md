# Proofs travel, identity stays home

The ID layer is the protocol stack that takes Vault's continuously verified human online without disclosing identity. The hub's secure element signs a per-second checkpoint into the trace log while the checks hold; BBS credentials carry attributes with selective disclosure and unlinkable derived proofs; a Groth16 circuit proves a fresh checkpoint sits in the log without revealing which; wrapped passport and EUDI proofs carry legal attributes; OpenID4VP 1.0 transports the presentation. This page specifies the key hierarchy, the credential formats, the proof constructions, the presentation flow, revocation, and the threat each mechanism addresses, then a build plan with pass marks.

*Standards are cited as of October 2026, and drafts are labelled as drafts. "Proposal" marks design choices made for Vault, and the pass marks below are proposals, not established benchmarks.*

## 1. The idea: what only Vault can prove

Deployed zero-knowledge identity systems verify once, at enrollment. zkPassport scans a passport chip — more than 130 countries — and generates the proof on the phone, so the verifier gets an answer, never the document [1]. Anon Aadhaar verifies the Indian government's RSA signature over the Aadhaar QR code inside a circuit [2]. World ID's Orb checks iris uniqueness once, for about 18 million people, and stores a Proof of Human on the phone — a proof of human, explicitly not of identity [3, 4, 5].

None of them can prove the sentence online services need: the verified owner's body is at the keyboard as of thirty seconds ago. The rig produces that all day [the rig](index.html); this layer carries it online.

| System | Proves | Checked when | The gap for online ID |
|---|---|---|---|
| zkPassport | The document is genuine and its attributes hold | Once, at the scan | Says nothing about who holds the phone now |
| Anon Aadhaar | The holder possesses a government-signed ID | Once, at enrollment | Same, and the project is still marked under development [2] |
| World ID | A unique human exists | Once, at the Orb | Uniqueness without continuity or identity |
| Vault | A specific, living, continuously verified human is present | Continuously, all day | What this page specifies |

## 2. Keys and trust anchors

| Key | Held by | Algorithm | Signs |
|---|---|---|---|
| Hub root key | The hub's secure element (SE051) | P-256 or Ed25519 | Checkpoints; certifies every other hub key |
| BBS issuer key | Hub software, certified by the root key | BLS12-381 | Z1 attribute credentials |
| Wallet key | The phone's hardware keystore (Secure Enclave / StrongBox class) | P-256 | Key binding on every presentation |
| Attribute-source keys | Passport document signers, EUDI member states, banks | RSA or ECDSA (external) | Z3 source documents and credentials |
| Verifier trust | Relying-party trust lists, eIDAS-style | — | Which issuer keys a site accepts |

The SE051 signs P-256 and Ed25519 but not pairing-based BLS12-381 [6], so the BBS issuer key is a hub software key certified by the secure element at pairing; checkpoint signing never leaves the element. BBS keys and proofs are defined over BLS12-381 [7].

## 3. The credentials

The hub issues the credential in the issuer-holder-verifier shape of the Verifiable Credential model [8]. Four kinds exist:

| Credential | Claims | Lifetime | Signed by |
|---|---|---|---|
| Checkpoint (trace-log leaf) | Epoch timestamp, checks-held bitmap, owner commitment | 60 s of validity | Hub root key, in the secure element |
| Presence proof (Z2) | None — a proof about a checkpoint | One presentation | The wallet, as a Groth16 proof |
| Attribute credential (Z1) | adult, resident-EU, per-verifier pseudonym, wallet-key commitment | Minutes to hours; long-lived attribute form up to 90 days | BBS issuer key |
| External credential (Z3) | Age, nationality, PID claims | Per source | The external issuer |

Predicates are issuer-signed booleans, not range proofs: at enrollment the hub reads the wrapped passport's date of birth, computes "adult", and signs the boolean (proposal). The holder discloses true or false; no birthdate is ever signed into circulation.

## 4. Z1: selective disclosure, in detail

**Issuance.** The hub BBS-signs the claim set plus a commitment to the wallet key, producing a constant-size signature of about 80 bytes [9, 10, 13].

**Presentation.** The wallet runs ProofGen over the signature, disclosing only the chosen claims, and produces a derived proof of about 272 + 32 × (number of hidden claims) bytes [13]. The proof is zero-knowledge over the hidden claims and the signature itself, and is unlinkable: the issuer cannot connect it to issuance, and two sites cannot connect it to each other [7, 10]. The presentation header carries the verifier's nonce and audience, binding the proof to one request [7].

**Key binding.** The wallet key is a committed message inside the credential; each presentation also carries a wallet-key signature over (nonce, audience), the same replay defense as SD-JWT's KB-JWT [11]. A credential lent to another phone fails this check.

**Per-verifier pseudonym.** The wallet derives λ_v = HMAC(wallet_secret, verifier_id) and includes it as a claim, disclosed on request: the same site sees the same pseudonym, different sites see unrelated ones (proposal).

**Format choice.** BBS is the default because it is the only signature algorithm being standardized that natively supports selective disclosure [13]. SD-JWT [11, 12] is the fallback where a JWT-only verifier exists, accepting its weaker unlinkability [22].

## 5. Z2: the presence proof, in detail

**What is proven.** A checkpoint signed by the hub root key sits in the trace log's Merkle tree, and its timestamp is within the last 60 seconds. Nothing about which checkpoint, which owner, or which checks leaks.

**The log.** Leaves are the per-second checkpoints; the tree is Poseidon-hashed (SNARK-friendly) at depth about 25 for a year of leaves. The hub publishes roots to a transparency log witnessed by owners' phones, the structure the report already uses for the trace log; verifiers fetch the current root set. A single-hub tree hides the checkpoint but not the hub; cross-owner anonymity needs a shared log across hubs, the Certificate Transparency pattern (proposal, listed in section 11).

**The circuit** (Groth16 over BN254 or BLS12-381 [14]):

| Public inputs | Private inputs |
|---|---|
| Merkle root R, hub root public key, freshness bound t_min, verifier nonce, nullifier N_v | Checkpoint leaf, its signature, Merkle path, wallet secret s |

Constraints: the signature verifies under the public key; the path connects the leaf to R; the leaf timestamp ≥ t_min; and N_v = Poseidon(s, verifier_id). The nullifier is the Semaphore pattern: one site sees a stable pseudonym, two sites cannot link [15]. Proof size is about 192 bytes and verification is two pairing checks, a few milliseconds server-side [14]. Phone-side proving for circuits of this size is the class zkPassport already runs [1]; the pass mark below sets the time budget.

## 6. Z3: wrapped legal attributes

**Passports.** The chip implements ICAO 9303 passive authentication: the document signer's key, chained to the country root, signs the data groups [16]. The phone reads the chip, and the circuit verifies that signature, checks the age predicate against the date-of-birth group, and emits a proof plus a nullifier — zkPassport's deployed construction [1]. Nothing else in the chip leaves the phone.

**EUDI wallet.** The phone receives member-state credentials over OpenID4VCI and presents them under the EU's ZKP profile [17, 18]. Vault adds the Z2 presence proof alongside; it does not replace the wallet. The obligation for every member state lands in December 2026, and 24 of 27 will miss it, so interop is real but staggered [19].

## 7. The presentation protocol

1. The relying party sends a signed OpenID4VP 1.0 authorization request: a DCQL query for the claims it may ask for ("adult", "presence within 60 s"), its nonce and audience [20].
2. The wallet checks the relying party's registration on a trust list, the same mutual identification the EU model requires [18].
3. The wallet derives the Z1 proof and runs the Z2 prover against the request nonce, then adds the key-binding signature.
4. The relying party verifies: the issuer trust anchor; BBS ProofVerify or Groth16 verification; key binding over (nonce, audience); the freshness window; revocation state. It logs a hash of the presentation, never the presentation itself.
5. Consequential presentations route through Vault's own gateway and confirm like any consequential command; a duress-marked credential is suppressed rather than presented (proposal).

Certified OpenID4VP verifiers have existed since August 2026, with more than 30 jurisdictions on the stack [21].

## 8. Revocation and expiry

Presence needs no revocation: the credential dies in 60 seconds, and a hub that stops seeing its owner simply stops signing. Attribute credentials live up to 90 days, so they need it: the issuer publishes a cryptographic accumulator over revoked serials, and the presentation proves non-revocation in-circuit, keeping unlinkability [7]. Status-list bitstrings are the fallback, at the cost of some cross-site correlation [22]. Succession follows the report's heir ceremony: a new hub root re-issues.

## 9. Threat model

| Attack | Stopped by |
|---|---|
| Replay of a captured presentation | Key binding over (nonce, audience); the presentation header [7, 11] |
| Credential sharing (lending the phone) | Key binding with the hardware wallet key, plus Z2 freshness: presence requires the rig, which is on the owner |
| Cross-site correlation | BBS unlinkability and per-verifier nullifiers [7, 15]; the EU flags this as the part weaker formats miss [22] |
| Forged attributes | BBS signature; Groth16 verification over the hub signature [7, 14] |
| Stale presence | The 60 s freshness bound in the circuit |
| Stolen credential | The 60 s TTL; the hub stops signing when checks fail |
| Coerced presentation | Duress suppression; residual risk documented in section 11 |
| Long-term quantum exposure | BBS and Groth16 are pairing-based; circuits stay portable to hash-based proving (proposal) |

## 10. Build plan

| Phase | Build | Pass mark (proposal) |
|---|---|---|
| Z0, phone only | A wallet holding a BBS credential from a test issuer [9]; a demo relying party speaking OpenID4VP 1.0 [20, 21]; per-verifier pseudonyms on the Semaphore pattern [15] | A Z1 presentation generates in under 1 s and verifies in under 100 ms; two sites cannot correlate 100 presentations |
| Z1, with the P1 hub | The secure element signs checkpoints; the Groth16 circuit [14] proves membership and freshness; presentations flow through the gateway | The Z2 proof generates in under 10 s on a 2026 phone (under 2 s as the optimization target) and verifies in under 50 ms; zero biometric-template or log-content bytes transmitted, asserted from captures; a duress-marked credential is suppressed in at least 99 of 100 trials |
| Z2, interop | zkPassport-style wrapping; EUDI presentations against the ETSI ZKP profile [18] | One demo site accepts a Vault-native proof and an EUDI credential through the same flow |

Z0 is pure software and runs in parallel with the P0 bench.

## 11. Open problems

- **Attribute anchoring.** Vault self-certifies presence; "born 1990" needs the passport, a bank or the EUDI wallet as source. All three are wrapped, none is stored.
- **Cross-owner anonymity.** A single-hub log hides the checkpoint, not the hub; hiding the owner across a population needs the shared transparency log of section 5, with its own governance.
- **Coercion.** Every tier passes for a coerced owner. Duress suppression covers presentations, but a verifier that watches the owner type can infer; the duress design must cover the online path explicitly.
- **Quantum.** Pairing-based throughout today; the swap path to hash-based proving is a port, not a redesign, only if the circuits stay small.
- **The SE boundary.** BBS lives in hub software because pairing curves are not in the SE051 [6]; a pairing-capable secure element or an HSM changes that line of the key table.

## 12. Sources

1. [zkPassport](https://zkpassport.id/). *Vendor page.*
2. [Anon Aadhaar documentation](https://documentation.anon-aadhaar.pse.dev/docs/intro). *Project documentation.*
3. [World ID](https://world.org/world-id). *Vendor page.*
4. [World, "World ID Full-Stack Proof of Human"](https://world.org/blog/announcements/world-id-full-stack-proof-of-human). *Vendor announcement.*
5. [World privacy FAQs](https://world.org/blog/world/world-privacy-faqs). *Vendor documentation.*
6. [NXP SE051 secure element](https://www.nxp.com/products/SE051). *Vendor product page.*
7. [Looker et al., The BBS Signature Scheme (IETF CFRG draft-12, Sept 2026)](https://www.ietf.org/archive/id/draft-irtf-cfrg-bbs-signatures-12.html). *IETF draft.*
8. [W3C, Verifiable Credentials Data Model 2.0](https://www.w3.org/TR/vc-data-model-2.0/). *W3C recommendation.*
9. [BBS signature reference implementation (GitHub)](https://github.com/decentralized-identity/bbs-signature). *Open-source project.*
10. [W3C, Data Integrity BBS Cryptosuites v1.0](https://www.w3.org/TR/vc-di-bbs). *W3C specification.*
11. [RFC 9901, Selective Disclosure for JSON Web Tokens (Nov 2025)](https://www.rfc-editor.org/rfc/rfc9901). *IETF RFC.*
12. [SD-JWT-based Verifiable Credentials (IETF draft-13)](https://www.ietf.org/archive/id/draft-ietf-oauth-sd-jwt-vc-13.html). *IETF draft.*
13. [W3C, Verifiable Credentials Overview](https://www.w3.org/TR/vc-overview). *W3C note.*
14. [Groth, "On the Size of Pairing-Based Non-Interactive Arguments" (EUROCRYPT 2016; ePrint 2016/260)](https://eprint.iacr.org/2016/260). *Peer-reviewed.*
15. [Semaphore](https://semaphore.appliedzkp.org/). *Open-source protocol.*
16. [ICAO Doc 9303, Machine Readable Travel Documents](https://www.icao.int/publications/pages/publication.aspx?docnum=9303). *International standard.*
17. [Regulation (EU) 2024/1183 (eIDAS 2.0)](https://eur-lex.europa.eu/eli/reg/2024/1183/oj). *EU regulation.*
18. [De Rosa (European Commission), "Proving age, revealing nothing else: zero-knowledge proofs in the EU age verification blueprint" (ETSI workshop, Sept 2026)](https://docbox.etsi.org/ESI/Open/workshops/202609%20ETSI_CEN%20workshop%20on%20EU%20Digital%20Framework%20centring%20on%20the%20EU%20Identity%20Wallet/Session%2005%20-%203%20-%20EU_AV_ZKP_ETSI_Workshop_v3.pdf). *Standards-body presentation.*
19. [Euronews, "EU digital wallet: 24 of 27 members will miss the deadline" (Sept 2026)](https://www.euronews.com/my-europe/2026/09/16/eu-digital-wallet-24-of-27-members-will-miss-the-deadline). *News coverage.*
20. [OpenID for Verifiable Presentations 1.0](https://openid.net/specs/openid-4-verifiable-presentations-1_0.html). *OpenID final specification.*
21. [OpenID Foundation, "OpenID4VP and OpenID4VCI conformance tests are complete and open for self-certification" (Aug 2026)](https://openid.net/openid4vp-and-openid4vci-conformance-tests-are-complete-and-open-for-self-certification). *Foundation announcement.*
22. [openideurope, "EUDI Wallet privacy: selective disclosure and unlinkability" (Oct 2026)](https://www.openideurope.eu/digital-identity/eudi-wallet-privacy). *Independent analysis.*
