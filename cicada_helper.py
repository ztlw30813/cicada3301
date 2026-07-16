#!/usr/bin/env python3
"""
Cicada 3301 Liber Primus Helper Tool
A comprehensive analysis and decryption assistant for the Liber Primus.
"""

import sys
import os
import json
from collections import Counter, OrderedDict
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from decryptor import (
    RUNE_MAP, DELIMITERS, runes_to_text, runes_to_decimal, runes_to_prime,
    caesar_decrypt, vigenere_decrypt, atbash_decrypt, rot13_decrypt,
    beaufort_decrypt, playfair_decrypt, autokey_decrypt, gronsfeld_decrypt,
    chi_squared_analysis, index_of_coincidence, frequency_analysis,
    find_best_caesar, find_best_vigenere
)

# ============================================================
# COLOR SYSTEM
# ============================================================

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def colored(text, color):
    return f"{color}{text}{Colors.END}"

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{Colors.END}\n")

def print_section(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}--- {text} ---{Colors.END}")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

# ============================================================
# LIBER PRIMUS STRUCTURE
# ============================================================

LIBER_PRIMUS_SECTIONS = {
    "00": "PREAMBLE (INSTRUCTIONS)",
    "01": "THE ANSWER",
    "02": "THE TRUTH",
    "03": "THE WAY",
    "04": "WELCOME",
    "05": "THE PUZZLE",
    "06": "THE ENLIGHTENMENT",
    "07": "THE DEATH",
    "08": "THE REBIRTH",
    "09": "THE ASCENSION",
    "10": "THE ILLUMINATION",
    "11": "THE TRANSCENDENCE",
    "12": "THE ENLIGHTENMENT II",
    "13": "THE KNOWLEDGE",
    "14": "THE WISDOM",
    "15": "THE UNDERSTANDING",
    "16": "THE TRUTH II",
    "17": "THE LIGHT",
    "18": "THE DARKNESS",
    "19": "THE BALANCE",
    "20": "THE HARMONY",
    "21": "THE UNITY",
    "22": "THE INFINITE",
    "23": "THE ETERNAL",
    "24": "THE SACRED",
    "25": "THE DIVINE",
    "26": "THE MYSTERY",
    "27": "THE SECRET",
    "28": "THE HIDDEN",
    "29": "THE LOST",
    "30": "THE FOUND",
    "31": "THE JOURNEY",
    "32": "THE DESTINATION",
    "33": "THE END",
    "34": "THE BEGINNING",
    "35": "THE CYCLE",
    "36": "THE SPIRAL",
    "37": "THE MANDALA",
    "38": "THE SIGIL",
    "39": "THE MARK",
    "40": "THE SIGN",
    "41": "THE SYMBOL",
    "42": "THE CODE",
    "43": "THE KEY",
    "44": "THE LOCK",
    "45": "THE DOOR",
    "46": "THE GATE",
    "47": "THE PATH",
    "48": "THE BRIDGE",
    "49": "THE CROSSING",
    "50": "THE OTHER SIDE",
}

KNOWN_SOLUTIONS = {
    "PSYOP": "PSYOP was a Vigenère key discovered during the 2014 puzzle",
    "ENLIGHTENMENT": "Related to the spiritual themes of Cicada 3301",
    "CICADA": "The name of the organization itself",
    "WELCOME": "First decoded message from the initial puzzle",
    "LUPUS": "Latin for 'wolf', associated with the constellation",
    "TOTEN": "German for 'death', connected to puzzle symbolism",
    "AGATHODAIMON": "Greek for 'good spirit', found in Liber Primus",
    "VEIOUS": "Roman deity associated with the underworld",
    "CONSUMPTION": "One of the decoded Liber Primus pages",
    "PRESERVATION": "Another decoded Liber Primus page",
}

