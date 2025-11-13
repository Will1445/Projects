# Workflow:

- Start remote_access_target.py file on target computor
- Start remote_access.py in terminal, replace the IP in the file with the IP of the target computor
- You are now ready to make inputs to the system

## Commands:

Just typing alone will send the text as keystrokes to the system. To use specific commands:

- cmd, runs a command in the terminal that remote_access_target.py was started in (cmd ls)
- browser, opens a website in the default browser (browser https://google.com)
- key, simulates a key press (key enter)
- hotkey, simulates a complex key press (hotkey alt+ctrl+t)

## Live stream (Outdated):

For a live view of the target system, ensure the correct screen width and height are set in live_stream_target and run live_stream_target.py on the target computor using: 

cmd sudo nohup /path to python file/python live_stream_target.py &

(ensure that you cd to the correct directory). Now run live_stream.py in a seperate terminal, the connection should establish and appear. To begin mirroring the mouse and mouse clicks, press f2 and the same to stop. Press q to quit the streaming.


## Debugging:

To view processes currently running on a given port run this on the target computor:

sudo lsof -i :5000 (for port 5000)

And to force kill any processes running:

sudo kill -9 <PID> 


## Problems to fix:

- Currently cannot start live_stream_target.py using remote_access.py, it must be started manually on the target computor 
- live_stream_target.py currently requires sudo to run properly otherwise it cannot detect the mouse or keyboard as inputs 
- Additionally, as this is required for the keylogger, you cannot obtain the sudo password to run live_stream_target.py yet

