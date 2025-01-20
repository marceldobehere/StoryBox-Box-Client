# StoryBox-Box-Client
Box Client for StoryBox for the Raspberry PI


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


## Make Audio Mono
Incase your device only has one speaker on the left side, you can edit the audio config to make it mono:


Edit your asound config file
```
sudo nano /home/marcel/.asoundrc
```

And make it the following:
```
pcm.card0 {
  type hw
  card 0
}

ctl.card0 {
  type hw
  card 0
}

pcm.monocard {
  slave.pcm card0
  slave.channels 2
#  type plug
  type route
  ttable {
    # Copy both input channels to output channel 0 (Left).
    0.0 1
    1.0 1
    # Send nothing to output channel 1 (Right).
    0.1 0
    1.1 0
  }
}

ctl.monocard {
  type hw
  card 0
}

pcm.!default monocard
```


Thats it
