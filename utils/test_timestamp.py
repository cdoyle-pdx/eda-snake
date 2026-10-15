from utils import timestamp

INPUT_TIMESTAMPS_1 = ["2023-12-24T20:59:09.5Z", "2023-12-24T20:58:57.748Z"]
INPUT_TIMESTAMPS_2 = ["2023-12-23T20:56:42.7Z", "2023-12-24T21:58:57.748Z"]
INPUT_TIMESTAMPS_3 = ["2023-12-25T20:56:42.7Z", "2023-12-24T21:58:57.748Z"]
INPUT_TIMESTAMPS_4 = ["2024-12-25T20:56:42.7Z", "2023-12-24T21:58:57.748Z"]
INPUT_TIMESTAMPS_5 = ["2024-01-25T20:56:42.7Z", "2023-12-24T21:58:57.748Z"]
INPUT_TIMESTAMPS_6 = ["2024-01-25T20:56:42.7Z", "2025-12-27T21:58:57.928Z", "2023-12-24T21:58:57.748Z"]


def test_get_normalized_timestamp():
    """Sanity test for function standardize_timestamp"""
    assert timestamp.get_normalized_timestamp("2023-12-24T20:59:09.5Z") == "2023-12-24T20:59:09.500Z"
    assert timestamp.get_normalized_timestamp("2023-12-24T20:58:57.748Z") == "2023-12-24T20:58:57.748Z"
    assert timestamp.get_normalized_timestamp("2024-12-24T20:58:57.900Z") == "2024-12-24T20:58:57.900Z"


def test_most_recent_timestamp():
    """Sanity test for function most_recent_timestamp"""
    assert timestamp.most_recent_timestamp(INPUT_TIMESTAMPS_1) == "2023-12-24T20:59:09.500Z"
    assert timestamp.most_recent_timestamp(INPUT_TIMESTAMPS_2) == "2023-12-24T21:58:57.748Z"
    assert timestamp.most_recent_timestamp(INPUT_TIMESTAMPS_3) == "2023-12-25T20:56:42.700Z"
    assert timestamp.most_recent_timestamp(INPUT_TIMESTAMPS_4) == "2024-12-25T20:56:42.700Z"
    assert timestamp.most_recent_timestamp(INPUT_TIMESTAMPS_5) == "2024-01-25T20:56:42.700Z"
    assert timestamp.most_recent_timestamp(INPUT_TIMESTAMPS_6) == "2025-12-27T21:58:57.928Z"


if __name__ == "__main__":
    test_get_normalized_timestamp()
    test_most_recent_timestamp()
