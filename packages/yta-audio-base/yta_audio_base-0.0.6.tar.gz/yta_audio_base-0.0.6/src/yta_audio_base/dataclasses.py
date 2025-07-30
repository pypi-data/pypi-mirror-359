from yta_validation.parameter import ParameterValidator
from dataclasses import dataclass

import numpy as np


@dataclass
class AudioNumpy:
    """
    A dataclass that contains the audio as a numpy
    array and the sample rate, used to make easier
    the transformations.

    This dataclass should be used only to be shared
    between simple methods.
    """

    def __init__(
        self,
        audio: 'np.ndarray',
        sample_rate: int = 44_100
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