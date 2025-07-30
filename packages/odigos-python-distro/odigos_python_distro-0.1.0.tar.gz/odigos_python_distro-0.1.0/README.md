# Odigos OpenTelemetry Python Distro

A custom [OpenTelemetry Python Distro](https://opentelemetry.io/docs/instrumentation/python/libraries/#distros) used by the Odigos instrumentation pipeline.

This package provides:
- A custom `BaseDistro` implementation that integrates with OpenTelemetry's auto-instrumentation
- Runtime tracking of which libraries were instrumented
- Logging and extensibility hooks for future observability and debugging use cases

---

## 📦 Installation

This package is meant to be installed **alongside** Odigos instrumentation agent (`odigos-opentelemetry-python`).
