rock paper scissors game!

use:
1) download all .py files
2) find local ip address (on mac, `ifconfig en0`) 
3) in network.py and server.py, replace the `server` variable with the ip address as string
4) in one terminal window run `python3 server.py`
5) in two others (not necessarily on the same machine), run `python3 client.py`
6) play rock paper scissors!

some notes:

- hit ctrl+C to finish the server script (reason why is currently I do not know how to terminate the server nicely 
after both clients finish (best I can do now has peer disconnected or similar, and that doesn't seem great)
- there are some additional options for client.py (for running different bot version, displaying debug output, etc.)

client.py options:

- `--debug`: print some extra debugging outputs
- `--random`: run a random bot instead of taking user input