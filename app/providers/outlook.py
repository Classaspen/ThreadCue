from .base import MailProvider


class OutlookProvider(MailProvider):
    """Reserved for phase two."""

    def authenticate(self) -> bool:
        raise NotImplementedError("Outlook support is planned for phase two")

    def fetch_messages(self, since):
        raise NotImplementedError("Outlook support is planned for phase two")
