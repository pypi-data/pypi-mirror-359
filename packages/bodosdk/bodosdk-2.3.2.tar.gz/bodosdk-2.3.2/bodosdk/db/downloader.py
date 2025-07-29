import concurrent.futures
import os

from bodosdk.api.request_wrapper import RequestWrapper


class FileDownloader:
    def __init__(self, url, file_name, request_wrapper, timeout=3600):
        self.url = url
        self.file_name = file_name
        self.request_wrapper = request_wrapper
        self.timeout = timeout

        self.result = None
        self.download_complete = False

    def download(self):
        response = self.request_wrapper.get(self.url, timeout=self.timeout)
        response.raise_for_status()

        with open(self.file_name, "wb") as temp_file:
            temp_file.write(response.content)
            self.result = temp_file
            self.download_complete = True
            os.sync()


class DownloadManager:
    MAX_WORKERS = 64

    def __init__(self, job_uuid, urls):
        self.urls = urls
        self.job_uuid = job_uuid
        self.workers = min(len(urls), self.MAX_WORKERS) if urls else 0
        self.request_wrapper = RequestWrapper()

    def download_files(self, cursor_uuid, timeout=3600):
        if not self.urls:
            return []

        files = []
        futures = []
        downloaders = []

        # Download files using ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.workers
        ) as executor:
            for index, url in enumerate(self.urls):
                filename = f"{cursor_uuid}-{self.job_uuid}-{index}.pq"
                downloader = FileDownloader(url, filename, self.request_wrapper)
                future = executor.submit(downloader.download)

                files.append(filename)
                downloaders.append(downloader)
                futures.append(future)

            concurrent.futures.wait(
                futures, timeout=timeout, return_when=concurrent.futures.ALL_COMPLETED
            )

        if not all([downloader.download_complete for downloader in downloaders]):
            raise TimeoutError(
                f"Could not download all results withing {timeout} seconds"
            )

        return files
