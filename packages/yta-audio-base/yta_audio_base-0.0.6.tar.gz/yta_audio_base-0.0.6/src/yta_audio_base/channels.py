from yta_audio_base.parser import AudioParser
from yta_audio_base.types import AudioType
from yta_constants.multimedia import DEFAULT_SCENE_WIDTH
from yta_constants.enum import YTAEnum as Enum
from yta_constants.file import FileType
from yta_validation.parameter import ParameterValidator
from yta_programming.decorators.requires_dependency import requires_dependency
from yta_programming.output import Output
from yta_file.filename import FilenameHandler

from typing import Union


class AudioChannel(Enum):
    """
    Simple Enum class to handle the audio channels
    easier.
    """

    LEFT = 1
    RIGHT = 0

# TODO: Refactor this and move to a class
def isolate_audio_channel(
    audio: AudioType,
    channel: AudioChannel = AudioChannel.LEFT,
    output_filename: Union[str, None] = None
):
    """
    Gets the provided 'audio' and isolates it to he given 'channel' onlye (that can
    be left or right). It will be stored as a local file if 'output_filename' 
    provided, and will return the new isolated audio as a pydub AudioSegment.
    """
    audio = AudioParser.as_audiosegment(audio)
    channel = AudioChannel.to_enum(channel)

    channel_pan = (
        -1.0
        if channel == AudioChannel.LEFT else
        1.0
    )
    
    audio = adjust_audio_channels(audio, channel_pan, None, 0, audio.duration_seconds * 1000)

    if output_filename:
        output_filename = Output.get_filename(output_filename, FileType.AUDIO)
        # TODO: Is this ok? or do I need the '.' in the
        # extension (?)
        audio.export(out_f = output_filename, format = FilenameHandler.get_extension(output_filename))

    return audio

def apply_8d_effect(
    audio: AudioType
):
    """
    Generates a 8d sound effect by splitting the 'audio'' into multiple 
    smaller pieces, pans each piece to make the sound source seem like 
    it is moving from L to R and R to L in loop, decreases volume towards
    center position to make the movement sound like it is a circle 
    instead of straight line.
    """
    audio = AudioParser.as_audiosegment(audio)

    SCREEN_SIZE = DEFAULT_SCENE_WIDTH
    NUM_OF_PARTS = 80
    AUDIO_PART_SCREEN_SIZE = SCREEN_SIZE / NUM_OF_PARTS
    AUDIO_PART_TIME = audio.duration_seconds * 1000 / NUM_OF_PARTS

    cont = 0
    while ((cont * AUDIO_PART_TIME) < audio.duration_seconds * 1000):
        coordinate = cont * AUDIO_PART_SCREEN_SIZE
        channel_pan = x_coordinate_to_channel_pan(coordinate)
        volume_adjustment = 5 - (abs(channel_pan) / NUM_OF_PARTS) * 5

        start_time = cont * AUDIO_PART_TIME
        end_time = (cont + 1) * AUDIO_PART_TIME
        # I do this because of a small error that makes it fail
        if end_time > audio.duration_seconds * 1000:
            end_time = audio.duration_seconds * 1000
        audio = adjust_audio_channels(audio, channel_pan, volume_adjustment, start_time, end_time)
        cont += 1

    return audio

def x_coordinate_to_channel_pan(
    x: int
):
    """
    This method calculates the corresponding channel pan value (between -1.0 and
    1.0) for the provided "x" coordinate (in an hypotetic scene of 1920x1080).
    This means that an "x" of 0 will generate a -1.0 value, and an "x" of 1919
    will generate a 1.0 value. Values out of limits (lower than 0 or greater
    than 1919) will be set as limit values (0 and 1919).

    This method has been created to be used in transition effects sounds, to be
    dynamically panned to fit the element screen position during the movement.
    """
    ParameterValidator.validate_mandatory_int('x', x)
    
    x = (
        0
        if x < 0 else
        DEFAULT_SCENE_WIDTH - 1
        if x > (DEFAULT_SCENE_WIDTH - 1) else
        x
    )

    return -1.0 + (x * 2.0 / DEFAULT_SCENE_WIDTH - 1)

