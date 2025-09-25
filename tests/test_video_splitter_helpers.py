import types


def _make_window(qapp):
    from video_splitter import VideoSplitterWindow
    return VideoSplitterWindow(None)


def test_convert_time_to_seconds(qapp):
    w = _make_window(qapp)
    assert w.convert_time_to_seconds("10") == 10
    assert w.convert_time_to_seconds("01:02") == 62
    assert w.convert_time_to_seconds("1:02:03") == 3723


def test_safe_filename_sanitization(qapp):
    w = _make_window(qapp)
    s = w._safe_filename('abc:/\\*?"<>|  name   ')
    assert "\n" not in s
    assert ":" not in s and "|" not in s
    assert s.startswith("abc") and s.endswith("name")


def test_ensure_final_segment_appends_end_marker(qapp, monkeypatch, tmp_path):
    w = _make_window(qapp)
    # Pretend duration is 100 seconds
    monkeypatch.setattr(w, "_get_video_duration", lambda _: 100.0)
    chapters = [(0, "A"), (30, "B"), (90, "C")]
    out = w._ensure_final_segment(str(tmp_path/"v.mp4"), chapters)
    assert out[-1][0] == 100  # end marker added


def test_ensure_final_segment_no_duplicate_end(qapp, monkeypatch, tmp_path):
    w = _make_window(qapp)
    monkeypatch.setattr(w, "_get_video_duration", lambda _: 100.0)
    chapters = [(0, "A"), (50, "B"), (100, "End")]
    out = w._ensure_final_segment(str(tmp_path/"v.mp4"), chapters)
    assert out[-1][0] == 100 and len(out) == 3


def test_build_ffmpeg_cmd_variants(qapp, tmp_path):
    from video_splitter import _SplitWorker
    video = str(tmp_path/"in.mp4")
    dest = str(tmp_path)
    worker = _SplitWorker(video_file=video, chapters=[(0, "A"), (10, "End")], dest_dir=dest, accurate=False)
    cmd = worker._build_ffmpeg_cmd(0, 10, str(tmp_path/"A.mp4"))
    assert "-c" in cmd and "copy" in cmd
    worker2 = _SplitWorker(video_file=video, chapters=[(0, "A"), (10, "End")], dest_dir=dest, accurate=True)
    cmd2 = worker2._build_ffmpeg_cmd(0, 10, str(tmp_path/"A.mp4"))
    assert "libx264" in cmd2

