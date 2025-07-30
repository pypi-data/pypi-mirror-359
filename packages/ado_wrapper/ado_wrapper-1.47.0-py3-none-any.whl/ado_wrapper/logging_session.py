import os
from datetime import datetime
from typing import Any

import requests

DEFAULT_KWARGS = {
    "allow_redirects": True,
    "data": None,
}


class LoggingSession(requests.Session):
    def __init__(self, latest_log_counter: int | None, log_directory: str) -> None:
        super().__init__()
        self.latest_log_counter = latest_log_counter
        self.log_directory = log_directory
        self.log_name = datetime.now().isoformat()

        if latest_log_counter is not None and not os.path.isdir(self.log_directory):
            os.makedirs(self.log_directory)

        self.cleanup_old_logs()

        if latest_log_counter is not None:
            with open(f"{self.log_directory}/{self.log_name}.log", "w", encoding="utf-8") as file:
                file.write("")

    def log_request(self, method: str, url: str, kwargs: dict[str, Any], duration_in_milliseconds: int) -> None:
        """Logs a request, but removes pre-defined kwargs to reduce spam."""
        if self.latest_log_counter is None:
            return
        with open(f"{self.log_directory}/{self.log_name}.log", "a", encoding="utf-8") as file:
            kwargs_copy = dict(kwargs.items())  # Copy
            for default_kwarg, default_kwarg_value in DEFAULT_KWARGS.items():
                # Can't set the default case to None since sometimes that's what we're looking for
                if kwargs.get(default_kwarg, -1) == default_kwarg_value:
                    del kwargs_copy[default_kwarg]
            file.write(f"{method.ljust(len('DELETE'))} @ {url}{' | '+str(kwargs_copy) if kwargs_copy else ''} | {duration_in_milliseconds}\n")  # fmt: skip

    def request(self, method: str, url: str, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> requests.Response:  # type: ignore[override]
        # Proceed with the actual request
        start_time = datetime.now()
        response = super().request(method, url, *args, **kwargs)  # type: ignore[arg-type]
        end_time = datetime.now()
        duration_in_milliseconds = (end_time - start_time).microseconds // 1000
        # Log the request using the log_request function
        self.log_request(method, url, kwargs, duration_in_milliseconds)
        return response

    def cleanup_old_logs(self) -> None:
        """Deletes old logs, if latest_log_counter is -1, keep all logs, if it's None, delete all logs."""
        if self.latest_log_counter == -1:  # -1 means infinite
            return
        logs = os.listdir(self.log_directory) if self.latest_log_counter is not None else []
        if self.latest_log_counter is not None and len(logs) < self.latest_log_counter - 1:
            return
        starting_index = self.latest_log_counter - 1 if self.latest_log_counter is not None else 0  # Remove 0 onward
        for file in sorted(logs, reverse=True)[starting_index:]:  # Delete any file that's not the newest x
            os.remove(f"{self.log_directory}/{file}")
