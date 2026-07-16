#!/usr/bin/env python3
"""
Cicada 3301 Liber Primus Decryptor - Ultimate Edition
Decrypts the Liber Primus using 25+ cipher methods.
"""

import sys
import string
import base64
import binascii
from collections import Counter
from itertools import cycle
import math

# Optional: numpy for Hill cipher (fallback if not available)
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# ============================================================
# GEMATRIA PRIMUS - Complete Rune System
# ============================================================

RUNE_MAP = {
    'ᚠ': ('F', 0, 2), 'ᚢ': ('U', 1, 3), 'ᚦ': ('TH', 2, 5),
    'ᚩ': ('O', 3, 7), 'ᚱ': ('R', 4, 11), 'ᚳ': ('C', 5, 13),
    'ᚷ': ('G', 6, 17), 'ᚹ': ('W', 7, 19), 'ᚻ': ('H', 8, 23),
    'ᚾ': ('N', 9, 29), 'ᛁ': ('I', 10, 31), 'ᛄ': ('J', 11, 37),
    'ᛇ': ('EO', 12, 41), 'ᛈ': ('P', 13, 43), 'ᛉ': ('X', 14, 47),
    'ᛋ': ('S', 15, 53), 'ᛏ': ('T', 16, 59), 'ᛒ': ('B', 17, 61),
    'ᛖ': ('E', 18, 67), 'ᛗ': ('M', 19, 71), 'ᛚ': ('L', 20, 73),
    'ᛝ': ('NG', 21, 79), 'ᛟ': ('OE', 22, 83), 'ᛞ': ('D', 23, 89),
    'ᚪ': ('A', 24, 97), 'ᚫ': ('AE', 25, 101), 'ᚣ': ('Y', 26, 103),
    'ᛡ': ('IO', 27, 107), 'ᛠ': ('EA', 28, 109)
}

LETTER_MAP = {}
RUNE_TO_DECIMAL = {}
RUNE_TO_PRIME = {}
for rune, (letter, decimal, prime) in RUNE_MAP.items():
    LETTER_MAP[letter] = rune
    RUNE_TO_DECIMAL[rune] = decimal
    RUNE_TO_PRIME[rune] = prime
    if len(letter) > 1:
        LETTER_MAP[letter[0]] = rune

DELIMITERS = {
    '-': ' ', '.': '.', '&': '\n', '$': ' ',
    '§': ' ', '/': '\n', '%': '\n',
}

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def runes_to_text(runes):
    """Convert runes to alphabetic text."""
    result = []
    i = 0
    while i < len(runes):
        rune = runes[i]
        if rune in RUNE_MAP:
            result.append(RUNE_MAP[rune][0])
        elif rune in DELIMITERS:
            result.append(DELIMITERS[rune])
        else:
            result.append(rune)
        i += 1
    return ''.join(result)

def runes_to_decimal(runes):
    """Convert runes to decimal values."""
    result = []
    for rune in runes:
        if rune in RUNE_TO_DECIMAL:
            result.append(RUNE_TO_DECIMAL[rune])
    return result

def runes_to_prime(runes):
    """Convert runes to prime values."""
    result = []
    for rune in runes:
        if rune in RUNE_TO_PRIME:
            result.append(RUNE_TO_PRIME[rune])
    return result

def chi_squared_analysis(text, expected_freq=None):
    """Calculate chi-squared statistic."""
    if expected_freq is None:
        expected_freq = {
            'A': 8.167, 'B': 1.492, 'C': 2.782, 'D': 4.253, 'E': 12.702,
            'F': 2.228, 'G': 2.015, 'H': 6.094, 'I': 6.966, 'J': 0.153,
            'K': 0.772, 'L': 4.025, 'M': 2.406, 'N': 6.749, 'O': 7.507,
            'P': 1.929, 'Q': 0.095, 'R': 5.987, 'S': 6.327, 'T': 9.056,
            'U': 2.758, 'V': 0.978, 'W': 2.361, 'X': 0.150, 'Y': 1.974,
            'Z': 0.074
        }
    text = text.upper()
    counter = Counter(c for c in text if c.isalpha())
    total = sum(counter.values())
    if total == 0:
        return float('inf')
    chi_sq = 0
    for letter in string.ascii_uppercase:
        observed = counter.get(letter, 0)
        expected = expected_freq.get(letter, 0) / 100 * total
        if expected > 0:
            chi_sq += (observed - expected) ** 2 / expected
    return chi_sq

def index_of_coincidence(text):
    """Calculate Index of Coincidence."""
    text = text.upper()
    counter = Counter(c for c in text if c.isalpha())
    n = sum(counter.values())
    if n <= 1:
        return 0
    ic = sum(count * (count - 1) for count in counter.values())
    return ic / (n * (n - 1))

