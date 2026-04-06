#!/usr/bin/env python3
"""
CRYPTANALYSIS SUPPORT PROGRAM
Version 1.0 (Python port)
Original: 4 October 1988, GW-BASIC, FM 34-40-2 Basic Cryptanalysis, Appendix F
Python port: faithfully reproduces all original functionality.

Supports:
  - Monoalphabetic and polyalphabetic (periodic & aperiodic) encipherment/decipherment
  - Monographic, digraphic, and periodic frequency counts with Index of Coincidence (IC)
  - Chi test for matching periodic alphabets
  - Repeat-finding (Kasiski examination aid)
  - Save/load text and statistics to disk
"""

import os
import sys
import random
import string

# ---------------------------------------------------------------------------
# Constants / printer setup
# ---------------------------------------------------------------------------
FORMFEED = "\x0c"

# ---------------------------------------------------------------------------
# Program state  (mirrors the GW-BASIC global variables)
# ---------------------------------------------------------------------------
MAX_LINES   = 25
MAX_ALPHABETS = 20
MAX_KEY_LEN = 200

ptextd  = [""] * (MAX_LINES + 1)   # display plaintext  (1-indexed)
ptexti  = [""] * (MAX_LINES + 1)   # internal plaintext (unused in this port)
ctextd  = [""] * (MAX_LINES + 1)   # display ciphertext
ctexti  = [""] * (MAX_LINES + 1)   # internal ciphertext (stripped)
ktextd  = [""] * (MAX_LINES + 1)   # key text (for display)
nrlines = 0

mfreq   = [0] * 27                 # monographic freqs  [1..26]
pfreq   = [[0]*28 for _ in range(MAX_ALPHABETS+1)]   # periodic freqs [1..20][1..27]
difreq  = [[0]*27 for _ in range(27)]                # digraphic freqs [1..26][1..26]
pmixfreq = [[0]*27 for _ in range(MAX_ALPHABETS+1)]  # mixed-alph periodic freqs

phimono = 0.0
phiperi = [0.0] * (MAX_ALPHABETS + 1)
phidig  = 0.0
perphisum  = [0.0] * (MAX_ALPHABETS + 1)
pertotltr  = [0]  * (MAX_ALPHABETS + 1)

set1  = [0] * 27
set2  = [0] * 28
match = [0.0] * 28

status   = [""] * 11   # main-menu status tags
stat     = [""] * 5    # freq-count status tags

pcomp  = "abcdefghijklmnopqrstuvwxyz"
ccompo = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ccomp  = [""] * (MAX_KEY_LEN + 1)   # cipher alphabets [1..period]
rkey   = "A" * MAX_ALPHABETS
repeatkey = ""
period = 1
lrk    = ""

mflag = dflag = pflag = 0
cmixflag = aflag = fileflag = 0
totltrs = 0
phisum  = 0.0
totdig  = 0
diphisum = 0.0

outfile_path = ""

alphmix = [""] * (MAX_ALPHABETS + 1)


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------
def cls():
    os.system("cls" if os.name == "nt" else "clear")


def input_str(prompt=""):
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        return ""


def input_int(prompt="", default=0):
    try:
        return int(input(prompt))
    except (ValueError, EOFError):
        return default


def open_output(path):
    """Return an open file handle for writing (text mode)."""
    return open(path, "w", encoding="ascii", errors="replace")


# ---------------------------------------------------------------------------
# Internal ciphertext preparation  (GW-BASIC lines 2660-2940)
# ---------------------------------------------------------------------------
def prep_ciphertext():
    """Strip all non-A-Z (and non-'.') characters from ctextd, store in ctexti."""
    global ctexti
    for tl in range(1, nrlines + 1):
        t = ctextd[tl]
        result = ""
        for ch in t:
            if (ord(ch) < 65 or ord(ch) > 90) and ch != ".":
                pass        # strip
            else:
                result += ch
        ctexti[tl] = result


