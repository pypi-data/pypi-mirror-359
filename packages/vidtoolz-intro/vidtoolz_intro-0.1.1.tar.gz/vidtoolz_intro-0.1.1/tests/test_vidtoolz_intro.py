import vidtoolz_intro as w

from argparse import ArgumentParser

import os
import pytest
from unittest.mock import patch, MagicMock


def test_create_parser():
    subparser = ArgumentParser().add_subparsers()
    parser = w.create_parser(subparser)

    assert parser is not None

    result = parser.parse_args(["hello.txt"])
    assert result.inputfile == "hello.txt"
    assert result.input is None
    assert result.output is None
    assert result.use_moviepy is False

    result = parser.parse_args(["-i" "one.mp4,1,5", "-i", "two.mp4,2,5"])
    assert result.inputfile is None
    assert result.input == ["one.mp4,1,5", "two.mp4,2,5"]
    assert result.output is None
    assert result.change_dir is None


def test_plugin(capsys):
    w.intro_plugin.hello(None)
    captured = capsys.readouterr()
    assert "Hello! This is an example ``vidtoolz`` plugin." in captured.out


@patch("vidtoolz_intro.VideoFileClip")  # Mocking VideoFileClip
@patch("vidtoolz_intro.concatenate_videoclips")  # Mocking concatenate function
def test_process_video_clips(mock_concat, mock_video):
    mock_clip = MagicMock()
    mock_video.return_value = mock_clip
    mock_concat.return_value = mock_clip

    input_data = "video1.mp4,0,5\nvideo2.mp4,3,8"

    result = w.process_video_clips(input_data)

    # Ensure clips were concatenated
    mock_concat.assert_called_once()


def test_determine_output_path():
    input_file = "/path/to/input/video.mp4"

    # Case 1: output_file is None
    expected = "/path/to/input/video_intro.mp4"
    assert w.determine_output_path(input_file, None) == expected

    # Case 2: output_file is an absolute path
    output_file = "/path/to/output/final.mp4"
    expected = output_file
    assert w.determine_output_path(input_file, output_file) == expected

    # Case 3: output_file has only filename (same directory as input_file)
    output_file = "final.mp4"
    expected = "/path/to/input/final.mp4"
    assert w.determine_output_path(input_file, output_file) == expected
