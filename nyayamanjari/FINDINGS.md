# Nyāyamañjarī of Jayanta Bhaṭṭa — digital text findings

Survey date: 2026-05-28.

## Environment caveat

This survey was run from an isolated cloud sandbox whose outbound network
allowlist permits **github.com** / **raw.githubusercontent.com** but blocks
archive.org, gretil.sub.uni-goettingen.de, sarit.indology.info,
digital.muktabodha.org, dcs.uni-heidelberg.de, kkataoka pages on
www2.lit.kyushu-u.ac.jp, www.sanskritdocuments.org, academia.edu, and
tylergneill.github.io. WebSearch returned indexed snippets, but I could not
directly retrieve files from those hosts. Anything below marked "verified" was
either pulled from a github.com / raw.githubusercontent.com URL and inspected on
disk, or is a snippet returned by WebSearch.

## Identity check

Fingerprint string from the user (Jayanta's definition of *pramāṇa*):

> *avyabhicāriṇīm asandigdhām arthopalabdhiṃ vidadhati bodhābodhasvabhāvā sāmagrī pramāṇam*

The SARIT TEI file (see below) prints this in Devanāgarī, sandhi-joined, in
Āhnika 1:

> अव्यभिचारिणीमसन्दिग्धामर्थोपलब्धिं विदधती बोधाबोधस्वभावा सामग्री प्रमाणम् ।

Located at offset ~50173 of the stripped plain-text dump
(`NM_sarit_plain.txt`); also restated twice more in the same passage. Word
spelling: *vidadhatī* (long final ī as a feminine present participle) where the
user's note had *vidadhati* — same word, the i/ī alternation is editorial. The
file passes the identity test for Jayanta Bhaṭṭa's NM and is NOT Jānakīnātha's
*Nyāyasiddhāntamañjarī*.

## Sources surveyed

| # | Source | URL | Format | Encoding | Coverage | Licence | Verified |
|---|--------|-----|--------|----------|----------|---------|----------|
| 1 | **SARIT-corpus** (github mirror) | https://github.com/sarit/SARIT-corpus/blob/master/nyayamanjari.xml — raw: https://raw.githubusercontent.com/sarit/SARIT-corpus/master/nyayamanjari.xml | TEI/XML | Devanāgarī | **all 12 āhnikas**, both volumes; `<div subtype="āhnika" n="1..12">` with `<pb>` elements keyed to Varadacharya pages I.1 — II.718 | **CC BY-SA 4.0** (per teiHeader) | **YES** — downloaded as `NM_sarit_raw.xml` (6.94 MB); fingerprint passes |
| 2 | SARIT website (TEI viewer) | https://sarit.indology.info/ (text id `nyayamanjari.xml`) | TEI/XML (same source) | Devanāgarī | same as #1 | CC BY-SA 4.0 | not directly reachable from sandbox; same file as #1 |
| 3 | GRETIL legacy directory `1_sanskr/6_sastra/3_phil/nyaya/` | https://gretil.sub.uni-goettingen.de/gretil/1_sanskr/6_sastra/3_phil/nyaya/ | (would be plain text / HTML) | — | — | — | **NO machine-readable NM** — host blocked from sandbox, but no NM file surfaced in INDOLOGY/GRETIL-mirror's tree or in WebSearch indices; the user's prior manual check also reported it absent |
| 4 | GRETIL corpustei (mmehner) | https://github.com/mmehner/gretil-corpus-tei | TEI/XML | — | — | — | **NO** — file listing inspected; only `sa_gautama-nyAyasUtra*`, `sa_dharmakIrti-*`, `sa_udayana-*`, `sa_jayatIrtha-nyAyasudhA.xml` etc. No NM file |
| 5 | INDOLOGY/GRETIL-mirror | https://github.com/INDOLOGY/GRETIL-mirror | mirror of legacy GRETIL | — | — | — | dir listing JS-rendered; github API rate-limited; nothing matched `nyay|manjar|jayanta` in unauth probe |
| 6 | Muktabodha Digital Library | https://muktabodha.org/digital-library/ | various e-texts | — | not catalogued | — | **NO** — no NM in indexed site results (search confirmed); the library focuses on tantric corpora |
| 7 | DCS (Hellwig, Heidelberg) | http://kjc-sv013.kjc.uni-heidelberg.de/dcs/ ; mirror github.com/ambuda-org/dcs | lemmatised TSV | IAST | — | CC BY 3.0 / 4.0 | **NO confirmation** — host unreachable; no NM in indexed DCS text-list snippets returned by WebSearch; ambuda-org/dcs README does not mention NM |
| 8 | sanskritdocuments.org | https://www.sanskritdocuments.org/ | HTML / ITX / Unicode | various | — | varies | **NO** — search returned only archive.org hits, no NM at this site |
| 9 | TITUS / Pandanus | http://titus.uni-frankfurt.de/ ; http://sanskrit.inria.fr/Pandanus/ | TEI / proprietary | — | — | — | **NO** — no indexed NM file |
| 10 | archive.org — Sūrya Nārāyaṇa Śukla edition (Kashi Sanskrit Series, 1934–36) | https://archive.org/details/TheNyayamanjariOfJayantaBhattaEdited...BySuryaNarayanaSukla — OCR text stream: https://archive.org/stream/TheNyayamanjariOfJayantaBhattaEdited...BySuryaNarayanaSukla/JayantaBhatta_nyayaManjari_1936-corrected_djvu.txt | scanned PDF + djvu.txt OCR | Devanāgarī (OCR; quality not assessable from here) | full work (this is the Kashi edition the user cites; verify which volume covers āhnika 2 by checking pagination) | public domain (pre-1965 in India; expired) | host blocked — *NOT downloaded*; URL recorded |
| 11 | archive.org — Cakradhara *Granthibhaṅga* commentary, Gaurinath Sastri ed. | vol 1: https://archive.org/details/nyayamanjariofjayantabhattawiththecommentarycranthibhangabycakradharagaurinathsastrivol1_202003_644_A ; vol 3 listed; vol 2 likely exists | scanned PDF + djvu.txt OCR | Devanāgarī (OCR) | NM + Cakradhara's commentary, multivolume | public domain | host blocked — URL only |
| 12 | archive.org — Jha & Jha, *Ananda* (āhnikas 3 & 4, vol. 1, incomplete) | https://archive.org/details/nyayamanjarijayantabhatta34vol1anandajhakishorenathjhaincomplete_202003_28_w | scanned PDF | Devanāgarī | āhnikas 3–4 only — irrelevant for āhnika 2 | public domain | URL only |
| 13 | archive.org — V.N. Jha, Āhnika 1 (Sat Guru Publications) | https://archive.org/details/nyayamanjarijayantabhattaahnika1jhav.n.satgurupublications_202003_742_q | scanned PDF + Sanskrit + English translation | Devanāgarī | **Āhnika 1 only** — *not* āhnika 2 | published 1980s/90s, status unclear | URL only |
| 14 | archive.org — J.V. Bhattacharya, *Compendium of Indian Speculative Logic* (MLBD) | https://archive.org/details/nyayamanjarijayantabhattacompendiumofindianspeculativelogicjanakivallabhabhattacharyamlbd_20200_751_v | scanned PDF + djvu.txt | English translation (not Sanskrit text) | full translation 1978 | likely still in copyright | URL only |
| 15 | archive.org — Kataoka, **Āgamaprāmāṇya** section critical edn | https://archive.org/details/nyayamanjarijayantabhattacriticaleditionoftheagamapramanyasectionkataokakei_202003_478_r | scanned PDF + djvu.txt | IAST + Devanāgarī | Āgamaprāmāṇya is in Āhnika **4–5** of the standard arrangement, not Āhnika 2 | author-deposited preprint; check before redistribution | URL only |
| 16 | archive.org — Kataoka, **Īśvarasiddhi** section critical edn | https://archive.org/details/nyayamanjarijayantabhattacriticaleditionoftheisvarasiddhisectionkataokakei_202003_226_e | scanned PDF + djvu.txt | IAST | Īśvarasiddhi (āhnika 3 in many counts; not āhnika 2) | author preprint | URL only |
| 17 | archive.org — Kataoka, **Vijñānādvaitavāda** section | https://archive.org/details/nyayamanjarijayantabhattacriticaleditionofthevijnanadvaitavadasectionkataokakei_202003_919_B | scanned PDF | IAST | Vijñānādvaitavāda critique (not āhnika 2) | author preprint | URL only |
| 18 | Kyushu University — Kataoka section editions, full list | https://www2.lit.kyushu-u.ac.jp/~kkataoka/Kataoka/ (host blocked from sandbox) | author-deposited PDFs | mostly IAST | Śāstrārambha (āhnika 1), Buddhist refutation of *jāti* (āhnika 7 sphere), Nyāyakalikā, Apoha refutation, Vijñānavāda critique. **No dedicated Āhnika 2 (pratyakṣa) edition by Kataoka** is visible in his published list. | author preprints (free) | URL only |
| 19 | academia.edu — "A Critical Edition of Bhaṭṭa Jayanta's Nyāyamañjarī" (single deposit page) | https://www.academia.edu/71839820/ | PDF | IAST | section-only — actual section depends on which paper is deposited; **login wall** | author preprint; login required | URL only |
| 20 | Graheli — sphoṭa-section critical edition (Vienna) | (not freely online; appears in Springer & Graheli 2015) | book / PDF | IAST | Sphoṭa section, *not* āhnika 2 | publisher-controlled | recorded for completeness |

## Conclusion

- The **single best machine-readable source for the entire Nyāyamañjarī, including
  the second āhnika (pratyakṣa-parīkṣā)**, is the SARIT TEI file derived from
  K.S. Varadācārya's Mysore ORI edition (Vol I 1969 / Vol II 1983 — the standard
  reference edition). Encoding is **Devanāgarī**, not IAST as the user's prompt
  speculated; conversion to IAST is straightforward (e.g. with `indic-transliteration`
  or `aksharamukha`).