def frequency_analysis(text):
    """Print frequency analysis."""
    text = text.upper()
    counter = Counter(c for c in text if c.isalpha())
    total = sum(counter.values())
    print(f"\n{'Letter':<10} {'Count':<10} {'Frequency':<10}")
    print("-" * 30)
    for letter, count in counter.most_common():
        freq = count / total * 100 if total > 0 else 0
        print(f"{letter:<10} {count:<10} {freq:.2f}%")

# ============================================================
# METHOD 1: CAESAR CIPHER
# ============================================================

def caesar_decrypt(text, shift):
    result = []
    for char in text:
        if char.isalpha():
            shifted = (ord(char) - ord('A') - shift) % 26
            result.append(chr(shifted + ord('A')))
        else:
            result.append(char)
    return ''.join(result)

def find_best_caesar(text):
    results = []
    for shift in range(26):
        decrypted = caesar_decrypt(text, shift)
        chi_sq = chi_squared_analysis(decrypted)
        results.append((shift, chi_sq, decrypted))
    results.sort(key=lambda x: x[1])
    return results

# ============================================================
# METHOD 2: VIGENERE CIPHER
# ============================================================

def vigenere_decrypt(ciphertext, key):
    result = []
    key = key.upper()
    key_idx = 0
    for char in ciphertext:
        if char.isalpha():
            shift = ord(key[key_idx % len(key)]) - ord('A')
            decrypted = (ord(char) - ord('A') - shift) % 26
            result.append(chr(decrypted + ord('A')))
            key_idx += 1
        else:
            result.append(char)
    return ''.join(result)

def find_best_vigenere(text):
    known_keys = [
        'PSYOP', 'ENLIGHTENMENT', 'CICADA', 'WELCOME', 'LUPUS',
        'TOTEN', 'QUID', 'OBSIDIAN', 'PUER', 'NOVUS', 'ORDO',
        'TEMPUS', 'FUGIT', 'SOLVED', 'PRIMUS', 'GEMATRIA',
        'LIGHT', 'SHADOW', 'SECRET', 'PUZZLE', 'CIPHER',
        'DECODE', 'RUNE', 'FUTHARK', 'ELDER', 'FUTHORC',
        'ILLUMINATI', 'CONSUMPTION', 'PRESERVATION',
        'ADHERENCE', 'DIVINITY', 'AGATHODAIMON', 'VEIOUS',
        'WISDOM', 'PRIMES', 'SACRED', 'TOTIENT', 'FUNCTION',
        'ENCRYPTED', 'KNOW', 'SHADOWS', 'VOID', 'CARDINAL',
        'OBSUCURA', 'FORM', 'MOBIUS', 'ANALOG', 'MOURNFUL'
    ]
    results = []
    for key in known_keys:
        decrypted = vigenere_decrypt(text, key)
        chi_sq = chi_squared_analysis(decrypted)
        results.append((key, chi_sq, decrypted))
    results.sort(key=lambda x: x[1])
    return results[:10]

# ============================================================
# METHOD 3: ATBASH CIPHER
# ============================================================

def atbash_decrypt(text):
    result = []
    for char in text:
        if char.isalpha():
            if char.isupper():
                result.append(chr(ord('Z') - (ord(char) - ord('A'))))
            else:
                result.append(chr(ord('z') - (ord(char) - ord('a'))))
        else:
            result.append(char)
    return ''.join(result)

# ============================================================
# METHOD 4: ROT13
# ============================================================

def rot13_decrypt(text):
    return caesar_decrypt(text, 13)

# ============================================================
# METHOD 5: XOR CIPHER
# ============================================================

def xor_decrypt(data, key):
    if isinstance(data, str):
        data = data.encode()
    if isinstance(key, str):
        key = key.encode()
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

def find_best_xor(text):
    results = []
    text_bytes = text.encode() if isinstance(text, str) else text
    for byte_val in range(256):
        decrypted = bytes([b ^ byte_val for b in text_bytes])
        try:
            decrypted_text = decrypted.decode('ascii', errors='ignore')
            if all(c.isprintable() or c in '\n\r\t' for c in decrypted_text):
                chi_sq = chi_squared_analysis(decrypted_text)
                if chi_sq < 10000:
                    results.append((f"0x{byte_val:02x}", chi_sq, decrypted_text))
        except:
            pass
    results.sort(key=lambda x: x[1])
    return results[:5]

# ============================================================
# METHOD 6: COLUMNAR TRANSPOSITION
# ============================================================

