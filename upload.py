import os
from hashlib import file_digest
from pathlib import Path
from discord import SyncWebhook, File

KILOBYTE = 1024
HUNDRED_MB = 100 * (KILOBYTE**2)


def sha256_hash(file_path: Path) -> str:
    """
    Gets the SHA256 hash of a file
    """
    # https://stackoverflow.com/a/44873382
    with open(file_path, "rb", buffering=0) as fd:
        return file_digest(fd, "sha256").hexdigest()


def upload_direct(ipa_path: Path, webhook: SyncWebhook):
    """
    Uploads the IPA directly to a webhook as an attachment.

    :param ipa_path: IPA path
    :param webhook: Webhook to upload to
    """
    with open(ipa_path, "rb") as fp:
        # Ignore the warning about `fp`'s type; `discord.py`'s typedef is a bit wrong
        ipa_file = File(fp, filename=os.path.basename(fp.name))

        print("Uploading {filename} to webhook...".format(filename=ipa_file.filename))

        try:
            webhook.send(file=ipa_file)
            print("Finished uploading file")
            os.remove(ipa_path)
        except Exception as e:
            print(e)
            print("Uploading to webhook failed, trying indirect method.")
            upload_indirect(ipa_path, webhook)


def upload_indirect(ipa_path: Path, webhook: SyncWebhook):
    """
    Uploads the IPA to a server and then sends the link to the webhook.
    Also includes the SHA256 hash for verification purposes.
    :param ipa_path: Path to the IPA
    :param webhook: Webhook to upload to
    """
    raise NotImplementedError("Uploading indirectly is not implemented yet.")


# Upload IPA to a channel
# Actually needs two webhooks, one for each channel (#stable and #testflight)
def upload_ipa(ipa_path: Path, is_testflight: bool):
    """
    Uploads the IPA to a Discord webhook.

    :param ipa_path: Path to the IPA
    :param is_testflight: Whether this IPA should go to the TestFlight webhook instead of stable
    """
    webhook_url_varname = "{branch}_WEBHOOK_URL".format(branch=("TESTFLIGHT" if is_testflight else "STABLE"))
    webhook = SyncWebhook.from_url(os.getenv(webhook_url_varname))

    ipa_size = ipa_path.stat().st_size

    if ipa_size > HUNDRED_MB:  # Too big to upload directly
        upload_indirect(ipa_path, webhook)
    else:
        upload_direct(ipa_path, webhook)
