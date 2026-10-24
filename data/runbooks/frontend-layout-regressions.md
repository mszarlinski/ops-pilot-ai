# Frontend Layout Regressions

## Symptoms

Users report visual issues on a web application: misaligned elements,
broken layouts on specific screen sizes or browsers, overlapping text, or
unresponsive navigation elements. These issues are typically cosmetic and
do not prevent users from eventually completing their task, but on more
severe occasions a layout bug can block navigation entirely (e.g. a menu
that doesn't respond to clicks).

## Likely Causes

- A recent frontend deploy introduced a CSS or layout regression.
- A third-party font, stylesheet, or script failed to load, causing
  layout to fall back to unstyled or default rendering.
- A browser-specific rendering quirk is not accounted for in the CSS
  (common with older Safari or mobile browser versions).
- A responsive breakpoint was not tested at a particular viewport width,
  causing elements to overlap or overflow.
- A JavaScript error during page load prevented interactive elements from
  being correctly wired up, making them appear present but unresponsive.

## Diagnostic Steps

1. Reproduce the issue in the reported browser and viewport size.
2. Check the browser's developer console for JavaScript errors or failed
   network requests (missing CSS/JS/font files).
3. Compare the current deploy against the previous known-good deploy to
   identify recent frontend changes.
4. Test across a small matrix of common browsers and viewport widths to
   determine the scope of the regression.
5. Check whether a third-party asset (CDN-hosted font, analytics script)
   is unavailable or slow to load.

## Resolution

- If a recent deploy caused the regression, roll back the frontend
  deploy and add a visual regression test for the affected component.
- If a third-party asset is the cause, add a local fallback or
  self-host the critical asset to avoid depending on external
  availability for core layout.
- If it's a browser-specific quirk, add a targeted CSS fix or polyfill
  and add that browser to the test matrix going forward.
- If a JavaScript error broke interactivity, fix the error and ensure a
  monitoring/alerting hook catches similar errors in production before
  users report them.

## Escalation

If the layout issue blocks a core user flow entirely (e.g. navigation is
completely unresponsive, or a checkout button cannot be clicked),
escalate immediately as a high-severity incident even though the root
cause is "only" frontend, since the customer impact is equivalent to an
outage.
