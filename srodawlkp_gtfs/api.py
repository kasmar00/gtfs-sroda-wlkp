import os
import time
from typing import Any, NamedTuple, TypedDict
import logging

import requests
from impuls.model import TimePoint
from typing import Any, NamedTuple, TypedDict
import http.client as http_client

# curl 'https://rozklad.kombus.pl/api/current_route_data' \
#   -H 'accept: application/json' \
#   -H 'accept-language: pl,en-GB;q=0.9,en-US;q=0.8,en;q=0.7' \
#   -H 'authorization: Basic c29uUld5dTB2d1JLZjUzM2ZuRVd6bktSNVcxWnlLUlVqb3ZZcDJqc25LRTE5RTFxWVdKZw==' \
#   -H 'cache-control: no-cache' \
#   -H 'content-type: application/json' \
#   -H 'origin: https://rozklad.kombus.pl' \
#   -H 'pragma: no-cache' \
#   -H 'priority: u=1, i' \
#   -H 'referer: https://rozklad.kombus.pl/route/1/direction/0' \
#   -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36' \
#   --data-raw '{"queryParams":{"route_id":"1"}}'


class Calendar(TypedDict):
    service_id: int
    start_date: int
    end_date: int
    monday: int
    tuesday: int
    wednesday: int
    thursday: int
    friday: int
    saturday: int
    sunday: int

class StopTime(TypedDict):
    trip_id: str
    stop_id: str
    stop_sequence: int
    arrival_time: TimePoint
    departure_time: TimePoint
    stop_headsign: str | None

class Stop(TypedDict):
    stop_id: str
    stop_name: str
    stop_lat: float
    stop_lon: float

class Trip(TypedDict):
    direction_id: str
    route_id: str
    service_id: str
    # shape_id: str
    trip_id: str

class Data(TypedDict):
    calendars: list[Calendar]
    # calendarsByDay: CalendarsByDay
    stopTimes: list[StopTime]
    stops: list[Stop]
    trips: list[Trip]


class Response(TypedDict):
    data: Data


class Endpoint:
    def __init__(self, pause_s: float = 0.05) -> None:
        self.session = requests.Session()
        # if proxy := os.getenv("POLREGIO_HTTP_PROXY"):
        #     self.session.proxies["http"] = proxy
        #     self.session.proxies["https"] = proxy
        self.last_call: float = 0.0
        self.pause = pause_s

        # http_client.HTTPConnection.debuglevel = 1

        # logging.basicConfig()
        # logging.getLogger().setLevel(logging.DEBUG)
        # requests_log = logging.getLogger("requests.packages.urllib3")
        # requests_log.setLevel(logging.DEBUG)
        # requests_log.propagate = True

    def _wait_between_calls(self) -> None:
        now = time.monotonic()
        delta = now - self.last_call
        if delta < self.pause:
            time.sleep(self.pause - delta)
            self.last_call = time.monotonic()
        else:
            self.last_call = now

    def _do_call(self, request: requests.Request) -> Any:
        self._wait_between_calls()
        prepared = self.session.prepare_request(request)
        with self.session.send(prepared) as response:
            response.raise_for_status()
            return response.json()

    def call(self, path: str, data: dict) -> Any:
        request = requests.Request(
            method="POST",
            url=f"https://rozklad.kombus.pl/api/{path}",
            json=data,
            headers={
                "Authorization": "Basic c29uUld5dTB2d1JLZjUzM2ZuRVd6bktSNVcxWnlLUlVqb3ZZcDJqc25LRTE5RTFxWVdKZw==",
                "Content-Type": "application/json",
            },
        )
        retries = 3
        for retry in range(1, retries + 1):
            try:
                return self._do_call(request)
            except requests.HTTPError:
                if retry == retries:
                    raise

    def get_current_route_data(self, route_id: str) -> Response:
        """
        Get current route data for a given route ID.
        """
        return self.call(
            path="current_route_data",
            data={"queryParams": {"route_id": route_id}},
        )