# ---------------------------------------------------------------------------
# Text Entry  (GW-BASIC lines 1580-2600)
# ---------------------------------------------------------------------------
def text_entry_menu():
    global nrlines, ptextd, ctextd, ctexti, status

    cls()
    print("          TEXT ENTRY MENU")
    print()
    print("    1. Enter plaintext from disk")
    print("    2. Enter ciphertext from disk")
    print("    3. Enter plaintext from keyboard")
    print("    4. Enter ciphertext from keyboard")
    print("    5. Return to Main Menu")
    print()
    choice = input_int("Enter your choice: ")

    if choice == 1:
        enter_plaintext_disk()
    elif choice == 2:
        enter_ciphertext_disk()
    elif choice == 3:
        enter_plaintext_keyboard()
    elif choice == 4:
        enter_ciphertext_keyboard()
    # 5 = return


def enter_plaintext_disk():
    global nrlines, ptextd, status
    fname = input_str("Enter input filename, e.g. sample.txt: ").strip()
    try:
        with open(fname, "r") as f:
            nrlines = 0
            for line in f:
                nrlines += 1
                ptextd[nrlines] = line.rstrip("\n")
                if nrlines >= MAX_LINES:
                    break
        status[1] = " (PLAINTEXT ENTERED)"
    except OSError as e:
        print(f"Error: {e}")


def enter_ciphertext_disk():
    global nrlines, ctextd, ctexti, status
    fname = input_str("Enter input filename, e.g. sample.txt: ").strip()
    try:
        with open(fname, "r") as f:
            nrlines = 0
            for line in f:
                nrlines += 1
                ctextd[nrlines] = line.rstrip("\n")
                if nrlines >= MAX_LINES:
                    break
        status[2] = " (CIPHERTEXT ENTERED)"
        prep_ciphertext()
    except OSError as e:
        print(f"Error: {e}")


def enter_plaintext_keyboard():
    global nrlines, ptextd, status
    print("Type a line of text. Use lower case letters only.")
    print("Use no commas in the text. When you are through,")
    print("type END on a new line.")
    nrlines = 0
    while True:
        t = input_str()
        if t.upper() == "END":
            status[1] = " (PLAINTEXT ENTERED)"
            return
        nrlines += 1
        ptextd[nrlines] = t
        if nrlines >= MAX_LINES:
            break


def enter_ciphertext_keyboard():
    global nrlines, ctextd, ctexti, status
    print("Type a line of text. Use CAPITAL letters only.")
    print("When you are through, type END on a new line.")
    nrlines = 0
    while True:
        t = input_str()
        if t.upper() == "END":
            status[2] = " (CIPHERTEXT ENTERED)"
            prep_ciphertext()
            return
        nrlines += 1
        ctextd[nrlines] = t
        if nrlines >= MAX_LINES:
            break


# ---------------------------------------------------------------------------
# Alphabet Entry  (GW-BASIC lines 3920-6040)
# ---------------------------------------------------------------------------
def alphabet_entry():
    """Entry point called before encipherment/decipherment."""
    global pcomp, ccompo, ccomp, rkey, repeatkey, period, aflag, lrk

    pcomp  = "abcdefghijklmnopqrstuvwxyz"
    ccompo = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    rkey   = "A" * MAX_ALPHABETS
    period = 1
    aflag  = 0
    lrk    = ""

    cls()
    print("Select type of system:")
    print()
    print("    1. Monoalphabetic uniliteral")
    print("    2. Periodic polyalphabetic")
    print("    3. Aperiodic polyalphabetic")
    print()
    sel = input_int("Enter your choice: ")
    if sel == 1:
        mono_alphabet_entry()
    elif sel == 2:
        periodic_alphabet_entry()
    elif sel == 3:
        aflag = 1
        periodic_alphabet_entry()


