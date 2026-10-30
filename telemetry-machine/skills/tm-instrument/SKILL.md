---
name: tm-instrument
description: >
  Load this whenever you add or change OpenTelemetry instrumentation (logs, traces,
  metrics, wide events), including SDK setup and Collector config, and when a
  Telemetry Machine guide has you send a system's data.
metadata:
  version: "0.1.3" # x-release-please-version
---

# Instrument with OpenTelemetry

1. Read `references/send-opentelemetry.md`, then the OpenTelemetry docs for this
   language's SDK at `https://opentelemetry.io/docs/languages/`.
2. Before you name an attribute or metric, look it up in the OpenTelemetry semantic
   conventions (MCP: `get_semconv`; `tm-cli semconv`). Give an attribute with no
   standard name the app's own namespace, such as `app.checkout.cart_size` (but defer
   to existing patterns in code if they disagree).
3. MCP only: if the user does not send anything to TM yet, offer to set it up with
   `get_onboarding_guide`.
