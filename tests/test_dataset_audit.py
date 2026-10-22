import csv
import struct

from tools.audit_datasets import audit_repository, audit_transcripts, audit_vectors, inspect_npy_header


def test_transcript_duplicates_missing_data_and_percentiles(tmp_path):
    path = tmp_path / "sample.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["transcript", "url"])
        writer.writerows([["Hello world", "https://example.com/a"], [" hello   WORLD ", "https://example.com/a"], ["", "bad-url"]])
    result = audit_transcripts(path)
    assert result["rows"] == 3
    assert result["duplicate_normalized_transcript_rows"] == 1
    assert result["duplicate_url_rows"] == 1
    assert result["empty_transcripts"] == 1
    assert result["invalid_urls"] == 1
    assert result["regex_tokens"]["p95"] == 2


def test_vector_quality_and_raw_byte_encoding(tmp_path):
    path = tmp_path / "vectors"
    path.write_bytes(b"A 1 0\nA 0 0\nA(2) nan 1\nB broken\nC 1 2 3\n\xc9 1 2\n")
    result = audit_vectors(path)
    assert result["duplicate_label_rows"] == 1
    assert result["alternate_pronunciation_labels"] == 1
    assert result["zero_vectors"] == 1
    assert result["nonfinite_rows"] == 1
    assert result["malformed_rows"] == 1
    assert result["invalid_utf8_lines"] == 1
    assert result["dimensions"][3] == 1


def test_binary_artifacts_are_only_fingerprinted(tmp_path):
    marker = tmp_path / "must-not-exist"
    # A pickle with an executable payload must never be loaded by the analyzer.
    path = tmp_path / "unsafe.pickle"
    path.write_bytes(f"cos\nsystem\n(S'echo unsafe > {marker}'\ntR.".encode())
    report = audit_repository(tmp_path)
    assert report["artifacts"]["unsafe.pickle"]["payload_loaded"] is False
    assert not marker.exists()
    assert len(report["artifacts"]["unsafe.pickle"]["sha256"]) == 64


def test_npy_header_inspected_without_object_payload(tmp_path):
    path = tmp_path / "objects.npy"
    header = b"{'descr': '|O', 'fortran_order': False, 'shape': (3,), }\n"
    path.write_bytes(b"\x93NUMPY\x01\x00" + struct.pack("<H", len(header)) + header + b"not-safe-to-load")
    result = inspect_npy_header(path)
    assert result["shape"] == [3]
    assert result["dtype"] == "|O"
    assert result["payload_loaded"] is False
