"""
Module to hold the main Audio class that is
capable of obtaining information, modifying
it, applying filters, etc.

The audio isusually presented in 2 columns
format, but depending on the library who is
handling the numpy array, the 2D information
can be different. The 'soundfile' library 
uses the (n_samples, n_channels) format while
the 'librosa' (mono = False) uses the 
(n_channels, n_samples) format.

TODO: Check the 'util.valid_audio(y)' within
the 'librosa' lib because it seems interesting
to validate a numpy audio array.
"""
from yta_audio_base.audio import Audio as BaseAudio
from yta_audio_advanced_filters import Filters
from yta_validation import PythonValidator
from typing import Union

import numpy as np
import librosa


class Audio(BaseAudio):
    """
    Class to represent and wrap a sound that is
    a numpy array to be able to work with it in
    an easy way.
    """

    def __init__(
        self,
        audio: 'np.ndarray',
        sample_rate: int = 44_100,
    ):
        super().__init__(audio, sample_rate)

    # TODO: Make this a 'init' helper, not the
    # instance initializer
    @staticmethod
    def init(
        audio: Union['np.ndarray', str],
        sample_rate: Union[int, None] = None
    ) -> 'Audio':
        """
        Initialize an Audio instance by an 'audio'
        parameter of any kind. It can be a numpy
        array, an AudioClip, an AudioSegment...
        """
        # 1. Process a filename
        if PythonValidator.is_string(audio):
            # TODO: Use 'try-catch' or validate audio file
            # sr=None preserves the original sample rate
            audio, sample_rate = librosa.load(audio, sr = sample_rate)
        elif PythonValidator.is_instance(audio, 'AudioClip'):
            # TODO: Parse with moviepy
            # TODO: I can now the sample rate only if there
            # is a file that has ben read
            pass
        elif PythonValidator.is_instance(audio, 'AudioSegment'):
            # We parse the pydub AudioSegment
            number_of_channels = audio.channels
            # Number of samples per channel 'frame_count'
            # frame_count = len(audio.get_array_of_samples()) // number_of_channels

            # Turn raw pydub AudioSegment to numpy array, with
            # raw data in bytes, width in bytes (2 for 16 bits)
            audio = np.frombuffer(audio.raw_data, dtype = {1: np.int8, 2: np.int16, 4: np.int32}[audio.sample_width])
            audio = (
                # Stereo or multichannel => reorder
                audio.reshape((-1, number_of_channels))
                if number_of_channels > 1 else
                audio
            )
        
        # TODO: Process 'AudioClip', 'AudioSegment', etc.
        # and turn them into numpy array to store
        # 2. Process a numpy array
        # TODO: Handle the type and process the input
        # TODO: Set the accepted input types
        # TODO: What about the sample rate (?)

        return Audio(audio, sample_rate)

    """
    Filters below. You can find 'with_' and 'apply_'
    methods below. The 'with_' returns a copy of the
    numpy array modified, but touching not the
    original audio, and the 'apply_' methods modify
    the original audio instance (and the values of 
    the original array).
    """
    # TODO: Some filtering methods below
    def with_lowpass(
        self
    ) -> 'np.ndarray':
        """
        Get the audio modified by applying a simple
        lowpass filter.
        """
        return Filters.low_pass(self.audio.copy())

    def apply_lowpass(
        self
    ) -> 'np.ndarray':
        """
        Modify the audio in the instance with the one
        after the low pass effect is applied.
        """
        self.audio = self.with_lowpass()

        return self.audio
    
    def with_fadeout(
        self,
        duration: float
    ):
        """
        Get the audio with a fade out effect applied. This
        method does not modify the original audio but 
        returns the audio modified.
        """
        return Filters.fadeout(self.audio.copy(), self.sample_rate, duration)
    
    def apply_fadeout(
        self
    ) -> 'np.ndarray':
        """
        Modify the audio instance by applying a fade
        out filter and return the audio modified.
        """
        self.audio = self.with_fadeout()

        return self.audio
    
    def with_fadein(
        self,
        duration: float
    ):
        """
        Get the audio with a fade in effect applied. This
        method does not modify the original audio but 
        returns the audio modified.
        """
        return Filters.fadein(self.audio.copy(), self.sample_rate, duration)
    
    def apply_fadein(
        self
    ) -> 'np.ndarray':
        """
        Modify the audio instance by applying a fade
        in filter and return the audio modified.
        """
        self.audio = self.with_fadein()

        return self.audio
    
    # TODO: Other modifying methods below
    def with_time_strech(
        self,
        rate: float = 0.5
    ):
        """
        Get the audio with a time stretch effect
        applied, which means changing the audio 
        duration without changing the pitch. This
        method does not modify the original audio but 
        returns the audio modified.

        TODO: Explain the 'rate' better.
        """
        return Filters.time_stretch(self.audio.copy(), rate)
    
    def apply_time_stretch(
        self,
        rate: float = 0.5
    ):
        """
        Modify the audio instance by applying a time
        stretch filter, which means changing the audio
        duration without changing the pitch, and
        return the audio modified.
        """
        audio, sample_rate = Filters.time_stretch(self.audio, rate)

        self.audio = audio
        self.sample_rate = sample_rate

        return self.audio
    
    def with_pitch_shift(
        self,
        n_steps: int
    ):
        """
        Get the audio with a pitch shift effect applied,
        which means changing the pitch but not the audio
        duration. This method does not modify the
        original audio but returns the audio modified.

        TODO: Explain 'n_steps' better.
        """
        return Filters.pitch_shift(self.audio.copy(), self.sample_rate, n_steps)
    
    def apply_pitch_shift(
        self,
        n_steps: int
    ):
        """
        Modify the audio instance by applying a pitch
        shifting filter, which means changing the pitch
        without changing the audio duration, and return
        the audio modified.
        """
        self.audio, self.sample_rate = Filters.pitch_shift(self.audio, self.sample_rate, n_steps)

        return self.audio
    
    def with_fft(
        self
    ):
        """
        Get the audio with a fft effect applied, which
        means looking for the Fourier spectrum per
        channel. This method does not modify the
        original audio but returns the audio modified.
        """
        return Filters.fft(self.audio.copy())

    def apply_fft(
        self
    ):
        """
        Modify the audio instance by applying an fft
        filter, which means looking for the Fourier
        spectrum per channel, and return the audio
        modified.
        """
        self.audio = Filters.fft(self.audio)

        return self.audio

# TODO: Please, remove this code below soon
# TODO: Old change volume method
def change_audio_volume(
    audio_frame: np.ndarray,
    factor: int = 100
):
    """
    Change the 'audio_frame' volume by applying the
    given 'factor'.

    Based on:
    https://github.com/Zulko/moviepy/blob/master/moviepy/audio/fx/MultiplyVolume.py
    """
    number_of_channels = len(list(audio_frame[0]))
    factors_array = np.array([
        factor
        for _ in range(audio_frame.shape[0])
    ])

    return (
        np.multiply(
            audio_frame,
            factors_array
        )
        if number_of_channels == 1 else
        np.multiply(
            audio_frame,
            np.array([
                factors_array
                for _ in range(number_of_channels)
            ]).T,
        )
        # if number_of_channels == 2:
    )