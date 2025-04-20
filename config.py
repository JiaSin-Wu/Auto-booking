from dotenv import load_dotenv
import os

load_dotenv(".env")

BOOKING_CONFIG = {
    "date": os.getenv("BOOKING_DATE"),
    "start_station": os.getenv("START_STATION"),
    "stop_station": os.getenv("STOP_STATION"),
    "train_ticket_count": os.getenv("TRAIN_TICKET_COUNT"),
    "id": os.getenv("USER_ID"),
    "phone": os.getenv("USER_PHONE"),
    "email": os.getenv("USER_EMAIL"),
    "window_size": os.getenv("WINDOW_SIZE"),
    "retry_interval_sec": int(os.getenv("RETRY_INTERVAL_SEC", 300))  # 預設值300
}

