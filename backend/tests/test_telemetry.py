def test_real_tracer_provider_configured():
    import app.main  # noqa: F401  (importing wires telemetry via init_telemetry)
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    provider = trace.get_tracer_provider()
    assert isinstance(provider, TracerProvider), type(provider)
    # resource carries our service name
    assert provider.resource.attributes.get("service.name") == "thesisos-backend"
