# Discord IPA Dumper

Script to dump Discord IPAs from an iOS device and upload them to the web.

The script does the following:

1. Extract the IPA from a jailbroken iOS device using [frida-ios-dump](https://github.com/miticollo/frida-ios-dump).
2. Upload the IPA over SFTP to the VPS hosting https://ipa.aspy.dev.
3. Send the link to a Discord webhook with the version number.

You must specify in CLI arguments whether the IPA is from the App Store or TestFlight.
This decides the webhook URL and whether the version information includes the build number (for TestFlight only).

> [!WARNING]
> I made this for my own purposes, to provide Discord IPAs for [Enmity](https://enmity.unbound.rip).
> If you'd like to use this for your own IPA extraction purposes, then feel free to edit the script as needed.
> I've tried to make it reasonably modular.
> However, I cannot guarantee support.

## Installing

Required CLIs:

- [git](https://git-scm.com)
- [Python 3](https://python.org)

Clone this repository with submodules:

```shell
git clone --recurse-submodules https://github.com/colin273/discord_ipa_dumper
```

Install dependencies:

```shell
pip install -r requirements.txt
```

Using `.env.example` as a template, create a new `.env` in this directory.
The variables are:

- `STABLE_WEBHOOK_URL`: webhook URL for uploading stable IPAs
- `TESTFLIGHT_WEBHOOK_URL`: webhook URL for uploading TestFlight IPAs
- `VPS_HOSTNAME`: hostname or IP address of the VPS that hosts the IPAs
- `VPS_PORT`: SSH port for the VPS
- `VPS_USERNAME`: username for your account on the VPS

Install Frida your jailbroken iOS device(s) from [Frida's tweak repository](https://build.frida.re).

## Running

1. Plug your jailbroken iOS device into your computer.
2. Install the version of Discord that you want to extract.
3. From this folder on your computer, run `python3 main.py` followed by either `-s` (for stable) or `-t` (for TestFlight).
4. Wait for the script to finish extracting and uploading the IPA.

## Credits

Thank you to:

- [Lorenzo Ferron](https://github.com/miticollo) for the [fork of frida-ios-dump](https://github.com/miticollo/frida-ios-dump) that powers decryption in this script
- [AloneMonkey](https://github.com/AloneMonkey) for the [original](https://github.com/AloneMonkey/frida-ios-dump) frida-ios-dump
- [Frida's developers](https://frida.re) for the reverse engineering tools that make this possible
- [Aiden](https://aspy.dev) for hosting the IPAs I upload