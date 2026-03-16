from sonic_tester import CheckResult

EXPECTED_PREFIXES = ["10.0.0.0/8", "192.168.1.0/24"]


def run_routing_check(client) -> CheckResult:
    """Validate that expected prefixes are present in 'show ip route' output."""
    output = client.run_command("show ip route")

    missing = [prefix for prefix in EXPECTED_PREFIXES if prefix not in output]

    if missing:
        return CheckResult(
            name="Routing Check",
            passed=False,
            details=f"Missing routes: {missing}",
        )
    return CheckResult(
        name="Routing Check",
        passed=True,
        details=f"All expected routes present: {EXPECTED_PREFIXES}",
    )
