# API 5xx Errors

## Symptoms

Clients calling an internal or public API receive HTTP 500, 502, or 503
responses instead of successful results. This may affect a single
endpoint, a single service, or cascade across dependent services. Error
rate dashboards show a spike correlated with a deploy, a dependency
failure, or a traffic surge.

## Likely Causes

- A recent deploy introduced a bug, an unhandled exception, or a
  misconfiguration (e.g. a missing environment variable).
- A downstream dependency (database, cache, another internal service, or
  a third-party API) is failing or responding slowly, and the failure is
  propagating upward without a circuit breaker.
- The service is out of memory or hitting CPU limits under current load,
  causing requests to fail or time out.
- A background job or queue consumer is blocking the request-handling
  threads or processes.

## Diagnostic Steps

1. Check error-rate and latency dashboards to identify when the issue
   started and correlate it with recent deploys.
2. Inspect application logs and exception traces for the specific error
   being returned.
3. Check the health and latency of downstream dependencies the service
   calls.
4. Review resource utilization (CPU, memory, open file descriptors,
   thread/connection pool usage) for the affected service instances.
5. If a deploy correlates with the start of the issue, review the diff for
   likely culprits.

## Resolution

- If a bad deploy is the cause, roll it back immediately and investigate
  the root cause before redeploying.
- If a downstream dependency is failing, add or tighten a circuit breaker
  and fallback behavior so one dependency's failure does not cascade.
- If the service is resource-constrained, scale it out horizontally or
  increase its resource limits, and investigate the underlying cause of
  increased resource usage.
- If a background job is blocking request handling, move it to a separate
  worker process or queue so it cannot starve the API of resources.

## Escalation

If the error rate exceeds a critical threshold (e.g. 10% of requests
failing) for more than 5 minutes on a customer-facing API, escalate to
the service owner and consider initiating an incident with customer
communication.