def mono_alphabet_entry():
    """Monoalphabetic alphabet entry (GW-BASIC 4240-4800)."""
    global pcomp, ccompo, ccomp

    while True:
        cls()
        print("     Present alphabet is--")
        print()
        p_row = "          P: " + "  ".join(list(pcomp))
        c_row = "          C: " + "  ".join(list(ccompo))
        print(p_row)
        print(c_row)
        print()
        print("                    1. Change plain component")
        print("                    2. Change cipher component")
        print("                    3. Change specific key")
        print("                    4. Accept alphabet as shown")
        print()
        choice = input_int("                  Enter your choice: ")

        if choice == 1:
            pcomp = input_component("plain (lowercase a-z): ", lowercase=True)
        elif choice == 2:
            ccompo = input_component("cipher (uppercase A-Z): ", lowercase=False)
        elif choice == 3:
            change_specific_key()
        elif choice == 4:
            ccomp[1] = ccompo
            return


def input_component(label, lowercase):
    """Read a 26-character alphabet component from keyboard."""
    while True:
        s = input_str(f"Enter 26-char {label}: ").strip()
        if lowercase:
            s = s.lower()
            if len(s) == 26 and all(c in string.ascii_lowercase for c in s):
                return s
        else:
            s = s.upper()
            if len(s) == 26 and all(c in string.ascii_uppercase for c in s):
                return s
        print("Invalid component. Must be exactly 26 letters.")


def change_specific_key():
    """Shift cipher component so a chosen letter enciphers as its match."""
    global ccompo
    while True:
        x = input_str("Enter ciphertext letter to align with A of plaintext: ").strip().upper()
        if x and x[0] in ccompo:
            n = ccompo.index(x[0])           # 0-based
            ccompo = ccompo[n:] + ccompo[:n]
            return
        print("CHARACTER NOT FOUND IN CIPHER COMPONENT")


def periodic_alphabet_entry():
    """Periodic/Aperiodic alphabet entry (GW-BASIC 4860-5960)."""
    global pcomp, ccompo, ccomp, rkey, repeatkey, period, cmixflag, aflag, lrk

    while True:
        cls()
        print("     Plain component is--")
        print("          P:  " + "".join(pcomp))
        print("     Cipher component is--")
        print("          C:  " + "-".join(list(ccompo)))
        print()
        if aflag == 0:
            print(f"     Length of period is: {period}")
            if period > 0 and len(rkey) >= period:
                repeatkey = rkey[:period]
            print(f"     Repeating key is: {repeatkey}")
        else:
            print(f"     Length of key is: {period}")
            print(f"     Long running key is: {repeatkey}")
        print()
        print("                    1. Change plain component")
        print("                    2. Change cipher component")
        if aflag == 0:
            print("                    3. Change repeating key")
            print("                    4. Show complete matrix")
        else:
            print("                    3. Generate long running key")
            print("                    4. Accept alphabets")
        print()
        choice = input_int("                  Enter your choice: ")

        if choice == 1:
            pcomp = input_component("plain (lowercase a-z): ", lowercase=True)
        elif choice == 2:
            ccompo = input_component("cipher (uppercase A-Z): ", lowercase=False)
            cmixflag = 1
        elif choice == 3:
            if aflag == 1:
                generate_lrk()
                return
            else:
                change_repeating_key()
        elif choice == 4:
            if aflag == 1:
                return   # accept
            else:
                show_matrix()


def change_repeating_key():
    """Enter a repeating key and build CCOMP$ array."""
    global rkey, period, ccomp, repeatkey
    rkey = input_str("Enter repeating key (uppercase): ").strip().upper()
    period = len(rkey)
    repeatkey = rkey
    build_ccomp_from_key()


def build_ccomp_from_key():
    """Build ccomp[1..period] by sliding ccompo based on each key letter."""
    global ccomp
    for n in range(1, period + 1):
        ch = repeatkey[n-1]
        if ch in ccompo:
            p = ccompo.index(ch)  # 0-based
            ccomp[n] = ccompo[p:] + ccompo[:p]
        else:
            ccomp[n] = ccompo


