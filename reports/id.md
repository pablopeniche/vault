# Proofs travel, identity stays home

The ID layer is how a verified human proves themselves online without handing over identity. The rig already produces the rarest credential on the internet — a hardware-rooted, continuously renewed proof that one specific living person is present — and the hub's secure element can sign that evidence into credentials. The owner's phone carries them and presents zero-knowledge proofs, so a relying party receives statements ("over 18", "an EU resident", "the same owner as last time", "a verified human at the keyboard right now") and no data. Three tiers do the work: selective-disclosure credentials for attributes, a membership proof over the trace log for presence, and wrapped external proofs for legal identity. The pieces exist and the regulatory wind is behind them — the EU has made zero-knowledge presentation mandatory for its wallet-based age verification — but no deployed system joins continuous verification to any of them. That join is the product. The layer is software, so its first phase needs nothing but a phone and can be built while the bench parts ship.

*Standards are cited as of October 2026, and drafts are labelled as drafts. "Proposal" marks design choices made for Vault, and the pass marks below are proposals, not established benchmarks.*

## 1. The idea: what only Vault can prove

Every deployed zero-knowledge identity system proves something once, at enrollment. zkPassport scans the chip in a passport or national ID — more than 130 countries — and generates the proof on the phone, so the verifier gets an answer and never the document [1]. Anon Aadhaar verifies the Indian government's RSA signature over the Aadhaar QR code inside a circuit and emits a proof that attests identity without revealing it [2]. World ID's Orb checks iris uniqueness once, for about 18 million people, and stores a Proof of Human on the phone — a proof of human, explicitly not of identity [3, 4, 5].

What none of them can say is the sentence online services actually need: the verified owner's body is at the keyboard as of thirty seconds ago. That is what the rig produces all day, every day [the rig](index.html). The ID layer's job is to carry that proof across the internet without carrying the person with it.

| System | Proves | Checked when | The gap for online ID |
|---|---|---|---|
| zkPassport | The document is genuine and its attributes hold | Once, at the scan | Says nothing about who holds the phone now |
| Anon Aadhaar | The holder possesses a government-signed ID | Once, at enrollment | Same, and the project is still marked under development [2] |
| World ID | A unique human exists | Once, at the Orb | Uniqueness without continuity or identity |
| Vault | A specific, living, continuously verified human is present | Continuously, all day | What this page is for |

## 2. Three tiers: attributes, presence, legal identity

| Tier | A relying party learns | How | Exists today |
|---|---|---|---|
| Z1, attributes without identity | "Over 18", "an EU resident", "the same owner as last time", a per-site pseudonym — never the birthdate, address or Vault ID | Selective disclosure: BBS signatures or SD-JWT, presented per site | BBS is at IETF draft-12; SD-JWT is RFC 9901; the W3C cryptosuites give unlinkable derived proofs [6, 7, 8, 9] |
| Z2, presence without location in the log | "A continuously verified Vault owner is presenting now" — without revealing which Vault, which checkpoint or which checks | A SNARK over the trace log: prove a hub-signed checkpoint sits in the Merkle tree within the last minute | Phone-class proving already ships [1]; the log is already a Merkle tree, see [the command chain](agents.html) |
| Z3, legal attributes without custody | "Government-verified age and nationality", without Vault or the site ever holding the document | Wrapped external proofs: passport NFC on the phone, EUDI wallet credentials | zkPassport ships; the EU wallet obligation lands in December 2026 [1, 10, 11] |

Z2 is the product. Anyone with a phone can do Z1 and Z3; only a rig can say who is present right now. And the tiers compose: one presentation can prove that a verified human is present, is over 18, and holds an EU passport, with each fact hidden from the others.

## 3. Architecture: issue, carry, prove

The hub issues the credential: its secure element already signs checkpoints, and a credential is the same signature over a set of claims, in the issuer-holder-verifier shape of the Verifiable Credential model [12]. The "human root" the [command chain](agents.html) defines becomes one: a living owner passed the checks at time T. Credentials expire fast — minutes, not years — so a stolen credential goes stale on its own (proposal).

