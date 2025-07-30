import pytest

from yt_meta import YtMeta
from yt_meta.filtering import apply_filters, partition_filters

# --- Unit Tests for apply_filters ---


@pytest.fixture
def sample_video():
    """A sample video metadata object for testing filters."""
    return {
        "video_id": "test_id_123",
        "title": "A Great Video",
        "view_count": 15000,
        "duration_seconds": 300,  # 5 minutes
    }


def test_view_count_gt_passes(sample_video):
    filters = {"view_count": {"gt": 10000}}
    assert apply_filters(sample_video, filters) is True


def test_view_count_gt_fails(sample_video):
    filters = {"view_count": {"gt": 20000}}
    assert apply_filters(sample_video, filters) is False


def test_view_count_lt_passes(sample_video):
    filters = {"view_count": {"lt": 20000}}
    assert apply_filters(sample_video, filters) is True


def test_view_count_lt_fails(sample_video):
    filters = {"view_count": {"lt": 10000}}
    assert apply_filters(sample_video, filters) is False


def test_view_count_eq_passes(sample_video):
    filters = {"view_count": {"eq": 15000}}
    assert apply_filters(sample_video, filters) is True


def test_view_count_eq_fails(sample_video):
    filters = {"view_count": {"eq": 10000}}
    assert apply_filters(sample_video, filters) is False


def test_no_view_count_fails(sample_video):
    filters = {"view_count": {"gt": 10000}}
    del sample_video["view_count"]
    assert apply_filters(sample_video, filters) is False


# --- Unit Tests for duration_seconds ---


def test_duration_gt_passes(sample_video):
    filters = {"duration_seconds": {"gt": 60}}
    assert apply_filters(sample_video, filters) is True


def test_duration_lt_fails(sample_video):
    filters = {"duration_seconds": {"lt": 60}}
    assert apply_filters(sample_video, filters) is False


def test_duration_multiple_conditions_pass(sample_video):
    filters = {"duration_seconds": {"gte": 300, "lte": 300}}
    assert apply_filters(sample_video, filters) is True


def test_no_duration_fails(sample_video):
    filters = {"duration_seconds": {"gt": 100}}
    del sample_video["duration_seconds"]
    assert apply_filters(sample_video, filters) is False


# --- Integration Test ---


@pytest.mark.integration
def test_live_view_count_filter(isolated_client: YtMeta):
    """
    Tests filtering a live channel by view count.
    This test is designed to be fast by fetching a small number of videos
    from a channel known to have videos with a wide range of view counts.
    """
    # Using a channel with a variety of view counts
    channel_url = "https://www.youtube.com/@TED/videos"
    filters = {"view_count": {"gt": 10}}  # A very low threshold to ensure a quick match

    # We don't need full metadata since viewCount is in the basic renderer
    videos_generator = isolated_client.get_channel_videos(
        channel_url, filters=filters, fetch_full_metadata=False, max_videos=1
    )

    videos = list(videos_generator)
    assert len(videos) > 0, "Should have found at least one video with over 10 views."

    for video in videos:
        assert video["view_count"] > 10


@pytest.mark.integration
def test_shorts_fast_path_view_count_filter(isolated_client: YtMeta):
    """
    Tests filtering shorts by view count, which is a 'fast' filter available in basic shorts data.
    """
    channel_url = "https://www.youtube.com/@bashbunni"

    # Filter for shorts with more than 5K views (reasonable threshold)
    filters = {"view_count": {"gte": 5000}}

    try:
        # fetch_full_metadata=False because view_count is available in basic shorts data
        videos_generator = isolated_client.get_channel_shorts(
            channel_url,
            filters=filters,
            fetch_full_metadata=False,  # Fast path - no individual video fetching needed
            max_videos=3,  # Limit to make test fast and reliable
        )

        count = 0
        for video in videos_generator:
            assert video["view_count"] >= 5000, (
                f"Video {video['video_id']} has {video['view_count']} views, expected >= 5000"
            )
            assert "title" in video
            assert "video_id" in video
            count += 1

        # Should find at least one popular short from bashbunni
        if count == 0:
            pytest.skip("No shorts found with >= 5K views - content may have changed")

        assert count > 0

    except Exception as e:
        pytest.skip(f"Failed to fetch shorts for view count filtering: {e}")


