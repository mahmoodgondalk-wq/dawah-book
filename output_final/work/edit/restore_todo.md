# Details dropped because of the old bracket cap (to restore with the new allowance, deletion-only + bracket corrections)
- E035: captions dropped Arabic names entirely (Muwatta, Uhud, Banu Qurayza) -> half-sentences deleted (missing words cannot be added; check only)
- E041: FR128, FR074, FR115 garbled names left misspelt ("Eunice" = Yunus, "Sierra" = Sirah, "NS bin Malik" = Anas bin Malik); some garbled fragments deleted
- E045: FR080:342-414 - Ibn Mas'ud "111 chapters" claim, his explicit report, Ubayy's "116 chapters" deleted (bracket cap)
- E047: FR088 etc. - lists of reciters and tribe names, Ibn Kathir reciting both forms of "sirat", examples of rejected readings deleted
- E054: DONE 2026-10-31 (FR313 restored: Ibn Atiyya, Mujahid, al-Hasan, the three-century gap, the second source; a few names still out)

# Reference boxes vs bracket-corrected verse numbers (check in the final polish)
- Editors sometimes correct a mis-cited verse in brackets (e.g. E135 ML065:1054-1092: "Quran 27:89" -> [18:27], "chapter 16 verse 115" -> [6] 115).
  The reference boxes come from approved_refs.json (resolved from the raw citation), so this passage still gets boxes for 27:89 and 16:115.
  Final polish: list every bracketed [n:n] / [n] verse correction, compare with the unit's approved refs, and fix the boxes
  (fetch the corrected verse from quran.com with fetch_quran.py, record a manual decision, drop the wrong box).

# Pure name insertions in brackets (the guide forbids adding missing words) - verify or remove in the final polish
- E134 ML065:794-843 [Hudhayfah]; ML065:974-1053 [Ibn Kathir] (Quran 3:3 quote), [al-Tabari] (3:50); also [Ibn Hazm], [Ibn Ishaq], [Saadia]
  (names identified by the editor from the quoted text; check against the tafsir texts, else delete the quotation).
- E068 FR098:1-168 "[Ibn Hazm and Imam] Muslim" (missing name before "and"; context makes it clear).
- DONE 2026-11-07: ML065:1063 box 27:89 -> 18:27, ML065:1074 box 16:115 -> 6:115 (manual_decisions.json + resolve_refs final +
  finalize_refs). The two old files are kept because the verbatim compilation (output_final/book) still shows them.
  Other bracketed verse numbers (26) checked: no other wrong Quran box (the rest are Bible references or have no box).
- DONE 2026-11-07 name polish (script): Ibraim->[Ibrahim] x7, Westenfeld->[Wüstenfeld] x2, Usery/usery->[usury] x3,
  Nejiran->[Najran] x2, Sierra->[Sirah], NS bin->[Anas] bin, Eunice->[Yunus] (E008, E031, E032, E034, E038, E040, E041; all re-checked OK).
  Left as captioned (unidentified): Damans, Benue, Alabri, Awiyazid; "Shamun" is an accepted spelling of Sham'un.
- CHECKED 2026-11-07 (kept): E134 [Hudhayfah] came to [Uthman] (Bukhari 4987, Hudhayfah's words to Uthman); [Ibn Hazm] d. 456 AH;
  [Ibn Ishaq] quoting the Gospel of John (his Sirah quotes John 15:23ff.); rabbi [Saadia] (for "s"; Saadia Gaon's Arabic Torah);
  [Ibn Kathir] on 3:3 and [al-Tabari] on the Injil/Torah confirmation (wording matches their tafsirs). All well grounded.
- DONE 2026-11-07 restore pass: E045 FR080:342-414 Ubayy's 116 chapters restored; E047 FR268:64-153 (tribes Asad, Bakr ibn Wa'il;
  al-Susi and Abu 'Amr; Kisa'i) and FR268:154-216 (Ibn Kathir the reciter reciting both forms) restored. Not restorable within
  the bracket allowance or because words are missing (not garbled): Ibn Mas'ud's 111 chapters, six reciters, rejected readings.