The phone carries and presents. It is already the trace-log witness, and it receives presenting rights through the command chain's narrowing tokens, so it can prove and never mint. Presentations are actions like any other: they flow through the same gateway and the same Merkle log, consequential disclosures confirm the way consequential commands do, and the duress finger suppresses a marked credential instead of unlocking anything (proposal). Transport is OpenID4VP 1.0, an OpenID final specification since July 2025 with conformance certification live since August 2026 and more than 30 jurisdictions on the stack, the EU wallet among them [13, 14].

External attributes arrive as proofs, not documents: the phone scans the passport chip and wraps it [1], or receives an EUDI credential, and the hub stores none of it.

## 4. Standards: build on what is finishing now

| Piece | What it gives | Status, October 2026 |
|---|---|---|
| BBS Signature Scheme | Selective disclosure and unlinkable proofs, constant-size signature | IETF CFRG draft-12 [6] |
| Data Integrity BBS Cryptosuites v1.0 | Unlinkable derived proofs for verifiable credentials | W3C specification [7] |
| SD-JWT and SD-JWT VC | Selective disclosure in the JWT world | RFC 9901 since Nov 2025; the VC format at draft-13 [8, 9] |
| OpenID4VP 1.0 and HAIP | Presentation protocol and interoperability profile | Final July 2025; certification since August 2026 [13, 14] |
| EU age verification app | The flagship consumer ZKP flow | ZKP is the mandatory presentation mechanism, with plain mDoc as fallback; ETSI TS 119 476-2 stable draft end-2026 [10] |
| eIDAS 2.0 wallet | Person identification data and attestations across the EU | Each member state must offer a wallet by about 24 December 2026; 24 of 27 will miss the deadline, with Italy furthest along [11, 15] |

The regulatory read matters more than any single specification. The EU's own analysis holds that selective disclosure is the mature part and unlinkability is the gap — signature-based formats such as SD-JWT and mDoc can still allow cross-service tracking, and it recommends exactly the stronger techniques this layer defaults to: zero-knowledge proofs and anonymous credentials [16]. The W3C's overview makes the same point from the format side: of the signature algorithms being standardized, only BBS natively supports selective disclosure [17].

## 5. What never leaves: the privacy ladder

- Biometric templates and raw signals never leave the hub. That is rig law, unchanged.
- Trace-log contents stay on the owner's side. A Z2 proof carries a Merkle membership, which is a hash, not a record.
- Attributes stay in the credential until revealed. A BBS presentation discloses only the chosen claims, and even the issuer cannot link a presentation back to issuance [6, 7].
- Wrapped documents never exist as documents online. The phone emits the proof; the passport stays in the pocket [1].

Revocation is the one place the ladder needs new work, and it is a design decision rather than a gap: unlinkable presentations cannot be checked against a serial-number list without re-linking them, so Z1 uses an accumulator or a published non-revocation root that the proof itself checks (proposal) [6].

## 6. Open problems: what still has to be solved

- **Who vouches for attributes.** Vault self-certifies presence (Z2); "born 1990" needs an anchor. Passport NFC, a bank or the EU wallet — the plan wraps all three and stores none.
- **Coercion.** Every tier passes for a coerced owner, so presentations gate like vault actions: the duress finger suppresses or downgrades a credential rather than unlocking anything (proposal).
- **Quantum.** BBS and pairing-based SNARKs are not post-quantum; the Z2 circuit stays portable to hash-based proving so the layer can swap without redesign (proposal).
- **Succession and recovery.** Credentials inherit the heirs and ceremonies the report already defines. A lost phone re-enrolls from the hub, which is the point of having a hub.
- **The issuer boundary.** The hub knows who the owner is; sites must never learn it. The presentation formats enforce the boundary, and the Z0 linkability pass mark audits it.

## 7. Build plan: Z0 can start now