def adjust_audio_channels(
    audio: AudioType,
    channel_pan: float = 0.0,
    volume_gain: float = 1.0,
    start_time: Union[float, None] = None,
    end_time: Union[float, None] = None
):
    """
    This method allows you to set the amount of 'audio' you want to be
    sounding on each of the 2 channels (speakers), right and left. The
    'channel_pan' parameter must be a value between -1.0, which means
    left channel, and 1.0, that means right channel. A value of 0 means
    that the sound will sound equally in left and right channel. A value
    of 0.5 means that it will sound 25% in left channel and 75% in right
    channel.

    The 'volume_gain', if 0, puts the fragment in silence. If 1, it has
    the same volume. If 2, the volume is twice.

    This method will apply the provided 'channel_pan' to the also provided
    'audio'. The 'start_time' and 'end_time' parameters determine the part
    of the audio you want the channel panning to be applied, and it is in
    seconds.
    """
    # -1.0 is left, 1.0 is right
    ParameterValidator.validate_mandatory_number_between('channel_pan', channel_pan, -1.0, 1.0)
    ParameterValidator.validate_mandatory_float('volume_gain', volume_gain)
    ParameterValidator.validate_positive_float('start_time', start_time)
    ParameterValidator.validate_positive_float('end_time', end_time)

    audio = AudioParser.as_audiosegment(audio)

    start_time = (
        0
        if not start_time else
        start_time
    )
    end_time = (
       audio.duration_seconds * 1000
       if not end_time else
       end_time 
    )

    if start_time > audio.duration_seconds * 1000:
        raise Exception('The "start_time" cannot be greater than the actual "audio" duration.')
    
    if start_time > end_time:
        raise Exception('The "start_time" cannot be greater than the "end_time".')
    
    if end_time > audio.duration_seconds * 1000:
        raise Exception('The "end_time" cannot be greater than the actual "audio" duration.')

    # Process the part we want
    modified_part = audio[start_time: end_time]
    modified_part = (
        # We minimize the audio (x3) if lower to 1
        modified_part - abs(modified_part.dBFS * (1 - volume_gain) * 3)
        if volume_gain < 1 else
        modified_part + abs(modified_part.dBFS * (volume_gain - 1))
    )
    modified_part = modified_part.pan(channel_pan)

    audio = (
        modified_part
        if (
            start_time == 0 and
            end_time == audio.duration_seconds * 1000
        ) else
        modified_part + audio[end_time: audio.duration_seconds * 1000]
        if start_time == 0 else
        audio[0: start_time] + modified_part
        if end_time == audio.duration_seconds * 1000 else
        audio[0: start_time] + modified_part + audio[end_time: audio.duration_seconds * 1000]
    )

    return audio

@requires_dependency('yta_multimedia_core', 'yta_audio_base', 'yta_multimedia_core')
@requires_dependency('moviepy', 'yta_audio_base', 'moviepy')
def get_audio_synchronized_with_video_by_position(
    audio: AudioType,
    video: Union[str, 'Clip']
):
    """
    This method iterates over the whole provided 'video' and uses its
    position in each frame to synchronize that position with the also
    provided 'audio' that will adjust its pan according to it.

    This method returns the audio adjusted as a pydub AudioSegment.
    """
    # TODO: This can make a cyclic import issue, but I
    # preserve the code by now because the functionality
    # was working and interesting
    from yta_multimedia_core.video.parser import VideoParser
    from moviepy.Clip import Clip

    audio = AudioParser.as_audiosegment(audio)
    # TODO: We cannot be using a VideoParser in this
    # lib, it will be a cyclic import issue
    video = VideoParser.to_moviepy(video)

    frames_number = int(video.fps * video.duration)
    frame_duration = video.duration / frames_number

    # I need to know the minimum x below 0 and the maximum above 1919
    minimum_x = 0
    maximum_x = DEFAULT_SCENE_WIDTH - 1
    for i in range(frames_number):
        t = frame_duration * i
        # We want the center of the video to be used
        video_x = video.pos(t)[0] + video.w / 2
        if video_x < 0 and video_x < minimum_x:
            minimum_x = video_x
        if video_x > (DEFAULT_SCENE_WIDTH - 1) and video_x > maximum_x:
            maximum_x = video_x

    for i in range(frames_number):
        t = frame_duration * i
        video_x = video.pos(t)[0] + video.w / 2

        # I want to make it sound always and skip our exception limits
        volume_gain = 1
        if video_x < 0:
            volume_gain -= abs(video_x / minimum_x)
            video_x = 0
        elif video_x > (DEFAULT_SCENE_WIDTH - 1):
            volume_gain -= abs((video_x - (DEFAULT_SCENE_WIDTH - 1)) / (maximum_x - (DEFAULT_SCENE_WIDTH - 1)))
            video_x = (DEFAULT_SCENE_WIDTH - 1)

        audio = adjust_audio_channels(audio, x_coordinate_to_channel_pan(video_x), volume_gain, t * 1000, (t + frame_duration) * 1000)

    return audio

@requires_dependency('moviepy', 'yta_audio_base', 'moviepy')
def synchronize_audio_pan_with_video_by_position(
    audio: AudioType,
    video: Union[str, 'Clip']
):
    """
    This method synchronizes the provided 'video' with the also provided
    'audio' by using its position to adjust the pan.

    This method returns the provided 'video' with the new audio 
    synchronized.
    """
    # TODO: This was .to_audiofileclip() before,
    # remove this comment if working
    return video.with_audio(AudioParser.as_audioclip(get_audio_synchronized_with_video_by_position(audio, video)))