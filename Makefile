app:
	export OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true
	opentelemetry-instrument --logs_exporter otlp --exporter_otlp_endpoint http://collector:4317 flask run -p 8081
