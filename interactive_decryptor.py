#!/usr/bin/env python3
"""
Interactive Cicada 3301 Liber Primus Decryptor
Provides an interactive interface for decrypting the Liber Primus.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from decryptor import (
    RUNE_MAP, DELIMITERS, runes_to_text, caesar_decrypt,
    vigenere_decrypt, frequency_analysis, chi_squared_analysis,
    find_best_caesar, find_best_vigenere
)

def print_banner():
    """Print the decryptor banner."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║              CICADA 3301 LIBER PRIMUS DECRYPTOR             ║
║                    ~ Interactive Mode ~                      ║
╚══════════════════════════════════════════════════════════════╝

Gematria Primus Reference:
ᚠ=F  ᚢ=U  ᚦ=TH ᚩ=O  ᚱ=R  ᚳ=C  ᚷ=G  ᚹ=W
ᚻ=H  ᚾ=N  ᛁ=I  ᛄ=J  ᛇ=EO ᛈ=P  ᛉ=X  ᛋ=S
ᛏ=T  ᛒ=B  ᛖ=E  ᛗ=M  ᛚ=L  ᛝ=NG ᛟ=OE ᛞ=D
ᚪ=A  ᚫ=AE ᚣ=Y  ᛡ=IO ᛠ=EA

Delimiters: - (word) . (clause) & (paragraph) 
            / (line) % (page) $ (segment)
""")


def interactive_mode():
    """Run interactive decryptor."""
    print_banner()
    
    while True:
        print("\n" + "=" * 50)
        print("MENU:")
        print("  1. Load Liber Primus file")
        print("  2. Enter rune text directly")
        print("  3. Decrypt with Caesar cipher")
        print("  4. Decrypt with Vigenère cipher")
        print("  5. Frequency analysis")
        print("  6. Find best Caesar shift")
        print("  7. Find best Vigenère key")
        print("  8. Try all methods")
        print("  9. Rune to text converter")
        print("  0. Exit")
        print("=" * 50)
        
        choice = input("\nEnter choice: ").strip()
        
        if choice == '0':
            print("Goodbye!")
            break
        
        elif choice == '1':
            filepath = input("Enter file path: ").strip()
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    text = f.read()
                print(f"\nLoaded {len(text)} characters")
                alpha = runes_to_text(text)
                print(f"\nFirst 500 chars of alphabetic text:\n{alpha[:500]}")
            except FileNotFoundError:
                print("File not found!")
        
        elif choice == '2':
            print("Enter rune text (press Enter twice to finish):")
            lines = []
            while True:
                line = input()
                if line == '' and lines and lines[-1] == '':
                    break
                lines.append(line)
            text = '\n'.join(lines[:-1])
            alpha = runes_to_text(text)
            print(f"\nAlphabetic text:\n{alpha}")
        
        elif choice == '3':
            text = input("Enter text to decrypt: ").strip()
            shift = int(input("Enter Caesar shift (0-25): ").strip())
            decrypted = caesar_decrypt(text, shift)
            print(f"\nDecrypted:\n{decrypted}")
        
        elif choice == '4':
            text = input("Enter text to decrypt: ").strip()
            key = input("Enter Vigenère key: ").strip()
            decrypted = vigenere_decrypt(text, key)
            print(f"\nDecrypted:\n{decrypted}")
        
        elif choice == '5':
            text = input("Enter text to analyze: ").strip()
            frequency_analysis(text)
        
        elif choice == '6':
            text = input("Enter text to analyze: ").strip()
            results = find_best_caesar(text)
            print("\nTop 5 Caesar shifts:")
            for shift, chi_sq, decrypted in results[:5]:
                print(f"  Shift {shift:2d} (χ²={chi_sq:.2f})")
                print(f"    {decrypted[:100]}...")
        
        elif choice == '7':
            text = input("Enter text to analyze: ").strip()
            results = find_best_vigenere(text)
            print("\nTop 5 Vigenère keys:")
            for key, chi_sq, decrypted in results[:5]:
                print(f"  Key '{key}' (χ²={chi_sq:.2f})")
                print(f"    {decrypted[:100]}...")
        
        elif choice == '8':
            filepath = input("Enter Liber Primus file path: ").strip()
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    text = f.read()
                
                alpha = runes_to_text(text)
                print(f"\nAlphabetic text:\n{alpha[:200]}...\n")
                
                # Caesar
                print("\n--- Caesar Analysis ---")
                caesar_results = find_best_caesar(alpha)
                for shift, chi_sq, decrypted in caesar_results[:3]:
                    print(f"  Shift {shift:2d}: {decrypted[:80]}...")
                
                # Vigenère
                print("\n--- Vigenère Analysis ---")
                vigenere_results = find_best_vigenere(alpha)
                for key, chi_sq, decrypted in vigenere_results[:3]:
                    print(f"  Key '{key}': {decrypted[:80]}...")
                
            except FileNotFoundError:
                print("File not found!")
        
        elif choice == '9':
            runes = input("Enter rune text: ").strip()
            result = runes_to_text(runes)
            print(f"\nConverted text:\n{result}")
        
        else:
            print("Invalid choice!")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Command line mode
        from decryptor import main
        main()
    else:
        # Interactive mode
        interactive_mode()
