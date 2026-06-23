from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor


def init_telemetry(app) -> None:
    FastAPIInstrumentor.instrument_app(app)
