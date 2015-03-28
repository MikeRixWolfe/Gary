from subprocess import check_output
from util import hook


@hook.command
def ping(inp):
    """.ping - Pings an IP address or domain."""
    try:
        out = check_output(["ping", "-c", "1", inp.split()[0]])
    except Exception as e:
        return "Unable to ping {}".format(inp)

    try:
        return out.split("\n")[1]
    except:
        return "Host not found."

