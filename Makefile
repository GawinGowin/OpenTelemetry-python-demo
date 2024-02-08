app:
	export OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true
	opentelemetry-instrument --logs_exporter otlp \
	--exporter_otlp_endpoint http://collector:4317 \
  --exporter_otlp_logs_endpoint http://collector:4317 \
  --exporter_otlp_metrics_endpoint http://collector:4317 \
	flask run -p 8080

app-local:
	export OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true
	opentelemetry-instrument --traces_exporter console --metrics_exporter console \
		--logs_exporter console --service_name dice-server flask run -p 8080

my_app:
	opentelemetry-instrument flask run -p 8080