- The SARIT XML has explicit `<div subtype="āhnika" n="2">`, and within it 225
  `<pb>` page-break elements keyed to Varadācārya Vol I pages **171 – 395**.
  This locates *every* sentence to a printed page of the standard edition.
- Licence is **CC BY-SA 4.0** (per the file's `<availability>` block), so
  redistribution, reuse, and derivative editions are all permitted with
  attribution.
- **No other machine-readable full text** (TEI or plain) of Jayanta's NM was
  located. GRETIL does not have it. SARIT does. DCS, Muktabodha, sanskritdocuments,
  TITUS, Pandanus all appear to lack it.
- Kataoka has produced critical editions of several sections of NM, but **not of
  Āhnika 2 specifically** (his deposited section editions cover Śāstrārambha
  ≈ Āhnika 1, Āgamaprāmāṇya, Īśvarasiddhi, Vijñānādvaitavāda, Apoha, refutation
  of *jāti*). For Āhnika 2 there is no published section-critical edition online.
- Scanned editions (Śukla / Tailaṅga / Cakradhara / Mysore) are on archive.org,
  pre-public-domain in India; the existing djvu.txt OCR layers for Devanāgarī
  prints are typically poor and would need re-OCR for serious use. Not downloaded
  per instructions.

## Files downloaded into this directory

- `NM_sarit_raw.xml` — full SARIT TEI file, 6.94 MB, Devanāgarī, CC BY-SA 4.0.
  Source: https://raw.githubusercontent.com/sarit/SARIT-corpus/master/nyayamanjari.xml
- `NM_sarit_plain.txt` — same file with XML tags stripped, ~4.8 MB Devanāgarī
  prose. Useful for grep / corpus work; loses page/line markup. Derived locally.
- `NM_ahnika2_sarit.xml` — Āhnika 2 only, wrapped in a minimal TEI root, 1.1 MB,
  with all original `<pb>` / `<lb>` / `<note>` / `<witness>` markup preserved.
  Derived locally from #1.
- `NM_ahnika2_sarit_plain.txt` — Āhnika 2 stripped to running Devanāgarī prose,
  934 KB. Derived locally from #1.

## Recommendation

For the user's stated goal (the second āhnika in a usable digital form):

1. **Use `NM_ahnika2_sarit.xml`** (or the full `NM_sarit_raw.xml`) — it is the
   only complete machine-readable witness, sourced from the standard print
   edition, openly licensed, with print-page anchors retained.
2. If IAST is required, transliterate at read time
   (`indic_transliteration.sanscript.transliterate(text, DEVANAGARI, IAST)` is
   a one-liner).
3. For text-critical work on Āhnika 2 specifically, cross-check the SARIT
   reading against the scans of:
   - Varadācārya Vol I (the SARIT base text): pp. **171–395**.
   - Śukla 1934/36 Kashi edition: vol I covers āhnika 1–4, so āhnika 2 sits in
     vol I; exact pagination not confirmed from this sandbox — check on
     archive.org.
   - Cakradhara *Granthibhaṅga* (Mysore / Gaurinath Sastri ed.): cross-check
     Cakradhara's gloss on perception passages.

## If only scanned PDFs had to be used

(They are not the best option here, since SARIT already exists — but documenting
in case the user wants a comparator edition.)

The Śukla 1936 archive.org item ships with a `*_djvu.txt` OCR layer
(see #10), which is what the search result preview is reading from; the OCR
quality on Devanāgarī from that era of scans is typically too poor for
philological use without manual correction.

**Proposed OCR pipeline (do NOT run yet — confirm with me first):**

1. Download the targeted PDF pages only from archive.org (the host is blocked
   from this sandbox; would need to be done from a permitted environment).
   For Varadācārya Vol I pp. 171–395: ~225 pages.
2. Split the PDF to single-page TIFFs at 600 dpi
   (`pdftoppm -r 600 vol1.pdf page -tiff -f 171 -l 395`).
3. Run **Tesseract 5** with the Sanskrit model: `tesseract page.tiff out -l san --psm 6`.
   Sanskrit-tuned alternatives worth trying: Google Cloud Vision (best
   Devanāgarī accuracy currently); Sanskrit-OCR (sanskrit.iitkgp / IIT
   Bombay's Udaan); E-OCR/Sanskrit by Hellwig.
4. Post-process: normalise anusvāra/visarga, join hyphenated line breaks,
   spot-check headers, run a Sanskrit lemma sanity pass (CLTK / Sanscript).
5. Align to the SARIT TEI file by `<pb n="I.NNN">` anchors and merge / diff.

Estimated cost / time: ~30 min compute for Tesseract, plus several hours of
manual correction per 100 pages even with a good model.
