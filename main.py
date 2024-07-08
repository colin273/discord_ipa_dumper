import argparse
import os
import sys
from pathlib import Path
from typing import List
from zipfile import ZipFile
import plistlib
from argparse import ArgumentParser, ArgumentError

from dotenv import load_dotenv

from frida_ios_dump.decrypter import DecrypterApplication

from upload import upload_ipa


def rename_ipa(ipa_path: Path, is_testflight: bool) -> tuple[Path, str, str]:
    print("Renaming IPA...")
    with ZipFile(ipa_path) as ipa_zip:
        # Technically I should search through the zip file's structure
        # in case this ever needs to work for other apps besides Discord
        # Meh
        with ipa_zip.open("Payload/Discord.app/Info.plist", "r") as info_plist:
            # Get version info from Info.plist
            info_contents = plistlib.load(info_plist)
            app_name = info_contents["CFBundleDisplayName"]
            version_number = info_contents["CFBundleShortVersionString"]
            build_id = info_contents["CFBundleVersion"]

            # Construct new IPA filename from info
            new_ipa_name = f"{app_name}_{version_number}"
            if is_testflight:
                new_ipa_name += f"_{build_id}"
            new_ipa_name += ".ipa"

            # Rename IPA
            new_ipa_path = ipa_path.joinpath("..", new_ipa_name).resolve()
            os.rename(ipa_path, new_ipa_path)
            print("IPA renamed.")

            return new_ipa_path, version_number, build_id


class DiscordDumperApplication(DecrypterApplication):
    def __init__(self):
        self.is_testflight = False  # May be overridden with args
        super().__init__()

    def _add_options(self, parser: argparse.ArgumentParser) -> None:
        # Custom arguments for which branch of Discord this is, stable or TestFlight
        # Application errors if both of these are provided or missing
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("-s", "--stable", action="store_true")
        group.add_argument("-t", "--testflight", action="store_true")
        super()._add_options(parser)

    def _initialize(self, parser: argparse.ArgumentParser, options: argparse.Namespace, args: List[str]) -> None:
        self.is_testflight = options.testflight  # Only true if stable is false, and vice versa
        super()._initialize(parser, options, args)

    def _exit(self, exit_status: int) -> None:
        # Intercept exiting if successful to process the IPA further.
        # Have to intercept _exit because frida-ios-dump doesn't use _stop.
        if exit_status == 0:
            # Rename output IPA with build ID
            cwd_path = Path(os.getcwd())
            ipa_name = f"{self._bundle_id}_{self._version}.ipa"
            new_ipa_path, version, build = rename_ipa(cwd_path / ipa_name, self.is_testflight)

            upload_ipa(new_ipa_path, self.is_testflight, version, build)
            os.remove(new_ipa_path)

        super()._exit(exit_status)


def main():
    # Environment variables specify webhook URLs
    load_dotenv()

    # Patching sys.argv is terribly hacky, but it works
    # Custom arguments are handled in the application class
    sys.argv += ["-U", "-f", "com.hammerandchisel.discord"]

    # Decrypt the app with Frida over USB
    DiscordDumperApplication().run()


if __name__ == '__main__':
    main()
