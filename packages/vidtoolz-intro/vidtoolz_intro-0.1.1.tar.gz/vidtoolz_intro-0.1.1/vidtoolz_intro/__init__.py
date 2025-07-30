import vidtoolz
import os
from moviepy import concatenate_videoclips, VideoFileClip
import vidtoolz_trim as vt
import vidtoolz_concat as vc
import tempfile
from moviepy.tools import convert_to_seconds


def determine_output_path(input_file, output_file):
    input_dir, input_filename = os.path.split(input_file)
    name, _ = os.path.splitext(input_filename)

    if output_file:
        output_dir, output_filename = os.path.split(output_file)
        if not output_dir:  # If no directory is specified, use input file's directory
            return os.path.join(input_dir, output_filename)
        return output_file
    else:
        return os.path.join(input_dir, f"{name}_intro.mp4")


def _trim_with_ffmpeg(i, video_name, start_time, end_time):
    tmpdir = tempfile.gettempdir()
    outfilefile = os.path.join(tmpdir, f"{video_name}-{i}_trim.mp4")
    _ = vt.trim_video(video_name, outfilefile, start_time, end_time)
    return outfilefile


def make_intro_with_ffmpeg(input_data, output, folder=None):
    video_clips = []
    if isinstance(input_data, str):
        lines = input_data.strip().split("\n")
    else:
        lines = input_data

    # Parse the input data into a list of tuples (video_name, start_time, end_time)
    for i, line in enumerate(lines, 1):
        parts = line.split(",")
        if len(parts) != 3:
            raise ValueError(f"Invalid input format: {line}")

        if folder is not None:
            video_name = os.path.join(folder, parts[0].strip())
        else:
            video_name = parts[0].strip()

        start_time = convert_to_seconds(parts[1].strip())
        end_time = convert_to_seconds(parts[2].strip())

        outfilefile = _trim_with_ffmpeg(i, video_name, start_time, end_time)
        video_clips.append(outfilefile)

    # now make video using concat
    iret = vc.make_video(video_clips, output)
    if iret == 0:
        # remove temporary *_trim clips
        for vid in video_clips:
            os.remove(vid)


def process_video_clips(input_data):

    video_clips = []
    if isinstance(input_data, str):
        lines = input_data.strip().split("\n")
    else:
        lines = input_data

    # Parse the input data into a list of tuples (video_name, start_time, end_time)
    vids = []
    for i, line in enumerate(lines, 1):
        parts = line.split(",")
        if len(parts) != 3:
            raise ValueError(f"Invalid input format: {line}")

        video_name = parts[0].strip()
        start_time = convert_to_seconds(parts[1].strip())
        end_time = convert_to_seconds(parts[2].strip())

        # Load the video and clip it
        outfilefile = _trim_with_ffmpeg(i, video_name, start_time, end_time)
        vids.append(outfilefile)
        clip = VideoFileClip(outfilefile)

        video_clips.append(clip)

    # Concatenate all clips together
    final_clip = concatenate_videoclips(video_clips)

    return final_clip, vids


def write_file(final_clip, output):
    # Write the output to a new file
    final_clip.write_videofile(output, codec="libx264", audio_codec="aac")
    final_clip.close()


def create_parser(subparser):
    parser = subparser.add_parser(
        "intro", description="Create intro video from a series of videos"
    )
    parser.add_argument(
        "inputfile",
        type=str,
        default=None,
        help="Text file containg. IMG102.mov,1,5\n IMG200.mov,2,4",
        nargs="?",
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        action="append",
        help="Input like  IMG102.mov,1,5 or like IMGA.mov,1:06,1:20",
    )
    parser.add_argument(
        "-o", "--output", type=str, default=None, help="Output filename, default None"
    )
    parser.add_argument(
        "-cd",
        "--change-dir",
        type=str,
        default=None,
        help="if Provided, go to this folder, before anything.",
    )

    parser.add_argument(
        "-um",
        "--use-moviepy",
        action="store_true",
        help="if Provided, use moviepy for intro else use ffmpeg.",
    )
    return parser


def write_textfile(textlist, outpath_tx):
    with open(outpath_tx, "w") as fout:
        fout.write("\n".join(textlist))


class ViztoolzPlugin:
    """Create intro video from a series of videos"""

    __name__ = "intro"

    @vidtoolz.hookimpl
    def register_commands(self, subparser):
        self.parser = create_parser(subparser)
        self.parser.set_defaults(func=self.run)

    def run(self, args):

        if args.input is None and args.inputfile is None:
            self.parser.error("Inputor input file must be specified.")

        if args.change_dir is not None:
            os.chdir(args.change_dir)
            folder = args.change_dir

        if args.input is not None:
            output = determine_output_path(args.input[0], args.output)
        else:
            output = determine_output_path(args.inputfile, args.output)

        if args.inputfile:
            with open(args.inputfile, "r") as fin:
                data = fin.read()
            folder = os.path.dirname(args.inputfile)
        elif args.input:
            data = args.input
            text_output = f"{output}.txt"
            write_textfile(data, text_output)

        if args.use_moviepy:
            final_clip, vids = process_video_clips(data)
            write_file(final_clip, output)
            # Remove vids
            for vid in vids:
                os.remove(vid)
        else:
            _ = make_intro_with_ffmpeg(data, output, folder)

    def hello(self, args):
        # this routine will be called when "vidtoolz "intro is called."
        print("Hello! This is an example ``vidtoolz`` plugin.")


intro_plugin = ViztoolzPlugin()
