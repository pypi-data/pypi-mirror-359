import concurrent.futures


class PersistentExecutor:
    def __init__(self, max_workers=4):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.futures = []

    def submit_job(self, func, *args, **kwargs):
        """Submit a job and return the future"""
        future = self.executor.submit(func, *args, **kwargs)
        self.futures.append(future)
        return future

    def get_completed_results(self):
        """Get results from completed jobs and clean up"""
        completed = []
        remaining = []

        for future in self.futures:
            if future.done():
                try:
                    result = future.result()
                    completed.append(result)
                except Exception as e:  # pylint: disable=broad-exception-caught
                    completed.append(f"Error: {e}")
            else:
                remaining.append(future)

        self.futures = remaining
        return completed

    def shutdown(self, wait=True):
        """Shutdown the executor"""
        self.executor.shutdown(wait=wait)
