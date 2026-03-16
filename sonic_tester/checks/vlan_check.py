from sonic_tester import CheckResult

EXPECTED_VLANS = {1, 10, 20}


def run_vlan_check(client) -> CheckResult:
    """Validate that all expected VLANs appear in 'show vlan brief' output."""
    output = client.run_command("show vlan brief")
    found = set()
    for line in output.splitlines():
        parts = line.split("|")
        if len(parts) > 1:
            try:
                found.add(int(parts[1].strip()))
            except ValueError:
                pass

    missing = EXPECTED_VLANS - found
    if missing:
        return CheckResult(
            name="VLAN Check",
            passed=False,
            details=f"Missing VLANs: {sorted(missing)}",
        )
    return CheckResult(
        name="VLAN Check",
        passed=True,
        details=f"All expected VLANs present: {sorted(EXPECTED_VLANS)}",
    )
