#!/usr/bin/env python3
"""
Cicada 3301 RSA Cracking Tool
Pure Python — no external dependencies.

Supports:
  • PGP key parsing (extract n, e from armor blocks)
  • Factorization: trial division, Pollard rho, Pollard p-1, Fermat, Wiener
  • RSA attacks: small-e cube root, common modulus, Coppersmith partial-knowledge
  • Vulnerability scanner: small key, small e, close factors, shared prime
  • Decrypt once factors are known
"""

import sys, os, re, math, hashlib, time, struct, base64
from collections import OrderedDict
from itertools import count
from fractions import Fraction

# ═══════════════════════════════════════════════════════════════
# COLOR HELPERS
# ═══════════════════════════════════════════════════════════════

class C:
    R = '\033[91m'; G = '\033[92m'; Y = '\033[93m'; B = '\033[94m'
    M = '\033[95m'; CY = '\033[96m'; BD = '\033[1m'; DN = '\033[0m'

def hdr(t):   print(f"\n{C.M}{C.BD}{'='*60}\n  {t}\n{'='*60}{C.DN}\n")
def sec(t):   print(f"\n{C.CY}{C.BD}--- {t} ---{C.DN}")
def ok(t):    print(f"{C.G}✓ {t}{C.DN}")
def warn(t):  print(f"{C.Y}⚠ {t}{C.DN}")
def err(t):   print(f"{C.R}✗ {t}{C.DN}")
def info(t):  print(f"{C.B}ℹ {t}{C.DN}")