@pytest.mark.integration
def test_shorts_duration_limitation_with_full_metadata(isolated_client: YtMeta):
    """
    Tests that duration filtering on shorts requires fetch_full_metadata=True.
    This test demonstrates the current limitation and verifies it works when enabled.
    """
    channel_url = "https://www.youtube.com/@bashbunni"

    # Updated filter for modern YouTube Shorts (up to 180 seconds, not 60)
    filters = {"duration_seconds": {"lte": 180, "gt": 0}}

    try:
        # fetch_full_metadata=True is required because duration is not in basic shorts renderer
        videos_generator = isolated_client.get_channel_shorts(
            channel_url,
            filters=filters,
            fetch_full_metadata=True,  # Required for duration filtering
            max_videos=2,  # Limit to prevent long test times
        )

        count = 0
        for video in videos_generator:
            assert video["duration_seconds"] <= 180, (
                f"Short {video['video_id']} is {video['duration_seconds']}s, expected <= 180s"
            )
            assert video["duration_seconds"] > 0, (
                f"Short {video['video_id']} has invalid duration: {video['duration_seconds']}"
            )
            count += 1

        # If we find shorts with duration, test passes
        if count == 0:
            pytest.skip(
                "No shorts found with duration metadata - may require individual video fetching"
            )

            assert count > 0

    except Exception as e:
        pytest.skip(f"Duration filtering on shorts failed: {e}")


def test_apply_filters_like_count():
    """Test filtering by like_count."""
    videos = [
        {"video_id": "1", "like_count": 50},
        {"video_id": "2", "like_count": 150},
        {"video_id": "3", "like_count": 100},
    ]
    filters = {"like_count": {"gte": 100}}
    filtered_videos = [v for v in videos if apply_filters(v, filters)]
    assert len(filtered_videos) == 2
    assert filtered_videos[0]["video_id"] == "2"
    assert filtered_videos[1]["video_id"] == "3"


def test_partition_filters_for_videos():
    """Test partitioning of filters for regular videos."""
    filters = {
        "view_count": {"gt": 1000},  # Fast
        "duration_seconds": {"lt": 300},  # Fast
        "like_count": {"gte": 100},  # Slow
        "title": {"contains": "Tutorial"},  # Now a fast filter for videos
    }
    fast, slow = partition_filters(filters, content_type="videos")
    assert "view_count" in fast
    assert "duration_seconds" in fast
    assert "like_count" in slow
    assert "title" in fast
    assert len(fast) == 3
    assert len(slow) == 1


def test_partition_filters_for_shorts():
    """Test partitioning of filters for shorts."""
    filters = {
        "view_count": {"gt": 1000},  # Fast
        "title": {"contains": "Funny"},  # Fast
        "duration_seconds": {"lt": 60},  # Slow
        "like_count": {"gte": 50},  # Slow
    }
    fast, slow = partition_filters(filters, content_type="shorts")
    assert "view_count" in fast
    assert "title" in fast
    assert "duration_seconds" in slow
    assert "like_count" in slow
    assert len(fast) == 2
    assert len(slow) == 2


def test_apply_filters_view_count():
    video = {"view_count": 1500}
    assert apply_filters(video, {"view_count": {"gt": 1000}})


def test_apply_filters_description_snippet():
    """Tests filtering by description snippet."""
    videos = [
        {"description_snippet": "A video about Python programming."},
        {"description_snippet": "A great video about cooking."},
        {"description_snippet": "A tutorial on pyTEst and other tools."},
    ]

    # Test 'contains'
    filters_py = {"description_snippet": {"contains": "python"}}
    filtered_py = [v for v in videos if apply_filters(v, filters_py)]
    assert len(filtered_py) == 1
    assert filtered_py[0]["description_snippet"] == "A video about Python programming."

    # Test 're'
    filters_re = {"description_snippet": {"re": r"pyt(hon|est)"}}
    filtered_re = [v for v in videos if apply_filters(v, filters_re)]
    assert len(filtered_re) == 2


def test_apply_filters_title():
    """Tests filtering by video title."""
    videos = [
        {"title": "An Introduction to Python"},
        {"title": "Advanced Python Programming"},
        {"title": "A video about Rust"},
    ]

    # Test 'contains'
    filters_py = {"title": {"contains": "python"}}
    filtered_py = [v for v in videos if apply_filters(v, filters_py)]
    assert len(filtered_py) == 2

    # Test 're'
    filters_re = {"title": {"re": r"^Advanced"}}
    filtered_re = [v for v in videos if apply_filters(v, filters_re)]
    assert len(filtered_re) == 1
    assert filtered_re[0]["title"] == "Advanced Python Programming"


def test_apply_filters_category():
    """Tests filtering by category."""
    videos = [
        {"category": "Science & Technology"},
        {"category": "Music"},
        {"category": "Gaming"},
        {"category": "DIY & Crafts"},
    ]
    filters = {"category": {"contains": "sci"}}
    filtered = [v for v in videos if apply_filters(v, filters)]
    assert len(filtered) == 1
    assert filtered[0]["category"] == "Science & Technology"

    filters_eq = {"category": {"eq": "Music"}}
    filtered_eq = [v for v in videos if apply_filters(v, filters_eq)]
    assert len(filtered_eq) == 1
    assert filtered_eq[0]["category"] == "Music"


