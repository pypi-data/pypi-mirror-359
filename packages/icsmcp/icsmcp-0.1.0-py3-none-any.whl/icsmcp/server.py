from datetime import timedelta
from typing import Annotated

from ics import Calendar
from ics import Event
from ics.alarm import DisplayAlarm
from mcp.server.fastmcp import FastMCP
from pydantic import Field

# https://github.com/jlowin/fastmcp/issues/81#issuecomment-2714245145
mcp = FastMCP("ICS MCP Server", log_level="ERROR")


@mcp.tool()
def create_ics_event(
    name: Annotated[str, Field(description="Event title/summary")],
    begin: Annotated[str, Field(description="Event start time in ISO format (e.g., '2024-01-01T10:00:00')")],
    end: Annotated[
        str | None, Field(description="Event end time in ISO format. If not provided, duration must be specified")
    ] = None,
    duration_minutes: Annotated[
        int | None, Field(description="Event duration in minutes. Ignored if end is provided")
    ] = None,
    description: Annotated[str | None, Field(description="Event description")] = None,
    location: Annotated[str | None, Field(description="Event location")] = None,
    url: Annotated[str | None, Field(description="Event URL")] = None,
    all_day: Annotated[bool, Field(description="Whether this is an all-day event")] = False,
    alarm_minutes_before: Annotated[int | None, Field(description="Minutes before event to trigger alarm")] = None,
) -> str:
    """Create an ICS calendar event and return the ICS format string."""

    # Create calendar and event
    calendar = Calendar()
    event = Event()

    # Set basic event properties
    event.name = name
    event.begin = begin

    if description:
        event.description = description
    if location:
        event.location = location
    if url:
        event.url = url

    # Handle end time or duration
    if end:
        event.end = end
    elif duration_minutes:
        event.duration = timedelta(minutes=duration_minutes)

    # Handle all-day events
    if all_day:
        event.make_all_day()

    # Add alarm if specified
    if alarm_minutes_before:
        alarm = DisplayAlarm(trigger=timedelta(minutes=-alarm_minutes_before))
        event.alarms.append(alarm)

    # Add event to calendar
    calendar.events.add(event)

    # Return ICS string
    return str(calendar)


def main() -> None:
    mcp.run()
