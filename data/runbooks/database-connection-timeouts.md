# Database Connection Timeouts

## Symptoms

Application servers report errors such as "connection timed out" or
"could not acquire connection from pool" when talking to the primary
database. Request latency spikes and some requests fail outright with a
504 or 500 status code. The issue may affect all services sharing the
database, or only services under heavy load.

## Likely Causes

- The database's connection pool is exhausted because a long-running query
  or transaction is holding connections open.
- The database host itself is under CPU, memory, or disk I/O pressure and
  is slow to respond to new connections.
- A network partition or firewall change between the application tier and
  the database host is dropping or delaying packets.
- A recent schema migration added a lock that is blocking other queries.

## Diagnostic Steps

1. Check the database's active connection count against its configured
   maximum. If it's near the limit, identify which service or query is
   holding connections.
2. Look at the database host's CPU, memory, and disk I/O metrics for the
   affected time window.
3. Run `SHOW PROCESSLIST` (or the equivalent for your database engine) to
   find long-running or blocked queries.
4. Check for recent deploys or migrations that changed query patterns or
   added new indexes/locks.
5. Verify network connectivity and latency between the application hosts
   and the database host.

## Resolution

- If a specific query or transaction is holding connections open, kill it
  and investigate why it ran long (missing index, large unbounded scan).
- If the pool size is simply too small for current traffic, increase the
  connection pool size and/or add read replicas to spread load.
- If the database host is resource-constrained, consider vertical scaling
  or query optimization to reduce load.
- If a migration introduced a lock, roll it back or schedule it for a
  lower-traffic window with proper lock timeouts.

## Escalation

If connections cannot be restored within 15 minutes and the primary
database is a single point of failure for customer-facing traffic,
escalate to the on-call database administrator and consider failing over
to a standby replica.
