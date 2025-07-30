from setuptools import setup, find_packages

setup(
    name="odigos-python-distro",
    version="0.1.0",
    description="Odigos Python Distro",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "opentelemetry_distro": [
            "odigos = otel_custom_distro.distro:OdigosDistro"
        ],
    },
)
