from datetime import datetime, timezone

from app.providers.gmail import GmailProvider


class FakeRequest:
    def __init__(self, value):
        self.value = value

    def execute(self):
        return self.value


class FakeMessages:
    def __init__(self):
        self.pages = [
            {"messages": [{"id": "one"}], "nextPageToken": "next"},
            {"messages": [{"id": "two"}]},
        ]
        self.page = 0
        self.full = {
            "one": {"id": "one", "threadId": "thread", "labelIds": [], "payload": {"headers": [{"name": "From", "value": "customer@example.com"}, {"name": "To", "value": "me@example.com"}, {"name": "Date", "value": "Mon, 01 Sep 2026 10:00:00 +0000"}, {"name": "Subject", "value": "Quote"}], "body": {"data": ""}, "parts": [{"mimeType": "text/plain", "body": {"data": "Please send a quote"}}]}},
            "two": {"id": "two", "threadId": "thread", "labelIds": ["SENT"], "payload": {"headers": [{"name": "From", "value": "me@example.com"}, {"name": "To", "value": "customer@example.com"}], "body": {"data": ""}, "parts": [{"mimeType": "text/html", "body": {"data": "PGI+VGhhbmsgeW91PC9iPg=="}}]}},
        }

    def list(self, **kwargs):
        value = self.pages[self.page]
        self.page += 1
        return FakeRequest(value)

    def get(self, userId, id, format):
        return FakeRequest(self.full[id])


class FakeUsers:
    def __init__(self):
        self.messages_api = FakeMessages()

    def getProfile(self, userId):
        return FakeRequest({"emailAddress": "me@example.com"})

    def messages(self):
        return self.messages_api


class FakeService:
    def __init__(self):
        self.users_api = FakeUsers()

    def users(self):
        return self.users_api


def test_fetch_messages_reads_all_pages_and_detects_outgoing():
    provider = GmailProvider()
    provider.service = FakeService()
    provider.account_email = "me@example.com"

    result = provider.fetch_messages(datetime.now(timezone.utc))

    assert [message.id for message in result] == ["one", "two"]
    assert result[0].is_outgoing is False
    assert result[1].is_outgoing is True
    assert result[1].body == "Thank you"
    assert result[0].recipients == ["me@example.com"]
