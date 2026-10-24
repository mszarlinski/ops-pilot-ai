# Object Storage Upload Failures

## Symptoms

Uploads to object storage (e.g. S3-compatible buckets) fail with 503
Service Unavailable, 500 Internal Server Error, or time out entirely.
Users may see failed file uploads, broken backups, or incomplete exports.
The issue can affect a single bucket, a single region, or all storage
traffic depending on the root cause.

## Likely Causes

- The object storage provider is experiencing a regional outage or
  degraded performance.
- The application is being throttled for exceeding request-rate limits on
  a bucket (too many PUT/GET requests per second).
- Credentials or IAM permissions for the storage bucket have expired or
  changed, causing authentication failures that surface as generic errors.
- Underlying disk or network capacity on a self-hosted storage array is
  saturated.
- A misconfigured retry policy is amplifying load during a transient
  blip, turning a minor hiccup into a sustained overload.

## Diagnostic Steps

1. Check the object storage provider's status page for ongoing incidents
   in the relevant region.
2. Review request-rate and error-rate metrics for the affected bucket to
   determine if throttling is occurring.
3. Verify that the IAM role or access keys used by the application are
   still valid and have not been rotated or revoked.
4. For self-hosted storage, check disk utilization, I/O wait, and network
   throughput on the storage array.
5. Check client-side retry logic for exponential backoff; a naive
   retry-immediately policy can worsen an outage.

## Resolution

- If it's a provider-side outage, there is often nothing to do but wait
  and communicate status to affected users; consider a fallback storage
  location if the architecture supports it.
- If requests are being throttled, implement exponential backoff with
  jitter, or request a rate-limit increase from the provider.
- If credentials have expired, rotate and redeploy them, and set up
  monitoring to alert before the next expiration.
- If a self-hosted array is saturated, add capacity or redistribute load
  across additional nodes.

## Escalation

If uploads remain broken for more than 30 minutes and are blocking a
customer-facing workflow (e.g. file sharing, backups), escalate to the
storage/infrastructure on-call and notify affected customers proactively.
