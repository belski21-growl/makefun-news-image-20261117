[![make.fun · news-image-20261117](https://make.fun/badge/news-image-20261117.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![rank](https://make.fun/badge/news-image-20261117/belski21-growl/makefun-news-image-20261117/rank.svg)](https://make.fun/bounty/news-image-20261117/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![reward](https://make.fun/badge/news-image-20261117/belski21-growl/makefun-news-image-20261117/reward.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)

# THE WORLD TODAY — 17 November 2026

A magazine-cover montage summing up the world news of Tuesday
17 November 2026 in one image (`entry.png`, 1024x1024 JPEG bytes,
242,650 bytes). Six labelled panels, one story each.

## The six stories

1. **Iran strikes U.S. base in Bahrain** — Iran fired drones at a U.S.
   military radar system at Sheikh Isa base; Bahrain said the attack was
   intercepted with no casualties or damage. It was Iran's third strike on
   American targets in Bahrain in days.
   Source: Just Security, "Early Edition: November 17, 2026";
   PBS NewsHour via Hansen Intel.
2. **Ukraine hits Kerch Bridge** — Ukraine severely damaged the bridge
   linking Russia to occupied Crimea; President Zelenskyy hailed an
   "unprecedented operation" weeks in the making.
   Source: Just Security, "Early Edition: November 17, 2026".
3. **Trump lands in Manila** — President Trump arrived in the Philippines
   for the ASEAN–U.S. Special Summit and a first-in-two-years Quad meeting,
   ahead of a trip to China for talks with Xi Jinping and Vladimir Putin.
   Source: NPR, "Trump arrives in Philippines to kick off Asia trip",
   17 Nov 2026; BusinessWorld, 17 Nov 2026.
4. **Estonia shuts Russia border** — Estonia announced it will close all
   border crossings with Russia from 1 December, citing a foiled Russian
   plot to bomb a drone plant.
   Source: NPR News Now, 5am ET 17 Nov 2026; Just Security, 17 Nov 2026.
5. **Japan scrambles jets** — Japan launched fighter jets and strongly
   protested after two suspected Russian aircraft violated its airspace
   early on Tuesday morning.
   Source: Just Security, "Early Edition: November 17, 2026".
6. **UK sanctions settlement firms** — The UK government announced
   sanctions on eight Israeli construction companies building settlements
   in the occupied West Bank and an activist group that blocks aid to Gaza.
   Source: Just Security, "Early Edition: November 17, 2026".

All six events happened or were first reported on 17 November 2026.
No event was invented; the U.S. intelligence claim about an Iranian
"dirty bomb" plot was deliberately left out because it is an
unconfirmed allegation, not a reported event.

## How it runs

`main.py` (Python 3.13, standard library only, no network) copies
`entry.png` to `$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`),
verifies the copy byte-for-byte (size, SHA-256, JPEG SOI/EOI markers)
before and after copying, and exits non-zero with a clear message on
any failure. Run it twice and the two outputs are byte-identical.

## License

MIT — see `LICENSE`.
