# VPN Connectivity Issues

## Symptoms

Employees or automated systems cannot establish or maintain a VPN
connection to internal networks (e.g. a data center or cloud VPC).
Symptoms range from complete inability to connect, to connections that
drop intermittently, to severe latency once connected. This blocks remote
access to internal tools, databases, and administrative systems.

## Likely Causes

- The VPN gateway or concentrator is overloaded or has crashed.
- A certificate used for VPN authentication has expired.
- An upstream ISP or network provider is experiencing an outage affecting
  the path to the VPN endpoint.
- A recent firewall or security group change inadvertently blocked VPN
  traffic (e.g. UDP 500/4500 for IPsec, or the relevant port for the VPN
  protocol in use).
- DNS resolution for the VPN endpoint hostname is failing.

## Diagnostic Steps

1. Check the VPN gateway's health metrics (CPU, active sessions, uptime).
2. Verify the validity of authentication certificates for both the server
   and affected clients.
3. Test connectivity to the VPN endpoint from multiple networks to isolate
   whether the issue is client-side, ISP-side, or gateway-side.
4. Review recent changes to firewall rules, security groups, or network
   ACLs that could affect VPN ports.
5. Confirm DNS resolution for the VPN endpoint from an unaffected network.

## Resolution

- If the gateway is overloaded, scale it horizontally or vertically, or
  shed non-critical load.
- If a certificate expired, issue and distribute a renewed certificate,
  and add monitoring for upcoming expirations.
- If a firewall change caused the outage, revert the offending rule and
  add a regression test or review step for future changes.
- If the issue is an upstream ISP outage, there may be nothing to do but
  wait; consider a secondary VPN endpoint on a different network path as
  a long-term mitigation.

## Escalation

If VPN access is down and blocking an active incident response or
critical administrative task, escalate immediately to the network
on-call, as this can compound other ongoing incidents by removing the
team's ability to investigate them remotely.
