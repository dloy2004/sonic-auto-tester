# sonic-auto-tester

A Python CLI framework for automated health-checking of SONiC Network OS switches.
Connects over SSH, runs a suite of network checks, and produces HTML + JSON reports — with CI-friendly exit codes.

```
$ python -m sonic_tester.cli --mock

[PASS] VLAN Check: All expected VLANs present: [1, 10, 20]
[PASS] Interface Check: All monitored interfaces are up
[PASS] Routing Check: All expected routes present
[PASS] BGP Check: All 2 BGP neighbors Established
Reports saved to reports/
```

---

## Why This Exists

Network OS validation is typically manual and error-prone. This framework automates the process:
run it in CI after a config change, point it at a real switch, or use the built-in mock to develop and test offline.

---

## Architecture

```
sonic-auto-tester/
├── sonic_tester/
│   ├── cli.py              # Entry point — argparse, orchestration
│   ├── ssh_client.py       # Paramiko SSH wrapper
│   ├── reporter.py         # HTML + JSON report generator (Jinja2)
│   └── checks/
│       ├── vlan_check.py       # Validates expected VLANs via 'show vlan brief'
│       ├── interface_check.py  # Checks port Oper state via 'show interface status'
│       ├── routing_check.py    # Verifies routes via 'show ip route'
│       └── bgp_check.py        # Checks BGP session state via 'show bgp summary'
├── mock_switch.py          # Simulates SSH responses — no hardware needed
├── tests/
│   └── test_checks.py      # pytest suite, fully offline
└── requirements.txt
```

Each check returns a `CheckResult(name, passed, details)` dataclass. The reporter consumes the list and writes `reports/report.html` and `reports/report.json`.

---

## Installation

```bash
git clone https://github.com/dloy2004/sonic-auto-tester.git
cd sonic-auto-tester
pip install -r requirements.txt
```

**Requirements:** Python 3.11+ · paramiko · jinja2 · pytest

---

## Usage

### Run locally with mock switch (no hardware required)

```bash
python -m sonic_tester.cli --mock
```

### Run against a real switch

```bash
python -m sonic_tester.cli --host 10.0.0.1 --user admin --password secret
```

### CI mode — exits with code 1 if any check fails

```bash
python -m sonic_tester.cli --mock --ci-mode
echo $?   # 0 = all passed, 1 = one or more failed
```

---

## Sample Report

The reporter generates two files in `reports/`:

**`report.json`**
```json
{
  "timestamp": "2026-03-17 12:00:00",
  "results": [
    { "name": "VLAN Check",      "passed": true,  "details": "All expected VLANs present: [1, 10, 20]" },
    { "name": "Interface Check", "passed": true,  "details": "All monitored interfaces are up" },
    { "name": "Routing Check",   "passed": true,  "details": "All expected routes present" },
    { "name": "BGP Check",       "passed": true,  "details": "All 2 BGP neighbors Established" }
  ]
}
```

**`report.html`** — a dark-themed, human-readable summary table with pass/fail coloring.

---

## Running Tests

```bash
pytest tests/ -v
```

All tests run fully offline using `MockClient` — no switch or SSH connection needed.

```
tests/test_checks.py::test_vlan_check_passes               PASSED
tests/test_checks.py::test_vlan_check_fails_missing_vlans  PASSED
tests/test_checks.py::test_interface_check_passes          PASSED
tests/test_checks.py::test_interface_check_fails_when_down PASSED
tests/test_checks.py::test_routing_check_passes            PASSED
tests/test_checks.py::test_routing_check_fails_missing_route PASSED
tests/test_checks.py::test_bgp_check_passes                PASSED
tests/test_checks.py::test_bgp_check_fails_not_established PASSED
tests/test_checks.py::test_bgp_check_fails_no_neighbors    PASSED
```

---

## CI Integration

Add to `.github/workflows/ci.yml`:

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v
      - run: python -m sonic_tester.cli --mock --ci-mode
```

---

## Extending the Framework

Adding a new check takes three steps:

1. Create `sonic_tester/checks/my_check.py` returning a `CheckResult`
2. Add a matching response in `mock_switch.py`
3. Export it from `sonic_tester/checks/__init__.py` and add it to the `checks` list in `cli.py`

---

## Tech Stack

| Layer | Tool |
|---|---|
| SSH transport | [Paramiko](https://www.paramiko.org/) |
| Report templating | [Jinja2](https://jinja.palletsprojects.com/) |
| Testing | [pytest](https://pytest.org/) |
| CLI | argparse (stdlib) |