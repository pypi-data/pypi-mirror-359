"""
Module to easily parse the audio.
"""
from yta_audio_base.converter import AudioConverter
from yta_audio_base.types import AudioType, validate_parameter_with_type


class AudioParser:
    """
    Class to simplify the way we parse audios.
    """

    @staticmethod
    def as_audioclip(
        audio: AudioType
    ) -> 'AudioClip':
        """
        Get the audio as a 'moviepy' AudioClip.
        """
        validate_parameter_with_type(AudioType, 'audio', audio, True)
        
        return AudioConverter.to_audioclip(audio).content
    
    @staticmethod
    def as_audiosegment(
        audio: AudioType
    ) -> 'AudioSegment':
        """
        Get the audio as a 'pydub' AudioSegment.
        """
        validate_parameter_with_type(AudioType, 'audio', audio, True)

        return AudioConverter.to_audiosegment(audio).content
    
    # TODO: '.as_numpy()' ? It is difficult due to rate
    # or strange mapping... (?)