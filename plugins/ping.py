import subprocess
from util import hook


@hook.command
def ping(inp):
    '''.ping - pings an IP address or domain'''

    command = "ping -c 1 " + inp
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()
    result = process.stdout.read()
    result = result.split('\n')
    return result[1] or "Host not found"
