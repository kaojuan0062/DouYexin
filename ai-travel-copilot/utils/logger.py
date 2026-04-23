import json
import logging
from typing import Any, Dict


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def log_event(
    logger: logging.Logger,
    request_id: str,
    agent_name: str,
    action: str,
    duration_ms: float,
    input_summary: Dict[str, Any],
    output_summary: Dict[str, Any],
) -> None:
    payload = {
        "request_id": request_id,
        "agent_name": agent_name,
        "action": action,
        "duration_ms": round(duration_ms, 2),
        "input_summary": input_summary,
        "output_summary": output_summary,
    }
    logger.info(json.dumps(payload, ensure_ascii=False))
