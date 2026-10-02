#import "template.typ": *

#page(header: none, footer: none, margin: (x: 25mm, y: 30mm))[
  #v(28%)
  #align(center)[
    #text(size: 30pt, weight: "semibold")[The Muslim Lantern \ and Farid Responds]
    #v(8mm)
    #line(length: 40%, stroke: 0.8pt + c-ref-line)
    #v(6mm)
    #text(size: 17pt, style: "italic", fill: c-other)[A Topical Compilation]
  ]
]

#page(header: none, footer: none, margin: (x: 25mm, y: 30mm))[
  #v(20%)
  #align(center)[
    #text(size: 22pt, weight: "semibold")[The Muslim Lantern and Farid Responds]
    #v(4mm)
    #text(size: 14pt, style: "italic")[A Topical Compilation]
    #v(14mm)
    #text(size: 11pt, fill: c-other)[The words of The Muslim Lantern and Farid Responds, \ compiled verbatim from the transcripts of their videos \ and arranged by topic]
  ]
]

#page(header: none)[
  #v(8mm)
  #text(size: 16pt, weight: "semibold")[How to read this book]
  #v(4mm)
  #set par(justify: false, spacing: 1.15em)
  #set text(size: 10.4pt)
  - The book is organized by topic, not by video. Every passage reproduces the speakers' words verbatim from the transcripts of the videos; only timestamps and caption noise were removed and line breaks were normalized into paragraphs.
  - Bold labels (*The Muslim Lantern:*, *Farid Responds:*) mark the words of the two hosts.
  - Indented passages in italic with a bar on the left are the words of other participants (labeled *Guest:*, or with the person's name when it is given in the video) or of people in clips played during a video (labeled *Clip:*). They are included only where they are needed to understand the host's words. A grey #text(fill: c-src)[\[…\]] at their start means that only the final part of that speech is shown.
  - The small line "Source: …" under each passage gives the channel and the title of the video, exactly as published.
  - Shaded boxes headed "Reference text: …" contain the text of a Quran verse (quran.com, Saheeh International translation), a hadith (sunnah.com) or a passage of a classical book (shamela.ws) whose reference is cited in the passage just above. They are not the speakers' words.
]

#page(header: none)[
  #v(4mm)
  #text(size: 19pt, weight: "semibold")[Contents]
  #v(6mm)
  #show outline.entry.where(level: 1): it => { v(0.7em, weak: true); strong(it) }
  #set text(size: 9.8pt)
  #outline(title: none, depth: 3, indent: auto)
]