GEMATRIA_REFERENCE = OrderedDict([
    ('ᚠ', ('F', 0, 2)), ('ᚢ', ('U', 1, 3)), ('ᚦ', ('TH', 2, 5)),
    ('ᚩ', ('O', 3, 7)), ('ᚱ', ('R', 4, 11)), ('ᚳ', ('C', 5, 13)),
    ('ᚷ', ('G', 6, 17)), ('ᚹ', ('W', 7, 19)), ('ᚻ', ('H', 8, 23)),
    ('ᚾ', ('N', 9, 29)), ('ᛁ', ('I', 10, 31)), ('ᛄ', ('J', 11, 37)),
    ('ᛇ', ('EO', 12, 41)), ('ᛈ', ('P', 13, 43)), ('ᛉ', ('X', 14, 47)),
    ('ᛋ', ('S', 15, 53)), ('ᛏ', ('T', 16, 59)), ('ᛒ', ('B', 17, 61)),
    ('ᛖ', ('E', 18, 67)), ('ᛗ', ('M', 19, 71)), ('ᛚ', ('L', 20, 73)),
    ('ᛝ', ('NG', 21, 79)), ('ᛟ', ('OE', 22, 83)), ('ᛞ', ('D', 23, 89)),
    ('ᚪ', ('A', 24, 97)), ('ᚫ', ('AE', 25, 101)), ('ᚣ', ('Y', 26, 103)),
    ('ᛡ', ('IO', 27, 107)), ('ᛠ', ('EA', 28, 109)),
])

# ============================================================
# MAIN HELPER CLASS
# ============================================================

class CicadaHelper:
    def __init__(self):
        self.rune_text = None
        self.alpha_text = None
        self.decimal_values = None
        self.prime_values = None
        self.load_liber_primus()

    def load_liber_primus(self):
        """Load the Liber Primus file."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(script_dir, 'LiberPrimus3301')
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.rune_text = f.read()
            self.alpha_text = runes_to_text(self.rune_text)
            self.decimal_values = runes_to_decimal(self.rune_text)
            self.prime_values = runes_to_prime(self.rune_text)
            print_success(f"Loaded Liber Primus: {len(self.rune_text)} runes")
        except FileNotFoundError:
            print_error("LiberPrimus3301 file not found!")

    def display_banner(self):
        """Display the main banner."""
        print(colored("""
