# Cicada 3301 Liber Primus Decryptor

A Python-based decryptor for the Cicada 3301 Liber Primus puzzle.

## Features

- **Rune to Text Conversion**: Converts Elder Futhark runes to alphabetic text using the Gematria Primus
- **Caesar Cipher Decryption**: Tries all 26 possible shifts and finds the best fit using chi-squared analysis
- **Vigenère Cipher Decryption**: Tests known Cicada 3301 keywords and common keys
- **Frequency Analysis**: Compares letter frequencies to standard English distribution
- **Interactive Mode**: User-friendly interface for exploring different decryption methods

## Usage

### Command Line Mode

```bash
# Analyze a file with all methods
python3 decryptor.py LiberPrimus3301 --all

# Caesar cipher with specific shift
python3 decryptor.py LiberPrimus3301 --caesar 13

# Vigenère cipher with specific key
python3 decryptor.py LiberPrimus3301 --vigenere PSYOP

# Show frequency analysis
python3 decryptor.py LiberPrimus3301 --frequency
```

### Interactive Mode

```bash
python3 interactive_decryptor.py
```

### Helper Tool

```bash
# Interactive mode (full menu system)
python3 cicada_helper.py

# Command line mode
python3 cicada_helper.py gematria      # Show Gematria reference table
python3 cicada_helper.py structure     # Analyze Liber Primus structure
python3 cicada_helper.py analyze       # Perform Gematria analysis
python3 cicada_helper.py decrypt       # Quick decryption menu
python3 cicada_helper.py frequency     # Frequency analysis
python3 cicada_helper.py solutions     # Known solutions
python3 cicada_helper.py export        # Export results to file
```

## Gematria Primus Reference

| Rune | Letter | Value | Rune | Letter | Value |
|------|--------|-------|------|--------|-------|
| ᚠ | F | 0 | ᛋ | S(Z) | 15 |
| ᚢ | V(U) | 1 | ᛏ | T | 16 |
| ᚦ | TH | 2 | ᛒ | B | 17 |
| ᚩ | O | 3 | ᛖ | E | 18 |
| ᚱ | R | 4 | ᛗ | M | 19 |
| ᚳ | C(K) | 5 | ᛚ | L | 20 |
| ᚷ | G | 6 | ᛝ | NG(ING) | 21 |
| ᚹ | W | 7 | ᛟ | OE | 22 |
| ᚻ | H | 8 | ᛞ | D | 23 |
| ᚾ | N | 9 | ᚪ | A | 24 |
| ᛁ | I | 10 | ᚫ | AE | 25 |
| ᛄ | J | 11 | ᚣ | Y | 26 |
| ᛇ | EO | 12 | ᛡ | IO | 27 |
| ᛈ | P | 13 | ᛠ | EA | 28 |
| ᛉ | X | 14 | | | |

## Delimiters

- `-` : Word separator
- `.` : Clause separator  
- `&` : Paragraph separator
- `$` : Segment separator
- `/` : Line separator
- `%` : Page separator

## Known Cicada 3301 Keywords

Some keys that have been discovered or are suspected:

- PSYOP
- ENLIGHTENMENT  
- CICADA
- WELCOME
- LUPUS
- TOTEN
- QUID
- OBSIDIAN
- PUER
- NOVUS
- ORDO
- TEMPUS
- FUGIT
- SOLVED
- PRIMUS
- GEMATRIA

## Files

- `decryptor.py` - Main decryptor with all cipher methods
- `interactive_decryptor.py` - Interactive user interface
- `cicada_helper.py` - Comprehensive helper tool with analysis features
- `GematriaPrimus` - Rune-to-letter mapping reference
- `LiberPrimus3301` - The Liber Primus text with runes
- `public.key` - Public key from Cicada 3301

## About Cicada 3301

Cicada 3301 was a series of complex puzzles posted online in 2012, 2013, and 2014. The puzzles focused on data security, encryption, and steganography. The Liber Primus is a book of runes that was part of the 2014 puzzle, and much of it remains unsolved to this day.

## License

This is for educational and research purposes only.
