import impuls


class AddCalendarExceptions(impuls.Task):
    def execute(self, r):
        with r.db.transaction():
            calendars = r.db.retrieve_all(impuls.model.Calendar)
            min_date = impuls.model.Date(2111, 11, 11)
            max_date = impuls.model.Date(1111, 11, 11)
            ids = []
            for cal in calendars:
                min_date = min(cal.start_date, min_date)
                max_date = max(cal.end_date, max_date)
                ids.append(cal.id)

            range = impuls.tools.temporal.BoundedDateRange(min_date, max_date)

            exceptions = impuls.tools.polish_calendar_exceptions.load_exceptions(
                r.resources["exceptions"],
                impuls.tools.polish_calendar_exceptions.PolishRegion.WIELKOPOLSKIE,
            )

            for date, exception in exceptions.items():
                if date not in range:
                    continue
                if (
                    impuls.tools.polish_calendar_exceptions.CalendarExceptionType.NO_SCHOOL
                    not in exception.typ
                    and impuls.tools.polish_calendar_exceptions.CalendarExceptionType.HOLIDAY
                    not in exception.typ
                ):
                    continue

                date_str = str(date)

                for id in ids:
                    if "_SCHOOL_ONLY" in id:
                        r.db.create(
                            impuls.model.CalendarException(
                                calendar_id=id,
                                date=date_str,
                                exception_type=impuls.model.CalendarException.Type.REMOVED,
                            )
                        )
