from datetime import datetime
from werkzeug.utils import secure_filename

def build_storage_path(from_number: str, timestamp: str, msg_id: str, ext: str):
    date_folder = datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d')
    filename = secure_filename(f"{msg_id}.{ext}")
    return f"{from_number}/{date_folder}", filename