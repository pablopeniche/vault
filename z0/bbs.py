"""BBS signature scheme, per IETF CFRG draft-irtf-cfrg-bbs-signatures-12.

Pure-Python reference over BLS12-381 (py_ecc). Implements KeyGen, Sign,
Verify, ProofGen and ProofVerify with selective disclosure, following the
draft's CoreSign / CoreProofGen / CoreProofVerify structure, the
serialize/proof octet formats (80-byte signatures, ~112 + 32*hidden-byte
proofs) and the SHAKE-256 ciphersuite
("BBS_BLS12381G1_XOF:SHAKE-256_SSWU_RO_").

Deviations from draft-12, documented for the Z0 prototype (see z0/README.md):

- Message generators and P1 are derived transparently as G1 * hash_to_scalar(seed)
  instead of the ciphersuite's RFC 9380 SSWU hash_to_curve. Sound for a
  self-consistent prototype; not interoperable with other draft-12 stacks.
- expand_message is a SHAKE-256 XOF close to RFC 9380's expand_message_xof,
  not byte-exact.
- Deserialized points are checked on-curve but not subgroup-checked (all
  points produced here are in the subgroup by construction).

Scalar field: r = curve_order. Points are py_ecc optimized Jacobian
triplets. Timeings: ProofGen does no pairings (fast); ProofVerify does two
(~1 s total in pure Python; the production target of <100 ms assumes the Rust
reference implementation).
"""

import hashlib
import os

from py_ecc.optimized_bls12_381 import (
    G1, G2, FQ, add, multiply, neg, normalize, pairing,
    curve_order as R, field_modulus as P, is_on_curve,
)

# --- Ciphersuite constants (draft-12, SHAKE-256 ciphersuite) --------------

CIPHERSUITE_ID = b"BBS_BLS12381G1_XOF:SHAKE-256_SSWU_RO_"
API_ID = CIPHERSUITE_ID + b"H2G_HM2S_"
OCTET_SCALAR_LENGTH = 32
OCTET_POINT_LENGTH = 48
EXPAND_LEN = 48
HASH_TO_SCALAR_DST = API_ID + b"H2S_"

B = FQ(4)  # y^2 = x^3 + 4


# --- XOF and hashing -------------------------------------------------------

def expand_message(msg: bytes, dst: bytes, length: int) -> bytes:
    """SHAKE-256 XOF, close to RFC 9380 expand_message_xof (see module doc)."""
    b_0 = hashlib.shake_256(
        msg + length.to_bytes(2, "big") + len(dst).to_bytes(1, "big") + dst
    ).digest(32)
    return hashlib.shake_256(
        b_0 + (0).to_bytes(1, "big") + length.to_bytes(2, "big")
    ).digest(length)


def hash_to_scalar(msg_octets: bytes, dst: bytes) -> int:
    return int.from_bytes(expand_message(msg_octets, dst, EXPAND_LEN), "big") % R


def i2osp(x: int, n: int) -> bytes:
    return x.to_bytes(n, "big")


# --- Point serialization (compressed, ZCash-style) --------------------------

def point_to_octets_E1(pt) -> bytes:
    x, y = normalize(pt)
    xb = x.n.to_bytes(OCTET_POINT_LENGTH, "big")
    head = (xb[0] & 0x1F) | 0x80 | (0x20 if y.n & 1 else 0)
    return bytes([head]) + xb[1:]


