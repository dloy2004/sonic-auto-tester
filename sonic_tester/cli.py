import argparse
import sys

from sonic_tester.checks import (
    run_bgp_check,
    run_interface_check,
    run_routing_check,
    run_vlan_check,
)
from sonic_tester.reporter import generate_report


def _parse_args():
    parser = argparse.ArgumentParser(
        description="SONiC Auto Tester — network switch health checks"
    )
    parser.add_argument("--mock", action="store_true", help="Use mock switch instead of real SSH")
    parser.add_argument("--ci-mode", action="store_true", help="Exit with code 1 if any check fails")
    parser.add_argument("--host", help="Switch IP or hostname")
    parser.add_argument("--user", help="SSH username")
    parser.add_argument("--password", help="SSH password")
    parser.add_argument("--port", type=int, default=22, help="SSH port (default: 22)")
    return parser.parse_args()


def _get_client(args):
    if args.mock:
        from mock_switch import MockSwitch
        return MockSwitch()
    if not all([args.host, args.user, args.password]):
        print("ERROR: --host, --user, and --password are required without --mock")
        sys.exit(1)
    from sonic_tester.ssh_client import SSHClient
    client = SSHClient(args.host, args.user, args.password, args.port)
    client.connect()
    return client


def main():
    args = _parse_args()
    client = _get_client(args)

    checks = [run_vlan_check, run_interface_check, run_routing_check, run_bgp_check]
    results = []

    for check in checks:
        result = check(client)
        status = "PASS" if result.passed else "FAIL"
        print(f"[{status}] {result.name}: {result.details}")
        results.append(result)

    if hasattr(client, "close"):
        client.close()

    generate_report(results)

    if args.ci_mode and any(not r.passed for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