def generate_lrk():
    """Generate a random long-running key (GW-BASIC 5820-5960)."""
    global period, repeatkey, rkey, lrk
    period = input_int("Enter the number of alphabets (up to 200): ")
    if period < 1:
        period = 1
    if period > MAX_KEY_LEN:
        period = MAX_KEY_LEN
    lrk = "".join(chr(random.randint(0, 25) + 65) for _ in range(period))
    repeatkey = lrk
    rkey = lrk
    build_ccomp_from_key()


def show_matrix():
    """Display the full Vigenere-style matrix for the current key."""
    global pcomp, ccomp
    print()
    print("         P:  " + "".join(pcomp))
    print("             " + "-" * 52)
    for p in range(1, period + 1):
        print(f"         C{p}: " + "-".join(list(ccomp[p])))
    print()
    choice = input_int("  1. Change matrix  2. Accept matrix\n  Enter your choice: ")
    if choice == 2:
        return   # accept


# ---------------------------------------------------------------------------
# Encipherment  (GW-BASIC lines 3000-3420)
# ---------------------------------------------------------------------------
def encipher():
    global ctextd, ktextd, status

    alphabet_entry()
    cyclepos = 0

    for lne in range(1, nrlines + 1):
        ctextd[lne] = ""
        ktextd[lne] = ""

    for lne in range(1, nrlines + 1):
        for ch in ptextd[lne]:
            pchar = ch
            if pchar == " ":
                ctextd[lne] += " "
                ktextd[lne] += ""
                continue
            cyclepos += 1
            if cyclepos > period:
                cyclepos = 1
            kchar = repeatkey[cyclepos - 1] if cyclepos <= len(repeatkey) else "A"
            # Normalise to lowercase
            if 65 <= ord(pchar) <= 90:
                pchar = chr(ord(pchar) + 32)
            if ord(pchar) < 97 or ord(pchar) > 122:
                pchar = "."
            if pchar == ".":
                ctextd[lne] += "."
                ktextd[lne] += kchar
                continue
            found = False
            for i, pc in enumerate(pcomp):
                if pchar == pc:
                    ctextd[lne] += ccomp[cyclepos][i]
                    found = True
                    break
            if not found:
                ctextd[lne] += "."
            ktextd[lne] += kchar

    prep_ciphertext()
    status[2] = " (ENCIPHERMENT COMPLETED)"


# ---------------------------------------------------------------------------
# Decipherment  (GW-BASIC lines 3480-3880)
# ---------------------------------------------------------------------------
def decipher():
    global ptextd, status

    alphabet_entry()
    cyclepos = 0

    for lne in range(1, nrlines + 1):
        ptextd[lne] = ""

    for lne in range(1, nrlines + 1):
        for ch in ctextd[lne]:
            cchar = ch
            if cchar == " ":
                ptextd[lne] += " "
                continue
            cyclepos += 1
            if cyclepos > period:
                cyclepos = 1
            # Normalise to uppercase
            if 97 <= ord(cchar) <= 122:
                cchar = chr(ord(cchar) - 32)
            if ord(cchar) < 65 or ord(cchar) > 90:
                cchar = "."
            if cchar == ".":
                ptextd[lne] += "."
                continue
            found = False
            for i, cc in enumerate(ccomp[cyclepos]):
                if cchar == cc:
                    ptextd[lne] += pcomp[i]
                    found = True
                    break
            if not found:
                ptextd[lne] += "."

    prep_ciphertext()
    status[3] = " (DECIPHERMENT COMPLETED)"


# ---------------------------------------------------------------------------
# Print text  (GW-BASIC lines 6060-6320)
# ---------------------------------------------------------------------------
def print_text():
    global status
    cls()
    ans = input_str("IS PRINTER READY (Y/N)? ").strip().upper()
    if ans == "N":
        return
    # In this Python port, we print to stdout (or redirect to printer externally)
    _write_text(sys.stdout)
    status[4] = " (TEXT PRINTED)"


def _write_text(fh):
    for n in range(1, nrlines + 1):
        fh.write(f"P: {ptextd[n]}\n")
        fh.write(f"C: {ctextd[n]}\n")
        fh.write(f"K: {ktextd[n]}\n")
        fh.write("\n")
    if period <= MAX_ALPHABETS:
        fh.write(f"PLAIN  COMPONENT: {pcomp}\n")
        for n in range(1, period + 1):
            fh.write(f"CIPHER COMPONENT {n}: {ccomp[n]}\n")


