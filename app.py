from opentelemetry.sdk.resources import SERVICE_NAME, Resource

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

from random import randint
from flask import Flask, request
import logging

# Service name is required for most backends
resource = Resource(attributes={
    SERVICE_NAME: "rolldice"
})

traceProvider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://collector:4317"))
traceProvider.add_span_processor(processor)
trace.set_tracer_provider(traceProvider)

reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint="http://collector:4317")
)
meterProvider = MeterProvider(resource=resource, metric_readers=[reader])
metrics.set_meter_provider(meterProvider)

# Acquire a tracer
tracer = trace.get_tracer_provider().get_tracer("rolldice")
# Acquire a meter.
meter = metrics.get_meter_provider().get_meter("rolldice")
# Now create a counter instrument to make measurements with
roll_counter = meter.create_counter(
    "dice.rolls",
    description="The number of rolls by roll value",
)

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route("/rolldice")
def roll_dice():
    # This creates a new span that's the child of the current one
    with tracer.start_as_current_span("roll") as roll_span:
        player = request.args.get('player', default = None, type = str)
        result = str(roll())
        roll_span.set_attribute("roll.value", result)
        # This adds 1 to the counter for the given roll value
        roll_counter.add(1, {"roll.value": result})
        if player:
            logger.warn("{} is rolling the dice: {}", player, result)
        else:
            logger.warn("Anonymous player is rolling the dice: %s", result)
        return result

def roll():
    return randint(1, 6)

if __name__=="__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)
