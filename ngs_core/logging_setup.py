# ngs_core/logging_setup.py

import logging
import os
import re
import sys
from collections.abc import Mapping
from typing import Any

import structlog

# --- Config via env ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "console").lower()  # console | json
SAMPLE_RATE = float(os.getenv("LOG_SAMPLE_RATE", "0"))  # 0..1 for DEBUG sampling

# --- Keys to mask (case-insensitive) ---
REDACT_KEYS = {
    "password",
    "passwd",
    "pwd",
    "secret",
    "token",
    "apikey",
    "api_key",
    "authorization",
    "auth",
    "jwt",
    "bearer",
    "access_key",
    "secret_key",
}

# --- Regexes to mask free text ---
MASK_PATTERNS = [
    re.compile(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"),  # emails
    re.compile(r"(AKIA[0-9A-Z]{16})"),  # AWS access key id
]


def _mask_text(log_string: str) -> str:
    """Masks sensitive patterns in a string."""
    masked = log_string
    for pat in MASK_PATTERNS:
        masked = pat.sub("*****", masked)
    return masked


def _redact_mapping(obj: Any) -> Any:
    """Recursively redacts sensitive keys and masks patterns in strings."""
    if isinstance(obj, Mapping):
        clean = {}
        for k, v in obj.items():
            if isinstance(k, str) and k.lower() in REDACT_KEYS:
                clean[k] = "[REDACTED]"
            else:
                clean[k] = _redact_mapping(v)
        return clean
    if isinstance(obj, (list, tuple)):
        return obj.__class__(_redact_mapping(v) for v in obj)
    if isinstance(obj, str):
        return _mask_text(obj)
    return obj


class RedactProcessor:
    """A structlog processor to redact and mask sensitive data."""

    def __call__(self, _logger, _method_name, event_dict: dict):
        return _redact_mapping(event_dict)


class AddEnvContext:
    """
    Attaches context from environment variables.

    Reads a comma-separated string from the LOG_CONTEXT_VARS environment
    variable. The format is "log_key=ENV_VAR_NAME,other_key=OTHER_ENV_VAR".
    """

    def __init__(self):
        default_vars = (
            "pod_name=HOSTNAME,pod_name=POD_NAME,"
            "task_name=NXF_TASK_NAME,process=NXF_PROCESS,"
            "xray_trace_id=_X_AMZN_TRACE_ID"
        )
        context_vars_str = os.getenv("LOG_CONTEXT_VARS", default_vars)

        self.env_context = {}
        if not context_vars_str:
            return

        pairs = context_vars_str.strip().split(",")
        for pair in pairs:
            if "=" not in pair:
                continue

            log_key, env_var = pair.strip().split("=", 1)
            value = os.getenv(env_var)

            if value:
                self.env_context[log_key] = value

    def __call__(self, _logger, _method_name, event_dict: dict) -> dict:
        event_dict.update(self.env_context)
        return event_dict


class SamplingProcessor:
    """Down-samples DEBUG logs based on a sample rate."""

    def __init__(self, rate: float):
        import random

        self.rate = max(0.0, min(1.0, rate))
        self._rand = random.Random()

    def __call__(self, logger, method_name, event_dict):
        if method_name == "debug" and self.rate < 1.0:
            if self._rand.random() > self.rate:
                raise structlog.DropEvent
        return event_dict


def setup_logging():
    """Configures structlog to be the standard logging provider."""
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, LOG_LEVEL, logging.INFO),
    )

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        SamplingProcessor(SAMPLE_RATE),
        AddEnvContext(),
        RedactProcessor(),
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if LOG_FORMAT == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
