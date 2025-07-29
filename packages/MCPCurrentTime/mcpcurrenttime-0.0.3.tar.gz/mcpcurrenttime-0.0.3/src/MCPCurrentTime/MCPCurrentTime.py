from mcp.server.fastmcp import FastMCP
from datetime import datetime
import pytz

mcp=FastMCP("CurrentTime")

@mcp.tool()
async def get_time(time_format: str = "%Y%m%d%H%M%S", timezone: str = "UTC") -> str:
    """Get the current time in a specified format using a specified timezone.
    
    default time_format is "%Y%m%d-%H%M%S" and default timezone is "UTC".

    time formats are based on Python's strftime directives.
    For example, "%Y-%m-%d %H:%M:%S" will return "2023-10-01 12:34:56".

    timezones are based on the pytz library.
    For example, "America/New_York" or "Europe/London".
    
    Args:
        time_format (str): The format in which to return the time.
        timezone (str): The timezone in which to get the current time.
    """

    if not isinstance(time_format, str):
        return "ERROR: time_format must be a string"
    if not isinstance(timezone, str):
        return "ERROR: timezone must be a string"

    #get the current datetime in the given timezone
    try:
        tz = pytz.timezone(timezone)
        dt = datetime.now(tz)
    except pytz.UnknownTimeZoneError:
        return f"ERROR: Unknown timezone: {timezone}"

    try:
        #format the datetime according to the given format
        dt = dt.strftime(time_format)
    except ValueError:
        return f"ERROR: Invalid time format: {time_format}"

    return dt


class MCPCurrentTime:
    """A server with a single tool to get the current time in a specified format and timezone."""

    def __init__(self):
        pass

    def run_server(self,mcp_args: dict = {"transport":"stdio"}):
        """Run the MCP server."""
        mcp.run(**mcp_args)


if __name__ == "__main__":
    MCPCurrentTime().run_server()