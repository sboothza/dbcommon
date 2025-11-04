from threading import Thread
from queue import Queue, Empty

from .session import Session
from .managed_cursor import ManagedCursor

class SqlCommand:
    def __init__(self, query: str, params: dict | None = None):
        self.query = query
        self.params = params if params is not None else {}

class QueuedSession(Thread):
    def __init__(self, session: Session):
        super().__init__()
        self.session = session
        self.command_queue: Queue[SqlCommand] = Queue()
        self.terminate = False
        self.daemon = True  # Thread will exit when main program exits

    def run(self):
        print("Starting....")
        while not self.terminate or not self.command_queue.empty():
            try:
                # Wait for queue item with timeout (allows checking terminate flag)
                cmd = self.command_queue.get(timeout=0.1)
                try:
                    self.session.execute(cmd.query, cmd.params)
                except Exception as e:
                    print(f"Error executing command: {e}")
                finally:
                    self.command_queue.task_done()
            except Empty:
                # Timeout - check if we should continue
                continue

        print("Exiting....")

    def __enter__(self):
        self.begin()
        # Start the thread when entering context manager
        if not self.is_alive():
            super().start()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        self.commit()
        self.terminate = True
        self.join(2000)
        self.session.close()

    def begin(self):
        self.session.start()

    def _drain_queue(self):
        """Wait for all queued commands to be executed."""
        self.command_queue.join()  # Blocks until all tasks are done

    def commit(self):
        self._drain_queue()
        self.session.commit()

    def rollback(self):
        # Clear all queued commands
        while True:
            try:
                self.command_queue.get_nowait()
                self.command_queue.task_done()
            except Empty:
                break
        self.session.rollback()

    def execute(self, query: str, params=None) -> None:
        """Queue a command for asynchronous execution."""
        self.command_queue.put(SqlCommand(query, params if params is not None else {}))

    def execute_lastrowid(self, query: str, params=None):
        self._drain_queue()
        return self.session.execute_lastrowid(query, params)

    def fetch_scalar(self, query: str, params=None):
        self._drain_queue()
        return self.session.fetch_scalar(query, params)

    def fetch_one(self, query: str, params=None):
        self._drain_queue()
        return self.session.fetch_one(query, params)

    def fetch(self, query: str, params=None) -> ManagedCursor:
        self._drain_queue()
        return self.session.fetch(query, params)