def columnar_transposition_decrypt(text, key_length):
    if key_length <= 0:
        return text
    alpha_text = ''.join(c for c in text if c.isalpha())
    n_rows = math.ceil(len(alpha_text) / key_length)
    n_full_cols = len(alpha_text) % key_length
    if n_full_cols == 0:
        n_full_cols = key_length
        n_rows -= 1
    col_lengths = [n_rows + 1 if i < n_full_cols else n_rows for i in range(key_length)]
    columns = []
    idx = 0
    for length in col_lengths:
        columns.append(alpha_text[idx:idx+length])
        idx += length
    result = []
    for row in range(n_rows + 1):
        for col in range(key_length):
            if row < len(columns[col]):
                result.append(columns[col][row])
    return ''.join(result)

def find_best_transposition(text):
    results = []
    for key_len in range(2, 15):
        decrypted = columnar_transposition_decrypt(text, key_len)
        chi_sq = chi_squared_analysis(decrypted)
        results.append((key_len, chi_sq, decrypted))
    results.sort(key=lambda x: x[1])
    return results[:5]

# ============================================================
# METHOD 7: RAIL FENCE CIPHER
# ============================================================

def rail_fence_decrypt(text, rails):
    if rails <= 1:
        return text
    alpha_text = ''.join(c for c in text if c.isalpha())
    n = len(alpha_text)
    fence = [['' for _ in range(n)] for _ in range(rails)]
    rail, direction = 0, 1
    for i in range(n):
        fence[rail][i] = alpha_text[i]
        rail += direction
        if rail == rails - 1 or rail == 0:
            direction = -direction
    result = []
    rail, direction = 0, 1
    idx = 0
    for i in range(n):
        if fence[rail][i] != '':
            result.append(alpha_text[idx])
            idx += 1
        rail += direction
        if rail == rails - 1 or rail == 0:
            direction = -direction
    return ''.join(result)

def find_best_rail_fence(text):
    results = []
    for rails in range(2, 10):
        decrypted = rail_fence_decrypt(text, rails)
        chi_sq = chi_squared_analysis(decrypted)
        results.append((rails, chi_sq, decrypted))
    results.sort(key=lambda x: x[1])
    return results[:5]

# ============================================================
# METHOD 8: AFFINE CIPHER
# ============================================================

def affine_decrypt(text, a, b):
    def mod_inverse(a, m):
        a = a % m
        for x in range(1, m):
            if (a * x) % m == 1:
                return x
        return None
    mod_inv = mod_inverse(a, 26)
    if mod_inv is None:
        return text
    result = []
    for char in text:
        if char.isalpha():
            y = ord(char.upper()) - ord('A')
            x = (mod_inv * (y - b)) % 26
            result.append(chr(x + ord('A')))
        else:
            result.append(char)
    return ''.join(result)

def find_best_affine(text):
    results = []
    valid_a = [1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25]
    for a in valid_a:
        for b in range(26):
            decrypted = affine_decrypt(text, a, b)
            chi_sq = chi_squared_analysis(decrypted)
            if chi_sq < 5000:
                results.append((f"a={a},b={b}", chi_sq, decrypted))
    results.sort(key=lambda x: x[1])
    return results[:5]

# ============================================================
# METHOD 9: BEAUFORT CIPHER
# ============================================================

def beaufort_decrypt(ciphertext, key):
    result = []
    key = key.upper()
    key_idx = 0
    for char in ciphertext:
        if char.isalpha():
            key_char = ord(key[key_idx % len(key)]) - ord('A')
            cipher_char = ord(char.upper()) - ord('A')
            plain_char = (key_char - cipher_char) % 26
            result.append(chr(plain_char + ord('A')))
            key_idx += 1
        else:
            result.append(char)
    return ''.join(result)

# ============================================================
# METHOD 10: POLYBIUS SQUARE
# ============================================================

def polybius_decrypt(text, square=None):
    if square is None:
        square = "ABCDEFGHIKLMNOPQRSTUVWXYZ"  # 5x5 (I/J combined)
    result = []
    i = 0
    while i < len(text):
        if i + 1 < len(text) and text[i].isdigit() and text[i+1].isdigit():
            row = int(text[i]) - 1
            col = int(text[i+1]) - 1
            if 0 <= row < 5 and 0 <= col < 5:
                idx = row * 5 + col
                if idx < len(square):
                    result.append(square[idx])
            i += 2
        else:
            result.append(text[i])
            i += 1
    return ''.join(result)

# ============================================================
# METHOD 11: A1Z26 (Number → Letter)
# ============================================================

def a1z26_decrypt(text):
    """Convert numbers to letters (1=A, 2=B, etc.)."""
    result = []
    tokens = text.replace('-', ' ').replace('.', ' ').split()
    for token in tokens:
        if token.isdigit():
            num = int(token)
            if 1 <= num <= 26:
                result.append(chr(num + ord('A') - 1))
            else:
                result.append(token)
        else:
            result.append(token)
    return ' '.join(result)

# ============================================================
# METHOD 12: MORSE CODE
# ============================================================

