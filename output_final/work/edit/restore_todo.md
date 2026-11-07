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
