"""Read-only aggregate inspection. Never unpickle or print transcript contents."""

import argparse
import ast
import csv
import hashlib
import json
import math
import re
import statistics
import struct
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse


def fingerprint(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return {"bytes": path.stat().st_size, "sha256": digest.hexdigest()}


def distribution(values):
    if not values:
        return {"min": None, "median": None, "p95": None, "max": None}
    ordered = sorted(values)
    return {"min": ordered[0], "median": statistics.median(ordered),
            "p95": ordered[max(0, math.ceil(len(ordered) * .95) - 1)], "max": ordered[-1]}


def audit_transcripts(path):
    lengths, token_counts = [], []
    hashes, urls, domains = Counter(), Counter(), Counter()
    empty = malformed = invalid_urls = non_ascii = 0
    csv.field_size_limit(10_000_000)
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not {"transcript", "url"}.issubset(reader.fieldnames):
            raise ValueError("Transcript CSV must have transcript and url columns.")
        columns = reader.fieldnames
        for row in reader:
            if None in row or any(row.get(key) is None for key in columns):
                malformed += 1
            transcript = row.get("transcript") or ""
            url = (row.get("url") or "").strip()
            lengths.append(len(transcript))
            token_counts.append(len(re.findall(r"\b[\w']+\b", transcript)))
            empty += not bool(transcript.strip())
            non_ascii += not transcript.isascii()
            normalized = re.sub(r"\s+", " ", transcript).strip().casefold()
            hashes[hashlib.sha256(normalized.encode("utf-8")).hexdigest()] += 1
            urls[url] += 1
            parsed = urlparse(url)
            if parsed.scheme not in {"http", "https"} or not parsed.hostname:
                invalid_urls += 1
            else:
                domains[parsed.hostname] += 1
    return {
        "columns": columns, "rows": len(lengths), "empty_transcripts": empty,
        "malformed_rows": malformed, "invalid_urls": invalid_urls,
        "duplicate_normalized_transcript_rows": sum(count - 1 for count in hashes.values()),
        "duplicate_url_rows": sum(count - 1 for count in urls.values()),
        "rows_with_non_ascii": non_ascii,
        "characters": distribution(lengths), "regex_tokens": distribution(token_counts),
        "url_domains": dict(sorted(domains.items())),
        "limitations": ["Regex tokens are not linguistic or clinical annotations.",
                        "No age, diagnosis, consent, speaker-group, audio, or outcome columns are provided.",
                        "Non-ASCII text does not establish language or quality.",
                        "No content-safety or reading-level certification was performed."],
    }


def audit_vectors(path):
    dimensions, words = Counter(), Counter()
    malformed = nonfinite = zero = alternate = rows = invalid_utf8 = 0
    norm_min, norm_max = math.inf, 0
    with path.open("rb") as handle:
        for line in handle:
            rows += 1
            try:
                line.decode("utf-8")
            except UnicodeDecodeError:
                invalid_utf8 += 1
            parts = line.split()
            if len(parts) < 2:
                malformed += 1
                continue
            word, *raw = parts
            words[word] += 1
            alternate += bool(re.search(rb"\(\d+\)$", word))
            try:
                vector = [float(value) for value in raw]
            except ValueError:
                malformed += 1
                continue
            dimensions[len(vector)] += 1
            if not all(math.isfinite(value) for value in vector):
                nonfinite += 1
                continue
            length = math.sqrt(sum(value * value for value in vector))
            zero += length == 0
            norm_min, norm_max = min(norm_min, length), max(norm_max, length)
    return {"rows": rows, "unique_labels": len(words),
            "duplicate_label_rows": sum(count - 1 for count in words.values()),
            "alternate_pronunciation_labels": alternate,
            "dimensions": dict(sorted(dimensions.items())), "malformed_rows": malformed,
            "nonfinite_rows": nonfinite, "zero_vectors": zero, "invalid_utf8_lines": invalid_utf8,
            "norm_min": None if norm_min == math.inf else round(norm_min, 6),
            "norm_max": round(norm_max, 6),
            "limitations": ["Numeric vectors, not child speech audio or therapeutic labels.",
                            "Filename alone does not establish upstream provenance, license, or embedding methodology.",
                            "Labels are compared as raw bytes; invalid UTF-8 is counted, not silently repaired."]}


def inspect_npy_header(path):
    with path.open("rb") as handle:
        if handle.read(6) != b"\x93NUMPY":
            raise ValueError("Invalid NumPy magic header.")
        version = tuple(handle.read(2))
        if version not in {(1, 0), (2, 0), (3, 0)}:
            raise ValueError(f"Unsupported NumPy version: {version}")
        size_format = "<H" if version == (1, 0) else "<I"
        header_length = struct.unpack(size_format, handle.read(struct.calcsize(size_format)))[0]
        if header_length > 65536:
            raise ValueError("NumPy header exceeds safe inspection limit.")
        header = ast.literal_eval(handle.read(header_length).decode("utf-8" if version == (3, 0) else "latin1").strip())
    return {"format_version": list(version), "dtype": header["descr"], "shape": list(header["shape"]),
            "fortran_order": header["fortran_order"], "payload_loaded": False,
            "warning": "Object arrays may contain pickle payloads. Header only; never loaded."}


def audit_repository(data_dir, notebook_dir=None):
    data_dir = Path(data_dir)
    report = {"schema_version": 1, "runtime_uses_legacy_data": False,
              "method": "Read-only streaming aggregate inspection; SHA-256 inventory; no unpickling or model execution.",
              "datasets": {}, "artifacts": {}}
    transcript = data_dir / "TED_transcripts.csv"
    vectors = data_dir / "cmudict-0.7b-simvecs"
    if transcript.exists():
        report["datasets"]["TED_transcripts.csv"] = {**fingerprint(transcript), **audit_transcripts(transcript)}
    if vectors.exists():
        report["datasets"]["cmudict-0.7b-simvecs"] = {**fingerprint(vectors), **audit_vectors(vectors)}
    for path in sorted(data_dir.rglob("*")):
        if not path.is_file() or path in {transcript, vectors}:
            continue
        entry = fingerprint(path)
        if path.suffix == ".pickle":
            entry.update(format="Python pickle (identified by extension)", payload_loaded=False,
                         warning="Executable serialization; provenance and contents not verified.")
        elif path.suffix == ".bin":
            with path.open("rb") as handle:
                header = handle.readline(128).strip()
            match = re.fullmatch(rb"(\d+) (\d+)", header)
            entry.update(format="binary embedding candidate", payload_loaded=False)
            if match:
                entry["declared_vocabulary"] = int(match[1])
                entry["declared_dimensions"] = int(match[2])
                entry["warning"] = "Header declarations only; binary rows and finiteness not verified."
        else:
            entry["payload_loaded"] = False
        report["artifacts"][str(path.relative_to(data_dir)).replace("\\", "/")] = entry
    if notebook_dir and Path(notebook_dir).is_dir():
        for path in sorted(Path(notebook_dir).iterdir()):
            if path.suffix not in {".pickle", ".npy"}:
                continue
            entry = {**fingerprint(path), "payload_loaded": False}
            if path.suffix == ".npy":
                entry.update(inspect_npy_header(path))
            else:
                entry["warning"] = "Legacy executable serialization; not unpickled."
            report["artifacts"][f"notebook/{path.name}"] = entry
    return report


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=root / "data")
    parser.add_argument("--notebook-dir", type=Path, default=root / "notebook")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.data_dir.is_dir():
        parser.error("Data directory does not exist.")
    if args.output.resolve().is_relative_to(args.data_dir.resolve()) or args.output.resolve().is_relative_to(args.notebook_dir.resolve()):
        parser.error("Write reports outside the source data and notebook directories.")
    report = audit_repository(args.data_dir, args.notebook_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Aggregate audit written to {args.output}")


if __name__ == "__main__":
    main()
