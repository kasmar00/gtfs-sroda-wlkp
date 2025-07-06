import impuls
import argparse
from datetime import datetime
from .consts import START_DATE, END_DATE
from .scrape_api import ScrapeAPI


GTFS_HEADERS = {
    "agency.txt": (
        "agency_id",
        "agency_name",
        "agency_url",
        "agency_timezone",
        "agency_lang",
        "agency_phone",
    ),
    "stops.txt": ("stop_id", "stop_name", "stop_lat", "stop_lon"),
    "routes.txt": (
        "agency_id",
        "route_id",
        "route_short_name",
        "route_long_name",
        "route_type",
        "route_color",
        "route_text_color",
    ),
    "trips.txt": (
        "route_id",
        "trip_id",
        "service_id",
        "trip_headsign",
        "trip_short_name",
        "block_id",
        "shape_id",
    ),
    "stop_times.txt": (
        "trip_id",
        "stop_sequence",
        "stop_id",
        "arrival_time",
        "departure_time",
    ),
    "calendar_dates.txt": ("service_id", "date", "exception_type"),
    "transfers.txt": (
        "from_stop_id",
        "to_stop_id",
        "from_trip_id",
        "to_trip_id",
        "transfer_type",
    ),
    "feed_info.txt": (
        "feed_publisher_name",
        "feed_publisher_url",
        "feed_lang",
        "default_lang",
        "feed_start_date",
        "feed_end_date",
        "feed_version",
        "feed_contact_email",
        "feed_contact_url",
    ),
    "calendar.txt": (
        "service_id",
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
        "start_date",
        "end_date",
    ),
    "shapes.txt": (
        "shape_id",
        "shape_pt_lat",
        "shape_pt_lon",
        "shape_pt_sequence",
    ),
}


class SrodaWalkpGTFS(impuls.App):
    """
    Sroda Walkp GTFS data importer.
    """

    def prepare(
        self, args: argparse.Namespace, options: impuls.PipelineOptions
    ) -> impuls.Pipeline:
        return impuls.Pipeline(
            tasks=[
                impuls.tasks.AddEntity(
                    impuls.model.Agency(
                        id="0",
                        name="Kombus",
                        url="https://zditmminskmaz.pl",
                        timezone="Europe/Warsaw",
                        lang="pl",
                        phone="+48721390112",
                    ),
                    task_name="AddAgency",
                ),
                impuls.tasks.AddEntity(
                    entity=impuls.model.FeedInfo(
                        publisher_name="kasmar00",
                        publisher_url="https://github.com/kasmar00/gtfs-warsaw-custom",
                        start_date=START_DATE,
                        end_date=END_DATE,
                        lang="pl",
                        version=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    ),
                    task_name="AddFeedInfo",
                ),
                ScrapeAPI(),
                impuls.tasks.ModifyRoutesFromCSV("routes.csv",),
                impuls.tasks.ModifyStopsFromCSV("stops.csv"),
                impuls.tasks.GenerateTripHeadsign(),
                impuls.tasks.SaveGTFS(
                    headers=GTFS_HEADERS,
                    target="latest.zip",
                ),
            ],
            resources={
                "stops.csv": impuls.LocalResource("stops.csv"),
                "routes.csv": impuls.LocalResource("routes.csv"),
            },
        )


def main() -> None:
    SrodaWalkpGTFS().run()
