from unittest.mock import MagicMock, patch

import llm

from llm_yt_transcript import yt_transcript_loader, get_log_level


def test_yt_transcript_loader():
    # Mock the dependencies of yt_transcript_loader
    mock_subtitles = """<tt xmlns=\"http://www.w3.org/ns/ttml\">
    <body>
        <div>
            <p begin=\"00:00:01.000\" end=\"00:00:04.000\">This is a test subtitle.</p>
        </div>
    </body>
    </tt>"""

    mock_parser = MagicMock()
    mock_parser.to_text.return_value = "This is a test subtitle."

    with (
        patch("llm_yt_transcript.download_subtitles") as mock_download,
        patch("llm_yt_transcript.TtmlParser", return_value=mock_parser),
    ):
        mock_download.return_value.read_text.return_value = mock_subtitles

        fragment = yt_transcript_loader("some_video_id")

        assert isinstance(fragment[0], llm.Fragment)
        assert fragment[0].source == "some_video_id"
        assert str(fragment[0]) == "This is a test subtitle."


def test_get_log_level():
    with patch("os.getenv", return_value="debug"):
        assert get_log_level() == "debug"

    with patch("os.getenv", return_value="info"):
        assert get_log_level() == "info"

    with patch("os.getenv", return_value="warning"):
        assert get_log_level() == "warning"

    with patch("os.getenv", return_value="error"):
        assert get_log_level() == "error"

    with patch("os.getenv", return_value="critical"):
        assert get_log_level() == "critical"

    with patch("os.getenv", return_value="unknown"):
        try:
            get_log_level()
        except ValueError as e:
            assert str(e) == "Unknown log mode: unknown. Valid options: debug, info, warning, error, critical"
