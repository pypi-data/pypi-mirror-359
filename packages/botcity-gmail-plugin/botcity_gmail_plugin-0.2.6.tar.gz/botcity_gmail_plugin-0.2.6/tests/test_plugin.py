import os
import pytest

from botcity.plugins.gmail import BotGmailPlugin, SearchBy


def test_send_message(bot: BotGmailPlugin, tmp_file: str, subject: str) -> None:
    # Defining the attributes that will compose the message
    to = [os.getenv("GOOGLE_GMAIL")]
    cc = [os.getenv("GOOGLE_GMAIL")]
    subject = subject
    body = "Hello! This is a test message!"
    files = [tmp_file]
    bot.send_message(subject, body, to, cc, attachments=files, use_html=False)


@pytest.mark.depends(name="test_send_message")
def test_search_message(bot: BotGmailPlugin, tmp_file: str, subject: str):
    messages = bot.search_messages(criteria=f"subject:{subject}+1")
    assert len(messages) == 0
    messages = bot.search_messages(criteria=f"subject:{subject}")
    assert len(messages) == 1


@pytest.mark.depends(name="test_search_message")
def test_reply(bot: BotGmailPlugin, tmp_file: str, subject: str):
    messages = bot.search_messages(criteria=f"subject:{subject}")
    for message in messages:
        bot.reply(msg=message, attachments=[tmp_file], text_content="Hey!", to_addrs=[os.getenv("GOOGLE_GMAIL")])
        print(message)
    messages = bot.search_messages(criteria=f"subject:{subject}")
    assert messages[0].subject == f"Re: {subject}"


@pytest.mark.depends(name="test_reply")
def test_reply_to_all(bot: BotGmailPlugin, tmp_file: str, subject: str):
    messages = bot.search_messages(criteria=f"subject:{subject}")
    bot.reply_to_all(msg=messages[0], attachments=[tmp_file], text_content="Hey reply to all!")
    messages = bot.search_messages(criteria=f"subject:{subject}")
    assert messages[0].subject == f"Re: Re: {subject}"


@pytest.mark.depends(name="test_reply_to_all")
def test_forward(bot: BotGmailPlugin, subject: str):
    messages = bot.search_messages(criteria=f"subject:{subject}")
    bot.forward(msg=messages[-1], to_addrs=[os.getenv("GOOGLE_GMAIL")])
    messages = bot.search_messages(criteria=f"Fwd: {subject}")
    assert messages[0].subject == f"Fwd: {subject}"


@pytest.mark.depends(name="test_forward")
def test_delete(bot: BotGmailPlugin, subject: str):
    messages = bot.search_messages(criteria=f"Fwd: {subject}")
    for message in messages:
        bot.delete(msg=message)
    messages = bot.search_messages(criteria=f"Fwd: {subject}")
    assert len(messages) == 0


def test_download_attachment(bot: BotGmailPlugin, subject: str, tmp_folder: str, tmp_file: str):
    os.remove(tmp_file)
    messages = bot.search_messages(criteria=f"subject:{subject}")
    bot.download_attachments(msg=messages[0], download_folder_path=tmp_folder)
    assert os.path.exists(path=f"{tmp_folder}/{messages[0].attachments[0].filename}")


def test_mark_as_read(bot: BotGmailPlugin, subject: str):
    messages = bot.search_messages(criteria=f"subject:{subject}")
    bot.mark_as_read(msg=messages[0])
    messages = bot.search_messages(criteria=f"subject:{subject}")
    assert "UNREAD" not in messages[0].labels


@pytest.mark.depends(name="test_mark_as_read")
def test_mark_as_unread(bot: BotGmailPlugin, subject: str):
    messages = bot.search_messages(criteria=f"subject:{subject}")
    bot.mark_as_unread(msg=messages[0])
    messages = bot.search_messages(criteria=f"subject:{subject}")
    assert "UNREAD" in messages[0].labels


def test_create_new_label(bot: BotGmailPlugin, subject: str):
    bot.create_new_label(label_name=subject)


@pytest.mark.depends(name="test_create_new_label")
def test_get_mail_labels(bot: BotGmailPlugin, subject: str):
    labels = bot.get_mail_labels()
    assert isinstance(labels, list)
    labels = [label for label in labels if label['name'] == subject]
    assert len(labels) > 0


@pytest.mark.depends(name="test_create_new_label")
def test_add_labels_to_message(bot: BotGmailPlugin, subject: str):
    messages = bot.search_messages(criteria=f"subject:{subject}")
    bot.add_labels_to_message(msg=messages[0], customized_labels=[subject])
    messages = bot.search_messages(criteria=f"subject:{subject}")
    labels = [label for label in messages[0].labels if label == subject]
    assert len(labels) > 0


@pytest.mark.depends(name="test_add_labels_to_message")
def test_remove_labels_to_message(bot: BotGmailPlugin, subject: str):
    messages = bot.search_messages(criteria=f"subject:{subject}")
    bot.remove_labels_from_message(msg=messages[0], customized_labels=[subject])
    messages = bot.search_messages(criteria=f"subject:{subject}")
    labels = [label for label in messages[0].labels if label == subject]
    assert len(labels) == 0


@pytest.mark.depends(name="test_remove_labels_to_message")
def test_get_label(bot: BotGmailPlugin, subject: str):
    label = bot.get_label(by=SearchBy.NAME, value=subject)
    assert isinstance(label, dict)
    assert label.get("name") == subject
    label_id = label.get("id")
    label = bot.get_label(by=SearchBy.ID, value=label.get("id"))
    assert isinstance(label, dict)
    assert label.get("id") == label_id


@pytest.mark.depends(name="test_get_label")
def test_delete_label(bot: BotGmailPlugin, subject: str):
    label = bot.get_label(by=SearchBy.NAME, value=subject)
    bot.delete_label(label_id=label.get("id"))


def test_get_label_id_error(bot: BotGmailPlugin):
    with pytest.raises(ValueError):
        labels = bot.get_mail_labels()
        bot._get_label_id(label_name="testing", mail_labels=labels)


def test_get_label_id(bot: BotGmailPlugin):
    labels = bot.get_mail_labels()
    label_id = bot._get_label_id(label_name="INBOX", mail_labels=labels)
    assert label_id == "INBOX"
