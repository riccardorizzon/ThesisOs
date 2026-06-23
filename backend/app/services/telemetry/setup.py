"""Minimal, provider-agnostic OpenTelemetry tracing setup.

Configures a real SDK ``TracerProvider`` with a batched span exporter selected
by environment (OTLP/HTTP when ``OTEL_EXPORTER_OTLP_ENDPOINT`` is set, otherwise
console). Kept dependency-safe: only ``opentelemetry-sdk`` and
``opentelemetry-instrumentation-fastapi`` are guaranteed installed; the OTLP
exporter import is guarded and degrades to console if unavailable.
"""

import os

from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

SERVICE_NAME = "thesisos-backend"


def _build_exporter():
    """Pick a span exporter: in-memory under tests, OTLP/HTTP if configured, else console."""
    if os.getenv("THESISOS_DISABLE_CONSOLE_TRACE"):
        # Keeps the provider real (spans recorded) without writing to a captured
        # stdout that pytest closes at teardown. Used by tests/conftest.py.
        from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
            InMemorySpanExporter,
        )

        return InMemorySpanExporter()
    if os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
        try:
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
                OTLPSpanExporter,
            )

            return OTLPSpanExporter()
        except ImportError:
            # OTLP exporter package isn't a guaranteed dependency; degrade gracefully.
            return ConsoleSpanExporter()
    return ConsoleSpanExporter()


def init_telemetry(app) -> None:
    """Wire a real, idempotent TracerProvider and instrument the FastAPI app."""
    current = trace.get_tracer_provider()
    if isinstance(current, TracerProvider):
        provider = current
    else:
        resource = Resource.create({"service.name": SERVICE_NAME})
        provider = TracerProvider(resource=resource)
        provider.add_span_processor(BatchSpanProcessor(_build_exporter()))
        trace.set_tracer_provider(provider)

    if not getattr(app, "_is_instrumented_by_opentelemetry", False):
        FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)
