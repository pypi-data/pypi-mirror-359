from yta_audio_base.saver import AudioSaver
from yta_validation.parameter import ParameterValidator
from yta_validation import PythonValidator
from typing import Union

import numpy as np
import librosa


class Audio:
    """
    A class to wrap the audio information and
    manipulate it a bit. Check the advanced
    library ('yta_audio_advanced') to get more
    advanced functionalities.
    """

    @property
    def number_of_channels(
        self
    ) -> int:
        """
        The number of channels of the audio.
        """
        shape = self.audio.shape

        return (
            1
            if len(shape) == 1 else
            shape[1]
        )
    
    @property
    def number_of_samples(
        self
    ) -> int:
        """
        The number of samples in the audio.
        """
        return self.audio.shape[0]
    
    @property
    def duration(
        self
    ) -> int:
        """
        The duration of the audio in seconds, which
        is calculated by applying the number of
        samples divided by the sample rate:

        - number_of_samples / sample_rate
        """
        return self.number_of_samples / self.sample_rate
    
    @property
    def is_stereo(
        self
    ) -> bool:
        """
        Check if the audio is stereo (includes
        two channels) or not.
        """
        return self.number_of_channels == 2
    
    @property
    def as_mono(
        self
    ) -> 'np.ndarray':
        """
        Get the audio forced to be mono. If the
        audio is not mono it is obtained by
        averaging samples across channels.
        """
        return (
            self.audio
            if self.is_mono else
            librosa.to_mono(self.audio.T)
        )
    
    # Other properties below
    @property
    def min(
        self
    ):
        """
        Get the min value of the audio.
        """
        return np.min(np.abs(self.audio))

    @property
    def max(
        self
    ):
        """
        Get the max value of the audio.
        """
        return np.max(np.abs(self.audio))
    
    @property
    def inverted(
        self
    ) -> np.ndarray:
        """
        Get the audio but inverted as an horizontal mirror.

        TODO: Wtf is this (?)
        """
        return -self.audio
    
    @property
    def reversed(
        self
    ) -> np.ndarray:
        """
        Get the audio but reversed.
        """
        return self.audio[::-1]
    
    @property
    def normalized(
        self
    ) -> np.ndarray:
        """
        Get the audio but normalized, which means that its
        maximum value is 1.0.
        """
        max_val = np.max(np.abs(self.audio))

        return (
            self.audio / max_val
            if max_val > 0 else
            self.audio
        )

    def __init__(
        self,
        audio: 'np.ndarray', # the audio as a numpy array
        sample_rate: int = 44_100 # the sample rate
    ):
        """
        Instantiate this Audio dataclass must be
        done by providing the numpy array and the
        sample rate.
        """
        ParameterValidator.validate_mandatory_numpy_array('audio', audio)
        ParameterValidator.validate_mandatory_positive_int('sample_rate', sample_rate)

        self.audio: 'np.ndarray' = audio
        """
        The numpy array that contains the audio 
        information.
        """
        self.sample_rate: int = sample_rate
        """
        The sample rate of the audio. A None value
        means that is unknown.
        """

    def trimmed(
        self,
        start: Union[float, None],
        end: Union[float, None]
    ) -> 'Audio':
        """
        Get a new instance with the audio array modified.
        """
        self.audio = self.trim(start, end)

        return self

    def trim(
        self,
        start: Union[float, None],
        end: Union[float, None]
    ) -> 'np.ndarray':
        """
        Get the audio trimmed from the provided 'start'
        to the also given 'end'.
        """
        ParameterValidator.validate_positive_number('start', start, do_include_zero = True)
        ParameterValidator.validate_positive_number('end', end, do_include_zero = True)

        start = (
            0
            if start is None else
            start
        )
        end = (
            self.duration
            if end is None else
            end
        )

        return self.audio[int(start * self.sample_rate):int(end * self.sample_rate)]
    
    def with_volume(
        self,
        volume: int = 100
    ):
        """
        Get the audio modified by applying the volume
        change according to the given parameter. The
        range of values for the 'volume' parameter is
        from 0 to 500.

        - 0 means silence (x0)
        - 50 means 50% of original volume (x0.5)
        - 500 means 500% of original volume (x5)
        """
        ParameterValidator.validate_mandatory_number_between('volume', volume, 0, 500)

        volume /= 100.0
        audio = self.audio.copy()

        audio_type = audio.dtype
        audio = (
            # int to float to avoid overflow, if needed
            audio.astype(np.float32)
            if np.issubdtype(audio_type, np.integer) else
            audio
        )

        audio *= volume

        # turn into original type if int to avoid overflow
        if np.issubdtype(audio_type, np.integer):
            info = np.iinfo(audio_type)
            audio = np.clip(audio, info.min, info.max)
            audio = audio.astype(audio_type)

        return audio

    def apply_volume(
        self,
        volume: int = 100
    ):
        """
        Modify the audio in the instance with the one
        after the volume change has been applied. The
        range of values for the 'volume' parameter is
        from 0 to 500.

        - 0 means silence (x0)
        - 50 means 50% of original volume (x0.5)
        - 500 means 500% of original volume (x5)
        """
        self.audio = self.with_volume(volume)

        return self.audio
    
    def save(
        self,
        filename: str
    ) -> str:
        """
        Write the audio to a file with the given
        'filename' and return that 'filename' if
        successfully written.

        You need to have one of these libraries
        installed to be able to save the file:
        - "soundfile"
        - "scipy"
        - "pydub"
        - "moviepy"
        - "torch" and "torchaudio" (both)
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)

        filename = (
            AudioSaver.save_with_soundfile(self.audio, self.sample_rate, filename)
            if PythonValidator.is_dependency_installed('soundfile') else
            AudioSaver.save_with_scipy(self.audio, self.sample_rate, filename)
            if PythonValidator.is_dependency_installed('scipy') else
            AudioSaver.save_with_pydub(self.audio, self.number_of_channels, self.sample_rate, filename)
            if PythonValidator.is_dependency_installed('pydub') else
            AudioSaver.save_with_moviepy(self.audio, self.sample_rate, filename)
            if PythonValidator.is_dependency_installed('moviepy') else
            AudioSaver.save_with_torch(self.audio, self.sample_rate, filename)
            if (
                PythonValidator.is_dependency_installed('torch') and
                PythonValidator.is_dependency_installed('torchaudio')
            ) else
            None
        )
        
        if filename is None:
            raise Exception('You need one of these libraries installed to be able to save the file: "soundfile", "scipy", "pydub", "moviepy" or "torch" and "torchaudio".')
        
        return filename