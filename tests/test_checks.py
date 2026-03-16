"""Offline pytest suite — all checks tested with mock output, no real switch needed."""
import pytest

from sonic_tester import CheckResult
from sonic_tester.checks.bgp_check import run_bgp_check
from sonic_tester.checks.interface_check import run_interface_check
from sonic_tester.checks.routing_check import run_routing_check
from sonic_tester.checks.vlan_check import run_vlan_check


class MockClient:
    def __init__(self, outputs: dict):
        self._outputs = outputs

    def run_command(self, command: str) -> str:
        return self._outputs.get(command, "")


# ---------------------------------------------------------------------------
# VLAN Check
# ---------------------------------------------------------------------------

VLAN_PASS = """\
+-----------+--------------+------------+
|   VLAN ID | IP Address   | Ports      |
+===========+==============+============+
|         1 | N/A          |            |
+-----------+--------------+------------+
|        10 | N/A          | Ethernet0  |
+-----------+--------------+------------+
|        20 | N/A          | Ethernet4  |
+-----------+--------------+------------+
"""

VLAN_FAIL = """\
+-----------+--------------+------------+
|   VLAN ID | IP Address   | Ports      |
+===========+==============+============+
|         1 | N/A          |            |
+-----------+--------------+------------+
"""


def test_vlan_check_passes():
    result = run_vlan_check(MockClient({"show vlan brief": VLAN_PASS}))
    assert isinstance(result, CheckResult)
    assert result.name == "VLAN Check"
    assert result.passed is True


def test_vlan_check_fails_missing_vlans():
    result = run_vlan_check(MockClient({"show vlan brief": VLAN_FAIL}))
    assert result.passed is False
    assert "10" in result.details or "20" in result.details


# ---------------------------------------------------------------------------
# Interface Check
# ---------------------------------------------------------------------------

IFACE_PASS = """\
  Interface    Speed    MTU    FEC    Alias         Vlan    Oper    Admin
-----------  -------  -----  -----  ------------  ------  ------  -------
  Ethernet0     100G   9100    N/A  hundredGigE1  trunk      up       up
  Ethernet4     100G   9100    N/A  hundredGigE2  trunk      up       up
"""

IFACE_FAIL = """\
  Interface    Speed    MTU    FEC    Alias         Vlan    Oper    Admin
-----------  -------  -----  -----  ------------  ------  ------  -------
  Ethernet0     100G   9100    N/A  hundredGigE1  trunk    down     down
  Ethernet4     100G   9100    N/A  hundredGigE2  trunk      up       up
"""


def test_interface_check_passes():
    result = run_interface_check(MockClient({"show interface status": IFACE_PASS}))
    assert isinstance(result, CheckResult)
    assert result.name == "Interface Check"
    assert result.passed is True


def test_interface_check_fails_when_down():
    result = run_interface_check(MockClient({"show interface status": IFACE_FAIL}))
    assert result.passed is False
    assert "Ethernet0" in result.details


# ---------------------------------------------------------------------------
# Routing Check
# ---------------------------------------------------------------------------

ROUTE_PASS = """\
B>* 10.0.0.0/8 [20/0] via 192.168.1.1, Ethernet0, 00:01:00
C>* 192.168.1.0/24 is directly connected, Ethernet0
"""

ROUTE_FAIL = """\
C>* 192.168.1.0/24 is directly connected, Ethernet0
"""


def test_routing_check_passes():
    result = run_routing_check(MockClient({"show ip route": ROUTE_PASS}))
    assert isinstance(result, CheckResult)
    assert result.name == "Routing Check"
    assert result.passed is True


def test_routing_check_fails_missing_route():
    result = run_routing_check(MockClient({"show ip route": ROUTE_FAIL}))
    assert result.passed is False
    assert "10.0.0.0/8" in result.details


# ---------------------------------------------------------------------------
# BGP Check
# ---------------------------------------------------------------------------

BGP_PASS = """\
Neighbor        V         AS   MsgRcvd   MsgSent   TblVer  InQ OutQ  Up/Down State/PfxRcd   PfxSnt Desc
192.168.1.2     4      65002       150       145       10    0    0 01:00:00 Established         5     10 N/A
192.168.1.3     4      65003       130       125       10    0    0 00:30:00 Established         3      8 N/A
"""

BGP_FAIL = """\
Neighbor        V         AS   MsgRcvd   MsgSent   TblVer  InQ OutQ  Up/Down State/PfxRcd   PfxSnt Desc
192.168.1.2     4      65002       150       145       10    0    0 01:00:00 Established         5     10 N/A
192.168.1.3     4      65003         0         0        0    0    0    never Active              0      0 N/A
"""

BGP_EMPTY = """\
IPv4 Unicast Summary:
No BGP neighbors configured.
"""


def test_bgp_check_passes():
    result = run_bgp_check(MockClient({"show bgp summary": BGP_PASS}))
    assert isinstance(result, CheckResult)
    assert result.name == "BGP Check"
    assert result.passed is True


def test_bgp_check_fails_not_established():
    result = run_bgp_check(MockClient({"show bgp summary": BGP_FAIL}))
    assert result.passed is False
    assert "192.168.1.3" in result.details


def test_bgp_check_fails_no_neighbors():
    result = run_bgp_check(MockClient({"show bgp summary": BGP_EMPTY}))
    assert result.passed is False
    assert "No BGP neighbors" in result.details
