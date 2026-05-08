from pathlib import Path
from core.journal_writer import JournalWriter
from core.models import JournalEntry
from core.secret_injector import SecretInjector


def test_journal_append(tmp_path: Path):
    path = tmp_path / "journal.json"
    w = JournalWriter(path, SecretInjector({"<TOKEN>": "secret"}))
    e = JournalEntry(timestamp="t", iteration=1, claude_request="r", claude_analysis="a", sanitized_responses=[])
    w.append(e)
    assert path.exists()
