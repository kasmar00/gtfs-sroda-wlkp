import sqlite3
import impuls

from . import api


class ScrapeAPI(impuls.Task):
    def __init__(self) -> None:
        super().__init__()
        self.endpoint = api.Endpoint()

    def execute(self, r: impuls.TaskRuntime) -> None:
        with r.db.transaction():
            for route_id in [
                "1",
                "2",
                "4",
                "5", "6", "7", "8", "10", "11", "12", "13", "14", "15","16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26"
            ]:
                data = self.endpoint.get_current_route_data(route_id)["data"]

                r.db.create(
                    impuls.model.Route(
                        id=route_id,
                        agency_id="0",
                        short_name="1",
                        long_name="1",
                        type=impuls.model.Route.Type.BUS,
                    )
                )

                for calendar in data["calendars"]:
                    start_date = _format_date(calendar["start_date"])
                    end_date = _format_date(calendar["end_date"])
                    try:
                        r.db.create(
                            impuls.model.Calendar(
                                id=calendar["service_id"],
                                start_date=start_date,
                                end_date=end_date,
                                monday=calendar["monday"],
                                tuesday=calendar["tuesday"],
                                wednesday=calendar["wednesday"],
                                thursday=calendar["thursday"],
                                friday=calendar["friday"],
                                saturday=calendar["saturday"],
                                sunday=calendar["sunday"],
                            )
                        )
                        r.db.create(
                            impuls.model.Calendar(
                                id=get_school_only_cal_id(calendar["service_id"]),
                                start_date=start_date,
                                end_date=end_date,
                                monday=calendar["monday"],
                                tuesday=calendar["tuesday"],
                                wednesday=calendar["wednesday"],
                                thursday=calendar["thursday"],
                                friday=calendar["friday"],
                                saturday=calendar["saturday"],
                                sunday=calendar["sunday"],
                            )
                        )
                    except sqlite3.IntegrityError:
                        # Calendar already exists, skip it
                        pass

                for trip in data["trips"]:
                    calendar_id = (
                        get_school_only_cal_id(trip["service_id"])
                        if is_school_trip_id(trip["trip_id"])
                        else trip["service_id"]
                    )
                    r.db.create(
                        impuls.model.Trip(
                            id=trip["trip_id"],
                            route_id=trip["route_id"],
                            calendar_id=calendar_id,
                            # direction=trip["direction_id"],
                        )
                    )

                for stop in data["stops"]:
                    try:
                        r.db.create(
                            impuls.model.Stop(
                                id=stop["stop_id"],
                                name=stop["stop_name"],
                                lat=stop["stop_lat"],
                                lon=stop["stop_lon"],
                            )
                        )

                    except sqlite3.IntegrityError:
                        # Stop already exists, skip it
                        pass

                for stop_time in data["stopTimes"]:
                    r.db.create(
                        impuls.model.StopTime(
                            trip_id=stop_time["trip_id"],
                            stop_id=stop_time["stop_id"],
                            stop_sequence=stop_time["stop_sequence"],
                            arrival_time=_hour_to_time_point(stop_time["arrival_time"]),
                            departure_time=_hour_to_time_point(stop_time["departure_time"]),
                            # stop_headsign=stop_time.get("stop_headsign"),
                        )
                    )


def _format_date(date: int) -> str:
    """Format date from YYYYMMDD to YYYY-MM-DD."""
    date = str(date)
    return f"{date[:4]}-{date[4:6]}-{date[6:]}"

def _hour_to_time_point(time: str) -> impuls.model.TimePoint:
    hour, minute = time.split(":")
    return impuls.model.TimePoint(hours=int(hour), minutes=int(minute))


def get_school_only_cal_id(calendar_id: str) -> str:
    return calendar_id + "_SCHOOL_ONLY"

def is_school_trip_id(trip_id: str) -> bool:
    for suffix in ["^s", "^SZ"]:
        if suffix in trip_id:
            return True
    return False