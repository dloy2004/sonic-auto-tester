from sonic_tester import CheckResult


def _is_ipv4(token: str) -> bool:
    parts = token.split(".")
    return len(parts) == 4 and all(p.isdigit() for p in parts)


def run_bgp_check(client) -> CheckResult:
    """Check that all BGP neighbors are Established via 'show bgp summary'."""
    output = client.run_command("show bgp summary")

    neighbors: list[str] = []
    not_established: list[str] = []

    for line in output.splitlines():
        cols = line.split()
        if not cols or not _is_ipv4(cols[0]):
            continue
        neighbors.append(cols[0])
        # Columns: Neighbor V AS MsgRcvd MsgSent TblVer InQ OutQ Up/Down State/PfxRcd ...
        if len(cols) < 10 or cols[9].lower() != "established":
            not_established.append(cols[0])

    if not neighbors:
        return CheckResult(
            name="BGP Check",
            passed=False,
            details="No BGP neighbors found",
        )
    if not_established:
        return CheckResult(
            name="BGP Check",
            passed=False,
            details=f"BGP neighbors not established: {not_established}",
        )
    return CheckResult(
        name="BGP Check",
        passed=True,
        details=f"All {len(neighbors)} BGP neighbors established: {neighbors}",
    )