def octets_to_point_E1(data: bytes):
    if len(data) != OCTET_POINT_LENGTH:
        return None
    x = ((data[0] & 0x1F) << 376) | int.from_bytes(data[1:], "big")
    y2 = (pow(x, 3, P) + 4) % P
    y = pow(y2, (P + 1) // 4, P)
    if (y * y) % P != y2:
        return None
    if (y & 1) != (1 if data[0] & 0x20 else 0):
        y = P - y
    pt = (FQ(x), FQ(y), FQ(1))
    return pt if is_on_curve(pt, B) else None


# --- Generators --------------------------------------------------------------

def _generator(seed: bytes, index: int) -> tuple:
    k = hash_to_scalar(seed + i2osp(index, 8), API_ID + b"Z0_GENERATOR_SEED_")
    return multiply(G1, k)


def create_generators(count: int, api_id: bytes) -> list:
    seed = api_id + b"MESSAGE_GENERATOR_SEED"
    return [_generator(seed, i + 1) for i in range(count)]


def P1_POINT() -> tuple:
    return _generator(CIPHERSUITE_ID + b"H2G_HM2S_BP_MESSAGE_GENERATOR_SEED", 1)


# --- serialize / octets (draft 4.2.4) ---------------------------------------

def serialize(elements) -> bytes:
    out = b""
    for el in elements:
        if isinstance(el, int):
            out += i2osp(el, 8) if el < 2**64 else i2osp(el % R, OCTET_SCALAR_LENGTH)
        elif isinstance(el, tuple):
            out += point_to_octets_E1(el)
        elif isinstance(el, bytes):
            out += el
        else:
            raise ValueError("bad element")
    return out


def signature_to_octets(signature) -> bytes:
    A, e = signature
    return point_to_octets_E1(A) + i2osp(e, OCTET_SCALAR_LENGTH)


def octets_to_signature(data: bytes):
    if len(data) != OCTET_POINT_LENGTH + OCTET_SCALAR_LENGTH:
        return None
    A = octets_to_point_E1(data[:OCTET_POINT_LENGTH])
    if A is None:
        return None
    e = int.from_bytes(data[OCTET_POINT_LENGTH:], "big")
    if e == 0 or e >= R:
        return None
    return (A, e)


def proof_to_octets(proof) -> bytes:
    Abar, Bbar, D, e_hat, r1_hat, r3_hat, commitments, c = proof
    out = serialize([Abar, Bbar, D]) + i2osp(e_hat, OCTET_SCALAR_LENGTH)
    out += i2osp(r1_hat, OCTET_SCALAR_LENGTH) + i2osp(r3_hat, OCTET_SCALAR_LENGTH)
    out += i2osp(len(commitments), 8)
    for m in commitments:
        out += i2osp(m, OCTET_SCALAR_LENGTH)
    out += i2osp(c, OCTET_SCALAR_LENGTH)
    return out


def octets_to_proof(data: bytes):
    pl, sl = OCTET_POINT_LENGTH, OCTET_SCALAR_LENGTH
    try:
        Abar = octets_to_point_E1(data[0:pl]); assert Abar is not None
        Bbar = octets_to_point_E1(data[pl:2 * pl]); assert Bbar is not None
        D = octets_to_point_E1(data[2 * pl:3 * pl]); assert D is not None
        o = 3 * pl
        e_hat = int.from_bytes(data[o:o + sl], "big"); o += sl
        r1_hat = int.from_bytes(data[o:o + sl], "big"); o += sl
        r3_hat = int.from_bytes(data[o:o + sl], "big"); o += sl
        n = int.from_bytes(data[o:o + 8], "big"); o += 8
        commitments = []
        for _ in range(n):
            commitments.append(int.from_bytes(data[o:o + sl], "big")); o += sl
        c = int.from_bytes(data[o:o + sl], "big"); o += sl
        assert o == len(data)
        return (Abar, Bbar, D, e_hat, r1_hat, r3_hat, commitments, c)
    except Exception:
        return None


# --- Keys --------------------------------------------------------------------

def keygen(sk: int = None) -> (int, tuple):
    """KeyGen/SkToPk: SK in [1, r), PK = SK * BP2 (a G2 point)."""
    if sk is None:
        sk = int.from_bytes(os.urandom(32), "big") % (R - 1) + 1
    assert 0 < sk < R
    return sk, multiply(G2, sk)


# --- Core operations (draft 3.6) --------------------------------------------

def _calculate_domain(pk_point, Q1, H_points, header: bytes, api_id: bytes) -> int:
    dom_array = [len(H_points), Q1] + list(H_points)
    dom_octs = serialize(dom_array) + api_id
    dom_input = point_to_octets_E2(pk_point) + dom_octs + i2osp(len(header), 8) + header
    return hash_to_scalar(dom_input, api_id + b"H2S_")


def point_to_octets_E2(pt) -> bytes:
    x, y = normalize(pt)
    x0, x1 = x.coeffs
    xb = x0.to_bytes(48, "big") + x1.to_bytes(48, "big")
    head = (xb[0] & 0x1F) | 0x80 | (0x20 if y.coeffs[1] & 1 else 0)
    return bytes([head]) + xb[1:]


def messages_to_scalars(messages, api_id=API_ID) -> list:
    return [hash_to_scalar(m, api_id + b"H2S_") for m in messages]


def _calculate_random_scalars(count: int) -> list:
    return [int.from_bytes(os.urandom(EXPAND_LEN), "big") % R for _ in range(count)]


def core_sign(sk, pk_point, generators, header, message_scalars, api_id=API_ID):
    Q1, Hs = generators[0], generators[1:]
    domain = _calculate_domain(pk_point, Q1, Hs, header, api_id)
    e = hash_to_scalar(
        serialize([sk] + list(message_scalars) + [domain]), api_id + b"H2S_"
    )
    p1 = P1_POINT()
    Bp = add(p1, multiply(Q1, domain))
    for H, m in zip(Hs, message_scalars):
        Bp = add(Bp, multiply(H, m))
    A = multiply(Bp, pow(sk + e, -1, R))
    return (A, e)


def core_verify(pk_point, signature, generators, header, message_scalars, api_id=API_ID):
    A, e = signature
    Q1, Hs = generators[0], generators[1:]
    domain = _calculate_domain(pk_point, Q1, Hs, header, api_id)
    Bp = add(P1_POINT(), multiply(Q1, domain))
    for H, m in zip(Hs, message_scalars):
        Bp = add(Bp, multiply(H, m))
    lhs = pairing(add(pk_point, multiply(G2, e)), A)
    rhs = pairing(G2, Bp)
    return lhs == rhs


# --- Proof protocol subroutines (draft 3.7) ----------------------------------

def _proof_init(pk_point, signature, generators, random_scalars, header,
               message_scalars, undisclosed_indexes, api_id):
    A, e = signature
    L = len(message_scalars)
    U = len(undisclosed_indexes)
    assert len(random_scalars) == U + 5
    r1, r2, e_t, r1_t, r3_t = random_scalars[:5]
    m_tildes = random_scalars[5:]
    Q1, Hs = generators[0], generators[1:]
    domain = _calculate_domain(pk_point, Q1, Hs, header, api_id)
    Bp = add(P1_POINT(), multiply(Q1, domain))
    for H, m in zip(Hs, message_scalars):
        Bp = add(Bp, multiply(H, m))
    D = multiply(Bp, r2)
    Abar = multiply(A, (r1 * r2) % R)
    Bbar = add(multiply(D, r1), neg(multiply(Abar, e)))
    T1 = add(multiply(Abar, e_t), multiply(D, r1_t))
    T2 = multiply(D, r3_t)
    for H_j, m_t in zip((Hs[j] for j in undisclosed_indexes), m_tildes):
        T2 = add(T2, multiply(H_j, m_t))
    return (Abar, Bbar, D, T1, T2, domain)


def _challenge(init_res, disclosed_messages, disclosed_indexes, ph, api_id):
    R_count = len(disclosed_indexes)
    c_arr = [R_count]
    for i, m in zip(disclosed_indexes, disclosed_messages):
        c_arr += [i, m]
    c_arr += list(init_res)
    c_octs = serialize(c_arr) + i2osp(len(ph), 8) + ph
    return hash_to_scalar(c_octs, api_id + b"H2S_")


def _proof_finalize(init_res, challenge, e_value, random_scalars, undisclosed_messages):
    U = len(undisclosed_messages)
    r1, r2, e_t, r1_t, r3_t = random_scalars[:5]
    m_tildes = random_scalars[5:]
    Abar, Bbar, D = init_res[0], init_res[1], init_res[2]
    r3 = pow(r2, -1, R)
    e_hat = (e_t + e_value * challenge) % R
    r1_hat = (r1_t - r1 * challenge) % R
    r3_hat = (r3_t - r3 * challenge) % R
    m_hats = [(m_t + m * challenge) % R
              for m_t, m in zip(m_tildes, undisclosed_messages)]
    return (Abar, Bbar, D, e_hat, r1_hat, r3_hat, m_hats, challenge)


def _proof_verify_init(pk_point, proof, generators, header,
                       disclosed_messages, disclosed_indexes, api_id):
    Abar, Bbar, D, e_hat, r1_hat, r3_hat, m_hats, c = proof
    U, Rd = len(m_hats), len(disclosed_indexes)
    L = Rd + U
    assert len(generators) == L + 1
    Q1, Hs = generators[0], generators[1:]
    all_idx = list(range(L))
    hidden_idx = [i for i in all_idx if i not in disclosed_indexes]
    domain = _calculate_domain(pk_point, Q1, Hs, header, api_id)
    T1 = add(add(multiply(Bbar, c), multiply(Abar, e_hat)), multiply(D, r1_hat))
    Bv = add(P1_POINT(), multiply(Q1, domain))
    for i, m in zip(disclosed_indexes, disclosed_messages):
        Bv = add(Bv, multiply(Hs[i], m))
    T2 = add(multiply(Bv, c), multiply(D, r3_hat))
    for j, m_hat in zip(hidden_idx, m_hats):
        T2 = add(T2, multiply(Hs[j], m_hat))
    return (Abar, Bbar, D, T1, T2, domain)


# --- Interface operations (draft 3.5) ---------------------------------------

def sign(sk, pk_point, header: bytes, messages: list) -> bytes:
    scalars = messages_to_scalars(messages)
    generators = create_generators(len(messages) + 1, API_ID)
    sig = core_sign(sk, pk_point, generators, header, scalars, API_ID)
    return signature_to_octets(sig)


def verify(pk_point, signature_octets: bytes, header: bytes, messages: list) -> bool:
    sig = octets_to_signature(signature_octets)
    if sig is None:
        return False
    scalars = messages_to_scalars(messages)
    generators = create_generators(len(messages) + 1, API_ID)
    return core_verify(pk_point, sig, generators, header, scalars, API_ID)


def proof_gen(sk_holder_signature_octets: bytes, pk_point, header: bytes,
             ph: bytes, messages: list, disclosed_indexes: list) -> bytes:
    signature = octets_to_signature(sk_holder_signature_octets)
    if signature is None:
        raise ValueError("bad signature")
    L = len(messages)
    scalars = messages_to_scalars(messages)
    generators = create_generators(L + 1, API_ID)
    undisclosed_indexes = [i for i in range(L) if i not in disclosed_indexes]
    random_scalars = _calculate_random_scalars(5 + len(undisclosed_indexes))
    init_res = _proof_init(pk_point, signature, generators, random_scalars,
                           header, scalars, undisclosed_indexes, API_ID)
    disclosed_messages = [scalars[i] for i in disclosed_indexes]
    challenge = _challenge(init_res, disclosed_messages, disclosed_indexes, ph, API_ID)
    undisclosed_messages = [scalars[i] for i in undisclosed_indexes]
    proof = _proof_finalize(init_res, challenge, signature[1],
                           random_scalars, undisclosed_messages)
    return proof_to_octets(proof)


def proof_verify(pk_point, proof_octets: bytes, header: bytes, ph: bytes,
                disclosed_messages: list, disclosed_indexes: list,
                total_message_count: int) -> bool:
    proof = octets_to_proof(proof_octets)
    if proof is None:
        return False
    if len(proof[6]) + len(disclosed_indexes) != total_message_count:
        return False
    disclosed = messages_to_scalars(disclosed_messages)
    generators = create_generators(total_message_count + 1, API_ID)
    init_res = _proof_verify_init(pk_point, proof, generators, header,
                                 disclosed, disclosed_indexes, API_ID)
    challenge = _challenge(init_res, disclosed, disclosed_indexes, ph, API_ID)
    if challenge != proof[7]:
        return False
    Abar, Bbar, D = proof[0], proof[1], proof[2]
    # From ProofInit: Bbar = r1*r2*(B - A*e) = Abar * x, so e(Abar, W) = e(Bbar, BP2)
    lhs = pairing(pk_point, Abar)
    rhs = pairing(G2, Bbar)
    return lhs == rhs
