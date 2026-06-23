import os

# Use an in-memory span exporter during tests so the BatchSpanProcessor's
# background flush never writes to pytest's captured (and later closed) stdout.
# Must be set before `app.main` is imported (conftest loads before collection).
os.environ.setdefault("THESISOS_DISABLE_CONSOLE_TRACE", "1")
