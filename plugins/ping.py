import subprocess
from util import hook


@hook.command(adminonly=True)
def ping(inp):
    """.ping - Pings an IP address or domain."""

    command = "ping -c 1 " + inp.split()[0]
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()
    result = process.stdout.read()
    result = result.split('\n')
    try:
        return result[1]
    except:
        "Host not found"
