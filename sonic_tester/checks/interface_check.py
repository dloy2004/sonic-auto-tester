from sonic_tester import CheckResult

EXPECTED_UP_INTERFACES = ["Ethernet0", "Ethernet4"]


def run_interface_check(client) -> CheckResult:
    """Check that expected interfaces are operationally up via 'show interface status'."""
    output = client.run_command("show interface status")

    oper_status: dict[str, str] = {}
    for line in output.splitlines():
        cols = line.split()
        if cols and cols[0].startswith("Ethernet") and len(cols) >= 7:
            # Columns: Interface Speed MTU FEC Alias Vlan Oper Admin ...
            oper_status[cols[0]] = cols[6].lower()

    down = [
        iface for iface in EXPECTED_UP_INTERFACES
        if oper_status.get(iface) != "up"
    ]

    if down:
        return CheckResult(
            name="Interface Check",
            passed=False,
            details=f"Interfaces not up: {down}",
        )
    return CheckResult(
        name="Interface Check",
        passed=True,
        details=f"All expected interfaces are up: {EXPECTED_UP_INTERFACES}",
    )
