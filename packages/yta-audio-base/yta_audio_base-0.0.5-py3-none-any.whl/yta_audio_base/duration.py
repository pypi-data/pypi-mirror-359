"""
TODO: Refactor this because it is only accepting
audio filenames and not binary or other type of
audios.
"""
from yta_audio_base.converter import AudioConverter
from yta_audio_base.types import AudioType
from yta_programming.decorators.requires_dependency import requires_dependency
from yta_programming.output import Output
from yta_validation.parameter import ParameterValidator
from yta_constants.file import FileType
from pydub.effects import speedup
from typing import Union


def crop_pydub(
    # TODO: Apply the correct type
    audio: AudioType,
    start: Union[float, None] = None,
    duration: Union[float, None] = None,
    output_filename: Union[str, None] = None
) -> any:
    """
    Using 'pydub'.

    Crop the provided 'audio' to start in the
    given 'start' and to last the also provided
    'duration' (in seconds).
    """
    ParameterValidator.validate_positive_float('start', start)
    ParameterValidator.validate_positive_float('duration', duration)

    audio = AudioConverter.to_audiosegment(audio)
    end = start + duration
    # Check that the 'end' is valid
    end = (
        audio.duration_seconds
        if end > audio.duration_seconds else
        end
    )
    audio = audio[start:end]

    if output_filename is not None:
        # TODO: Check the format and use the right one
        audio.export(Output.get_filename(output_filename, FileType.AUDIO), format = 'mp3')

    return audio

@requires_dependency('moviepy', 'yta_audio_base', 'moviepy')
def crop_moviepy(
    # TODO: Apply the correct type
    audio: AudioType,
    start: Union[float, None] = None,
    duration: Union[float, None] = None,
    output_filename: Union[str, None] = None
) -> any:
    """
    Using 'moviepy'.

    Crop the provided 'audio' to start in the
    given 'start' and to last the also provided
    'duration' (in seconds).
    """
    ParameterValidator.validate_positive_float('start', start)
    ParameterValidator.validate_positive_float('duration', duration)

    audio = AudioConverter.to_audioclip(audio)
    end = start + duration

    # Check that the 'end' is valid
    end = (
        audio.duration
        if end > audio.duration else
        end
    )
    audio = audio.with_duration(start + end)
    
    if output_filename is not None:
        # TODO: Check the format and use the right one
        audio.write_audiofile(Output.get_filename(output_filename, FileType.AUDIO))

    return audio

# TODO: Are these methods working and also
# working to make them longer not only
# shorter (?)
def speedup_pydub(
    # TODO: Apply the correct type
    audio: AudioType,
    duration: Union[float, None] = None,
    output_filename: Union[str, None] = None
) -> any:
    """
    Using 'pydub'.

    Speedup the given 'audio' to make it have
    the also provide 'duration'.
    """
    ParameterValidator.validate_positive_float('duration', duration)

    audio = AudioConverter.to_audiosegment(audio)

    if duration <= audio.duration_seconds:
        # The chunk_size is optional but is the size of
        # chunks in milliseconds for processing. Smaller
        # chunks means better pitch preservation but
        # longer processing time.
        audio = speedup(audio, speed_factor = audio.duration_seconds / duration, chunk_size = 150) 

    if output_filename is not None:
        # TODO: Check the format and use the right one
        audio.export(Output.get_filename(output_filename, FileType.AUDIO), format = 'mp3')

    return audio

# TODO: This is not working yet
@requires_dependency('moviepy', 'yta_audio_base', 'moviepy')
def speedup_moviepy(
    # TODO: Apply the correct type
    audio: AudioType,
    duration: Union[float, None] = None,
    output_filename: Union[str, None] = None
) -> any:
    """
    Using 'moviepy'.

    Speedup the given 'audio' to make it have
    the also provide 'duration'.
    """
    ParameterValidator.validate_positive_float('duration', duration)

    audio = AudioConverter.to_audioclip(audio)

    if duration <= audio.duration:
        # TODO: Apply the Speedup effect
        # There is no 'AccelDecel' or 'SpeedUp'
        # effect for the 'afx', so I think we 
        # need to use the vfx.AccelDecel
        audio = audio.with_effects([vfx.AccelDecel(duration)])
#        audio = audio.with_effects(audio_speedx, audio.duration / duration)

    if output_filename is not None:
        # TODO: Check the format and use the right one
        audio.export(Output.get_filename(output_filename, FileType.AUDIO), format = 'mp3')

    return audio