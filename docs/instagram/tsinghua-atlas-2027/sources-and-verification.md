# Tsinghua Atlası — kaynak ve doğrulama notları

**Kontrol tarihi:** 10 Ekim 2026 · **Durum:** tasarım sitesi incelemesi için; insan yaratıcı kabulü ve Instagram paylaşımı bekliyor.

## Teyit edilen metinler

| Slayt | Metin / sayı | Birincil kaynak ve nitelendirme |
|---|---|---|
| 01–02 | QS dünya sıralaması #14 (2027) | [QS Tsinghua profile](https://www.topuniversities.com/universities/tsinghua-university). Profile history lists 2026 #17 and 2027 #14. |
| 02 | THE dünya sıralaması #11 (2027) | [THE World University Rankings 2027](https://www.timeshighereducation.com/world-university-rankings/latest/world-ranking). |
| 02 | U.S. News Best Global Universities #6 (2026–2027) | [U.S. News Tsinghua profile](https://www.usnews.com/education/best-global-universities/tsinghua-university-503146); also listed by [Tsinghua Undergraduate Admissions — Advantages](https://international.join-tsinghua.edu.cn/Discover_Tsinghua1/Advantages.htm). |
| 03 | QS 2026 top-10 subject ranks: Environmental Sciences #7; Civil and Structural Engineering #8; Architecture and Built Environment #9; Materials Sciences #9; Data Science and Artificial Intelligence #10; Chemical Engineering #10 | [Tsinghua Undergraduate Admissions — Advantages](https://international.join-tsinghua.edu.cn/Discover_Tsinghua1/Advantages.htm) lists all six together under QS Subject Rankings 2026. These are subject-level world rankings, not degree-program quality guarantees. |
| 04 | 93 undergraduate majors; 45 minors; 12 discipline categories | [Tsinghua Undergraduate Programs Overview](https://international.join-tsinghua.edu.cn/Admission1/Undergraduate_Programs_Overview.htm). Counts describe the university's full catalog, not guaranteed availability to international applicants. |
| 05 | Three fully English-taught program guides for 2027 | [Official English-taught program listing](https://international.join-tsinghua.edu.cn/English_Taught_Programs.htm): Global Talents in Science and Engineering; Urban Regeneration and Design; Politics, Economics and Sociology for Global Leaders in Smart Society. Guide links: [Global Talents](https://international.join-tsinghua.edu.cn/info/1082/1185.htm), [Urban Regeneration and Design](https://international.join-tsinghua.edu.cn/info/1082/1184.htm), [Politics, Economics and Sociology](https://international.join-tsinghua.edu.cn/info/1082/1183.htm). Copy limits the statement to listed programs; it does not imply all Tsinghua undergraduate teaching is in English. |
| 06 | ¥30,000/year for selected Chinese-English-taught programs; ¥100,000/year for Global Talents in Science and Engineering; ¥800 application fee; ¥800/year medical insurance | [Official Fees](https://international.join-tsinghua.edu.cn/Admission1/Fees.htm) and the 2027 [Global Talents admission guide](https://international.join-tsinghua.edu.cn/info/1082/1185.htm). Tuition applies by program; amounts are RMB. |
| 06 | Approximately 45% of international undergraduate freshmen awarded a Tsinghua scholarship in 2026 | [Official Freshmen Scholarships page](https://international.join-tsinghua.edu.cn/Admission1/Freshmen_Scholarships1.htm). One prior cohort's approximate rate; not an individual award probability or guarantee. |
| 07 | First application round closes 20 Nov 2026, 17:00 Beijing time; second closes 28 Feb 2027, 17:00 Beijing time | [Official 2027 Schedule](https://international.join-tsinghua.edu.cn/Admission1/Schedule.htm). First round opens Sep 30; second opens Nov 21. Some programs have round restrictions; the official schedule/program guide controls. |

## Photography and rights

1. **Main building, cover:** Soramimi, “Main building of Tsinghua University 2.JPG,” photographed 30 Aug 2015; [Wikimedia Commons file page](https://commons.wikimedia.org/wiki/File:Main_building_of_Tsinghua_University_2.JPG); [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Crop/gradient overlay applied; photo identifies the real Tsinghua main building. Attribution does not imply endorsement.
2. **Old library, slide 04:** Soramimi, “Old library of Tsinghua University 2.JPG,” photographed 30 Aug 2015; [Wikimedia Commons file page](https://commons.wikimedia.org/wiki/File:Old_library_of_Tsinghua_University_2.JPG); [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Crop applied; photo identifies the real Tsinghua old library. Attribution does not imply endorsement.

No AI-generated image was used. The classroom photograph explored during research was excluded from the final bundle. No implied Tsinghua partnership or endorsement is stated.

## Canonical identity check

- Asya’da Eğitim identity remains **approved seal + approved lockup family only**; no complete `brand-system.md` exists, and this application brief is not a canonical brand-system approval.
- Cover: exact copied `P-01/light` at 390px wide (manifest minimum 352px). Interior slides 02–06: exact copied `D-04/light` at 250px (minimum 200px). Closing: exact copied `D-04/dark` at 250px (minimum 200px). D-04 stays Turkish-only.
- Copied SVG hashes are compared to original manifest-listed canonical SVGs by `verify.mjs`. Seal hash recorded for every branded output: `8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a`.
- Dedicated canonical-lockup verifier passed with the repository-pinned Pillow 12.0.0 under Python 3.12 (`uv run --python 3.12 --with Pillow==12.0.0 python studio/tools/verify_asyada_canonical_lockups.py`): all 15 approved records, source hashes, display minima and production references passed.

## Render and review record

PNG slides are 1080×1350. Editable source is one HTML document per slide in `source/`; render with `node render.mjs` where Chrome and the documented Playwright runtime are available. The outputs were rendered by Chrome through Playwright and inspected as actual PNGs, individually and as a contact sheet. See `quality-review.md` for observations. Rendering uses native SVG placements, local Jost VF, and real, credited campus photographs; no generated raster.
