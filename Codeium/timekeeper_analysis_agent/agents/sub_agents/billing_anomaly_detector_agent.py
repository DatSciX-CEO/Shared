# Copyright 2025 DatSciX
# Billing Anomaly Detector Agent

"""Agent specialized in detecting billing anomalies and compliance issues."""

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from prompts import BILLING_ANOMALY_PROMPT
from services import get_ollama_model
from tools import calculate_statistics, detect_anomalies


billing_anomaly_detector = Agent(
    name="billing_anomaly_detector",
    model=get_ollama_model(),
    description=(
        "Detects unusual billing patterns, rate anomalies, hours spikes, "
        "and potential compliance concerns in timekeeper data."
    ),
    instruction=BILLING_ANOMALY_PROMPT,
    tools=[
        FunctionTool(calculate_statistics),
        FunctionTool(detect_anomalies),
    ],
    output_key="billing_anomaly_analysis",
)