# ---------------------------------------------------------------------------
# Save text to disk  (GW-BASIC lines 6360-6780)
# ---------------------------------------------------------------------------
def save_text():
    global status, fileflag
    cls()
    print("Enter complete disk filename for the saved text, for example,")
    fname = input_str("mysave.txt: ").strip()
    if not fname:
        return
    try:
        with open(fname, "w") as f:
            _write_text(f)
        status[5] = " (TEXT SAVED)"
    except OSError as e:
        print(f"Error saving: {e}")


# ---------------------------------------------------------------------------
# Frequency Count menu  (GW-BASIC lines 6840-7060)
# ---------------------------------------------------------------------------
def freq_count_menu():
    global status

    while True:
        cls()
        print("Select the routine you want to run:")
        print()
        print(f"    1. Monographic frequencies and ICs {stat[1]}")
        print(f"    2. Digraphic frequencies and ICs {stat[2]}")
        print(f"    3. Periodic frequencies and ICs {stat[3]}")
        print(f"    4. Chi test {stat[4]}")
        print("    5. RETURN TO MAIN MENU")
        choice = input_str("Your choice: ").strip()
        if not choice or not choice[0].isdigit():
            continue
        c = int(choice[0])
        if c == 1:
            mono_freq_ic()
        elif c == 2:
            digraph_freq_ic()
        elif c == 3:
            periodic_freq_ic()
        elif c == 4:
            chi_test()
        elif c == 5:
            return
        status[6] = " (COMPLETED)"


# ---------------------------------------------------------------------------
# Monographic frequency & IC  (GW-BASIC 7120-7380)
# ---------------------------------------------------------------------------
def mono_freq_ic():
    global mfreq, totltrs, phisum, phimono, mflag

    mfreq   = [0] * 27
    totltrs = 0
    phisum  = 0.0

    for lne in range(1, nrlines + 1):
        for ch in ctexti[lne]:
            z = ord(ch) - 64
            if 1 <= z <= 26:
                mfreq[z] += 1

    for z in range(1, 27):
        totltrs += mfreq[z]
        phisum  += mfreq[z] * (mfreq[z] - 1)

    if totltrs > 1:
        phimono = 26 * phisum / (totltrs * (totltrs - 1))
    else:
        phimono = 0.0

    mflag   = 1
    stat[1] = " (COMPLETED)"
    status[6] = " (COMPLETED)"
    print(f"\nMonographic IC = {phimono:.4f}  (Total letters: {totltrs})")
    input_str("\nPress ENTER to continue.")


