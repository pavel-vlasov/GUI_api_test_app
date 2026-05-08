"""HTML report generation from session journal."""
from __future__ import annotations

from pathlib import Path
import json

from jinja2 import Template


REPORT_TEMPLATE = """
<!doctype html><html><head><meta charset='utf-8'><title>API Test Report</title>
<script src='https://cdn.jsdelivr.net/npm/chart.js'></script></head><body>
<h1>Autonomous API Test Dashboard</h1>
<div><b>Total tests:</b> {{ summary.total_tests }} | <b>Error rate:</b> {{ summary.error_rate }}% | <b>Total exec ms:</b> {{ summary.total_exec_ms }}</div>
<canvas id='chart'></canvas>
<h2>Iteration Timeline</h2>
{% for e in entries %}<details><summary>Iteration {{e.iteration}} - {{e.timestamp}}</summary><pre>{{e.sanitized_responses | tojson(indent=2)}}</pre></details>{% endfor %}
<script>new Chart(document.getElementById('chart'),{type:'bar',data:{labels:{{labels|safe}},datasets:[{label:'errors',data:{{errors|safe}}}]}});</script>
</body></html>
"""


class ReportGenerator:
    """Generate interactive report.html from session journal."""

    def generate(self, journal_path: Path, report_path: Path) -> None:
        """Render HTML dashboard and write to target path."""

        entries = json.loads(journal_path.read_text(encoding="utf-8")) if journal_path.exists() else []
        total_tests = sum(len(e.get("sanitized_responses", [])) for e in entries)
        total_errors = sum(1 for e in entries for r in e.get("sanitized_responses", []) if r.get("status_code", 0) >= 400)
        total_exec_ms = sum(r.get("elapsed_ms", 0) for e in entries for r in e.get("sanitized_responses", []))
        labels = [str(e.get("iteration")) for e in entries]
        errors = [sum(1 for r in e.get("sanitized_responses", []) if r.get("status_code", 0) >= 400) for e in entries]
        summary = {"total_tests": total_tests, "error_rate": round((total_errors / total_tests * 100), 2) if total_tests else 0, "total_exec_ms": total_exec_ms}
        html = Template(REPORT_TEMPLATE).render(entries=entries, summary=summary, labels=labels, errors=errors)
        report_path.write_text(html, encoding="utf-8")
