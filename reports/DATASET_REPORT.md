# Dataset assessment

This is an engineering data audit, not a clinical evaluation. The measured results
come from [`dataset-audit.json`](dataset-audit.json), generated with:

```powershell
.\.venv\Scripts\python.exe tools\audit_datasets.py --output reports\dataset-audit.json
```

The analyzer uses Python's standard library. It streams text, counts quality
indicators, inventories SHA-256 checksums, and reads only safe file headers for
binary artifacts. It never executes notebooks, loads pickles, or reproduces talk
text. Counts refer to the bundled checkout, not a newly downloaded dataset.
Raw file sizes and checksums depend on checkout line endings: the original files
are tracked as text and a Windows `core.autocrlf=true` checkout changes their bytes.
Cross-platform comparisons should compare aggregate measurements, or first use
identical Git line-ending settings. No source data was rewritten for this audit.

## 1. TED transcripts

| Measurement | Observed |
|---|---:|
| Rows | 2,467 |
| Columns | `transcript`, `url` |
| Empty transcripts | 0 |
| Structurally malformed rows | 0 |
| Invalid HTTP(S) URLs | 0 |
| Repeated normalized transcript rows, beyond first occurrence | 3 |
| Repeated URL rows, beyond first occurrence | 3 |
| Median transcript length | 11,539 characters |
| 95th percentile transcript length | 19,511 characters |
| Maximum transcript length | 51,355 characters |
| Median regex token count | 2,058 |
| Maximum regex token count | 9,176 |
| Rows containing non-ASCII text | 2,262 |

All 2,467 URLs use `www.ted.com`. That does **not** establish copyright clearance,
the exact upstream dataset version, consent, language distribution, or child
suitability. Non-ASCII text is not an error or a language label.

**What this supports:** research into general written language after provenance
and licensing are verified.

**What this does not support:** autism diagnosis, child speech recognition,
pronunciation scoring, articulation assessment, treatment selection, or claims
that an exercise improves communication. The CSV has no child audio, age,
diagnosis, clinical outcome, or consent columns. Adult talks are not a curated
starter vocabulary for children.

**If reused for research:** remove exact/normalized duplicates before splitting;
group by speaker and talk identity using verified external metadata to prevent
leakage; review content and rights; document language and population coverage.
The present CSV alone cannot establish speaker-disjoint evaluation.

## 2. Phonetic vector candidate

| Measurement | Observed |
|---|---:|
| Vector rows / unique byte labels | 133,859 / 133,859 |
| Dimensions per valid row | 50 |
| Repeated exact byte labels | 0 |
| Alternate-pronunciation-shaped labels, e.g. suffix `(2)` | 8,779 |
| Malformed numeric rows | 0 |
| Rows containing non-finite values | 0 |
| Zero vectors | 0 |
| Minimum / maximum vector norm | 3.718455 / 12.651953 |
| Lines not valid UTF-8 | 1 |

The first attempted UTF-8 text read failed. The final analyzer intentionally
compares labels as raw bytes and records invalid UTF-8 rather than silently
repairing or discarding labels. The single invalid line requires provenance and
encoding investigation before downstream text processing.

The filename suggests a CMU-derived vocabulary, but is **not proof** of the
upstream release, license chain, or vector construction method. Alternate
pronunciations are vocabulary variants, not separate people or recordings.
Vectors must not be treated as therapeutic difficulty labels. No ground-truth
child outcomes are supplied.

## 3. Serialized and binary artifacts

| Artifact | Inspection | Finding / restriction |
|---|---|---|
| `data/phonetic_embd.pickle` | Hash and file size only | Executable serialization; not deserialized |
| `data/word_embeddings/glove.wikipedia.bin` | Hash, size, bounded ASCII header | Header declares 50,000 entries, 300 dimensions; payload not validated |
| `notebook/TED_transcript_tokens.npy` | NumPy header only | Shape `(2467,)`, object dtype `\|O`; payload may contain pickle objects |
| `notebook/res.pickle`, `res2.pickle` | Hash and file size only | Unknown serialized research outputs; not deserialized |
| `data/default_content.txt` | Hash and file size only | Original writing sample; not used as child-facing content |

Filenames and plausible headers are not authenticity, safety, or license checks.
The manifest documents what is known and what is missing. No new redistribution
rights are asserted. These files remain in Git history and the checkout for
research continuity, but are not served over HTTP or loaded by the application.

## 4. Child-facing content

The runtime uses **24 original communication cards and 18 original optional
activities**, in `communication/content/`. Activities cover choices, needs,
self-advocacy, feelings, connection, and optional word play. They accept speech,
AAC, gesture/sign, listening, mixed participation, or skipping.

This is a transparent starter set, **not a clinical dataset or validated treatment
protocol**. Content is English-only and may not suit a child's language, motor
access, comprehension, sensory needs, or existing AAC vocabulary. Line drawings
and labels require individual comprehension checks. The library has not been
reviewed by a speech-language professional or tested with autistic children.

## 5. Research and evaluation required before clinical claims

1. Co-design the vocabulary, interaction patterns, and access methods with autistic
   people, caregivers, and qualified speech-language professionals. Include
   nonspeaking people and people with different motor and sensory access needs.
2. Obtain documented permissions, safeguarding review, informed caregiver consent,
   and developmentally appropriate assent before collecting any child data.
   Respect withdrawal and provide meaningful deletion and retention policies.
3. If speech modeling is introduced, collect only the data required for a defined
   task. Document languages, dialects, ages, recording conditions, and relevant
   access needs without unnecessary sensitive labels.
4. Split by participant, household, and recording session before model fitting.
   Keep preprocessing and tuning separate from the held-out evaluation.
5. Evaluate the actual task with suitable metrics and subgroup uncertainty.
   Recognition error is not a measure of intelligence, communication value,
   disability severity, or therapeutic progress.
6. Agree on meaningful outcomes with participants and clinicians. Observation
   counts, app use, and task completion alone do not demonstrate clinical benefit.
7. Complete independent accessibility and privacy assessments, usability work
   with intended users, and jurisdiction-specific legal/regulatory review before
   any public or clinical deployment.

No additional speech dataset was downloaded, no model was trained, and no
accuracy or effectiveness claim is made by this upgrade.
