from unittest.mock import MagicMock

from discord_utils.images import format_attachment_data


def _make_attachment(content_type, url="http://example.com/img.png"):
    att = MagicMock()
    att.content_type = content_type
    att.url = url
    return att


class TestFormatAttachmentData:
    def test_no_attachments(self):
        msg = MagicMock()
        msg.attachments = []
        assert format_attachment_data(msg) == []

    def test_single_image(self):
        msg = MagicMock()
        msg.attachments = [_make_attachment("image/png", "http://example.com/a.png")]
        result = format_attachment_data(msg)
        assert len(result) == 2  # instruction text + 1 image block

    def test_multiple_images(self):
        msg = MagicMock()
        msg.attachments = [
            _make_attachment("image/png", "http://example.com/a.png"),
            _make_attachment("image/jpeg", "http://example.com/b.jpg"),
        ]
        result = format_attachment_data(msg)
        assert len(result) == 3  # instruction text + 2 image blocks

    def test_non_image_ignored(self):
        msg = MagicMock()
        msg.attachments = [_make_attachment("application/pdf")]
        assert format_attachment_data(msg) == []

    def test_mixed_attachments(self):
        msg = MagicMock()
        msg.attachments = [
            _make_attachment("image/png", "http://example.com/a.png"),
            _make_attachment("application/pdf"),
        ]
        result = format_attachment_data(msg)
        assert len(result) == 2  # instruction text + 1 image block

    def test_none_content_type_skipped(self):
        msg = MagicMock()
        msg.attachments = [_make_attachment(None)]
        assert format_attachment_data(msg) == []

    def test_image_block_structure(self):
        url = "http://example.com/photo.png"
        msg = MagicMock()
        msg.attachments = [_make_attachment("image/png", url)]
        result = format_attachment_data(msg)
        image_block = result[1]
        assert image_block == {
            "type": "image",
            "source": {
                "type": "url",
                "url": url,
            },
        }

    def test_instruction_text_prepended(self):
        msg = MagicMock()
        msg.attachments = [_make_attachment("image/png")]
        result = format_attachment_data(msg)
        assert result[0]["type"] == "text"
        assert "image" in result[0]["text"].lower()
