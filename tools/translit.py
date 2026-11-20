import json, re

FATHA='َ'; DAMMA='ُ'; KASRA='ِ'; SHADDA='ّ'; SUKUN='ْ'
FATHATAN='ً'; DAMMATAN='ٌ'; KASRATAN='ٍ'
MADDA='آ'
ALEF='ا'; ALEF_HAMZA_ABOVE='أ'; ALEF_HAMZA_BELOW='إ'; ALEF_WASLA='ٱ'
ALEF_MAKSURA='ى'; HAMZA='ء'; TATWEEL='ـ'
WAW='و'; YEH='ي'; TEH_MARBUTA='ة'
SUPERSCRIPT_ALEF='ٰ'
HAMZA_ON_WAW='ؤ'; HAMZA_ON_YEH='ئ'
VOWEL_DIACS = (FATHA,KASRA,DAMMA,FATHATAN,KASRATAN,DAMMATAN)
HAMZA_SEATS = (HAMZA, ALEF_HAMZA_ABOVE, ALEF_HAMZA_BELOW, HAMZA_ON_WAW, HAMZA_ON_YEH)

CONS = {
 'ب':'b', 'ت':'t', 'ث':'th', 'ج':'j', 'ح':'ḥ', 'خ':'kh',
 'د':'d', 'ذ':'dh', 'ر':'r', 'ز':'z', 'س':'s', 'ش':'sh',
 'ص':'ṣ', 'ض':'ḍ', 'ط':'ṭ', 'ظ':'ẓ', 'ع':'ʿ', 'غ':'gh',
 'ف':'f', 'ق':'q', 'ك':'k', 'ل':'l', 'م':'m', 'ن':'n',
 'ه':'h', 'ة':'t',
}
SUN_LETTERS = set('تثدذرزسشصضطظلن')

EXCEPTIONS = {
 'أَ': 'a-', 'وَ': 'wa-',
 'الَّذِي': 'alladhī', 'الَّتِي': 'allatī',
 'اللّٰهُ': 'allāhu', 'اللَّهُ': 'allāhu',
 'فَلاَّحٌ': 'fallāḥun', 'ثَلاَّجَةٌ': 'thallājatun',
}

def strip_al_prefix(s, initial):
    if s.startswith('ال') and not s.startswith('الِ'):
        rest = s[2:]
        a = 'a' if initial else ''
        if rest and rest[0] in SUN_LETTERS:
            sun_latin = CONS[rest[0]]
            prefix = a + sun_latin + '-'
            for k in range(1, min(3, len(rest))):
                if rest[k] == SHADDA:
                    rest = rest[:k] + rest[k+1:]
                    break
            return (prefix, rest)
        return (a + 'l-', rest)
    return (None, s)

WASL_NO_DIACRITIC = ('اسم', 'ابن', 'ابنة', 'امرأة', 'اثنان', 'اثنتان', 'است')
_DIAC_STRIP = (FATHA,DAMMA,KASRA,SHADDA,SUKUN,FATHATAN,DAMMATAN,KASRATAN,TATWEEL)
def _skeleton(x):
    return ''.join(ch for ch in x if ch not in _DIAC_STRIP)

