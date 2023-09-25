import os
import sys
from pathlib import Path
from zipfile import ZipFile
import plistlib

from dotenv import load_dotenv

from frida_ios_dump.decrypter import DecrypterApplication

from upload import upload_ipa
from user_prompt import user_choice


def rename_ipa(ipa_path: Path, is_testflight: bool) -> tuple[Path, str, str]:
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

            return new_ipa_path, version_number, build_id


class DiscordDumperApplication(DecrypterApplication):
    def _exit(self, exit_status: int) -> None:
        # Intercept exiting if successful to process the IPA further
        if exit_status == 0:
            is_testflight = bool(user_choice("Is this a TestFlight build?", ["No", "Yes"]))

            # Rename output IPA with build ID
            cwd_path = Path(os.getcwd())
            ipa_name = f"{self._bundle_id}_{self._version}.ipa"
            new_ipa_path, version, build = rename_ipa(cwd_path / ipa_name, is_testflight)

            try:
                upload_ipa(new_ipa_path, is_testflight, version, build)
                os.remove(new_ipa_path)
            except Exception as err:
                print(err.__traceback__)
                print(f"Failed to upload {new_ipa_path.name}. Please upload manually.")

        super()._exit(exit_status)


def main():
    # Environment variables specify webhook URLs
    load_dotenv()

    # Patching sys.argv is terribly hacky, but it works
    sys.argv += ["-U", "-f", "com.hammerandchisel.discord"]

    # Decrypt the app with Frida over USB
    app = DiscordDumperApplication()
    app.run()


if __name__ == '__main__':
    main()
