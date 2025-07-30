"""
Tests for the parsing functions.
"""

import json

from tests.conftest import get_fixture
from yt_meta import parsing
from yt_meta.parsing import (
    extract_and_parse_json,
    extract_shorts_from_renderers,
)


def test_placeholder():
    """A placeholder test to ensure the test runner discovers this file."""
    assert True


def test_find_ytcfg(channel_page):
    """
    Tests that the ytcfg data can be extracted from a raw HTML string.
    """
    ytcfg = parsing.find_ytcfg(channel_page)
    assert isinstance(ytcfg, dict)
    assert "INNERTUBE_API_KEY" in ytcfg
    assert ytcfg.get("INNERTUBE_CLIENT_NAME") == "WEB"


def test_extract_and_parse_json():
    """
    Tests that a JSON blob can be extracted from a script tag in an HTML string.
    """
    html_with_json = (
        '<html><body><script>var myVar = {"key": "value"};</script></body></html>'
    )
    data = parsing.extract_and_parse_json(html_with_json, "myVar")
    assert data == {"key": "value"}


def test_parse_duration():
    """
    Tests that duration labels are correctly parsed into seconds.
    """
    assert parsing.parse_duration("11 minutes, 6 seconds") == 666
    assert parsing.parse_duration("1 hour, 30 minutes, 5 seconds") == 5405
    assert parsing.parse_duration("5 seconds") == 5
    assert parsing.parse_duration(None) is None
    assert parsing.parse_duration("") is None


def test_parse_view_count():
    """
    Tests that view count strings are correctly parsed into integers.
    """
    assert parsing.parse_view_count("2,905,010 views") == 2905010
    assert parsing.parse_view_count("1 view") == 1
    assert parsing.parse_view_count("No views") is None
    assert parsing.parse_view_count(None) is None
    assert parsing.parse_view_count("") is None


def test_find_like_count():
    """
    Tests that the like count can be extracted from player response data.
    """
    player_response_data = {
        "microformat": {"playerMicroformatRenderer": {"likeCount": "12345"}}
    }
    assert parsing.find_like_count(player_response_data) == 12345
    assert parsing.find_like_count({}) is None


def test_find_heatmap():
    """
    Tests that the heatmap data can be extracted from the initial data.
    """
    initial_data = {
        "frameworkUpdates": {
            "entityBatchUpdate": {
                "mutations": [
                    {
                        "payload": {
                            "macroMarkersListEntity": {
                                "markersList": [
                                    {
                                        "value": {
                                            "macroMarkersMarkersListRenderer": {
                                                "contents": [
                                                    {
                                                        "marker": {
                                                            "heatmapMarker": {
                                                                "timeRangeStartMarker": {
                                                                    "markerDurationFromStartMillis": "1000"
                                                                },
                                                                "markerDurationMillis": "2000",
                                                                "intensityScoreNormalized": 0.5,
                                                            }
                                                        }
                                                    }
                                                ]
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    }
                ]
            }
        }
    }
    heatmap = parsing.find_heatmap(initial_data)
    assert isinstance(heatmap, list)
    assert len(heatmap) == 1
    assert heatmap[0]["startMillis"] == "1000"
    assert heatmap[0]["durationMillis"] == "2000"
    assert heatmap[0]["intensityScoreNormalized"] == 0.5
    assert parsing.find_heatmap({}) is None


def test_extract_videos_from_renderers_no_continuation(youtube_channel_video_renderers):
    """
    Tests that video data can be extracted from a list of video renderers.
    """
    videos, continuation_token = parsing.extract_videos_from_renderers(
        youtube_channel_video_renderers
    )
    assert isinstance(videos, list)
    assert len(videos) > 0
    assert "video_id" in videos[0]
    assert continuation_token is None


def test_extract_videos_from_renderers_with_continuation(youtube_channel_initial_data):
    """
    Tests that video data can be extracted from a list of video renderers.
    """
    renderers = youtube_channel_initial_data["contents"][
        "twoColumnBrowseResultsRenderer"
    ]["tabs"][1]["tabRenderer"]["content"]["richGridRenderer"]["contents"]
    videos, continuation_token = parsing.extract_videos_from_renderers(renderers)
    assert isinstance(videos, list)
    assert len(videos) > 0
    assert "video_id" in videos[0]
    assert continuation_token is not None


def test_parse_channel_metadata(bulwark_channel_initial_data):
    """
    Tests that channel metadata can be parsed correctly from the initial data.
    """
    metadata = parsing.parse_channel_metadata(bulwark_channel_initial_data)
    assert metadata is not None
    assert metadata["title"] == "The Bulwark"
    assert isinstance(metadata["description"], str)
    assert len(metadata["description"]) > 0
    assert metadata["channel_id"] == "UCG4Hp1KbGw4e02N7FpPXDgQ"
    assert "bulwarkmedia" in metadata["vanity_url"]
    assert isinstance(metadata["is_family_safe"], bool)


def test_parse_video_metadata(initial_data, player_response_data):
    metadata = parsing.parse_video_metadata(player_response_data, initial_data)
    assert metadata["video_id"] == "B68agR-OeJM"
    assert (
        metadata["title"] == "Metrik & Linguistics | Live @ Hospitality Printworks 2023"
    )
    assert metadata["channel_name"] == "Hospital Records"
    assert metadata["channel_id"] == "UCw49uOTAJjGUdoAeUcp7tOg"
    assert metadata["duration_seconds"] == 3582
    assert int(metadata["view_count"]) > 300000
    assert metadata["publish_date"] == "2023-06-19T11:00:10-07:00"
    assert metadata["category"] == "Music"
    assert isinstance(metadata["view_count"], int)
    assert metadata["view_count"] > 300000
    assert metadata["like_count"] >= 4613  # Like count may increase over time
    assert isinstance(metadata["keywords"], list)
    assert isinstance(metadata["thumbnails"], list)
    assert len(metadata["thumbnails"]) > 0
    first_thumbnail = metadata["thumbnails"][0]
    assert "url" in first_thumbnail
    assert "width" in first_thumbnail
    assert "height" in first_thumbnail
    assert isinstance(metadata["full_description"], str)
    assert "Printworks London" in metadata["full_description"]
    assert isinstance(metadata["heatmap"], list)
    assert isinstance(metadata["subscriber_count_text"], str)
    assert (
        "subscribers" in metadata["subscriber_count_text"]
    )  # Count may change over time


def test_extract_shorts_from_renderers():
    html = get_fixture("mr_beast_shorts_page.html")
    initial_data = extract_and_parse_json(html, "ytInitialData")

    # This is a deep path, specific to finding the shorts data
    tabs = initial_data["contents"]["twoColumnBrowseResultsRenderer"]["tabs"]
    shorts_tab = next(
        tab for tab in tabs if tab.get("tabRenderer", {}).get("title") == "Shorts"
    )
    renderers = shorts_tab["tabRenderer"]["content"]["richGridRenderer"]["contents"]

    videos, continuation_token = extract_shorts_from_renderers(renderers)

    assert len(videos) > 0
    assert continuation_token is not None


def test_extract_videos_from_renderers():
    renderers = json.loads(get_fixture("aimakerspace_channel_video_renderers.json"))
    videos, continuation = parsing.extract_videos_from_renderers(renderers)

    assert len(videos) == 30
    assert continuation is None


# def test_extract_videos_from_renderers_with_continuation():
#     renderers = json.loads(get_fixture("continuation_fixture.json"))
#     videos, continuation_token = parsing.extract_videos_from_renderers(renderers)

#     assert len(videos) == 1
#     assert continuation_token == "some_continuation_token"
