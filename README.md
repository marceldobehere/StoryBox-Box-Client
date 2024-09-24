# StoryBox-Box-Client
Box Client for StoryBox


## Notes
Before you can use it:
* Install stuff: `sudo apt install python3-dev python3-pip python3-venv vlc pulseaudio`
* Activate SPI dev by doing `sudo raspi-config` and then enabling it in `Interfacing options -> SPI`
* Run `./initEnv.sh`
* Restart the device

## Running it
To run it, use the `./start.sh` file.

## Setup autostart
Open your rc.local file `sudo nano /etc/rc.local`
Add the autostart script to it. (Use a full path)

Something like this: `bash /home/marcel/StoryBox-Box-Client/autostart.sh &`

It should be pasted in at the end, but before any sort of exit commands.



Thats it