MORSE_TO_CHAR = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
    '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
    '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
    '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
    '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
    '--..': 'Z', '-----': '0', '.----': '1', '..---': '2',
    '...--': '3', '....-': '4', '.....': '5', '-....': '6',
    '--...': '7', '---..': '8', '----.': '9'
}

CHAR_TO_MORSE = {v: k for k, v in MORSE_TO_CHAR.items()}

def morse_decrypt(text):
    words = text.split(' / ')
    result = []
    for word in words:
        letters = word.split(' ')
        for letter in letters:
            if letter in MORSE_TO_CHAR:
                result.append(MORSE_TO_CHAR[letter])
        result.append(' ')
    return ''.join(result).strip()

# ============================================================
# METHOD 13: BACONIAN CIPHER
# ============================================================

def baconian_decrypt(text):
    """Decrypt Baconian cipher (5-bit binary using A/B)."""
    text = text.upper().replace(' ', '')
    result = []
    for i in range(0, len(text) - 4, 5):
        chunk = text[i:i+5]
        if all(c in 'AB' for c in chunk):
            value = sum((1 if c == 'B' else 0) << (4 - j) for j, c in enumerate(chunk))
            if value < 26:
                result.append(chr(value + ord('A')))
    return ''.join(result)

# ============================================================
# METHOD 14: HILL CIPHER (2x2)
# ============================================================

def mod_inverse(a, m):
    """Calculate modular multiplicative inverse."""
    a = a % m
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return None

def hill_decrypt(text, key_matrix):
    """Decrypt Hill cipher with 2x2 matrix."""
    if not HAS_NUMPY:
        # Manual implementation without numpy
        a, b = key_matrix[0][0], key_matrix[0][1]
        c, d = key_matrix[1][0], key_matrix[1][1]
        
        det = (a * d - b * c) % 26
        det_inv = mod_inverse(det, 26)
        if det_inv is None:
            return text
        
        # Inverse matrix
        inv_a = (d * det_inv) % 26
        inv_b = (-b * det_inv) % 26
        inv_c = (-c * det_inv) % 26
        inv_d = (a * det_inv) % 26
        
        text = ''.join(c for c in text.upper() if c.isalpha())
        if len(text) % 2 != 0:
            text += 'X'
        
        result = []
        for i in range(0, len(text), 2):
            x = ord(text[i]) - ord('A')
            y = ord(text[i+1]) - ord('A')
            dec1 = (inv_a * x + inv_b * y) % 26
            dec2 = (inv_c * x + inv_d * y) % 26
            result.append(chr(dec1 + ord('A')))
            result.append(chr(dec2 + ord('A')))
        return ''.join(result)
    
    # Numpy implementation
    text = ''.join(c for c in text.upper() if c.isalpha())
    if len(text) % 2 != 0:
        text += 'X'
    
    key_matrix = np.array(key_matrix)
    det = int(np.round(np.linalg.det(key_matrix))) % 26
    det_inv = pow(det, -1, 26)
    inv_matrix = np.round(np.linalg.inv(key_matrix) * det * det_inv).astype(int) % 26
    
    result = []
    for i in range(0, len(text), 2):
        vec = np.array([[ord(text[i]) - ord('A')], [ord(text[i+1]) - ord('A')]])
        decrypted = inv_matrix @ vec % 26
        result.append(chr(int(decrypted[0][0]) + ord('A')))
        result.append(chr(int(decrypted[1][0]) + ord('A')))
    return ''.join(result)

def find_best_hill(text):
    """Try common Hill cipher keys."""
    common_keys = [
        [[3, 3], [2, 5]],
        [[6, 25], [1, 15]],
        [[5, 8], [17, 3]],
        [[2, 5], [1, 3]],
        [[3, 7], [2, 5]],
    ]
    results = []
    for key in common_keys:
        try:
            decrypted = hill_decrypt(text, key)
            chi_sq = chi_squared_analysis(decrypted)
            results.append((str(key), chi_sq, decrypted))
        except:
            pass
    results.sort(key=lambda x: x[1])
    return results[:5]

# ============================================================
# METHOD 15: PLAYFAIR CIPHER
# ============================================================

def generate_playfair_matrix(key):
    key = key.upper().replace('J', 'I')
    matrix = []
    used = set()
    for char in key:
        if char.isalpha() and char not in used:
            matrix.append(char)
            used.add(char)
    for char in 'ABCDEFGHIKLMNOPQRSTUVWXYZ':
        if char not in used:
            matrix.append(char)
            used.add(char)
    return [matrix[i:i+5] for i in range(0, 25, 5)]

