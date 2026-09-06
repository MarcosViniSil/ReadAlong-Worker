from abc import ABC, abstractmethod
from dotenv import load_dotenv
import os

load_dotenv()
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import url2pathname


class CommonData(ABC):
    @abstractmethod
    def get_worker_id() -> None:
        return os.getenv(
            "WORKER_ID",
            "",
        )

    @abstractmethod
    def file_size_from_path(file_url: str) -> None:
        parsed_url = urlparse(file_url)
        local_path = url2pathname(parsed_url.path)
        file_info = Path(local_path)
        return file_info.stat().st_size