╔══════════════════════════════════════════════════════════════════╗
║                  CICADA 3301 LIBER PRIMUS                       ║
║                    ~ Helper Tool v2.0 ~                         ║
║                                                                  ║
║              "A journey of a thousand miles                      ║
║                   begins with a single step"                     ║
╚══════════════════════════════════════════════════════════════════╝
        """, Colors.CYAN))

    def display_gematria_table(self):
        """Display the Gematria Primus reference table."""
        print_header("GEMATRIA PRIMUS REFERENCE")
        print(colored("Rune  Letter   Decimal  Prime", Colors.BOLD))
        print("-" * 40)
        for rune, (letter, decimal, prime) in GEMATRIA_REFERENCE.items():
            print(f"  {rune}    {letter:<6}   {decimal:<6}   {prime}")

    def display_delimiters(self):
        """Display delimiter reference."""
        print_header("DELIMITER REFERENCE")
        delimiters = {
            '-': 'Word separator',
            '.': 'Clause separator',
            '&': 'Paragraph separator',
            '$': 'Segment separator',
            '/': 'Line separator',
            '%': 'Page separator',
        }
        for delim, desc in delimiters.items():
            print(f"  {colored(delim, Colors.YELLOW)} : {desc}")

    def analyze_structure(self):
        """Analyze the structure of the Liber Primus."""
        print_header("LIBER PRIMUS STRUCTURE ANALYSIS")

        if not self.rune_text:
            print_error("No rune text loaded!")
            return

        print_info(f"Total characters: {len(self.rune_text):,}")
        print_info(f"Total runes (non-delimiter): {sum(1 for c in self.rune_text if c in RUNE_MAP):,}")

        # Count delimiters
        delim_counts = Counter()
        for c in self.rune_text:
            if c in DELIMITERS:
                delim_counts[c] += 1

        print_section("Delimiter Distribution")
        for delim, count in delim_counts.most_common():
            desc = DELIMITERS.get(delim, 'Unknown')
            print(f"  '{delim}' : {count:,} occurrences")

        # Analyze rune frequency
        rune_freq = Counter(c for c in self.rune_text if c in RUNE_MAP)
        print_section("Top 10 Most Common Runes")
        for rune, count in rune_freq.most_common(10):
            letter, decimal, prime = RUNE_MAP[rune]
            print(f"  {rune} ({letter}) : {count:,} times")

    def analyze_gematria(self):
        """Perform detailed Gematria analysis."""
        print_header("GEMATRIA PRIMUS ANALYSIS")

        if not self.decimal_values:
            print_error("No decimal values to analyze!")
            return

        decimal_sum = sum(self.decimal_values)
        prime_sum = sum(self.prime_values)
        decimal_avg = decimal_sum / len(self.decimal_values)
        prime_avg = prime_sum / len(self.prime_values)

        print_section("Value Sums")
        print(f"  Decimal sum: {colored(f'{decimal_sum:,}', Colors.GREEN)}")
        print(f"  Prime sum:   {colored(f'{prime_sum:,}', Colors.GREEN)}")

        print_section("Averages")
        print(f"  Decimal avg: {decimal_avg:.2f}")
        print(f"  Prime avg:   {prime_avg:.2f}")

        # Check for prime properties
        print_section("Prime Properties")
        all_prime = all(v > 1 and self._is_prime(v) for v in self.prime_values)
        if all_prime:
            print_success("All prime values are actually prime!")
        else:
            print_warning("Some values may not be prime")

        # Fibonacci primes
        fib_primes = {2, 3, 5, 13, 89}
        found = [v for v in self.prime_values if v in fib_primes]
        print_info(f"Fibonacci primes found: {len(found)} occurrences")

    def _is_prime(self, n):
        """Check if a number is prime."""
        if n < 2:
            return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return False
        return True

    def quick_decryption_menu(self):
        """Interactive quick decryption menu."""
        print_header("QUICK DECRYPTION MENU")

        if not self.alpha_text:
            print_error("No alphabetic text available!")
            return

        menu_items = [
            ("1", "Caesar Cipher (Best Fit)", self._caesar_best),
            ("2", "Caesar Cipher (Custom Shift)", self._caesar_custom),
            ("3", "Vigenère (Best Fit)", self._vigenere_best),
            ("4", "Vigenère (Custom Key)", self._vigenere_custom),
            ("5", "Atbash Cipher", self._atbash),
            ("6", "ROT13", self._rot13),
            ("7", "Beaufort Cipher", self._beaufort),
            ("8", "Gronsfeld Cipher", self._gronsfeld),
            ("9", "Index of Coincidence", self._ioc),
            ("0", "Back to Main Menu", None),
        ]

        for key, desc, _ in menu_items:
            print(f"  {colored(key, Colors.CYAN)} : {desc}")

        choice = input(f"\n{Colors.YELLOW}Select option: {Colors.END}").strip()

        for key, desc, func in menu_items:
            if choice == key and func:
                func()
                return

    def _caesar_best(self):
        """Find best Caesar shift."""
        print_section("CAESAR CIPHER - BEST FIT")
        results = find_best_caesar(self.alpha_text)
        print(f"\nTop 5 results:")
        for shift, chi_sq, decrypted in results[:5]:
            print(f"\n  Shift {colored(str(shift), Colors.GREEN)} (χ²={chi_sq:.2f}):")
            print(f"  {decrypted[:150]}...")

    def _caesar_custom(self):
        """Custom Caesar shift."""
        print_section("CAESAR CIPHER - CUSTOM SHIFT")
        try:
            shift = int(input("Enter shift (0-25): ").strip())
            result = caesar_decrypt(self.alpha_text, shift)
            chi_sq = chi_squared_analysis(result)
            print(f"\n  Shift {shift} (χ²={chi_sq:.2f}):")
            print(f"  {result[:200]}...")
        except ValueError:
            print_error("Invalid shift value!")

    def _vigenere_best(self):
        """Find best Vigenère key."""
        print_section("VIGENERE CIPHER - BEST FIT")
        results = find_best_vigenere(self.alpha_text)
        print(f"\nTop 5 results:")
        for key, chi_sq, decrypted in results[:5]:
            print(f"\n  Key '{colored(key, Colors.GREEN)}' (χ²={chi_sq:.2f}):")
            print(f"  {decrypted[:150]}...")

    def _vigenere_custom(self):
        """Custom Vigenère key."""
        print_section("VIGENERE CIPHER - CUSTOM KEY")
        key = input("Enter key: ").strip().upper()
        result = vigenere_decrypt(self.alpha_text, key)
        chi_sq = chi_squared_analysis(result)
        print(f"\n  Key '{key}' (χ²={chi_sq:.2f}):")
        print(f"  {result[:200]}...")

    def _atbash(self):
        """Atbash cipher."""
        print_section("ATBASH CIPHER")
        result = atbash_decrypt(self.alpha_text)
        chi_sq = chi_squared_analysis(result)
        print(f"\n  χ²={chi_sq:.2f}:")
        print(f"  {result[:200]}...")

    def _rot13(self):
        """ROT13 cipher."""
        print_section("ROT13")
        result = rot13_decrypt(self.alpha_text)
        chi_sq = chi_squared_analysis(result)
        print(f"\n  χ²={chi_sq:.2f}:")
        print(f"  {result[:200]}...")

    def _beaufort(self):
        """Beaufort cipher."""
        print_section("BEAUFORT CIPHER")
        keys = ['PSYOP', 'CICADA', 'LUPUS', 'SECRET']
        for key in keys:
            result = beaufort_decrypt(self.alpha_text, key)
            chi_sq = chi_squared_analysis(result)
            print(f"\n  Key '{key}' (χ²={chi_sq:.2f}):")
            print(f"  {result[:100]}...")

    def _gronsfeld(self):
        """Gronsfeld cipher."""
        print_section("GRONSFELD CIPHER")
        keys = [123, 3301, 33, 17, 7]
        for key in keys:
            result = gronsfeld_decrypt(self.alpha_text, key)
            chi_sq = chi_squared_analysis(result)
            print(f"\n  Key {key} (χ²={chi_sq:.2f}):")
            print(f"  {result[:100]}...")

    def _ioc(self):
        """Index of Coincidence."""
        print_section("INDEX OF COINCIDENCE")
        ioc = index_of_coincidence(self.alpha_text)
        print(f"\n  IC = {colored(f'{ioc:.4f}', Colors.GREEN)}")
        print(f"  English reference: 0.0667")
        if 0.06 <= ioc <= 0.08:
            print_success("→ Likely plaintext or simple substitution")
        elif 0.03 <= ioc <= 0.05:
            print_warning("→ Likely polyalphabetic cipher")
        else:
            print_info("→ Unusual distribution")

    def frequency_analysis_display(self):
        """Display frequency analysis."""
        print_header("FREQUENCY ANALYSIS")
        if not self.alpha_text:
            print_error("No text to analyze!")
            return

        text = self.alpha_text.upper()
        counter = Counter(c for c in text if c.isalpha())
        total = sum(counter.values())

        print(f"\n{'Letter':<8} {'Count':<8} {'Freq %':<8} {'Bar'}")
        print("-" * 50)
        for letter, count in counter.most_common():
            freq = count / total * 100 if total > 0 else 0
            bar = '█' * int(freq)
            print(f"{letter:<8} {count:<8} {freq:<8.2f} {colored(bar, Colors.GREEN)}")

    def known_solutions_display(self):
        """Display known solutions and discoveries."""
        print_header("KNOWN SOLUTIONS & DISCOVERIES")

        for key, desc in KNOWN_SOLUTIONS.items():
            print(f"\n  {colored(key, Colors.GREEN)}")
            print(f"    {desc}")

        print_section("Decoded Liber Primus Pages")
        decoded_pages = [
            "Page 00: Preamble/Instructions",
            "Page 01: 'THE ANSWER' - First decoded message",
            "Page 04: 'WELCOME' - Greeting message",
            "Page 33: 'THE END' - Final page designation",
        ]
        for page in decoded_pages:
            print(f"  • {page}")

    def interactive_rune_converter(self):
        """Interactive rune converter."""
        print_header("RUNE CONVERTER")
        print("Enter runes to convert (or 'quit' to exit):")
        print("Example: ᚠᚢᚦᚩᚱᚳ")

        while True:
            runes = input(f"\n{Colors.YELLOW}Runes: {Colors.END}").strip()
            if runes.lower() in ('quit', 'exit', 'q'):
                break

            result = runes_to_text(runes)
            decimal = runes_to_decimal(runes)
            prime = runes_to_prime(runes)

            print(f"\n  Text:    {colored(result, Colors.GREEN)}")
            print(f"  Decimal: {decimal}")
            print(f"  Prime:   {prime}")

    def export_results(self):
        """Export analysis results to file."""
        print_header("EXPORT RESULTS")

        if not self.alpha_text:
            print_error("No data to export!")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cicada_analysis_{timestamp}.txt"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write("CICADA 3301 LIBER PRIMUS ANALYSIS\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")

            f.write("ALPHABETIC TEXT (first 1000 chars):\n")
            f.write(self.alpha_text[:1000] + "\n\n")

            f.write("GEMATRIA SUMMARY:\n")
            f.write(f"  Total runes: {len(self.rune_text):,}\n")
            f.write(f"  Decimal sum: {sum(self.decimal_values):,}\n")
            f.write(f"  Prime sum: {sum(self.prime_values):,}\n\n")

            f.write("TOP CAESAR SHIFTS:\n")
            results = find_best_caesar(self.alpha_text)
            for shift, chi_sq, decrypted in results[:5]:
                f.write(f"  Shift {shift} (χ²={chi_sq:.2f}): {decrypted[:100]}\n")

        print_success(f"Results exported to {filename}")

    def main_menu(self):
        """Display and handle main menu."""
        self.display_banner()

        menu_items = [
            ("1", "Gematria Primus Reference Table", self.display_gematria_table),
            ("2", "Delimiter Reference", self.display_delimiters),
            ("3", "Liber Primus Structure Analysis", self.analyze_structure),
            ("4", "Gematria Analysis", self.analyze_gematria),
            ("5", "Quick Decryption Menu", self.quick_decryption_menu),
            ("6", "Frequency Analysis", self.frequency_analysis_display),
            ("7", "Known Solutions", self.known_solutions_display),
            ("8", "Rune Converter", self.interactive_rune_converter),
            ("9", "Export Results", self.export_results),
            ("0", "Exit", None),
        ]

        while True:
            print(f"\n{Colors.BOLD}MAIN MENU{Colors.END}")
            print("-" * 40)
            for key, desc, _ in menu_items:
                print(f"  {colored(key, Colors.CYAN)} : {desc}")
            print("-" * 40)

            choice = input(f"\n{Colors.YELLOW}Select option: {Colors.END}").strip()

            if choice == '0':
                print(colored("\nGoodbye! The truth awaits those who seek it.", Colors.CYAN))
                break

            for key, desc, func in menu_items:
                if choice == key and func:
                    try:
                        func()
                    except KeyboardInterrupt:
                        print("\n")
                    except Exception as e:
                        print_error(f"Error: {e}")
                    break
            else:
                print_warning("Invalid option! Please try again.")


def main():
    """Main entry point."""
    helper = CicadaHelper()

    if len(sys.argv) > 1:
        # Command line mode
        command = sys.argv[1].lower()
        if command == 'gematria':
            helper.display_gematria_table()
        elif command == 'structure':
            helper.analyze_structure()
        elif command == 'analyze':
            helper.analyze_gematria()
        elif command == 'decrypt':
            helper.quick_decryption_menu()
        elif command == 'frequency':
            helper.frequency_analysis_display()
        elif command == 'solutions':
            helper.known_solutions_display()
        elif command == 'export':
            helper.export_results()
        else:
            print("Usage: python cicada_helper.py [command]")
            print("\nCommands:")
            print("  gematria    - Show Gematria reference table")
            print("  structure   - Analyze Liber Primus structure")
            print("  analyze     - Perform Gematria analysis")
            print("  decrypt     - Quick decryption menu")
            print("  frequency   - Frequency analysis")
            print("  solutions   - Known solutions")
            print("  export      - Export results")
            print("\nRun without arguments for interactive mode.")
    else:
        # Interactive mode
        try:
            helper.main_menu()
        except KeyboardInterrupt:
            print(colored("\n\nGoodbye!", Colors.CYAN))


if __name__ == '__main__':
    main()