def playfair_decrypt(ciphertext, key):
    matrix = generate_playfair_matrix(key)
    pos = {}
    for r in range(5):
        for c in range(5):
            pos[matrix[r][c]] = (r, c)
    
    ciphertext = ciphertext.upper().replace('J', 'I').replace(' ', '')
    if len(ciphertext) % 2 != 0:
        ciphertext += 'X'
    
    result = []
    for i in range(0, len(ciphertext), 2):
        a, b = ciphertext[i], ciphertext[i+1]
        if a not in pos or b not in pos:
            result.extend([a, b])
            continue
        r1, c1 = pos[a]
        r2, c2 = pos[b]
        
        if r1 == r2:  # Same row
            result.append(matrix[r1][(c1 - 1) % 5])
            result.append(matrix[r2][(c2 - 1) % 5])
        elif c1 == c2:  # Same column
            result.append(matrix[(r1 - 1) % 5][c1])
            result.append(matrix[(r2 - 1) % 5][c2])
        else:  # Rectangle
            result.append(matrix[r1][c2])
            result.append(matrix[r2][c1])
    
    return ''.join(result)

def find_best_playfair(text):
    known_keys = ['CICADA', 'PSYOP', 'LUPUS', 'TOTEN', 'SECRET', 'RUNE']
    results = []
    for key in known_keys:
        decrypted = playfair_decrypt(text, key)
        chi_sq = chi_squared_analysis(decrypted)
        results.append((key, chi_sq, decrypted))
    results.sort(key=lambda x: x[1])
    return results[:5]

# ============================================================
# METHOD 16: FOUR-SQUARE CIPHER
# ============================================================

def generate_four_square_matrices(key1, key2):
    def gen_matrix(key):
        key = key.upper().replace('J', 'I')
        matrix = []
        used = set()
        for char in key:
            if char.isalpha() and char not in used:
                matrix.append(char)
                used.add(char)
        for char in 'ABCDEFGHIKLMNOPQRSTUVWXYZ':
            if char not in used:
                matrix.append(char)
                used.add(char)
        return [matrix[i:i+5] for i in range(0, 25, 5)]
    
    plain1 = gen_matrix("")
    cipher1 = gen_matrix(key1)
    plain2 = gen_matrix(key2)
    cipher2 = gen_matrix("")
    
    return plain1, cipher1, plain2, cipher2

# ============================================================
# METHOD 17: GEMATRIA ANALYSIS
# ============================================================

def gematria_analysis(runes):
    """Analyze runes using Gematria Primus values."""
    decimal_values = runes_to_decimal(runes)
    prime_values = runes_to_prime(runes)
    
    print("\n=== GEMATRIA PRIMUS ANALYSIS ===")
    print(f"Total runes: {len(decimal_values)}")
    print(f"Decimal sum: {sum(decimal_values)}")
    print(f"Prime sum: {sum(prime_values)}")
    print(f"Decimal average: {sum(decimal_values)/len(decimal_values):.2f}" if decimal_values else "")
    print(f"Prime average: {sum(prime_values)/len(prime_values):.2f}" if prime_values else "")
    
    # Find patterns
    print("\nDecimal value frequency:")
    decimal_counter = Counter(decimal_values)
    for val, count in decimal_counter.most_common(10):
        print(f"  {val}: {count} times")
    
    print("\nPrime value frequency:")
    prime_counter = Counter(prime_values)
    for val, count in prime_counter.most_common(10):
        print(f"  {val}: {count} times")
    
    return decimal_values, prime_values

# ============================================================
# METHOD 18: PRIME NUMBER ANALYSIS
# ============================================================

def prime_analysis(prime_values):
    """Analyze prime values for patterns."""
    print("\n=== PRIME NUMBER ANALYSIS ===")
    
    if not prime_values:
        print("No prime values to analyze")
        return
    
    # Check if values are prime
    def is_prime(n):
        if n < 2:
            return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return False
        return True
    
    primes = [v for v in prime_values if is_prime(v)]
    non_primes = [v for v in prime_values if not is_prime(v)]
    
    print(f"Prime values: {len(primes)} ({len(primes)/len(prime_values)*100:.1f}%)")
    print(f"Non-prime values: {len(non_primes)} ({len(non_primes)/len(prime_values)*100:.1f}%)")
    
    # Check for Fibonacci primes
    fib_primes = [2, 3, 5, 13, 89]
    found_fib = [v for v in prime_values if v in fib_primes]
    print(f"Fibonacci primes found: {found_fib}")

# ============================================================
# METHOD 19: BINARY PATTERNS
# ============================================================

def binary_analysis(text):
    """Convert text to binary and look for patterns."""
    print("\n=== BINARY PATTERN ANALYSIS ===")
    binary = ' '.join(format(ord(c), '08b') for c in text if c.isalpha())
    print(f"Binary representation (first 200 bits):")
    print(binary[:200])
    
    # Count 1s and 0s
    ones = binary.count('1')
    zeros = binary.count('0')
    print(f"\n1s: {ones}, 0s: {zeros}")
    print(f"Ratio: {ones/(ones+zeros):.3f}" if ones+zeros > 0 else "")

