from subprocess import check_output
from util import hook


@hook.command
def ping(inp):
    """.ping - Pings an IP address or domain."""
    out = check_output(["ping", "-c", "1", inp.split()[0]])

    try:
        return out.split("\n")[1]
    except:
        return "Host not found."

