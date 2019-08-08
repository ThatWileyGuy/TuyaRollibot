## Credit

The Tuya REST interface was basically forked from https://github.com/sean6541/tuyaapi . I modified it to do phone logon and stripped out a lot of client metadata that Tuya doesn't seem to require, but the original structure and all the crypto comes from there.

## Configuration

You need to write a config file (I'll call it config.cfg). It needs to look like this:

```
[TuyaAccess]
Id = aaaaaaaaaa # Tuya access ID
Key = aaaaaaaaa # Tuya access Key

# As far as I could find, Tuya only gives API access IDs and keys to developers
# in mainland China. I ended up "borrowing" mine from the Rollibot app, which helpfully
# logs them to ADB. No need to root the phone.

[TuyaCredentials]
User = 1111111111 # Tuya/Rollibot username (for me this was my phone number)
Password = aaaaaaaaaa # Tuya/Rollibot password
```

## Usage

Once you have your config (config.cfg for example purposes)...

`./localkeys.py config.cfg` will print the local keys for all your devices

`./thermostat.py config.cfg "Office AC" 72` will run a basic thermostat state machine to keep the Office AC (this is the name that shows up in the Rollibot app) close to 72 degrees.


Note that these are all using the cloud APIs. I'm poking at local control now that I have my local keys, but I'll likely be doing that in C#.