# ---------------------------------------------------------------------------
# Digraphic frequency & IC  (GW-BASIC 7440-7840)
# ---------------------------------------------------------------------------
def digraph_freq_ic():
    global ctexti, difreq, totdig, diphisum, phidig, dflag

    # local copy for manipulation
    ci = ctexti[:]
    difreq   = [[0]*27 for _ in range(27)]
    totdig   = 0
    diphisum = 0.0

    # Carry odd characters to the next line
    for lne in range(1, nrlines):
        if len(ci[lne]) % 2 != 0:
            carry = ci[lne][-1]
            ci[lne] = ci[lne][:-1]
            ci[lne+1] = carry + ci[lne+1]

    for lne in range(1, nrlines + 1):
        s = ci[lne]
        for dig in range(1, len(s)//2 + 1):
            ltr1 = ord(s[dig*2-2]) - 64
            ltr2 = ord(s[dig*2-1]) - 64
            if ltr1 == -18 or ltr2 == -18:   # period char
                continue
            if 1 <= ltr1 <= 26 and 1 <= ltr2 <= 26:
                difreq[ltr1][ltr2] += 1

    for r in range(1, 27):
        for c in range(1, 27):
            totdig   += difreq[r][c]
            diphisum += difreq[r][c] * (difreq[r][c] - 1)

    if totdig > 1:
        phidig = 676 * diphisum / (totdig * (totdig - 1))
    else:
        phidig = 0.0

    dflag   = 1
    stat[2] = " (COMPLETED)"
    status[6] = " (COMPLETED)"
    print(f"\nDigraphic IC = {phidig:.4f}  (Total digraphs: {totdig})")
    input_str("\nPress ENTER to continue.")


# ---------------------------------------------------------------------------
# Periodic frequency & IC  (GW-BASIC 7900-8540)
# ---------------------------------------------------------------------------
def periodic_freq_ic():
    global pfreq, perphisum, pertotltr, phiperi, pmixfreq, pflag, period

    period = input_int("What period do you want to use? ")
    if period < 1:
        return

    pfreq      = [[0]*28 for _ in range(MAX_ALPHABETS+1)]
    perphisum  = [0.0] * (MAX_ALPHABETS + 1)
    pertotltr  = [0]   * (MAX_ALPHABETS + 1)

    cyclepos = 0
    for n in range(1, nrlines + 1):
        for ch in ctexti[n]:
            cyclepos += 1
            if cyclepos > period:
                cyclepos = 1
            z = ord(ch) - 64
            if z == -18:
                z = 27
            if 1 <= cyclepos <= MAX_ALPHABETS:
                pfreq[cyclepos][z] += 1

    for m in range(1, period + 1):
        for n in range(1, 27):
            pertotltr[m] += pfreq[m][n]
            perphisum[m] += pfreq[m][n] * (pfreq[m][n] - 1)
        if pertotltr[m] > 1:
            phiperi[m] = 26 * perphisum[m] / (pertotltr[m] * (pertotltr[m] - 1))
        else:
            phiperi[m] = 0.0

    pflag   = 1
    stat[3] = " (COMPLETED)"
    status[6] = " (COMPLETED)"

    # Mixed-alphabet reordering
    if cmixflag:
        for m in range(1, period + 1):
            for n in range(1, 27):
                idx = ord(ccompo[n-1]) - 64
                pmixfreq[m][n] = pfreq[m][idx] if 1 <= idx <= 26 else 0

    print(f"\nPeriodic ICs (period={period}):")
    for m in range(1, period + 1):
        print(f"  Alphabet {m}: IC={phiperi[m]:.4f}  Letters={pertotltr[m]}")
    input_str("\nPress ENTER to continue.")


# ---------------------------------------------------------------------------
# Print frequency counts/ICs  (GW-BASIC 8600-9560)
# ---------------------------------------------------------------------------
def print_freq():
    global status
    cls()
    ans = input_str("IS PRINTER READY — output to screen (Y/N)? ").strip().upper()
    if ans == "N":
        return
    _write_freq(sys.stdout)
    status[7] = " (FREQ PRINTED)"


def _write_freq(fh):
    alph = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if mflag:
        _print_mono_stats(fh, alph)
        fh.write(FORMFEED)
    if dflag:
        _print_digraph_stats(fh, alph)
        fh.write(FORMFEED)
    if pflag:
        _print_periodic_stats(fh, alph)
        fh.write(FORMFEED)
    if cmixflag:
        _print_mixed_stats(fh)
        fh.write(FORMFEED)


def _print_mono_stats(fh, alph):
    fh.write("\n\n")
    fh.write(alph + "\n")
    fh.write("".join(f"{mfreq[n]:3d}" for n in range(1, 27)) + "\n")
    fh.write("\n")
    fh.write(f"TOTAL LETTERS = {totltrs}  MONOGRAPHIC IC = {phimono:.4f}\n")


def _print_digraph_stats(fh, alph):
    fh.write("\n\n")
    fh.write("    " + "  ".join(alph) + "\n")
    for n in range(1, 27):
        row = chr(n + 64) + " "
        row += "".join(f"{difreq[n][m]:3d}" for m in range(1, 27))
        fh.write(row + "\n")
    fh.write("\n")
    fh.write(f"TOTAL DIGRAPHS = {totdig}  DIGRAPHIC IC = {phidig:.4f}\n")


def _print_periodic_stats(fh, alph):
    fh.write("\n\n")
    for n in range(1, period + 1):
        fh.write(alph + "\n")
        fh.write("".join(f"{pfreq[n][m]:3d}" for m in range(1, 27)) + "\n")
        fh.write(f"TOTAL LETTERS = {pertotltr[n]}  IC = {phiperi[n]:.4f}\n\n")


def _print_mixed_stats(fh):
    fh.write("\n\n")
    for m in range(1, period + 1):
        header = "   " + "  ".join(ccompo)
        fh.write(header + "\n")
        fh.write("".join(f"{pmixfreq[m][n]:3d}" for n in range(1, 27)) + "\n")
        fh.write(f"TOTAL LETTERS = {pertotltr[m]}  IC = {phiperi[m]:.4f}\n\n")


# ---------------------------------------------------------------------------
# Save freq stats to disk  (GW-BASIC 9960-10180)
# ---------------------------------------------------------------------------
def save_freq():
    global status
    cls()
    print("Enter the complete disk filename for the saved statistics, for example,")
    fname = input_str("mystat.txt: ").strip()
    if not fname:
        return
    try:
        with open(fname, "w") as f:
            _write_freq(f)
        status[8] = " (FREQ SAVED)"
    except OSError as e:
        print(f"Error saving: {e}")


# ---------------------------------------------------------------------------
# Find Repeats / Kasiski  (GW-BASIC 10240-10920)
# ---------------------------------------------------------------------------
def find_repeats():
    rptlen = input_int("What is the shortest length repeat you want listed? ")
    if rptlen < 2:
        print("Minimum repeat length is 2.")
        input_str("Press ENTER.")
        return

    results = []

    for tline in range(1, nrlines):
        ct = ctexti[tline] + (ctexti[tline+1] if tline < nrlines else "")

        for altr in range(len(ctexti[tline])):
            a = ct[altr:altr+rptlen]
            if len(a) < rptlen:
                continue

            # Search rest of same line
            for bltr in range(altr + 2, len(ctexti[tline]) + 2):
                ctb = ct
                if bltr >= len(ctexti[tline]):
                    break
                b = ctb[bltr:bltr+rptlen]
                if a == b:
                    longer = find_longer(ct, ctb, altr, bltr, rptlen)
                    results.append(
                        f"{ct[altr:altr+longer]} AT LINE {tline}, LETTER {altr+1} "
                        f"AND AT LINE {tline}, LETTER {bltr+1}"
                    )

            # Search subsequent lines
            for bline in range(tline + 1, nrlines + 1):
                ctb = ctexti[bline] + (ctexti[bline+1] if bline < nrlines else "")
                for bltr in range(len(ctexti[bline])):
                    b = ctb[bltr:bltr+rptlen]
                    if a == b:
                        longer = find_longer(ct, ctb, altr, bltr, rptlen)
                        results.append(
                            f"{ct[altr:altr+longer]} AT LINE {tline}, LETTER {altr+1} "
                            f"AND AT LINE {bline}, LETTER {bltr+1}"
                        )

    if results:
        print(f"\nFound {len(results)} repeat(s):\n")
        for r in results:
            print(r)
    else:
        print("\nNo repeats found.")

    status[9] = " (REPEATS FOUND)" if results else " (NO REPEATS)"
    input_str("\nPress ENTER to continue.")


def find_longer(ct, ctb, altr, bltr, rptlen):
    """Extend the match as long as possible."""
    longer = rptlen
    while True:
        longer += 1
        if ct[altr:altr+longer] != ctb[bltr:bltr+longer]:
            return longer - 1
        if altr + longer > len(ct) or bltr + longer > len(ctb):
            return longer - 1


# ---------------------------------------------------------------------------
# Chi Test  (GW-BASIC 11120-12080)
# ---------------------------------------------------------------------------
def chi_test():
    global stat

    print("Do you want to print results or save to disk as text file?")
    s = input_str("Enter P for printer, D for disk, or Q to quit: ").strip().upper()
    if s == "Q":
        return
    if s == "D":
        fname = input_str("Enter the complete disk filename: ").strip()
        fh = open_output(fname)
    else:
        fh = sys.stdout

    while True:
        print(f"\nWhich of the {period} alphabets do you want to match?")
        alf1 = input_int("Enter number of 1st alphabet to be matched: ")
        alf2 = input_int("Enter number of 2nd alphabet to be matched: ")

        print(f"MATCHING ALPHABET {alf1} AND ALPHABET {alf2}")
        fh.write(f"MATCHING ALPHABET {alf1} AND ALPHABET {alf2}\n")

        for n in range(1, 27):
            if cmixflag:
                set1[n] = pmixfreq[alf1][n]
                set2[n] = pmixfreq[alf2][n]
            else:
                set1[n] = pfreq[alf1][n]
                set2[n] = pfreq[alf2][n]

        local_set2 = set2[:]

        for m in range(1, 27):
            # Print first sequence header
            fh.write(" " + " ".join(ccompo) + "\n")
            fh.write("".join(f"{set1[l]:3d}" for l in range(1, 27)) + "\n")

            # Print second sequence (shifted by m-1)
            row2 = ""
            for l in range(0, 26):
                ltrpos = m + l
                if ltrpos > 26:
                    ltrpos -= 26
                row2 += " " + ccompo[ltrpos-1]
            fh.write(row2 + "\n")

            match_val = 0.0
            freq_row = ""
            for n in range(1, 27):
                match_val += set1[n] * local_set2[n]
                freq_row  += f"{local_set2[n]:3d}"
            fh.write(freq_row + "\n")

            match[m] = match_val
            label = f"MATCH {m}: {match_val:.0f}"
            if m % 2 != 0:
                print(f"  {label}", end="   ")
                fh.write(f" {label}\n\n")
            else:
                print(label)
                fh.write(f" {label}\n\n")

            # Rotate set2 left by 1
            local_set2[27] = local_set2[1]
            for n in range(1, 27):
                local_set2[n] = local_set2[n+1]

        q = input_str("\nANOTHER MATCH (Y/N)? ").strip().upper()
        if q != "Y":
            break

    if fh != sys.stdout:
        fh.close()

    stat[4] = " (COMPLETED)"


# ---------------------------------------------------------------------------
# Quit  (GW-BASIC 10980-11060)
# ---------------------------------------------------------------------------
def quit_program():
    choice = input_str("Are you sure you want to quit (Y/N)? ").strip().upper()
    if choice == "Y":
        sys.exit(0)


# ---------------------------------------------------------------------------
# Main Menu  (GW-BASIC 1160-1540)
# ---------------------------------------------------------------------------
def main_menu():
    while True:
        cls()
        print("          CRYPTANALYSIS SUPPORT PROGRAM")
        print()
        print(f"    1. Enter text {status[1]}")
        print(f"    2. Encipher text {status[2]}")
        print(f"    3. Decipher text {status[3]}")
        print(f"    4. Print text {status[4]}")
        print(f"    5. Save text to disk {status[5]}")
        print(f"    6. Calculate frequency counts, ICs {status[6]}")
        print(f"    7. Print frequency counts, ICs {status[7]}")
        print(f"    8. Save frequency counts, ICs to disk {status[8]}")
        print(f"    9. Find repeats {status[9]}")
        print("   10. Quit")
        print()

        sel = input_int("Enter your choice: ")
        if sel == 1:
            text_entry_menu()
        elif sel == 2:
            encipher()
        elif sel == 3:
            decipher()
        elif sel == 4:
            print_text()
        elif sel == 5:
            save_text()
        elif sel == 6:
            freq_count_menu()
        elif sel == 7:
            print_freq()
        elif sel == 8:
            save_freq()
        elif sel == 9:
            find_repeats()
        elif sel == 10:
            quit_program()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main_menu()
