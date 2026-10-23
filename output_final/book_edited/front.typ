#import "template.typ": *

#page(header: none, footer: none, margin: (x: 25mm, y: 30mm))[
  #v(28%)
  #align(center)[
    #text(size: 30pt, weight: "semibold")[The Muslim Lantern \ and Farid Responds]
    #v(8mm)
    #line(length: 40%, stroke: 0.8pt + c-ref-line)
    #v(6mm)
    #text(size: 17pt, style: "italic", fill: c-other)[The Arguments]
  ]
]

#page(header: none, footer: none, margin: (x: 25mm, y: 30mm))[
  #v(20%)
  #align(center)[
    #text(size: 22pt, weight: "semibold")[The Muslim Lantern and Farid Responds]
    #v(4mm)
    #text(size: 14pt, style: "italic")[The Arguments]
    #v(14mm)
    #set par(first-line-indent: 0pt)
    #text(size: 11pt, fill: c-other)[The arguments of The Muslim Lantern and Farid Responds, \ in their own words, taken from the transcripts of their videos, \ edited for reading and arranged by topic]
  ]
]

#page(header: none)[
  #v(8mm)
  #text(size: 16pt, weight: "semibold")[About this book]
  #v(4mm)
  #set par(justify: false, spacing: 1.15em, first-line-indent: 0pt)
  #set text(size: 10.4pt)
  - The book is organized by topic, not by video. Each passage is made of the words of one of the two hosts as spoken in a video, edited for reading by deletion only: fillers, false starts, repetitions, remarks addressed to callers and stream logistics were removed, and where the same point is made in several videos it is given once, in its fullest telling. Punctuation and paragraphs were added. No word was added, changed or reordered, and nothing was summarized. The only exception is a word in square brackets, which replaces a word garbled by the automatic captions (for example a misheard name): "the [fitrah]".
  - The words of callers, guests and people in played clips are not included; passages that consisted only of greetings, announcements or logistics were left out.
  - A small line in capitals (THE MUSLIM LANTERN, FARID RESPONDS) marks whose words follow when the author changes within a section. The footnote at the end of each passage gives the channel and the title of the video it comes from, exactly as published.
  - Shaded boxes headed "Reference text: …" contain the text of a Quran verse (quran.com, Saheeh International translation) or a hadith (sunnah.com) whose reference is cited in the passage just above. They are not the hosts' words.
  - The written articles published by Farid Responds are reproduced as their original pages.
]

#page(header: none)[
  #v(4mm)
  #text(size: 19pt, weight: "semibold")[Contents]
  #v(6mm)
  #show outline.entry.where(level: 1): it => { v(0.7em, weak: true); strong(it) }
  #set text(size: 9.8pt)
  #set par(first-line-indent: 0pt)
  #outline(title: none, depth: 3, indent: auto)
]
