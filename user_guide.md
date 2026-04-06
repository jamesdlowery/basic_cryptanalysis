# Cryptanalysis Support Program — User Guide

**FM 34-40-2 · Appendix F · GW-BASIC / Python port**

---

## Contents

1. [Getting started](#1-getting-started)
2. [Entering text](#2-entering-text)
3. [Enciphering a message](#3-enciphering-a-message)
4. [Deciphering a message](#4-deciphering-a-message)
5. [Frequency counts & ICs](#5-frequency-counts--ics)
6. [Chi test](#6-chi-test)
7. [Finding repeats (Kasiski)](#7-finding-repeats-kasiski)
8. [Saving your work](#8-saving-your-work)

---

## 1. Getting started

The program runs from your terminal. Launch it with:

```
python3 crypto.py
```

You will see the main menu every time you complete an action. Menu items show a status tag when they have been completed during the session — for example, `(PLAINTEXT ENTERED)` or `(COMPLETED)`.

```
           CRYPTANALYSIS SUPPORT PROGRAM

    1. Enter text  (PLAINTEXT ENTERED)
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

> **Note:** Up to 25 lines of text can be held in memory at once. All processing happens on your current session's text — nothing is remembered between runs unless you save it to disk.

---

## 2. Entering text

Choose **option 1** from the main menu. You can load plaintext or ciphertext from a file on disk, or type it directly at the keyboard.

### From the keyboard

1. Select `3` for plaintext or `4` for ciphertext.
2. Type your text. Use **lowercase letters only** for plaintext and **UPPERCASE LETTERS ONLY** for ciphertext. Spaces are preserved exactly as typed.
3. When finished, type `END` on a new line and press Enter.

### From a file on disk

1. Select `1` for plaintext or `2` for ciphertext.
2. Enter the full file path, e.g. `sample.txt` or `/home/user/message.txt`.
3. Each line in the file becomes one line of text in memory (maximum 25 lines).

> **Warning:** Do not use commas in plaintext typed from the keyboard. The original GW-BASIC `INPUT` statement treats commas as field separators; the Python port preserves this restriction.

When ciphertext is entered, the program automatically strips spaces and any non-letter characters (except periods, which mark unknowns) to create the *internal form* used for all statistical analysis.

---

## 3. Enciphering a message

Choose **option 2**. You must have plaintext loaded first (option 1). The program will prompt you to choose a cipher system before enciphering begins.

### Monoalphabetic — system 1

One fixed substitution alphabet is used throughout the entire message. After selecting it, you may:

1. **Change plain component** — enter any 26-letter sequence as the plaintext alphabet (default: `abcdefghijklmnopqrstuvwxyz`).
2. **Change cipher component** — enter the 26-letter ciphertext alphabet (default: `ABCDEFGHIJKLMNOPQRSTUVWXYZ`).
3. **Change specific key** — shift the cipher component so that a chosen letter aligns with A of the plain component. Useful for setting a Caesar-style offset.
4. **Accept alphabet as shown** — proceed immediately to encipher.

**Example — identity cipher (no changes):**

```
P: hello world
C: HELLO WORLD
```

### Periodic polyalphabetic — system 2 (Vigenère)

A repeating key cycles through multiple cipher alphabets. After setting the plain and cipher components, enter the repeating key (e.g. `KEY`). The length of the key becomes the period. You can view and confirm the full matrix before accepting.

**Example — key: KEY:**

```
P: attack at dawn
K: KEYKEYKE YK EYK
C: KXEKMK KX NKAQ
```

### Aperiodic (long random key) — system 3

The program generates a random non-repeating key of whatever length you specify (up to 200 characters). Because the key never repeats, periodic frequency analysis will not work against it — making this the strongest option available in the program.

> **Tip:** After enciphering, the ciphertext is automatically stored in internal format and is ready for frequency analysis or saving — no extra steps are needed.

---

## 4. Deciphering a message

Choose **option 3**. You must have ciphertext loaded first (option 1, choice 2 or 4). The alphabet setup process is identical to enciphering — you must supply the *same* key and components that were used to encipher the message.

1. Load ciphertext via option 1, choosing ciphertext from disk or from keyboard (UPPERCASE).
2. Choose option 3 from the main menu.
3. Select the same system type (mono / periodic / aperiodic) and enter the exact same key and alphabets.
4. The recovered plaintext is stored in memory. Print or save it using options 4 or 5.

> **Warning:** Characters in the ciphertext that cannot be matched in the cipher component are output as a period (`.`). Unexpected periods in your recovered plaintext mean the wrong key or alphabet was used.

---

## 5. Frequency counts & ICs

Choose **option 6** to calculate statistics, **option 7** to print them, or **option 8** to save them to a file. You need ciphertext loaded. The sub-menu offers four analyses:

### 1. Monographic frequencies and IC

Counts each of the 26 letters across all ciphertext lines and computes the monographic Index of Coincidence (IC).

| IC value | Likely meaning |
|---|---|
| ≈ 0.038 | Random or well-mixed polyalphabetic cipher |
| 0.040 – 0.060 | Polyalphabetic — investigate key length |
| ≈ 0.065 | Close to English plaintext — likely monoalphabetic or short key |

### 2. Digraphic frequencies and IC

Counts all 676 two-letter pairs (digraphs) and computes the digraphic IC. Useful for confirming suspected alphabets and identifying transposition ciphers, which preserve the natural digraph distribution of English.

### 3. Periodic frequencies and IC

Splits the ciphertext by a guessed period and computes a separate frequency count and IC for each alphabetic position. Use this when you suspect a Vigenère-type cipher.

1. Enter the period (key length) you want to test.
2. The program shows one frequency table per alphabet position.
3. If all per-position ICs are near 0.065, your guessed period is likely correct.

> **Tip:** Run options 1, 2, and 3 in sequence during analysis. Each builds on the previous to narrow down the cipher type and likely key length before you attempt decipherment.

---

## 6. Chi test

Accessible as sub-menu **option 4** under option 6. The chi test compares two periodic alphabet positions to measure how well their frequency distributions match when one is shifted against the other. This reveals the *relative displacement* between two cipher alphabets — a critical step in breaking Vigenère and similar ciphers.

1. Run the periodic frequency count (option 3) for your suspected period first.
2. Choose whether to output to screen (`P`), save to disk (`D`), or quit (`Q`).
3. Enter the numbers of the two alphabets to compare (e.g. `1` and `2`).
4. The program prints 26 rows, each shifting one alphabet one position relative to the other, with a match score for each shift.
5. The **highest match score** reveals the relative shift between the two alphabets.
6. Repeat for all pairs (1&2, 1&3, 2&3 …) to reconstruct the complete key.

---

## 7. Finding repeats (Kasiski)

Choose **option 9**. This implements a Kasiski-style repeat search: it locates repeated character sequences in the ciphertext and reports their positions. The distances between occurrences of the same repeated sequence are multiples of the key period, making this a powerful tool for determining key length.

1. Enter the minimum length of repeat to search for (minimum allowed: `2`). Use `3` or `4` to reduce noise from accidental coincidences.
2. The program reports every qualifying repeat, showing the repeated string, which line it appeared on, and the letter position within that line.
3. For each repeated sequence, note all positions. Calculate the distances between occurrences and find their Greatest Common Divisor (GCD) — that GCD is a strong candidate for the key length.

**Example output:**

```
XYZ AT LINE 1, LETTER 4 AND AT LINE 2, LETTER 11
XYZ AT LINE 1, LETTER 4 AND AT LINE 3, LETTER 6
```

---

## 8. Saving your work

### Save text (option 5)

Writes plaintext, ciphertext, and key text to a file — one set of three lines per message line, with a blank line between them. The plain and cipher components are appended at the end if the period is 20 or fewer alphabets. Enter any filename, e.g. `mysave.txt`.

### Save frequency statistics (option 8)

Writes whichever statistics have been calculated in the current session (monographic, digraphic, periodic, mixed-alphabet) to a text file for off-line study or printing. Enter any filename, e.g. `mystat.txt`.

> **Warning:** All data in memory is lost when the program exits. Always save before choosing option 10 (Quit) if you intend to resume the analysis.

### Recommended analysis workflow

| Step | Action |
|------|--------|
| 1 | Load ciphertext (option 1) |
| 2 | Run monographic IC check (option 6 → 1) |
| 3 | Find repeats to estimate key length (option 9) |
| 4 | Run periodic IC for your guessed period (option 6 → 3) |
| 5 | Run chi test on all alphabet pairs (option 6 → 4) |
| 6 | Decipher with recovered key (option 3) and save (option 5) |

---

*Cryptanalysis Support Program · FM 34-40-2 Appendix F · Version 1.0 (4 October 1988) · Python port*
