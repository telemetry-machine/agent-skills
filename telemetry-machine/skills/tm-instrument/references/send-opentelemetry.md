# Send OpenTelemetry Data

Telemetry Machine receives standard OTLP, so the [OpenTelemetry docs](https://opentelemetry.io/docs/) apply as written. This page lists only what is particular to Telemetry Machine.

## Endpoint and protocol

| Setting  | Value                                                         |
| -------- | ------------------------------------------------------------- |
| Endpoint | `https://api.telemetrymachine.com`                            |
| Paths    | `/v1/traces`, `/v1/logs`, `/v1/metrics`                       |
| Protocol | OTLP over HTTP (`http/protobuf` or `http/json`)               |
| Headers  | `X-API-Key` (an ingest key) and `X-Dataset-Name` on each call |

Telemetry Machine does not expose OTLP over gRPC. It accepts gzip-compressed bodies.

A sender that can set only a URL and a token can send the key as `Authorization: Bearer <key>` and name the dataset in the URL instead: `https://api.telemetrymachine.com/datasets/<dataset>` as the endpoint, or `/datasets/<dataset>/v1/metrics` as a full path. See [Send Render Metrics](https://telemetrymachine.com/docs/render).

`/v1/events` takes JSON events, not OTLP. See [Send JSON Events](https://telemetrymachine.com/docs/json-events).

## One dataset per signal

Each dataset holds one type of data: traces, logs, metrics, or events. OTLP goes to traces, logs, and metrics datasets; events datasets take JSON instead (see [Send JSON Events](https://telemetrymachine.com/docs/json-events)). Telemetry Machine routes each request by its `X-Dataset-Name` header, or by the dataset in its URL, so every signal needs its own header or URL. Set the per-signal variables, not `OTEL_EXPORTER_OTLP_HEADERS`:

```bash
OTEL_EXPORTER_OTLP_ENDPOINT=https://api.telemetrymachine.com
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
OTEL_EXPORTER_OTLP_TRACES_HEADERS=X-API-Key=<ingest-key>,X-Dataset-Name=shop-prod-traces
OTEL_EXPORTER_OTLP_LOGS_HEADERS=X-API-Key=<ingest-key>,X-Dataset-Name=shop-prod-logs
```

Name datasets `<app>-<environment>-<signal>`, such as `shop-prod-traces`. All the services of one app share its datasets; `service.name` tells them apart.

## Collector

A Collector needs one `otlp_http` exporter for each dataset, and a pipeline for each signal that uses that signal's exporter. Collector versions before v0.144.0 call this exporter `otlphttp`:

```yaml title="otel-collector.yaml"
exporters:
  otlp_http/traces:
    endpoint: https://api.telemetrymachine.com
    headers:
      X-API-Key: ${env:TM_INGEST_KEY}
      X-Dataset-Name: shop-prod-traces
  otlp_http/logs:
    endpoint: https://api.telemetrymachine.com
    headers:
      X-API-Key: ${env:TM_INGEST_KEY}
      X-Dataset-Name: shop-prod-logs

service:
  pipelines:
    traces:
      exporters: [otlp_http/traces]
    logs:
      exporters: [otlp_http/logs]
```

## AWS Lambda

Follow the OpenTelemetry docs for [the Lambda layer](https://opentelemetry.io/docs/platforms/faas/lambda-auto-instrument/). By default, the layer's Collector does not export to Telemetry Machine. Give it a Collector config with the exporters above, and set `OPENTELEMETRY_COLLECTOR_CONFIG_URI` to that file. Leave `OTEL_EXPORTER_OTLP_ENDPOINT` unset, so the function sends to the layer's Collector, which exports after the function returns.

## Attribute and metric names

Before you name an attribute or a metric, look it up in the [OpenTelemetry semantic conventions](https://opentelemetry.io/docs/specs/semconv/), and use the standard name, type and values when one fits. Agents can search them with the Telemetry Machine MCP server's `get_semconv` tool or with `tm-cli semconv search "<words>"`. Put an attribute that has no standard name under your app's own namespace, such as `app.checkout.cart_size`.

## Exceptions and span events

Telemetry Machine keeps a span's events in one JSON column, `events`, which queries cannot group by. Record exceptions as log records instead of span events: severity `ERROR` with the [`exception.*` attributes](https://opentelemetry.io/docs/specs/semconv/exceptions/exceptions-logs/), emitted while the span is active so the log carries its trace ID. Also set the span's status to error.

## Error slugs

Give each place that raises or handles an error a fixed ID, set as the `exception.slug` attribute on the span and on the exception's log record, such as `err-payment-declined`. You can search the code for a slug, group errors by it, and find errors that nobody handled:

```sql
"status_code" = 2 AND "attr.exception.slug" IS NULL
```

## Prometheus metrics

Telemetry Machine has no Prometheus `remote_write` endpoint. Scrape the targets you need with the Collector's [`prometheus` receiver](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/prometheusreceiver) and send them over OTLP to a metrics dataset.

## Rust

Enable the `reqwest-rustls` feature of `opentelemetry-otlp`. Without a TLS backend, export to `https://api.telemetrymachine.com` fails, and the SDK reports that only through `tracing::error!`. Keep a `tracing_subscriber::fmt` layer during setup, so you see export errors.

## How fields are stored

Attributes become columns: `attr.*` for span, log, and data-point attributes, and `resource.*` for resource attributes. Their values are stored as strings. See [Schema Management](https://telemetrymachine.com/docs/schema-management).

## OpenTelemetry docs

| Topic                                                            | Link                                                                       |
| ---------------------------------------------------------------- | -------------------------------------------------------------------------- |
| SDKs by language                                                 | <https://opentelemetry.io/docs/languages/>                                 |
| Zero-code instrumentation (Java agent, Python, Node.js, .NET)    | <https://opentelemetry.io/docs/zero-code/>                                 |
| OTLP exporter environment variables                              | <https://opentelemetry.io/docs/languages/sdk-configuration/otlp-exporter/> |
| Context propagation                                              | <https://opentelemetry.io/docs/concepts/context-propagation/>              |
| Logs and logging bridges                                         | <https://opentelemetry.io/docs/concepts/signals/logs/>                     |
| Semantic conventions                                             | <https://opentelemetry.io/docs/specs/semconv/>                             |
| LLM and agent apps (GenAI spans, agent spans, MCP)               | <https://opentelemetry.io/docs/specs/semconv/gen-ai/>                      |
| AWS Lambda, with the layer                                       | <https://opentelemetry.io/docs/platforms/faas/lambda-auto-instrument/>     |
| AWS Lambda, by hand                                              | <https://opentelemetry.io/docs/platforms/faas/lambda-manual-instrument/>   |
| Browser and mobile apps                                          | <https://opentelemetry.io/docs/platforms/client-apps/>                     |
| Collector: install, configure, deploy                            | <https://opentelemetry.io/docs/collector/>                                 |
| Kubernetes (Collector Helm chart, Operator auto-instrumentation) | <https://opentelemetry.io/docs/platforms/kubernetes/>                      |