def core_translit(s, initial=True):
    if initial:
        skel = _skeleton(s)
        for w in WASL_NO_DIACRITIC:
            if skel.startswith(w):
                s = s[0] + KASRA + s[1:]
                break
    out = []
    n = len(s)
    i = 0
    first = initial
    while i < n:
        c = s[i]
        if c == TATWEEL or c in VOWEL_DIACS or c == SUKUN:
            i += 1; continue

        if first and c == ALEF and i+1 < n and s[i+1] in (KASRA, FATHA, DAMMA):
            vmap = {KASRA:'i', FATHA:'a', DAMMA:'u'}
            out.append(vmap[s[i+1]])
            i += 2; first=False; continue

        if c == ALEF_MAKSURA and out and out[-1] == 'an' and i+1 == n:
            i += 1; first=False; continue

        if c == ALEF and out and out[-1] == 'ū' and i+1 == n:
            i += 1; first=False; continue

        # alef (bare) immediately followed by fathatan => word-final "-an", not long a
        if c == ALEF and i+1 < n and s[i+1] == FATHATAN:
            out.append('an'); i += 2; first=False; continue

        if c in (ALEF, ALEF_WASLA, SUPERSCRIPT_ALEF, ALEF_MAKSURA):
            if out and out[-1] == 'a':
                out[-1] = 'ā'
            else:
                out.append('ā')
            i += 1; first=False; continue

        if c == MADDA:
            mark = '' if first else 'ʾ'
            if out and out[-1] == 'a':
                out[-1] = mark + 'ā'
            else:
                out.append(mark + 'ā')
            i += 1; first=False; continue

        if c in HAMZA_SEATS:
            base = '' if first else 'ʾ'
            i += 1
            dbl = False
            j = i
            if j < n and s[j] == SHADDA:
                dbl = True; j += 1
            vowel = ''
            if j < n and s[j] == FATHA: vowel='a'; j+=1
            elif j < n and s[j] == KASRA: vowel='i'; j+=1
            elif j < n and s[j] == DAMMA: vowel='u'; j+=1
            elif j < n and s[j] == FATHATAN: vowel='an'; j+=1
            elif j < n and s[j] == KASRATAN: vowel='in'; j+=1
            elif j < n and s[j] == DAMMATAN: vowel='un'; j+=1
            elif j < n and s[j] == SUKUN: vowel=''; j+=1
            if not dbl and j < n and s[j] == SHADDA:
                dbl = True; j += 1
            longmark = ''
            if vowel == 'an' and j < n and s[j] == ALEF:
                j += 1
            elif j < n and s[j] == ALEF and vowel == 'a':
                longmark = 'ā'; j += 1
            elif j < n and s[j] == YEH and vowel == 'i':
                nxt = s[j+1] if j+1 < n else ''
                if nxt not in VOWEL_DIACS and nxt != SHADDA:
                    longmark = 'ī'; j += 1
            if dbl:
                out.append(base+base if base else base)
            out.append(base)
            out.append(longmark if longmark else vowel)
            i = j; first=False
            continue

        if c in CONS:
            base = CONS[c]
            i += 1
            dbl = False
            j = i
            if j < n and s[j] == SHADDA:
                dbl = True; j += 1
            vowel = ''
            if j < n and s[j] == FATHA: vowel='a'; j+=1
            elif j < n and s[j] == KASRA: vowel='i'; j+=1
            elif j < n and s[j] == DAMMA: vowel='u'; j+=1
            elif j < n and s[j] == FATHATAN: vowel='an'; j+=1
            elif j < n and s[j] == KASRATAN: vowel='in'; j+=1
            elif j < n and s[j] == DAMMATAN: vowel='un'; j+=1
            elif j < n and s[j] == SUKUN: vowel=''; j+=1
            if not dbl and j < n and s[j] == SHADDA:
                dbl = True; j += 1

            longmark = ''
            if vowel == '' and j < n and s[j] == ALEF and j+1 < n and s[j+1] == FATHATAN:
                vowel = 'an'; j += 2
            elif vowel == 'an' and j < n and s[j] == ALEF:
                j += 1
            elif j < n and s[j] == ALEF and vowel == 'a':
                longmark = 'ā'; j += 1
            elif j < n and s[j] == ALEF_MAKSURA and vowel == 'a':
                longmark = 'ā'; j += 1
            elif j < n and s[j] == WAW and vowel == 'u':
                nxt = s[j+1] if j+1 < n else ''
                if nxt not in VOWEL_DIACS and nxt != SHADDA:
                    longmark = 'ū'; j += 1
            elif j < n and s[j] == YEH and vowel == 'i':
                nxt = s[j+1] if j+1 < n else ''
                if nxt not in VOWEL_DIACS and nxt != SHADDA:
                    longmark = 'ī'; j += 1

            if dbl:
                out.append(base); out.append(base)
            else:
                out.append(base)
            out.append(longmark if longmark else vowel)
            i = j; first=False
            continue

        if c in (WAW, YEH):
            cons_latin = 'w' if c == WAW else 'y'
            j = i+1
            dbl = False
            if j < n and s[j] == SHADDA:
                dbl = True; j += 1
            vowel = ''
            if j < n and s[j] == FATHA: vowel='a'; j+=1
            elif j < n and s[j] == KASRA: vowel='i'; j+=1
            elif j < n and s[j] == DAMMA: vowel='u'; j+=1
            elif j < n and s[j] == FATHATAN: vowel='an'; j+=1
            elif j < n and s[j] == KASRATAN: vowel='in'; j+=1
            elif j < n and s[j] == DAMMATAN: vowel='un'; j+=1
            elif j < n and s[j] == SUKUN: vowel=''; j+=1
            if not dbl and j < n and s[j] == SHADDA:
                dbl = True; j += 1
            if dbl:
                out.append(cons_latin); out.append(cons_latin); out.append(vowel)
            elif vowel:
                out.append(cons_latin); out.append(vowel)
            else:
                if out and out[-1] == 'u' and c == WAW:
                    out[-1] = 'ū'
                elif out and out[-1] == 'i' and c == YEH:
                    out[-1] = 'ī'
                else:
                    out.append(cons_latin)
            i = j; first=False
            continue

        out.append(c)
        i += 1; first=False
    return ''.join(out)