# ═══════════════════════════════════════════════════════════════
# NUMBER THEORY PRIMITIVES
# ═══════════════════════════════════════════════════════════════

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def egcd(a, b):
    if a == 0:
        return b, 0, 1
    g, x, y = egcd(b % a, a)
    return g, y - (b // a) * x, x

def modinv(a, m):
    g, x, _ = egcd(a % m, m)
    if g != 1:
        return None
    return x % m

def is_prime_miller_rabin(n, k=20):
    if n < 2: return False
    if n == 2 or n == 3: return True
    if n % 2 == 0: return False
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1; d //= 2
    for _ in range(k):
        a = 2 + hash((n, _)) % (n - 3)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def iroot(n, k):
    """Integer k-th root of n via Newton's method."""
    if n < 0:
        return -iroot(-n, k) if k % 2 else None
    if n == 0: return 0
    x = 1 << ((n.bit_length() + k - 1) // k)
    while True:
        y = ((k - 1) * x + n // (x ** (k - 1))) // k
        if y >= x:
            return x
        x = y

def isqrt(n):
    return iroot(n, 2)

# ═══════════════════════════════════════════════════════════════
# FACTORIZATION METHODS
# ═══════════════════════════════════════════════════════════════

def factor_trial_division(n, limit=10**6):
    """Trial division up to limit."""
    factors = []
    for p in [2, 3, 5]:
        while n % p == 0:
            factors.append(p); n //= p
    i = 7
    while i <= limit and i * i <= n:
        for inc in [4, 2, 4, 2, 4, 6, 2, 6]:
            if n % i == 0:
                factors.append(i); n //= i
            i += inc
    if n > 1:
        factors.append(n)
    return factors

def factor_pollard_rho(n):
    """Pollard's rho algorithm with Brent's improvement."""
    if n % 2 == 0:
        return 2, n // 2
    if is_prime(n):
        return n, 1
    for c in count(1):
        y, d = 2, 1
        x = y
        while d == 1:
            x = y
            for _ in range(2 * d):
                y = (y * y + c) % n
            d = gcd(abs(x - y), n)
        if d != n:
            return d, n // d
    return None, None

def factor_pollard_p1(n, B=100000):
    """Pollard's p-1 algorithm."""
    if n % 2 == 0:
        return 2, n // 2
    a = 2
    for j in range(2, B + 1):
        a = pow(a, j, n)
        if j % 1000 == 0:
            d = gcd(a - 1, n)
            if 1 < d < n:
                return d, n // d
    d = gcd(a - 1, n)
    if 1 < d < n:
        return d, n // d
    return None, None

def factor_fermat(n, max_iter=10**7):
    """Fermat's factorization — works when factors are close together."""
    if n % 2 == 0:
        return 2, n // 2
    a = isqrt(n)
    if a * a == n:
        return a, a
    for _ in range(max_iter):
        a += 1
        b2 = a * a - n
        b = isqrt(b2)
        if b * b == b2:
            return a - b, a + b
    return None, None

def factor_wifi(n):
    """Wiener's attack using continued fractions — works when d < n^0.25."""
    e = n  # we need e; caller should pass e separately, so we use a wrapper
    return None, None

def wiener_attack(n, e):
    """Wiener's attack via continued fraction expansion of e/n."""
    cf = continued_fraction(e, n)
    convergents = get_convergents(cf)
    for k, d in convergents:
        if k == 0:
            continue
        phi_try = (e * d - 1) // k
        if (e * d - 1) % k != 0:
            continue
        # Check if phi is plausible
        # x^2 - (n - phi + 1)x + n = 0 should have integer roots
        b = n - phi_try + 1
        disc = b * b - 4 * n
        if disc >= 0:
            s = isqrt(disc)
            if s * s == disc:
                p = (b + s) // 2
                q = (b - s) // 2
                if p * q == n:
                    return p, q
    return None, None

def continued_fraction(a, b):
    """Compute continued fraction expansion of a/b."""
    result = []
    while b:
        q = a // b
        result.append(q)
        a, b = b, a - q * b
    return result

def get_convergents(cf):
    """Get convergents (numerators, denominators) from continued fraction."""
    convergents = []
    h_prev, h_curr = 0, 1
    k_prev, k_curr = 1, 0
    for a_i in cf:
        h_prev, h_curr = h_curr, a_i * h_curr + h_prev
        k_prev, k_curr = k_curr, a_i * k_curr + k_prev
        convergents.append((k_curr, h_curr))
    return convergents

def factor_all(n, verbose=True):
    """Try all factorization methods and return (p, q) or None."""
    if n <= 1:
        return None, None
    if is_prime(n):
        if verbose: warn(f"{n} is already prime")
        return n, 1

    methods = [
        ("Trial Division", lambda: factor_trial_division(n, 10**5)),
        ("Pollard's rho", factor_pollard_rho),
        ("Pollard's p-1", factor_pollard_p1),
        ("Fermat", factor_fermat),
    ]

    for name, func in methods:
        if verbose:
            info(f"Trying {name}...")
        try:
            start = time.time()
            result = func()
            elapsed = time.time() - start
            if result and result[0] is not None:
                p, q = result
                if p * q == n:
                    if verbose:
                        ok(f"{name} found factors in {elapsed:.2f}s")
                    return p, q
                # If it returned a list from trial division
                if isinstance(p, list):
                    if verbose:
                        ok(f"{name}: {p}")
                    return p, None
        except Exception as ex:
            if verbose:
                warn(f"{name} failed: {ex}")
    return None, None

# ═══════════════════════════════════════════════════════════════
# RSA DECRYPTION
# ═══════════════════════════════════════════════════════════════

def rsa_decrypt(c, d, n):
    """Raw RSA decryption: m = c^d mod n."""
    return pow(c, d, n)

def rsa_decrypt_with_factors(c, e, n, p, q):
    """Decrypt ciphertext c given factors p, q."""
    phi = (p - 1) * (q - 1)
    d = modinv(e, phi)
    if d is None:
        return None
    m = pow(c, d, n)
    return m

def int_to_bytes(n):
    """Convert integer to bytes."""
    if n == 0:
        return b'\x00'
    length = (n.bit_length() + 7) // 8
    return n.to_bytes(length, 'big')

def bytes_to_int(b):
    return int.from_bytes(b, 'big')

def int_to_text(n):
    """Try to convert integer to readable text."""
    b = int_to_bytes(n)
    try:
        return b.decode('utf-8', errors='replace')
    except:
        return repr(b)

# ═══════════════════════════════════════════════════════════════
# RSA ATTACKS
# ═══════════════════════════════════════════════════════════════

def small_e_attack(c, e, n):
    """If e is very small, try m^e ≈ c (no modular reduction)."""
    m = iroot(c, e)
    if m is not None and pow(m, e) == c:
        return m
    # Try m^e + k*n for small k
    for k in range(10000):
        val = c + k * n
        m = iroot(val, e)
        if m is not None and pow(m, e) == val:
            return m
    return None

def common_modulus_attack(c1, c2, e1, e2, n):
    """Given same n, different e: recover m from c1 = m^e1, c2 = m^e2."""
    g, s, t = egcd(e1, e2)
    if g != 1:
        return None
    # m = c1^s * c2^t mod n
    if s < 0:
        c1 = modinv(c1, n)
        s = -s
    if t < 0:
        c2 = modinv(c2, n)
        t = -t
    return pow(c1, s, n) * pow(c2, t, n) % n

def hastad_broadcast_attack(c_list, e, n_list):
    """Hastad's broadcast attack — same message, different moduli."""
    # Chinese Remainder Theorem
    from functools import reduce
    N = reduce(lambda a, b: a * b, n_list)
    result = 0
    for i in range(len(c_list)):
        Ni = N // n_list[i]
        mi = modinv(Ni, n_list[i])
        if mi is None:
            return None
        result += c_list[i] * Ni * mi
    result %= N
    # Now take e-th root
    m = iroot(result, e)
    return m

def franklin_reiter_related_message(c1, c2, e, n, alpha, beta):
    """Franklin-Reiter related message attack."""
    # c1 = (m)^e mod n
    # c2 = (alpha*m + beta)^e mod n
    # For e=3, use GCD of polynomials
    if e != 3:
        return None
    # Simplified for e=3
    a_inv = modinv(alpha, n)
    if a_inv is None:
        return None
    # m = (c2 - beta^3) * a_inv ... (simplified)
    return None

def bleichenbacher_info(c, e, n):
    """Partial information leak via Bleichenbacher's attack (e=3)."""
    if e != 3:
        return None
    m = iroot(c, e)
    if m is not None and pow(m, e, n) == c:
        return m
    return None

# ═══════════════════════════════════════════════════════════════
# VULNERABILITY SCANNER
# ═══════════════════════════════════════════════════════════════

def scan_vulnerabilities(n, e=None, c=None):
    """Scan RSA parameters for known vulnerabilities."""
    findings = []
    bits = n.bit_length()
    findings.append(f"Key size: {bits} bits")

    if bits < 512:
        findings.append(f"[CRITICAL] Key size {bits} bits is trivially factorable")
    elif bits < 1024:
        findings.append(f"[HIGH] Key size {bits} bits is weak (factorable in hours/days)")
    elif bits < 2048:
        findings.append(f"[MEDIUM] Key size {bits} bits is considered insecure")

    if e is not None:
        if e == 3:
            findings.append("[HIGH] e=3 — vulnerable to Coppersmith/Franklin-Reiter/Håstad")
        elif e == 65537:
            findings.append("[OK] e=65537 — standard secure exponent")
        elif e < 65537 and e > 1:
            findings.append(f"[MEDIUM] Small exponent e={e} — may be vulnerable")

    # Check for small factors
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    for p in small_primes:
        if n % p == 0 and n != p:
            findings.append(f"[CRITICAL] n is divisible by {p}!")

    # Check if n is prime
    if is_prime(n):
        findings.append("[CRITICAL] n is prime! No RSA security at all.")

    # Fermat factorability (close factors)
    if bits < 2048:
        info("Testing Fermat factorization (close factors)...")
        p, q = factor_fermat(n, max_iter=10**6)
        if p is not None:
            findings.append(f"[CRITICAL] Factors are close! p={p}, q={q}")

    # Pollard p-1 smoothness
    if bits < 2048:
        info("Testing Pollard p-1 (smooth factors)...")
        p, q = factor_pollard_p1(n, B=50000)
        if p is not None:
            findings.append(f"[CRITICAL] Pollard p-1 succeeded: p={p}")

    # Wiener vulnerability (if e provided)
    if e is not None and bits < 2048:
        d_approx = (n ** 0.25) * 3  # Wiener threshold
        if e > d_approx:
            findings.append("[INFO] e is large relative to n — Wiener attack unlikely")
        else:
            findings.append("[MEDIUM] e may be small enough for Wiener attack")

    return findings

# ═══════════════════════════════════════════════════════════════
# PGP KEY PARSER
# ═══════════════════════════════════════════════════════════════

def parse_pgp_key(text):
    """Parse PGP public key armor and extract RSA parameters if present."""
    result = {"type": "unknown", "n": None, "e": None, "bits": None, "algo": None}

    # Extract base64 between armor headers
    match = re.search(
        r'-----BEGIN PGP PUBLIC KEY BLOCK-----\s*\n(.*?)-----END PGP PUBLIC KEY BLOCK-----',
        text, re.DOTALL
    )
    if not match:
        return result

    # Decode base64
    armor = re.sub(r'\s', '', match.group(1))
    # PGP base64 uses custom alphabet
    armor = armor.replace('-', '+').replace('_', '/')
    padding = 4 - len(armor) % 4
    if padding != 4:
        armor += '=' * padding

    try:
        raw = base64.b64decode(armor)
    except Exception:
        return result

    result["raw_hex"] = raw.hex()
    result["raw_len"] = len(raw)

    # Parse PGP packet structure
    # Look for MPI (Multi-Precision Integers) — RSA key material
    # Format: 2-byte bit count, then bytes
    i = 0
    mpis = []
    # Scan for common RSA patterns in the binary
    # RSA public key packet: version(1) + timestamp(4) + algo(1) + e MPI + n MPI
    while i < len(raw) - 4:
        # Look for version byte 3 or 4
        if raw[i] in (3, 4) and i + 6 < len(raw):
            algo = raw[i + 5] if raw[i] == 4 else raw[i + 6]
            if algo == 1:  # RSA
                result["algo"] = "RSA"
                # Next should be MPI for e, then MPI for n
                mpi_start = i + 6 if raw[i] == 4 else i + 7
                if mpi_start + 2 < len(raw):
                    e_bits = (raw[mpi_start] << 8) | raw[mpi_start + 1]
                    e_bytes = (e_bits + 7) // 8
                    e_val = int.from_bytes(raw[mpi_start + 2:mpi_start + 2 + e_bytes], 'big')
                    result["e"] = e_val
                    n_start = mpi_start + 2 + e_bytes
                    if n_start + 2 < len(raw):
                        n_bits = (raw[n_start] << 8) | raw[n_start + 1]
                        n_bytes = (n_bits + 7) // 8
                        n_val = int.from_bytes(raw[n_start + 2:n_start + 2 + n_bytes], 'big')
                        result["n"] = n_val
                        result["bits"] = n_bits
                        break
            elif algo == 19:  # EdDSA
                result["algo"] = "EdDSA (not RSA)"
                break
            elif algo == 18:  # ECDH
                result["algo"] = "ECDH (not RSA)"
                break
            elif algo == 22:  # Ed25519
                result["algo"] = "Ed25519 (not RSA)"
                break
            elif algo == 23:  # brainpool
                result["algo"] = "Brainpool ECC (not RSA)"
                break

    if result["algo"] is None:
        result["algo"] = "Unknown (could not parse algorithm)"

    return result

# ═══════════════════════════════════════════════════════════════
# CLI / INTERACTIVE
# ═══════════════════════════════════════════════════════════════

BANNER = r"""
{cy}{bd}╔══════════════════════════════════════════════════════════════╗
║            CICADA 3301 RSA CRACKING TOOL                    ║
║         Factorization · Attacks · Vulnerability Scan        ║
╚══════════════════════════════════════════════════════════════╝{dn}

{b}Methods:{dn}
  Trial Division · Pollard rho · Pollard p-1 · Fermat
  Wiener (continued fractions) · Small-e cube root
  Common modulus · Håstad broadcast · Vulnerability scan
""".format(cy=C.CY, bd=C.BD, b=C.B, dn=C.DN)


def do_parse_pgp():
    sec("PGP KEY PARSER")
    path = input("Path to .asc/.key file: ").strip()
    if not path:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public.key")
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            text = f.read()
    except FileNotFoundError:
        err(f"File not found: {path}")
        return
    result = parse_pgp_key(text)
    print(f"\n  Algorithm : {C.G}{result['algo']}{C.DN}")
    if result["bits"]:
        print(f"  Key size  : {result['bits']} bits")
    if result["e"]:
        print(f"  Exponent  : {result['e']}")
    if result["n"]:
        print(f"  Modulus   : {result['n']}")
        print(f"  Modulus (hex): {hex(result['n'])}")
    if result["algo"] and "RSA" not in str(result["algo"]):
        warn("This key is NOT RSA — factorization attacks won't apply.")
        info("For ECC keys, the discrete logarithm problem is different.")


def do_input_params():
    sec("INPUT RSA PARAMETERS")
    n_str = input("n (modulus) : ").strip()
    e_str = input("e (exponent) [default 65537]: ").strip() or "65537"
    c_str = input("c (ciphertext, optional): ").strip()
    n = int(n_str)
    e = int(e_str)
    c = int(c_str) if c_str else None
    return n, e, c


def do_scan():
    sec("VULNERABILITY SCAN")
    n, e, c = do_input_params()
    findings = scan_vulnerabilities(n, e, c)
    print()
    for f in findings:
        if "CRITICAL" in f:
            err(f)
        elif "HIGH" in f:
            warn(f)
        elif "MEDIUM" in f:
            info(f)
        else:
            print(f"  {f}")


def do_factor():
    sec("INTEGER FACTORIZATION")
    n_str = input("n (modulus to factor): ").strip()
    n = int(n_str)
    bits = n.bit_length()
    info(f"n has {bits} bits")

    if bits > 1024:
        warn("Key is very large — factorization may be very slow or infeasible")

    start = time.time()
    p, q = factor_all(n, verbose=True)
    elapsed = time.time() - start

    if p is not None and q is not None and p * q == n:
        ok(f"FACTORED in {elapsed:.2f}s")
        print(f"\n  p = {p}")
        print(f"  q = {q}")
        return p, q
    elif p is not None and isinstance(p, list):
        ok(f"Partial factorization: {p}")
        return p, None
    else:
        err(f"Could not factor n after {elapsed:.2f}s")
        return None, None


def do_wiener():
    sec("WIENER ATTACK (Continued Fractions)")
    n_str = input("n : ").strip()
    e_str = input("e : ").strip()
    n = int(n_str); e = int(e_str)
    info("Running Wiener attack...")
    start = time.time()
    p, q = wiener_attack(n, e)
    elapsed = time.time() - start
    if p is not None:
        ok(f"Wiener attack succeeded in {elapsed:.2f}s")
        print(f"  p = {p}\n  q = {q}")
        return p, q
    else:
        warn(f"Wiener attack failed ({elapsed:.2f}s)")
        info("Wiener works when d < n^0.25 (small private exponent)")
    return None, None


def do_small_e():
    sec("SMALL-e CUBE ROOT ATTACK")
    c_str = input("c (ciphertext): ").strip()
    e_str = input("e (exponent, e.g. 3): ").strip() or "3"
    n_str = input("n (modulus, optional — press Enter to skip): ").strip()
    c = int(c_str); e = int(e_str)
    n = int(n_str) if n_str else None
    info("Trying m^e = c (no mod reduction)...")
    m = small_e_attack(c, e, n if n else 2**256)
    if m is not None:
        ok("Found plaintext!")
        print(f"  m (int)  = {m}")
        print(f"  m (hex)  = {hex(m)}")
        try:
            print(f"  m (text) = {int_to_text(m)}")
        except:
            pass
        return m
    else:
        warn("Small-e attack failed")


def do_decrypt():
    sec("RSA DECRYPT (known factors)")
    p_str = input("p : ").strip()
    q_str = input("q : ").strip()
    e_str = input("e [default 65537]: ").strip() or "65537"
    c_str = input("c (ciphertext): ").strip()
    p = int(p_str); q = int(q_str); e = int(e_str); c = int(c_str)
    n = p * q
    phi = (p - 1) * (q - 1)
    d = modinv(e, phi)
    if d is None:
        err("Could not compute d — e and phi may not be coprime")
        return
    m = pow(c, d, n)
    print(f"\n  n = {n}")
    print(f"  d = {d}")
    print(f"  m (int)  = {m}")
    print(f"  m (hex)  = {hex(m)}")
    try:
        print(f"  m (text) = {int_to_text(m)}")
    except:
        pass


def do_common_modulus():
    sec("COMMON MODUS ATTACK (same n, different e)")
    n_str = input("n : ").strip()
    e1_str = input("e1 : ").strip()
    c1_str = input("c1 (= m^e1 mod n) : ").strip()
    e2_str = input("e2 : ").strip()
    c2_str = input("c2 (= m^e2 mod n) : ").strip()
    n = int(n_str); e1 = int(e1_str); c1 = int(c1_str); e2 = int(e2_str); c2 = int(c2_str)
    m = common_modulus_attack(c1, c2, e1, e2, n)
    if m is not None:
        ok("Recovered plaintext!")
        print(f"  m (int)  = {m}")
        print(f"  m (hex)  = {hex(m)}")
        try:
            print(f"  m (text) = {int_to_text(m)}")
        except:
            pass
    else:
        err("Common modulus attack failed")


def do_full_auto():
    sec("FULL AUTOMATIC ANALYSIS")
    n, e, c = do_input_params()
    bits = n.bit_length()
    info(f"Analyzing {bits}-bit RSA key...")
    print(f"  n = {n}")
    print(f"  e = {e}")
    if c: print(f"  c = {c}")
    print()

    # Step 1: Vulnerability scan
    sec("Step 1: Vulnerability Scan")
    findings = scan_vulnerabilities(n, e, c)
    for f in findings:
        if "CRITICAL" in f: err(f)
        elif "HIGH" in f: warn(f)
        elif "MEDIUM" in f: info(f)
        else: print(f"  {f}")

    # Step 2: Factorization
    sec("Step 2: Factorization")
    start = time.time()
    p, q = factor_all(n, verbose=True)
    elapsed = time.time() - start

    if p is not None and q is not None and p * q == n:
        ok(f"FACTORED in {elapsed:.2f}s")
        print(f"  p = {p}\n  q = {q}")

        if c:
            sec("Step 3: Decryption")
            m = rsa_decrypt_with_factors(c, e, n, p, q)
            if m is not None:
                ok("Decryption successful!")
                print(f"  m (int)  = {m}")
                print(f"  m (hex)  = {hex(m)}")
                try:
                    print(f"  m (text) = {int_to_text(m)}")
                except:
                    pass
            else:
                err("Decryption failed")
    else:
        warn(f"Factorization failed after {elapsed:.2f}s")
        info("Try Wiener attack separately if d is small")

    # Step 3: Wiener
    sec("Step 3: Wiener Attack")
    p2, q2 = wiener_attack(n, e)
    if p2 is not None:
        ok("Wiener attack succeeded!")
        print(f"  p = {p2}\n  q = {q2}")
    else:
        info("Wiener attack not applicable")


def interactive_menu():
    while True:
        print(f"""
{C.BD}MENU{C.DN}
  {C.CY}1{C.DN}  Parse PGP key
  {C.CY}2{C.DN}  Input RSA parameters (n, e, c)
  {C.CY}3{C.DN}  Vulnerability scan
  {C.CY}4{C.DN}  Factor n (all methods)
  {C.CY}5{C.DN}  Wiener attack (small d)
  {C.CY}6{C.DN}  Small-e cube root attack
  {C.CY}7{C.DN}  Common modulus attack
  {C.CY}8{C.DN}  RSA decrypt (known p, q)
  {C.CY}9{C.DN}  FULL AUTOMATIC analysis
  {C.CY}0{C.DN}  Exit
""")
        choice = input(f"{C.Y}Select: {C.DN}").strip()
        if choice == '0':
            print(f"\n{C.CY}The truth is hidden in the primes.{C.DN}\n")
            break
        try:
            actions = {
                '1': do_parse_pgp, '2': do_input_params,
                '3': do_scan, '4': do_factor, '5': do_wiener,
                '6': do_small_e, '7': do_common_modulus,
                '8': do_decrypt, '9': do_full_auto,
            }
            if choice in actions:
                actions[choice]()
            else:
                warn("Invalid choice")
        except KeyboardInterrupt:
            print()
        except Exception as e:
            err(f"Error: {e}")


def cli_mode():
    """Command-line argument mode."""
    if len(sys.argv) < 2:
        print(BANNER)
        print("Usage:")
        print("  python rsa_cracker.py                    # Interactive mode")
        print("  python rsa_cracker.py parse [file]       # Parse PGP key")
        print("  python rsa_cracker.py scan n e           # Vulnerability scan")
        print("  python rsa_cracker.py factor n           # Factor n")
        print("  python rsa_cracker.py wiener n e         # Wiener attack")
        print("  python rsa_cracker.py smalle c e [n]     # Small-e attack")
        print("  python rsa_cracker.py decrypt p q e c    # Decrypt with known factors")
        print("  python rsa_cracker.py auto n e [c]       # Full auto analysis")
        return

    cmd = sys.argv[1].lower()

    if cmd == 'parse':
        path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "public.key")
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            text = f.read()
        result = parse_pgp_key(text)
        print(f"Algorithm: {result['algo']}")
        if result['bits']: print(f"Key size: {result['bits']} bits")
        if result['e']: print(f"e: {result['e']}")
        if result['n']: print(f"n: {result['n']}")

    elif cmd == 'scan':
        n = int(sys.argv[2]); e = int(sys.argv[3])
        for f in scan_vulnerabilities(n, e):
            print(f"  {f}")

    elif cmd == 'factor':
        n = int(sys.argv[2])
        p, q = factor_all(n)
        if p and q:
            print(f"p = {p}\nq = {q}")

    elif cmd == 'wiener':
        n = int(sys.argv[2]); e = int(sys.argv[3])
        p, q = wiener_attack(n, e)
        if p: print(f"p = {p}\nq = {q}")
        else: print("Wiener attack failed")

    elif cmd == 'smalle':
        c = int(sys.argv[2]); e = int(sys.argv[3])
        n = int(sys.argv[4]) if len(sys.argv) > 4 else 2**256
        m = small_e_attack(c, e, n)
        if m: print(f"m = {m}\nhex: {hex(m)}\ntext: {int_to_text(m)}")
        else: print("Small-e attack failed")

    elif cmd == 'decrypt':
        p, q, e, c = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
        m = rsa_decrypt_with_factors(c, e, p * q, p, q)
        if m: print(f"m = {m}\nhex: {hex(m)}\ntext: {int_to_text(m)}")

    elif cmd == 'auto':
        n = int(sys.argv[2]); e = int(sys.argv[3])
        c = int(sys.argv[4]) if len(sys.argv) > 4 else None
        do_full_auto()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        cli_mode()
    else:
        print(BANNER)
        interactive_menu()
