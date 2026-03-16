import json
import os
from datetime import datetime

from jinja2 import Template

from sonic_tester import CheckResult

REPORT_DIR = "reports"

_HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>SONiC Auto Tester Report</title>
  <style>
    body { font-family: monospace; padding: 2rem; background: #1a1a1a; color: #eee; }
    h1 { color: #00c8ff; }
    .pass { color: #00ff88; }
    .fail { color: #ff4444; }
    table { border-collapse: collapse; width: 100%; margin-top: 1rem; }
    th, td { text-align: left; padding: 8px 12px; border: 1px solid #333; }
    th { background: #333; }
    tr:nth-child(even) { background: #222; }
    .summary { margin-top: 1rem; font-size: 1.1em; }
  </style>
</head>
<body>
  <h1>SONiC Auto Tester Report</h1>
  <p>Generated: {{ timestamp }}</p>
  <div class="summary">
    Total: {{ results|length }} |
    <span class="pass">Passed: {{ results|selectattr("passed")|list|length }}</span> |
    <span class="fail">Failed: {{ results|rejectattr("passed")|list|length }}</span>
  </div>
  <table>
    <tr><th>Check</th><th>Status</th><th>Details</th></tr>
    {% for r in results %}
    <tr>
      <td>{{ r.name }}</td>
      <td class="{{ 'pass' if r.passed else 'fail' }}">{{ 'PASS' if r.passed else 'FAIL' }}</td>
      <td>{{ r.details }}</td>
    </tr>
    {% endfor %}
  </table>
</body>
</html>
"""


def generate_report(results: list[CheckResult]) -> None:
    """Write report.html and report.json to the reports/ directory."""
    os.makedirs(REPORT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    data = {
        "timestamp": timestamp,
        "results": [
            {"name": r.name, "passed": r.passed, "details": r.details}
            for r in results
        ],
    }
    json_path = os.path.join(REPORT_DIR, "report.json")
    with open(json_path, "w") as f:
        json.dump(data, f, indent=2)

    html = Template(_HTML_TEMPLATE).render(results=results, timestamp=timestamp)
    html_path = os.path.join(REPORT_DIR, "report.html")
    with open(html_path, "w") as f:
        f.write(html)

    print(f"Reports saved to {REPORT_DIR}/")
