# storage/jobRepository/jobRepositoryProvider.py

from abc import ABC, abstractmethod


class JobRepositoryProvider(ABC):

    @abstractmethod
    async def claim(
        self,
        job_id: str,
        worker_id: str,
    ): ...

    @abstractmethod
    async def complete(
        self,
        job_id: str,
        worker_id: str,
    ) -> None: ...

    @abstractmethod
    async def fail(
        self,
        job_id: str,
        worker_id: str,
        error_code: int | None,
        error_message: str,
    ) -> None: ...
