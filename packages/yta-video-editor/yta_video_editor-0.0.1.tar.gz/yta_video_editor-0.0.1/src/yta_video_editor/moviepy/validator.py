from yta_validation.parameter import ParameterValidator
from yta_validation import PythonValidator


"""
Temporary limits below:
"""
# TODO: This is just temporary, refactor and
# move them to a constants file (?)
VIDEO_MIN_SIZE = (1, 1)
VIDEO_MAX_SIZE = (1920 * 4, 1080 * 4)
VIDEO_MIN_DURATION = 1 / 60
VIDEO_MAX_DURATION = 120
VIDEO_MIN_FPS = 5
VIDEO_MAX_FPS = 120
# TODO: Is this explanation below correct?
VIDEO_MIN_OPACITY = 0.0
"""
The opacity that makes a moviepy video
pixel transparent = 0.0
"""
VIDEO_MAX_OPACITY = 1.0
"""
The opacity that makes a moviepy video
pixel opaque = 1.0
"""

def validate_size(
    size: tuple
) -> None:
    """
    Check if the 'size' parameter is a valid
    tuple, list or array of 2 elements with
    values between the limits and raise an
    Exception if not.
    """
    if not PythonValidator.is_numeric_tuple_or_list_or_array_of_2_elements_between_values(size, VIDEO_MIN_SIZE[0], VIDEO_MAX_SIZE[0], VIDEO_MIN_SIZE[1], VIDEO_MAX_SIZE[1]):
        # TODO: Print the limits.
        raise Exception('The provided "size" is not a tuple between the limits.')
    
def validate_duration(
    duration: float
) -> None:
    """
    Check if the 'duration' parameter is a 
    positive number between the limits and
    raise an Exception if not.
    """
    ParameterValidator.validate_mandatory_number_between('duration', duration, VIDEO_MIN_DURATION, VIDEO_MAX_DURATION)

def validate_fps(
    fps: float
) -> None:
    """
    Check if the 'fps' parameter is a positive
    number between the limits and raise an
    Exception if not.
    """
    ParameterValidator.validate_mandatory_number_between('fps', fps, VIDEO_MIN_FPS, VIDEO_MAX_FPS)

def validate_opacity(
    opacity: float
) -> None:
    """
    Check if the 'opacity' parameter is a
    positive number between the limits and
    raise an Exception if not.
    """
    ParameterValidator.validate_mandatory_number_between('opacity', opacity, VIDEO_MIN_OPACITY, VIDEO_MAX_OPACITY)