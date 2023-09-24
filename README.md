# Discord IPA Dumper

Script to dump Discord IPAs from a jailbroken iOS device
using [frida-ios-dump](https://github.com/miticollo/frida-ios-dump)
and upload them to a Discord webhook.

Disclaimer: I made this for [Enmity](https://enmity.app), to serve my own specific needs.
Feel free to edit this program as needed.

Originally, this was much more complex, stripping out personal information and using SSH over USB
with the [old version of frida-ios-dump](https://github.com/miticollo/frida-ios-dump/tree/legacy).
Since then, miticollo has released a much better version based on Frida's own CLI tooling,
so my code no longer has to do much heavy lifting.

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

Frida must also be installed on your jailbroken iOS device(s).

## Running

1. Plug your jailbroken iOS device into your computer.
2. Make sure you have installed the version of Discord that you want to dump.
3. From this folder on your computer, run `python3 main.py`.
4. Follow the prompts and wait for it to finish.

## Customizing

Any part of this can be edited if you'd like to use this
but don't have the same requirements as I do.