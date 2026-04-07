# Cryptanalysis Support Program

A faithful Python 3 port of the **GW-BASIC Cryptanalysis Support Program** originally published in **FM 34-40-2, *Basic Cryptanalysis*, Appendix F** (US Army, 4 October 1988). The original `.bas` source file is also included.

---

## Overview

This program supports the analysis and breaking of classical substitution ciphers. It provides:

- **Encipherment and decipherment** — monoalphabetic, periodic polyalphabetic (Vigenère), and aperiodic (long random key) systems
- **Monographic frequency analysis** with Index of Coincidence (IC)
- **Digraphic frequency analysis** with IC
- **Periodic frequency analysis** by alphabet position with per-alphabet IC
- **Chi test** for determining relative key displacements between periodic alphabets
- **Repeat finding** (Kasiski examination) to estimate key length
- **Save and load** text and statistics to/from disk

It was developed to support training in cryptanalytic techniques as described in FM 34-40-2 and is particularly useful for preparing examples and exercises.

---

## Files

| File | Description |
|---|---|
| `crypto.py` | Python 3 port — main program to run |
| `crypto.bas` | Original GW-BASIC source (598 lines, FM 34-40-2 Appendix F) |
| `docs/guide.md` | User guide (Markdown) |
| `docs/guide.html` | User guide (standalone HTML) |
| `docs/guide.pdf` | User guide (PDF) |
| `docs/guide.docx` | User guide (Word document) |

---

## Requirements

- Python 3.7 or later
- No third-party packages required — standard library only

---

## Quick Start

```bash
# Clone the repo
git clone https://github.com/YOUR-USERNAME/cryptanalysis-support-program.git
cd cryptanalysis-support-program

# Run the program
python3 crypto.py
```

You will be presented with the main menu:

```
          CRYPTANALYSIS SUPPORT PROGRAM

    1. Enter text
    2. Encipher text
    3. Decipher text
    4. Print text
    5. Save text to disk
    6. Calculate frequency counts, ICs
    7. Print frequency counts, ICs
    8. Save frequency counts, ICs to disk
    9. Find repeats
   10. Quit
```

---

## Usage Summary

### Entering text

- Choose **option 1** to enter plaintext or ciphertext from the keyboard or from a file.
- Plaintext must be entered in **lowercase**; ciphertext in **UPPERCASE**.
- Type `END` on a new line to finish keyboard entry.

### Enciphering / Deciphering

Choose **option 2** to encipher or **option 3** to decipher. Three cipher systems are supported:

| System | Description |
|---|---|
| 1 — Monoalphabetic | Single fixed substitution alphabet |
| 2 — Periodic polyalphabetic | Repeating key (Vigenère-style) |
| 3 — Aperiodic | Random non-repeating key (up to 200 characters) |

### Frequency Analysis Workflow

For an unknown ciphertext, a typical analysis sequence is:

1. Load ciphertext — option 1
2. Check monographic IC — option 6 → 1
3. Find repeats to estimate key length — option 9
4. Run periodic IC for your guessed period — option 6 → 3
5. Run chi test on alphabet pairs — option 6 → 4
6. Decipher with recovered key — option 3
7. Save results — option 5

### Index of Coincidence reference

| IC | Interpretation |
|---|---|
| ≈ 0.038 | Random / well-mixed polyalphabetic |
| 0.040 – 0.060 | Polyalphabetic — investigate key length |
| ≈ 0.065 | Near English plaintext — likely monoalphabetic |

---

## Background

FM 34-40-2, *Basic Cryptanalysis*, is a US Army field manual covering classical cryptanalytic techniques including frequency analysis, the Index of Coincidence, the Kasiski examination, and the chi test. Appendix F contains the complete GW-BASIC source listing of this support program, written to run on MS-DOS personal computers of the era.

This repository preserves that program by:

1. Transcribing the original GW-BASIC source verbatim from the scanned appendix pages (`crypto.bas`)
2. Porting it line-by-line to modern Python 3 (`crypto.py`), preserving all original logic, variable names, and menu structure

The port makes no changes to the underlying algorithms or program flow. The GW-BASIC source is included for historical reference and comparison.

---

## Known Limitations

- Up to **25 lines** of text can be held in memory per session (increase `MAX_LINES` in `crypto.py` to raise this limit).
- Up to **20 periodic alphabets** are supported for frequency analysis (increase `MAX_ALPHABETS` to raise this).
- Aperiodic keys are limited to **200 characters** (increase `MAX_KEY_LEN` to raise this).
- The program targets **stdout** rather than a physical printer. Redirect output to a file if a paper record is needed.
- The chi test and periodic analysis sub-menus do not support on-screen interactive trial recovery — see FM 34-40-2 Appendix F, paragraph F-2, for notes on extending the program to support this.

---

## Recommended Suggested Branch Structure

```
main          ← stable, tagged releases
dev           ← active development
```

---

## License and Attribution

The original GW-BASIC program is a work of the United States Government (US Army) and is in the **public domain** under 17 U.S.C. § 105.

This Python port and all accompanying documentation are released to the **public domain** under the same basis. No rights reserved.

**Original source:**
> Headquarters, Department of the Army. *FM 34-40-2: Basic Cryptanalysis*, Appendix F — Cryptanalysis Support Program. Washington, DC: Department of the Army, 1990.
