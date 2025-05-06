"""
Tracing configuration for a FastAPI application using OpenTelemetry.
"""

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from core.config import TracingSettings

tracing_settings = TracingSettings()


def configure_tracer(
    service_name: str,
    tracer_container_name: str,
    tracer_port: int,
) -> None:
    """Configures the global OpenTelemetry tracer provider.

    Args:
        service_name (str): The name of the service for identifying traces.
        tracer_container_name (str): Hostname or container name where the OTLP collector is running.
        tracer_port (int): Port on which the OTLP collector listens for trace data.
    """
    resource = Resource(attributes={SERVICE_NAME: service_name})
    trace.set_tracer_provider(TracerProvider(resource=resource))
    otlp_exporter = OTLPSpanExporter(
        endpoint=f"http://{tracer_container_name}:{tracer_port}/v1/traces"
    )
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))  # type: ignore[attr-defined]


def add_tracer(app: FastAPI) -> None:
    """Adds tracing to the given FastAPI application by configuring the tracer
    and instrumenting the app.

    Args:
        app (FastAPI): The FastAPI application to instrument.
    """
    configure_tracer(
        service_name=app.title,
        tracer_container_name=tracing_settings.container_name,
        tracer_port=tracing_settings.port,
    )
    FastAPIInstrumentor.instrument_app(app)
