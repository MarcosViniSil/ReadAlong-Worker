from models.Job import Job
from models.enum.JobType import JobType
from models.enum.BookStatus import BookStatus
from storage.config_db.database import Database
from storage.JobRepository.jobRepositoryProvider import JobRepositoryProvider


class JobRepositoryImpl(JobRepositoryProvider):

    def __init__(self, db: Database):
        self._db = db

    @staticmethod
    def _job_from_row(row: dict) -> Job:
        return Job(
            id=str(row["id"]),
            processing_run_id=str(row["processing_run_id"]),
            page_id=str(row["page_id"]),
            chunk_id=str(row["chunk_id"]) if row["chunk_id"] else None,
            type=JobType(row["type"]),
            status=BookStatus(row["status"]),
            worker_id=str(row["worker_id"]) if row["worker_id"] else None,
            attempt=row["attempt"],
            queued_at=row["queued_at"],
            started_at=row["started_at"],
            finished_at=row["finished_at"],
            error_code=row["error_code"],
            error_message=row["error_message"],
        )

    async def claim(
        self,
        job_id: str,
    ) -> Job | None:

        async with self._db.transaction() as tx:

            cursor = await tx.execute(
                """
                UPDATE jobs
                SET
                    status = 'processing',
                    started_at = NOW(),
                    attempt = attempt + 1
                WHERE
                    id = %s::uuid
                    AND status = 'pending'
                RETURNING *
                """,
                [job_id],
            )

            row = await cursor.fetchone()

        return self._job_from_row(row)


    async def complete(
        self,
        job_id: str,
    ) -> Job:

        async with self._db.transaction() as tx:

            cursor = await tx.execute(
                """
                UPDATE jobs
                SET
                    status = 'completed',
                    finished_at = NOW()
                WHERE
                    id = %s::uuid
                    AND status = 'processing'
                RETURNING id
                """,
                [job_id],
            )
            row = await cursor.fetchone()

            if row is None:
                raise RuntimeError(f"Não foi possível completar o job {job_id}")
        self._job_from_row(row)

    async def fail(
        self,
        job_id: str,
        error_code: int | None,
        error_message: str,
    ) -> None:

        async with self._db.transaction() as tx:

            await tx.execute(
                """
                UPDATE jobs
                SET
                    status = 'failed',
                    finished_at = NOW(),
                    error_code = %s,
                    error_message = %s
                WHERE
                    id = %s::uuid
                    AND status = 'processing'
                """,
                [
                    error_code,
                    error_message,
                    job_id,
                ],
            )
