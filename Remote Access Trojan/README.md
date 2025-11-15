# Workflow:

- Start target_streaming.cpp on target computer
- Note that this must be started with admin permissions (e.g. sudo) to use the live_stream functionality
- Start remote_access.py, replace the IP in the file with the IP of the target computer
- You are now ready to make inputs to the system

## Commands:

Just typing alone will send the text as keystrokes to the system. To use specific commands:

- cmd, runs a command in the terminal that remote_access_target.py was started in (cmd ls)
- browser, opens a website in the default browser (browser https://google.com)
- key, simulates a key press (key enter)
- hotkey, simulates a complex key press (hotkey alt+ctrl+t)

## Live stream (Outdated):

Run live_stream_cpp.py to view the live feed from the target machine. Press f2 to toggle mouse mirroring. 
