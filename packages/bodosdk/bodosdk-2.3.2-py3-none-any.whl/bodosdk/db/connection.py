import json
import os
from typing import Union, Any, Sequence, Dict
from uuid import uuid4

import pyarrow.parquet as pq

from bodosdk.api.request_wrapper import RequestWrapper
from bodosdk.db.downloader import DownloadManager
from bodosdk.db.exc import DatabaseError, NotSupportedError
from bodosdk.exceptions import TimeoutException
from bodosdk.interfaces import ICluster, IJobRun, ICursor


class Cursor(ICursor):
    """
    A cursor for executing and fetching results from SQL queries on a cluster.
    """

    def __init__(
        self, catalog: str, cluster: ICluster, timeout: int = 3600, query_id=None
    ):
        """
        Initialize the cursor with catalog, cluster, timeout, and optional query ID.

        :param catalog: The catalog to use for the query.
        :param cluster: The cluster to run the query on.
        :param timeout: The timeout for the query execution.
        :param query_id: Optional query ID for resuming a previous query.
        """
        self._catalog = catalog
        self.cluster = cluster
        self._timeout = timeout
        self._current_row = None
        self._metadata = None
        self._results_urls = None
        self._file_index = 0
        self._results = []
        self._rows_stripped = 0
        self._request_wrapper = RequestWrapper()

        self.uuid = uuid4()
        self._files = []
        if query_id:
            self._job = cluster._workspace_client.JobClient.JobRun(uuid=query_id)
        else:
            self._job: IJobRun = None

    def __enter__(self) -> "Cursor":
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __iter__(self):
        row = self.fetchone()
        while row:
            yield tuple(row.values()) if isinstance(row, dict) else row
            row = self.fetchone()

    @property
    def rownumber(self):
        """
        Get the current row number.

        :return: The current row number.
        """
        return self._current_row

    @property
    def rowcount(self):
        """
        Get the number of rows in the result set.

        :return: The number of rows in the result set.
        """
        self._wait_for_finished_job()
        self._load_metadata()
        if isinstance(self._metadata, dict) and "num_rows" in self._metadata:
            return self._metadata["num_rows"]
        else:
            return 0

    def execute(self, query: str, args: Union[Sequence[Any], Dict] = None):
        """
        Execute a SQL query synchronously.

        :param query: The SQL query to execute.
        :param args: Optional arguments for the query.
        :return: The cursor instance.
        """
        self._results_urls = None
        self._file_index = 0
        self._current_row = None
        self._metadata = None
        self._results = []
        self._rows_stripped = 0
        self._job = self.cluster.run_sql_query(
            catalog=self._catalog,
            sql_query=query,
            args=args,
            timeout=self._timeout,
            store_result=True,
        )
        self._wait_for_finished_job()
        self._load_metadata()
        return self

    def execute_async(
        self, query: str, args: Union[Sequence[Any], Dict] = None
    ) -> "Cursor":
        """
        Execute a SQL query asynchronously.

        :param query: The SQL query to execute.
        :param args: Optional arguments for the query.
        :return: The cursor instance.
        """
        self._results_urls = None
        self._file_index = None
        self._current_row = None
        self._metadata = None
        self._results = []
        self._rows_stripped = 0
        self._job = self.cluster.run_sql_query(
            catalog=self._catalog, sql_query=query, args=args, store_result=True
        )
        return self

    def fetchone(self):
        """
        Fetch the next row of the result set.

        :return: The next row, or None if no more rows are available.
        """
        self._wait_for_finished_job()
        self._load_metadata()
        if self._current_row >= self.rowcount:
            return None

        if self._job.is_ddl:
            results = self._job.sql_query_result["result"]
            record = results[self._current_row]
            self._current_row += 1
            return tuple(record.values()) if isinstance(record, dict) else record

        if self._current_row >= len(self._results) + self._rows_stripped:
            self._load_next_file()

        record = self._results[self._current_row - self._rows_stripped]
        self._current_row += 1
        return tuple(record.values()) if isinstance(record, dict) else record

    def fetchmany(self, size):
        """
        Fetch the next set of rows of the result set.

        :param size: The number of rows to fetch.
        :return: A list of rows.
        """
        self._wait_for_finished_job()
        self._load_metadata()
        if self._job.is_ddl:
            results = self._job.sql_query_result["result"]
            data_to_return = list(
                tuple(v for k, v in item.items()) for item in results
            )[
                self._current_row : size  # noqa: E203
            ]
            self._current_row += min(size, len(results))
            return data_to_return
        if self._current_row >= self.rowcount:
            return []

        results = list(self._results)
        while size > len(results):
            if self._load_next_file():
                results.extend(self._results)
            else:
                break
        data_to_return = results[
            max(self._current_row - self._rows_stripped, 0) : size  # noqa: E203
        ]
        self._results = list(
            results[
                max(self._current_row - self._rows_stripped, 0) + size :  # noqa: E203
            ]
        )
        self._current_row += min(size, len(results))
        self._rows_stripped = self._current_row
        return list(data_to_return)

    def fetchall(self):
        """
        Fetch all remaining rows of the result set.

        :return: A list of all remaining rows.
        """
        self._wait_for_finished_job()
        self._load_metadata()
        if self._job.is_ddl:
            return list(
                tuple(v for k, v in item.items())
                for item in self._job.sql_query_result["result"]
            )
        results = []
        results.extend(self._results)
        while self._load_next_file():
            results.extend(self._results)
        self._current_row = self.rowcount

        return results

    def setinputsizes(self, sizes):
        """
        Set the sizes of input parameters (not supported).

        :param sizes: Input sizes.
        """
        pass

    def setoutputsize(self, size, column=None):
        """
        Set the size of the output (not supported).

        :param size: The output size.
        :param column: The column to set the size for.
        """
        pass

    def _load_metadata(self):
        """
        Load metadata for the result set.
        """
        if self._job.is_ddl:
            if not self._current_row:
                self._current_row = 0
            self._metadata = self._job.sql_query_result.get("metadata")
            return
        if not self._results_urls:
            self._results_urls = self._job.get_result_urls()
            metadata_url = self._results_urls[0]
            response = self._request_wrapper.get(metadata_url)
            self._metadata = json.loads(response.content)
            self._file_index = 0
            self._current_row = 0
            self.download_manager = DownloadManager(
                self._job.uuid, self._results_urls[1:]
            )
            self._files.extend(
                self.download_manager.download_files(self.uuid, self._timeout)
            )

    def _load_next_file(self):
        """
        Load the next file of the result set.

        :return: True if a file was loaded, False otherwise.
        """
        if self._metadata is None or self._metadata.get("num_rows", 0) <= 0:
            return False

        filename = f"{self.uuid}-{self._job.uuid}-{self._file_index}.pq"
        try:
            df = pq.read_table(filename).to_pandas()
            data = list(df.to_records(index=False))
        except FileNotFoundError:
            return False
        try:
            os.remove(filename)
        except FileNotFoundError:
            pass
        else:
            if filename in self._files:
                del self._files[self._files.index(filename)]
        self._rows_stripped += len(self._results)
        self._results = data
        self._file_index += 1
        return True

    def _wait_for_finished_job(self):
        """
        Wait for the query job to finish.

        :raise DatabaseError: If the query times out or fails.
        """

        try:
            self._job.wait_for_status(
                ["SUCCEEDED", "FAILED", "CANCELLED"], timeout=self._timeout
            )
        except TimeoutException:
            raise DatabaseError("Query timed out")

        if self._job.status in ["FAILED", "CANCELLED"]:
            raise DatabaseError(
                f"Query failed due to {self._job.reason}. {self._job.get_stderr()}"
            )

    def close(self):
        """
        Close the cursor and clean up resources.
        """
        self._results = []
        self._file_index = 0
        self._rows_stripped = 0
        self._metadata = None
        self._results_urls = None
        self._current_row = None
        for file in self._files:
            try:
                os.remove(file)
            except FileNotFoundError:
                pass
        self._files = []

    @property
    def query_id(self):
        """
        Get the query ID.

        :return: The query ID.
        """
        if self._job:
            return self._job.id

    @property
    def description(self):
        """
        Get the description of the result set columns.

        :return: A list of column descriptions.
        """
        if self._metadata:
            return [
                (
                    x["name"],
                    x["type"],
                    self._metadata["num_rows"],
                    None,
                    x["precision"],
                    x["scale"],
                    x["nullable"],
                )
                for x in self._metadata["schema"]
            ]
        return (None, None, None, None, None, None, None)


