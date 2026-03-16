"""Simulates SSH responses for SONiC switch commands — no real switch required."""

MOCK_OUTPUTS = {
    "show vlan brief": """\
+-----------+--------------+------------+----------------+-------------+-----------------------+
|   VLAN ID | IP Address   | Ports      | Port Tagging   | DHCP Helper | Proxy ARP Enabled     |
+===========+==============+============+================+=============+=======================+
|         1 | N/A          |            | N/A            | N/A         | Disabled              |
+-----------+--------------+------------+----------------+-------------+-----------------------+
|        10 | N/A          | Ethernet0  | tagged         | N/A         | Disabled              |
+-----------+--------------+------------+----------------+-------------+-----------------------+
|        20 | N/A          | Ethernet4  | tagged         | N/A         | Disabled              |
+-----------+--------------+------------+----------------+-------------+-----------------------+
""",
    "show interface status": """\
  Interface    Speed    MTU    FEC    Alias         Vlan    Oper    Admin    Type    Asym PFC
-----------  -------  -----  -----  ------------  ------  ------  -------  ------  ----------
  Ethernet0     100G   9100    N/A  hundredGigE1  trunk      up       up     N/A      off
  Ethernet4     100G   9100    N/A  hundredGigE2  trunk      up       up     N/A      off
  Ethernet8     100G   9100    N/A  hundredGigE3  routed   down     down    N/A      off
""",
    "show ip route": """\
Codes: K - kernel route, C - connected, S - static, R - RIP,
       O - OSPF, I - IS-IS, B - BGP, > - selected route, * - FIB route

B>* 10.0.0.0/8 [20/0] via 192.168.1.1, Ethernet0, 00:01:00
C>* 192.168.1.0/24 is directly connected, Ethernet0, 00:10:00
""",
    "show bgp summary": """\
IPv4 Unicast Summary:
BGP router identifier 10.0.0.1, local AS number 65001 vrf-id 0
BGP table version 10

Neighbor        V         AS   MsgRcvd   MsgSent   TblVer  InQ OutQ  Up/Down State/PfxRcd   PfxSnt Desc
192.168.1.2     4      65002       150       145       10    0    0 01:00:00 Established         5     10 N/A
192.168.1.3     4      65003       130       125       10    0    0 00:30:00 Established         3      8 N/A
""",
}


class MockSwitch:
    """Drop-in replacement for SSHClient that returns pre-canned SONiC output."""

    def run_command(self, command: str) -> str:
        return MOCK_OUTPUTS.get(command, f"% Unknown command: {command}\n")
