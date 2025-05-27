import logging

logging.basicConfig(
    filename="ignis.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_event(event):
    logging.info(event)