class Connection:
    """
    A connection to a catalog and cluster for executing queries.
    """

    def __init__(self, catalog: str, cluster: ICluster, timeout=3600):
        """
        Initialize the connection with catalog, cluster, and timeout.

        :param catalog: The catalog to use for queries.
        :param cluster: The cluster to execute queries on.
        :param timeout: The timeout for query execution.
        """
        self._catalog = catalog
        self._cluster = cluster
        self._timeout = timeout
        self._cursors = {}

    def __enter__(self) -> "Connection":
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __del__(self):
        self.close()

    def cursor(self, query_id=None):
        """
        Create a new cursor for executing queries.

        :param query_id: Optional query ID for resuming a previous query.
        :return: A new cursor instance.
        """
        c = Cursor(self._catalog, self._cluster, self._timeout, query_id)
        self._cursors[c.uuid] = c
        return c

    def commit(self):
        """
        No-op because Bodo does not support transactions.
        """
        pass

    def close(self):
        """
        Close the connection and all associated cursors.
        """
        for c_uuid, cursor in self._cursors.items():
            cursor.close()
        self._cursors = {}

    def rollback(self):
        """
        Rollback is not supported as transactions are not supported on Bodo.

        :raise NotSupportedError: Always raised as rollback is not supported.
        """
        raise NotSupportedError("Transactions are not supported on Bodo")
