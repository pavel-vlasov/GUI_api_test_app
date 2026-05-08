from pathlib import Path
from core.request_executor import RequestExecutor


def test_split_headers_body():
    raw = "HTTP/1.1 200 OK\nA: b\n\n{\"ok\":true}"
    headers, body = RequestExecutor._split_headers_body(raw)
    assert headers["A"] == "b"
    assert "ok" in body


def test_execute_batch_smoke(tmp_path: Path):
    out = tmp_path / "results.json"
    ex = RequestExecutor(out)
    rec = ex.execute_batch(1, ["echo 'HTTP/1.1 200 OK\n\nhello'"])
    assert rec.iteration == 1
    assert out.exists()
