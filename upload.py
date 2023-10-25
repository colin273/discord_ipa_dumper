import os
from hashlib import file_digest
from pathlib import Path
from shlex import quote

from discord import SyncWebhook, File
from paramiko import SSHClient

# Assume the Discord server is boosted to level 3.
# 100 MiB is the file upload limit for everyone without $10 Nitro,
# including webhooks.
KILOBYTE = 1024
HUNDRED_MB = 100 * (KILOBYTE**2)


def sha256_hash(file_path: Path) -> str:
    """
    Gets the SHA256 hash of a file

    :param file_path: Path to file
    :return: SHA256 hash
    """
    # https://stackoverflow.com/a/44873382
    with open(file_path, "rb", buffering=0) as fd:
        return file_digest(fd, "sha256").hexdigest()


def upload_direct(ipa_path: Path, webhook: SyncWebhook, is_testflight: bool, version: str, build: str):
    """
    Uploads the IPA directly to a webhook as an attachment.

    :param ipa_path: IPA path
    :param webhook: Webhook to upload to
    :param is_testflight: Whether the IPA is from TestFlight (for indirect upload fallback)
    :param version: Version number (for indirect fallback)
    :param build: Build ID (for indirect fallback)
    """
    with open(ipa_path, "rb") as fp:
        # Ignore the warning about `fp`'s type; `discord.py`'s typedef is a bit wrong
        ipa_file = File(fp, filename=os.path.basename(fp.name))

        print(f"Uploading {ipa_file.filename} to webhook...")

        try:
            webhook.send(file=ipa_file)
            print("Finished uploading file")
        except Exception as e:
            print(e)
            print("Uploading to webhook failed, trying indirect method.")
            upload_indirect(ipa_path, webhook, is_testflight, version, build)


def upload_indirect(ipa_path: Path, webhook: SyncWebhook, is_testflight: bool, version: str, build: str):
    """
    Uploads the IPA to a server and then sends the link to the webhook.
    Also includes the SHA256 hash for verification purposes.

    :param ipa_path: Path to the IPA
    :param webhook: Webhook to upload to
    :param is_testflight: Whether the IPA is from TestFlight
    :param version: Version number
    :param build: Build ID
    """

    vps_host = os.getenv("VPS_HOSTNAME")
    vps_port = int(os.getenv("VPS_PORT"))
    vps_user = os.getenv("VPS_USERNAME")
    vps_pass = os.getenv("VPS_PASSWORD")

    print("Starting upload to VPS...")

    # Create SSH/SFTP client
    client = SSHClient()
    client.load_system_host_keys()
    client.connect(hostname=vps_host, port=vps_port, username=vps_user)

    # File structure on the VPS
    # /
    #   home/
    #     <username>/
    #       [Discord_###.ipa will initially be uploaded to this folder]
    #       ipa/  <-- Root folder of IPA web service (need sudo to modify files)
    #         discord/
    #           stable/
    #           testflight/
    # Example IPA URL: https://ipa.aspy.dev/discord/stable/Discord_196.0.ipa
    vps_home_path = Path("/") / "home" / vps_user
    vps_ipa_path = vps_home_path / ipa_path.name
    ipa_url_path = Path("discord") / ("testflight" if is_testflight else "stable") / ipa_path.name
    vps_dest_path = vps_home_path / "ipa" / ipa_url_path

    # Upload to home directory on VPS
    sftp_session = client.open_sftp()
    sftp_session.put(str(ipa_path), str(vps_ipa_path))
    sftp_session.close()

    # Move IPA to appropriate folder on VPS using SSH
    client.exec_command(f"echo {quote(vps_pass)} | sudo -S mv {vps_ipa_path} {vps_dest_path}")

    # Close SSH client
    client.close()
    print("Uploaded IPA to VPS.")

    # Upload link for IPA to ipa.aspy.dev
    # SHA256 for integrity verification (in case anyone cares)
    ipa_hash = sha256_hash(ipa_path)

    # Send IPA version info, link, and hash to the webhook
    # Example message:
    # Discord 197.0 (50096)
    # https://ipa.aspy.dev/discord/testflight/Discord_197.0_50096.ipa
    # SHA256 6d60f68b250f2559ac3900db21ae255178b9bf0375c4df3e62c64ba5a6bd234f
    version_line = f"Discord {version}"
    if is_testflight:
        version_line += f" ({build})"

    message = "\n".join([
        version_line,
        f"https://ipa.aspy.dev/{ipa_url_path}",
        f"SHA256 {ipa_hash}"
    ])

    print(message)  # For me
    webhook.send(message)  # For distribution


# Upload IPA to a channel
# Actually needs two webhooks, one for each channel (#stable and #testflight)
def upload_ipa(ipa_path: Path, is_testflight: bool, version: str, build: str):
    """
    Uploads the IPA to a Discord webhook.

    :param ipa_path: Path to the IPA
    :param is_testflight: Whether this IPA should go to the TestFlight webhook instead of stable
    :param version: Version number
    :param build: Build ID
    """
    print("Uploading IPA...")
    webhook_url_varname = f'{"TESTFLIGHT" if is_testflight else "STABLE"}_WEBHOOK_URL'
    webhook = SyncWebhook.from_url(os.getenv(webhook_url_varname))

    # ipa_size = ipa_path.stat().st_size

    # File size check is no longer relevant.
    # Discord's crackdown on external usage of its CDN means that
    # uploading IPAs directly to Discord is no longer reliable for CI purposes.
    # Even if the file is small enough to upload directly,
    # an external server is more useful.
    # if ipa_size > HUNDRED_MB:  # Too big to upload directly
    upload_indirect(ipa_path, webhook, is_testflight, version, build)
    # else:
    #     upload_direct(ipa_path, webhook, is_testflight, version, build)