# ============================================================
# METHOD 20: SUBSTITUTION CIPHER (manual)
# ============================================================

def substitution_decrypt(text, mapping):
    result = []
    for char in text.upper():
        result.append(mapping.get(char, char))
    return ''.join(result)

# ============================================================
# METHOD 21: ROT47
# ============================================================

def rot47_decrypt(text):
    result = []
    for char in text:
        if 33 <= ord(char) <= 126:
            result.append(chr(33 + (ord(char) - 33 + 47) % 94))
        else:
            result.append(char)
    return ''.join(result)

# ============================================================
# METHOD 22: XOR MULTI-BYTE
# ============================================================

def find_best_xor_multibyte(text, max_key_len=8):
    """Try multi-byte XOR keys."""
    results = []
    text_bytes = text.encode() if isinstance(text, str) else text
    
    for key_len in range(2, max_key_len + 1):
        # Try common keys
        common_keys = [
            bytes([i] * key_len) for i in range(256)
        ][:10]  # Limit for performance
        
        for key in common_keys:
            decrypted = xor_decrypt(text_bytes, key)
            try:
                decrypted_text = decrypted.decode('ascii', errors='ignore')
                if all(c.isprintable() or c in '\n\r\t' for c in decrypted_text):
                    chi_sq = chi_squared_analysis(decrypted_text)
                    if chi_sq < 5000:
                        results.append((key.hex(), chi_sq, decrypted_text))
            except:
                pass
    
    results.sort(key=lambda x: x[1])
    return results[:5]

# ============================================================
# METHOD 23: AUTOKEY CIPHER
# ============================================================

def autokey_decrypt(ciphertext, key):
    result = []
    key = key.upper()
    full_key = list(key)
    
    for i, char in enumerate(ciphertext):
        if char.isalpha():
            if i < len(full_key):
                shift = ord(full_key[i]) - ord('A')
            else:
                shift = ord(result[i - len(key)].upper()) - ord('A') if i >= len(key) else 0
            
            decrypted = (ord(char.upper()) - ord('A') - shift) % 26
            result.append(chr(decrypted + ord('A')))
        else:
            result.append(char)
    
    return ''.join(result)

# ============================================================
# METHOD 24: RUNNING KEY CIPHER
# ============================================================

def running_key_decrypt(ciphertext, key):
    """Decrypt running key cipher."""
    result = []
    key_idx = 0
    for char in ciphertext:
        if char.isalpha():
            if key_idx < len(key):
                shift = ord(key[key_idx].upper()) - ord('A')
            else:
                shift = 0
            decrypted = (ord(char.upper()) - ord('A') - shift) % 26
            result.append(chr(decrypted + ord('A')))
            key_idx += 1
        else:
            result.append(char)
    return ''.join(result)

# ============================================================
# METHOD 25: GRONSFELD CIPHER
# ============================================================

def gronsfeld_decrypt(ciphertext, key):
    """Decrypt Gronsfeld cipher (Vigenère with numeric key)."""
    result = []
    key = [int(d) for d in str(key)]
    key_idx = 0
    for char in ciphertext:
        if char.isalpha():
            shift = key[key_idx % len(key)]
            decrypted = (ord(char.upper()) - ord('A') - shift) % 26
            result.append(chr(decrypted + ord('A')))
            key_idx += 1
        else:
            result.append(char)
    return ''.join(result)

# ============================================================
# MAIN DECRYPTION FUNCTION
# ============================================================

