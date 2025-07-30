# otel_custom_distro/instrumentation_registry.py

_instrumented = []

def add_instrumented_library(name, entry_point):
    _instrumented.append({"name": name, "entry_point": entry_point})

def get_instrumented_libraries():
    return list(_instrumented)
