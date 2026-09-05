from abc import ABC, abstractmethod
from dotenv import load_dotenv
import os
load_dotenv()

class CommonData(ABC):
    @abstractmethod
    def get_worker_id() -> None:
        return os.getenv("WORKER_ID","",)