def try_all_methods(rune_text):
    """Try all decryption methods on the rune text."""
    print("\n" + "=" * 70)
    print("    CICADA 3301 LIBER PRIMUS DECRYPTOR - ULTIMATE EDITION")
    print("           25+ Cipher Methods | Gematria Analysis")
    print("=" * 70)
    
    # Step 1: Convert runes to letters
    print("\n[1] CONVERTING RUNES TO LETTERS...")
    alpha_text = runes_to_text(rune_text)
    print(f"\nAlphabetic text (first 500 chars):\n{alpha_text[:500]}...")
    
    # Step 2: Gematria Analysis
    print("\n" + "-" * 70)
    print("[2] GEMATRIA PRIMUS ANALYSIS")
    print("-" * 70)
    decimal_values, prime_values = gematria_analysis(rune_text)
    
    # Step 3: Prime Analysis
    print("\n" + "-" * 70)
    print("[3] PRIME NUMBER ANALYSIS")
    print("-" * 70)
    prime_analysis(prime_values)
    
    # Step 4: Caesar cipher
    print("\n" + "-" * 70)
    print("[4] CAESAR CIPHER (26 shifts)")
    print("-" * 70)
    caesar_results = find_best_caesar(alpha_text)
    for shift, chi_sq, decrypted in caesar_results[:3]:
        print(f"  Shift {shift:2d} (χ²={chi_sq:.2f}): {decrypted[:80]}...")
    
    # Step 5: Vigenère cipher
    print("\n" + "-" * 70)
    print("[5] VIGENERE CIPHER (30+ keys)")
    print("-" * 70)
    vigenere_results = find_best_vigenere(alpha_text)
    for key, chi_sq, decrypted in vigenere_results[:3]:
        print(f"  Key '{key}' (χ²={chi_sq:.2f}): {decrypted[:80]}...")
    
    # Step 6: Atbash
    print("\n" + "-" * 70)
    print("[6] ATBASH CIPHER")
    print("-" * 70)
    atbash_result = atbash_decrypt(alpha_text)
    chi_sq = chi_squared_analysis(atbash_result)
    print(f"  χ²={chi_sq:.2f}: {atbash_result[:100]}...")
    
    # Step 7: ROT13
    print("\n" + "-" * 70)
    print("[7] ROT13")
    print("-" * 70)
    rot13_result = rot13_decrypt(alpha_text)
    chi_sq = chi_squared_analysis(rot13_result)
    print(f"  χ²={chi_sq:.2f}: {rot13_result[:100]}...")
    
    # Step 8: XOR
    print("\n" + "-" * 70)
    print("[8] XOR CIPHER")
    print("-" * 70)
    xor_results = find_best_xor(alpha_text[:1000])
    for key, chi_sq, decrypted in xor_results[:3]:
        print(f"  Key {key} (χ²={chi_sq:.2f}): {decrypted[:80]}...")
    
    # Step 9: Transposition
    print("\n" + "-" * 70)
    print("[9] COLUMNAR TRANSPOSITION")
    print("-" * 70)
    trans_results = find_best_transposition(alpha_text)
    for key_len, chi_sq, decrypted in trans_results[:3]:
        print(f"  Key length {key_len} (χ²={chi_sq:.2f}): {decrypted[:80]}...")
    
    # Step 10: Rail Fence
    print("\n" + "-" * 70)
    print("[10] RAIL FENCE CIPHER")
    print("-" * 70)
    rail_results = find_best_rail_fence(alpha_text)
    for rails, chi_sq, decrypted in rail_results[:3]:
        print(f"  Rails {rails} (χ²={chi_sq:.2f}): {decrypted[:80]}...")
    
    # Step 11: Affine
    print("\n" + "-" * 70)
    print("[11] AFFINE CIPHER")
    print("-" * 70)
    affine_results = find_best_affine(alpha_text)
    for params, chi_sq, decrypted in affine_results[:3]:
        print(f"  {params} (χ²={chi_sq:.2f}): {decrypted[:80]}...")
    
    # Step 12: Beaufort
    print("\n" + "-" * 70)
    print("[12] BEAUFORT CIPHER")
    print("-" * 70)
    for key in ['PSYOP', 'CICADA', 'LUPUS']:
        decrypted = beaufort_decrypt(alpha_text, key)
        chi_sq = chi_squared_analysis(decrypted)
        print(f"  Key '{key}' (χ²={chi_sq:.2f}): {decrypted[:80]}...")
    
    # Step 13: Playfair
    print("\n" + "-" * 70)
    print("[13] PLAYFAIR CIPHER")
    print("-" * 70)
    playfair_results = find_best_playfair(alpha_text)
    for key, chi_sq, decrypted in playfair_results[:3]:
        print(f"  Key '{key}' (χ²={chi_sq:.2f}): {decrypted[:80]}...")
    
    # Step 14: Hill Cipher
    print("\n" + "-" * 70)
    print("[14] HILL CIPHER (2x2)")
    print("-" * 70)
    hill_results = find_best_hill(alpha_text[:200])
    for key, chi_sq, decrypted in hill_results[:3]:
        print(f"  Key {key} (χ²={chi_sq:.2f}): {decrypted[:80]}...")
    
    # Step 15: ROT47
    print("\n" + "-" * 70)
    print("[15] ROT47")
    print("-" * 70)
    rot47_result = rot47_decrypt(alpha_text)
    chi_sq = chi_squared_analysis(rot47_result)
    print(f"  χ²={chi_sq:.2f}: {rot47_result[:100]}...")
    
    # Step 16: Autokey
    print("\n" + "-" * 70)
    print("[16] AUTOKEY CIPHER")
    print("-" * 70)
    for key in ['SECRET', 'CIPHER', 'RUNE']:
        decrypted = autokey_decrypt(alpha_text, key)
        chi_sq = chi_squared_analysis(decrypted)
        print(f"  Key '{key}' (χ²={chi_sq:.2f}): {decrypted[:80]}...")
    
    # Step 17: Gronsfeld
    print("\n" + "-" * 70)
    print("[17] GRONSFELD CIPHER")
    print("-" * 70)
    for key in [123, 3301, 33, 17]:
        decrypted = gronsfeld_decrypt(alpha_text, key)
        chi_sq = chi_squared_analysis(decrypted)
        print(f"  Key {key} (χ²={chi_sq:.2f}): {decrypted[:80]}...")
    
    # Step 18: Binary Analysis
    print("\n" + "-" * 70)
    print("[18] BINARY PATTERN ANALYSIS")
    print("-" * 70)
    binary_analysis(alpha_text[:200])
    
    # Step 19: Frequency Analysis
    print("\n" + "-" * 70)
    print("[19] FREQUENCY ANALYSIS")
    print("-" * 70)
    frequency_analysis(alpha_text)
    
    # Step 20: Index of Coincidence
    print("\n" + "-" * 70)
    print("[20] INDEX OF COINCIDENCE")
    print("-" * 70)
    ic = index_of_coincidence(alpha_text)
    print(f"  IC = {ic:.4f} (English ≈ 0.0667)")
    if 0.06 <= ic <= 0.08:
        print("  → Likely plaintext or simple substitution")
    elif 0.03 <= ic <= 0.05:
        print("  → Likely polyalphabetic cipher")
    else:
        print("  → Unusual distribution")
    
    print("\n" + "=" * 70)
    print("                    DECRYPTION COMPLETE")
    print("=" * 70)
    
    return alpha_text


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Cicada 3301 Liber Primus Decryptor - Ultimate Edition',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Methods supported:
  Caesar, Vigenère, Atbash, ROT13, XOR, Transposition, Rail Fence,
  Affine, Beaufort, Polybius, A1Z26, Morse, Baconian, Hill, Playfair,
  Four-Square, Gematria Analysis, Prime Analysis, Binary Patterns,
  ROT47, Autokey, Running Key, Gronsfeld, and more!
        """
    )
    parser.add_argument('file', nargs='?', help='Input file with rune text')
    parser.add_argument('--runes', '-r', help='Direct rune text input')
    parser.add_argument('--caesar', '-c', type=int, help='Caesar shift (0-25)')
    parser.add_argument('--vigenere', '-v', help='Vigenère key')
    parser.add_argument('--atbash', action='store_true', help='Atbash cipher')
    parser.add_argument('--rot13', action='store_true', help='ROT13')
    parser.add_argument('--xor', help='XOR key (hex or string)')
    parser.add_argument('--beaufort', '-b', help='Beaufort key')
    parser.add_argument('--playfair', help='Playfair key')
    parser.add_argument('--autokey', help='Autokey key')
    parser.add_argument('--gematria', '-g', action='store_true', help='Gematria analysis')
    parser.add_argument('--frequency', '-f', action='store_true', help='Frequency analysis')
    parser.add_argument('--all', '-a', '-all', action='store_true', help='Try ALL methods')
    
    args = parser.parse_args()
    
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            rune_text = f.read()
    elif args.runes:
        rune_text = args.runes
    else:
        print("Usage: python decryptor.py <file> [options]")
        print("\nQuick examples:")
        print("  python decryptor.py LiberPrimus3301 --all")
        print("  python decryptor.py LiberPrimus3301 --gematria")
        print("  python decryptor.py LiberPrimus3301 --vigenere PSYOP")
        print("  python decryptor.py LiberPrimus3301 --caesar 13")
        sys.exit(1)
    
    if args.all:
        try_all_methods(rune_text)
    else:
        alpha_text = runes_to_text(rune_text)
        print(f"Alphabetic text:\n{alpha_text}\n")
        
        if args.caesar is not None:
            print(f"\nCaesar (shift {args.caesar}):")
            print(caesar_decrypt(alpha_text, args.caesar))
        
        if args.vigenere:
            print(f"\nVigenère (key '{args.vigenere}'):")
            print(vigenere_decrypt(alpha_text, args.vigenere))
        
        if args.atbash:
            print(f"\nAtbash:")
            print(atbash_decrypt(alpha_text))
        
        if args.rot13:
            print(f"\nROT13:")
            print(rot13_decrypt(alpha_text))
        
        if args.beaufort:
            print(f"\nBeaufort (key '{args.beaufort}'):")
            print(beaufort_decrypt(alpha_text, args.beaufort))
        
        if args.playfair:
            print(f"\nPlayfair (key '{args.playfair}'):")
            print(playfair_decrypt(alpha_text, args.playfair))
        
        if args.autokey:
            print(f"\nAutokey (key '{args.autokey}'):")
            print(autokey_decrypt(alpha_text, args.autokey))
        
        if args.gematria:
            gematria_analysis(rune_text)
        
        if args.frequency:
            frequency_analysis(alpha_text)


if __name__ == '__main__':
    main()
