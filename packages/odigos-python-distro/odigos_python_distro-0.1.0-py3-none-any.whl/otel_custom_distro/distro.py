# otel_custom_distro/distro.py

from opentelemetry.instrumentation.distro import BaseDistro
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from importlib.metadata import EntryPoint
from .instrumentation_registry import add_instrumented_library

class OdigosDistro(BaseDistro):
    def _configure(self, **kwargs):
        pass

    def load_instrumentor(self, entry_point: EntryPoint, **kwargs):
        instrumentor: BaseInstrumentor = entry_point.load()
        instrumentor().instrument(**kwargs)
        add_instrumented_library(entry_point.name, entry_point.value)