| Phase | Build | Pass mark (proposal) |
|---|---|---|
| Z0, phone only | A wallet holding a BBS credential from a test issuer; a demo relying party verifying "over 18" and a per-site pseudonym over OpenID4VP | A presentation generates in under 1 s on the phone and verifies in under 100 ms; two sites cannot correlate 100 presentations from one holder |
| Z1, with the P1 hub | The secure element signs the human-root credential; a SNARK proves a checkpoint sits in the trace log within 60 s; presentations go through the gateway and log | The Z2 proof runs in under 1 s on the phone; zero biometric-template or log-content bytes ever transmitted, asserted from captures; a duress-marked credential is suppressed in at least 99 of 100 trials |
| Z2, interop | zkPassport wrapping for government attributes; EUDI presentations against the ETSI ZKP profile | One demo site accepts a Vault-native proof and an EUDI credential through the same flow |

Z0 is pure software: no bench, no hub, no unproven physiology. It runs in parallel with the P0 bench from day one, and its demo relying party is the natural first customer of the whole layer.

## 8. Sources

1. [zkPassport](https://zkpassport.id/). *Vendor page.*
2. [Anon Aadhaar documentation](https://documentation.anon-aadhaar.pse.dev/docs/intro). *Project documentation.*
3. [World ID](https://world.org/world-id). *Vendor page.*
4. [World, "World ID Full-Stack Proof of Human"](https://world.org/blog/announcements/world-id-full-stack-proof-of-human). *Vendor announcement.*
5. [World privacy FAQs](https://world.org/blog/world/world-privacy-faqs). *Vendor documentation.*
6. [Looker et al., The BBS Signature Scheme (IETF CFRG draft-12, Sept 2026)](https://www.ietf.org/archive/id/draft-irtf-cfrg-bbs-signatures-12.html). *IETF draft.*
7. [W3C, Data Integrity BBS Cryptosuites v1.0](https://www.w3.org/TR/vc-di-bbs). *W3C specification.*
8. [RFC 9901, Selective Disclosure for JSON Web Tokens (Nov 2025)](https://www.rfc-editor.org/rfc/rfc9901). *IETF RFC.*
9. [SD-JWT-based Verifiable Credentials (IETF draft-13)](https://www.ietf.org/archive/id/draft-ietf-oauth-sd-jwt-vc-13.html). *IETF draft.*
10. [De Rosa (European Commission), "Proving age, revealing nothing else: zero-knowledge proofs in the EU age verification blueprint" (ETSI workshop, Sept 2026)](https://docbox.etsi.org/ESI/Open/workshops/202609%20ETSI_CEN%20workshop%20on%20EU%20Digital%20Framework%20centring%20on%20the%20EU%20Identity%20Wallet/Session%2005%20-%203%20-%20EU_AV_ZKP_ETSI_Workshop_v3.pdf). *Standards-body presentation.*
11. [Regulation (EU) 2024/1183 (eIDAS 2.0)](https://eur-lex.europa.eu/eli/reg/2024/1183/oj). *EU regulation.*
12. [W3C, Verifiable Credentials Data Model 2.0](https://www.w3.org/TR/vc-data-model-2.0/). *W3C recommendation.*
13. [OpenID for Verifiable Presentations 1.0](https://openid.net/specs/openid-4-verifiable-presentations-1_0.html). *OpenID final specification.*
14. [OpenID Foundation, "OpenID4VP and OpenID4VCI conformance tests are complete and open for self-certification" (Aug 2026)](https://openid.net/openid4vp-and-openid4vci-conformance-tests-are-complete-and-open-for-self-certification). *Foundation announcement.*
15. [Euronews, "EU digital wallet: 24 of 27 members will miss the deadline" (Sept 2026)](https://www.euronews.com/my-europe/2026/09/16/eu-digital-wallet-24-of-27-members-will-miss-the-deadline). *News coverage.*
16. [openideurope, "EUDI Wallet privacy: selective disclosure and unlinkability" (Oct 2026)](https://www.openideurope.eu/digital-identity/eudi-wallet-privacy). *Independent analysis.*
17. [W3C, Verifiable Credentials Overview](https://www.w3.org/TR/vc-overview). *W3C note.*