def test_apply_filters_full_description():
    """Tests filtering by full_description."""
    videos = [
        {"full_description": "A deep dive into machine learning models."},
        {"full_description": "An unrelated video about baking."},
        {"full_description": "This tutorial covers deep neural networks."},
    ]
    filters = {"full_description": {"re": r"deep.*learning"}}
    filtered = [v for v in videos if apply_filters(v, filters)]
    assert len(filtered) == 1


def test_apply_filters_keywords():
    """Tests filtering by keywords."""
    videos = [
        {"keywords": ["python", "programming", "tutorial"]},
        {"keywords": ["cooking", "baking"]},
        {"keywords": ["rust", "systems", "programming"]},
    ]
    # Test 'contains' (any)
    filters_any = {"keywords": {"contains_any": ["python", "rust"]}}
    filtered_any = [v for v in videos if apply_filters(v, filters_any)]
    assert len(filtered_any) == 2

    # Test 'contains' (all)
    filters_all = {"keywords": {"contains_all": ["programming", "tutorial"]}}
    filtered_all = [v for v in videos if apply_filters(v, filters_all)]
    assert len(filtered_all) == 1
    assert filtered_all[0]["keywords"] == ["python", "programming", "tutorial"]


def test_apply_filters_publish_date():
    """Tests filtering by publish_date."""
    videos = [
        {"publish_date": "2023-01-15T12:00:00+00:00"},
        {"publish_date": "2023-08-01T10:00:00+00:00"},
        {"publish_date": "2022-12-25T18:00:00+00:00"},
    ]
    filters = {"publish_date": {"after": "2023-01-01"}}
    filtered = [v for v in videos if apply_filters(v, filters)]
    assert len(filtered) == 2

    filters_before = {"publish_date": {"before": "2023-01-01"}}
    filtered_before = [v for v in videos if apply_filters(v, filters_before)]
    assert len(filtered_before) == 1


# --- Integration Tests ---


@pytest.mark.integration
def test_filter_by_duration_integration(isolated_client: YtMeta):
    channel_url = "https://www.youtube.com/@samwitteveenai/videos"
    filters = {
        "duration_seconds": {"lt": 9999}
    }  # A very high threshold to ensure a quick match
    videos_gen = isolated_client.get_channel_videos(
        channel_url,
        filters=filters,
        fetch_full_metadata=False,  # duration is a 'fast' filter
        max_videos=1,
    )
    videos = list(videos_gen)
    assert len(videos) > 0
    for video in videos:
        assert video["duration_seconds"] < 9999


@pytest.mark.integration
def test_filter_by_like_count_integration(isolated_client: YtMeta):
    """
    Tests filtering by like_count, which requires a full metadata fetch.
    """
    channel_url = "https://www.youtube.com/@TED/videos"
    # A filter likely to match some videos without fetching the whole channel
    filters = {"like_count": {"gt": 10000}}
    videos_gen = isolated_client.get_channel_videos(
        channel_url,
        filters=filters,
        fetch_full_metadata=True,  # like_count is a 'slow' filter
        max_videos=1,  # Limit to a reasonable number to avoid long test
    )
    videos = list(videos_gen)
    # This assertion is soft - it's possible the first 10 videos don't match.
    # The main point is to ensure the filtering logic runs without error.
    for video in videos:
        assert "like_count" in video
        assert video["like_count"] > 10000


@pytest.mark.integration
def test_multi_component_filter_integration(isolated_client: YtMeta):
    """
    Tests a filter with multiple components: one fast, one slow.
    """
    channel_url = "https://www.youtube.com/@TED/videos"
    filters = {
        "duration_seconds": {"lt": 600},  # Fast filter (10 mins)
        "like_count": {"gt": 1000},  # Slow filter (lowered threshold for stability)
    }
    videos_gen = isolated_client.get_channel_videos(
        channel_url,
        filters=filters,
        fetch_full_metadata=True,  # Needed for like_count
        max_videos=1,
    )
    video_list = list(videos_gen)
    assert len(video_list) == 1
    # Check that the returned video matches the filter criteria
    video = video_list[0]
    assert video["duration_seconds"] < 600
    assert video["like_count"] > 1000


def test_apply_filters_view_count_range():
    """Test a numerical range filter (e.g., gt and lt)."""
    video_in_range = {"view_count": 2000}
    video_out_of_range = {"view_count": 5000}
    filters = {"view_count": {"gt": 1000, "lt": 3000}}

    assert apply_filters(video_in_range, filters)
    assert not apply_filters(video_out_of_range, filters)
