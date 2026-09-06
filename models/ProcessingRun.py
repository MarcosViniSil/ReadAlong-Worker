from dataclasses import dataclass
import datetime
from models.enum import BookStatus
from models.enum.finalFileStatus import FinalFileStatus

@dataclass
class ProcessingRun:
    id: str = ""
    book_id: str = ""
    status: BookStatus = ""
    page_size: int = 0
    final_file_status: FinalFileStatus
    created_at: datetime = None
    started_at: datetime = None
    completed_at: datetime = None
