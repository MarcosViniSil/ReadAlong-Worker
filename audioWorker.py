import time

from jobs_queue.queue import AudioQueue
from storage.JobRepository.jobRepositoryProvider import JobRepositoryProvider

class AudioWorker:

    def __init__(
        self,
        queue: AudioQueue,
        jobs: JobRepositoryProvider,
    ):
        self._queue = queue
        self._jobs = jobs

    async def run(self):

        while True:

            message = await self._queue.consume()

            if message is None:
                continue

            print("message ",message)

            job_id = message.get("job_id")

            if not job_id:
                continue

            job = await self._jobs.claim(
               job_id=job_id,
            )

            if job is None:
           
               # Outro worker já adquiriu o job
               # ou ele não está mais pending.
               continue

            try:

                # await self.process(job)
                print("message ", message)
                print("job_id ", job_id)
                print("job ",job)
                time.sleep(10)

            except Exception as exc:
                pass

                # await self._jobs.fail(
                #    job_id=job_id,
                #    worker_id=self._worker_id,
                #    error_code=500,
                #    error_message=str(exc),
                # )

            else:
                pass

                # await self._jobs.complete(
                #    job_id=job_id,
                #    worker_id=self._worker_id,
                # )
