import pytest


def _make_window(qapp):
    # Lazy import inside test to avoid hard dependency at collection time
    from youtube_uploader import YouTubeUploaderWindow
    return YouTubeUploaderWindow(None)


def test_apply_yaml_basic_fields(qapp):
    w = _make_window(qapp)
    data = {
        "video": "/tmp/video.mp4",
        "title": "My Title",
        "description": "Line 1\nLine 2",
        "tags": ["a", "b", "c"],
        "category": 28,
        "privacy": "unlisted",
        "creds": "/home/user/credentials.json",
        "thumbnail": "/tmp/thumb.jpg",
    }
    w._apply_yaml(data)
    assert w.video_path.text() == data["video"]
    assert w.title_input.text() == data["title"]
    assert w.desc_input.toPlainText() == data["description"]
    assert w.tags_input.text().replace(" ", "") == "a,b,c"
    assert w.creds_path.text() == data["creds"]
    assert w.thumb_path.text() == data["thumbnail"]
    # Category ID 28 should be selected
    assert w.category_combo.currentData() == 28
    # Privacy should be set
    assert w.privacy_combo.currentText() == "unlisted"


def test_apply_yaml_aliases_and_string_tags(qapp):
    w = _make_window(qapp)
    data = {
        "video_path": "/vid.mp4",
        "desc": "d",
        "tags": "x, y, z",
        "categoryId": "27",
        "privacyStatus": "public",
        "credentials": "/c.json",
        "thumb": "/t.jpg",
    }
    w._apply_yaml(data)
    assert w.video_path.text() == "/vid.mp4"
    assert w.desc_input.toPlainText() == "d"
    assert w.tags_input.text().replace(" ", "") == "x,y,z"
    assert w.category_combo.currentData() == 27
    assert w.privacy_combo.currentText() == "public"
    assert w.creds_path.text() == "/c.json"
    assert w.thumb_path.text() == "/t.jpg"


@pytest.mark.parametrize(
    "value, expected",
    [
        ("Education", 27),
        (27, 27),
        ("28", 28),
        ("Science & Technology", 28),
    ],
)
def test_set_category_by_name_and_id(qapp, value, expected):
    w = _make_window(qapp)
    w._set_category(value)
    assert w.category_combo.currentData() == expected

