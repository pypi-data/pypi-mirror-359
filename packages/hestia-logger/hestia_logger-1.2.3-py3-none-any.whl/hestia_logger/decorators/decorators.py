import functools
import time
import asyncio
import json
import inspect
import traceback
from hestia_logger.core.custom_logger import get_logger

SENSITIVE_KEYS = {"password", "token", "secret", "apikey", "api_key"}

# Optional: Import known types for type-based redaction
try:
    from fastapi import UploadFile, Request
except ImportError:
    UploadFile = None
    Request = None

try:
    from sqlalchemy.orm import Session
except ImportError:
    Session = None


def mask_sensitive_data(obj):
    """Recursively masks sensitive keys in nested dicts/lists."""
    if isinstance(obj, dict):
        return {
            k: "***" if k.lower() in SENSITIVE_KEYS else mask_sensitive_data(v)
            for k, v in obj.items()
        }
    elif isinstance(obj, list):
        return [mask_sensitive_data(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(mask_sensitive_data(item) for item in obj)
    elif isinstance(obj, set):
        return {mask_sensitive_data(item) for item in obj}
    return obj


def sanitize_module_name(module_name):
    """Converts "__module__" format to "module_module" for cleaner log file names."""
    if module_name.startswith("__") and module_name.endswith("__"):
        return f"{module_name.strip('_')}"
    return module_name


def redact_large(value, max_length):
    serialized = str(value)
    return (
        serialized
        if len(serialized) <= max_length
        else f"{serialized[:max_length]}... [TRUNCATED]"
    )


def safe_serialize(obj, max_length=300):
    """Recursively convert objects into JSON-serializable formats."""
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    elif isinstance(obj, dict):
        return {
            safe_serialize(k, max_length): safe_serialize(v, max_length)
            for k, v in obj.items()
        }
    elif isinstance(obj, (list, tuple, set)):
        return [safe_serialize(i, max_length) for i in obj]
    elif UploadFile and isinstance(obj, UploadFile):
        return {"filename": obj.filename, "content_type": obj.content_type}
    elif Request and isinstance(obj, Request):
        return {"method": obj.method, "url": str(obj.url)}
    elif Session and isinstance(obj, Session):
        return "<SQLAlchemy Session>"
    elif isinstance(obj, (bytes, memoryview)):
        return "[BINARY DATA REDACTED]"
    elif hasattr(obj, "__dict__"):
        return safe_serialize(vars(obj), max_length)
    elif hasattr(obj, "__str__"):
        return redact_large(obj, max_length)
    else:
        return repr(obj)


def log_execution(func=None, *, logger_name=None, max_length=300):
    """Logs function execution start, end, and duration."""

    if func is None:
        return lambda f: log_execution(
            f, logger_name=logger_name, max_length=max_length
        )

    module_name = func.__module__
    sanitized_name = sanitize_module_name(module_name)

    service_logger = get_logger(logger_name or sanitized_name)
    app_logger = get_logger("app", internal=True)

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        masked_kwargs = mask_sensitive_data(kwargs)

        log_entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.Z", time.gmtime()),
            "service": service_logger.name,
            "function": func.__name__,
            "status": "started",
            "args": safe_serialize(mask_sensitive_data(args), max_length),
            "kwargs": safe_serialize(masked_kwargs, max_length),
        }

        app_logger.info(log_entry)
        service_logger.info(f"Started: {func.__name__}()")

        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time

            log_entry.update(
                {
                    "status": "completed",
                    "duration": f"{duration:.4f} sec",
                    "result": safe_serialize(mask_sensitive_data(result), max_length),
                }
            )

            app_logger.info(log_entry)
            service_logger.info(f"Finished: {func.__name__}() in {duration:.4f} sec")

            return result
        except Exception as e:
            log_entry.update(
                {
                    "status": "error",
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                }
            )

            app_logger.error(log_entry)
            service_logger.error(f"Error in {func.__name__}: {e}")

            raise

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            return asyncio.run(async_wrapper(*args, **kwargs))

        return sync_wrapper
