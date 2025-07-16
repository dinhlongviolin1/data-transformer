import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def get_logger(name: str = "default") -> logging.Logger:
    return logging.getLogger(f"data_transformer.{name}")