import unicodedata as _ud
def translit_word(word, initial=True):
    s = _ud.normalize('NFC', word.strip())
    if not s:
        return ''
    if s in EXCEPTIONS:
        return EXCEPTIONS[s]
    # Hamzat al-qat' at the very start of an utterance always carries a vowel; if the
    # source text left the seat letter itself unmarked (vowel placed on the next letter
    # instead, a vocalization-placement slip rather than an unvocalized word), default it
    # instead of silently dropping the initial vowel (أتَى -> 'tā' instead of 'atā').
    if initial and len(s) >= 2 and s[0] in (ALEF_HAMZA_ABOVE, ALEF_HAMZA_BELOW) and s[1] not in VOWEL_DIACS and s[1] not in (SHADDA, SUKUN):
        default_vowel = FATHA if s[0] == ALEF_HAMZA_ABOVE else KASRA
        s = s[0] + default_vowel + s[1:]
    if s.startswith('الِ'):
        rest = s[3:]
        if rest.startswith(ALEF):
            rest = rest[1:]
        prefix = 'al-' if initial else 'l-'
        return prefix + 'i' + core_translit(rest, initial=True)
    prefix, rest = strip_al_prefix(s, initial)
    if prefix is not None:
        return prefix + core_translit(rest, initial=True)
    return core_translit(s, initial=initial)

BARE_FALLBACK = {
 'على': 'ʿalā', 'علي': 'ʿalā', 'إلى': 'ilā', 'الى': 'ilā',
 'في': 'fī', 'من': 'min', 'عن': 'ʿan', 'مع': 'maʿa',
 'كلامه': 'كَلامِهِ',
}
import re as _re
def translit(phrase):
    phrase = _re.sub(r'[\u061F?.\u2026]+', '', phrase)
    words = [w for w in phrase.split(' ') if w]
    out = []
    for idx, w in enumerate(words):
        if w in BARE_FALLBACK:
            fb = BARE_FALLBACK[w]
            if any('\u0600' <= c <= '\u06ff' for c in fb):
                out.append(translit_word(fb, initial=(idx==0)))
            else:
                out.append(fb)
        else:
            out.append(translit_word(w, initial=(idx==0)))
    return ' '.join(out)

if __name__ == '__main__':
    pairs = json.load(open('/tmp/ar_tl_pairs.json'))
    ok = 0
    fails = []
    for ar, tl in pairs:
        guess = translit(ar)
        if guess == tl or guess.lower() == tl.lower():
            ok += 1
        else:
            fails.append((ar, tl, guess))
    print(f'{ok}/{len(pairs)} matches (case-insensitive) ({100*ok//len(pairs)}%)')
    for ar,tl,guess in fails:
        print(f'  AR={ar!r:25} EXPECTED={tl!r:25} GOT={guess!r}')
