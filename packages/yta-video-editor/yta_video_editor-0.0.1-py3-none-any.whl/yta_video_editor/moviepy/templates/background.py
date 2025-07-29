"""
Module to simplify the way we create
different type of base videos that are
used in other advanced functionalities.
"""
from yta_video_editor.moviepy.templates.mask import MaskTemplate
from yta_video_editor.moviepy.validator import validate_duration, validate_fps, validate_opacity, validate_size, VIDEO_MIN_OPACITY, VIDEO_MAX_OPACITY
from yta_constants.multimedia import DEFAULT_SCENE_SIZE
from yta_validation.parameter import ParameterValidator
from yta_colors import Color
from moviepy import ColorClip
from typing import Union


class BackgroundTemplate:
    """
    Class to wrap basic video generation
    functionality.
    """

    @staticmethod
    def color_background(
        size: tuple,
        color: Union[str, Color],
        duration: float,
        fps: float,
        opacity: float
    ) -> ColorClip:
        """
        Get a moviepy ColorClip with the provided 'size',
        'color', 'duration', 'fps' and 'opacity'.
        """
        validate_size(size)
        color = Color.parse(color)
        validate_duration(duration)
        validate_fps(fps)
        validate_opacity(opacity)

        color_clip: ColorClip = ColorClip(size, color.as_rgb_array(), duration = duration).with_fps(fps)

        # A full opaque clip doesn't need a mask because it is,
        # by definition, full opaque
        return (
            color_clip.with_mask(MaskTemplate.uniform_mask(color_clip.size, color_clip.duration, color_clip.fps, opacity))
            if opacity < 1.0 else
            color_clip
        )
    
    @staticmethod
    def black_background(
        size: tuple,
        duration: float,
        fps: float,
        opacity: float
    ) -> ColorClip:
        """
        Get a moviepy black ColorClip with the
        provided 'size', 'duration', 'fps' and
        'opacity'.
        """
        return BackgroundTemplate.color_background(size, [0, 0, 0], duration, fps, opacity)
    
    # TODO: Validate that this below is working because I've
    # never before used a transparent black background
    @staticmethod
    def default_background(
        size: tuple = DEFAULT_SCENE_SIZE,
        duration: float = 1 / 60,
        fps: float = 60,
        is_transparent: bool = True
    ) -> ColorClip:
        """
        Default full black background video that lasts
        'duration' seconds that represents our default moviepy
        scenario of 1920x1080 dimensions. This background is
        used for the basic position calculations. Check the
        transparent option if you are planning to stack some
        videos.

        The background can be build with a full transparent
        mask if 'is_transparent' provided as True.
        """
        ParameterValidator.validate_mandatory_bool('is_transparent', is_transparent)

        opacity = (
            VIDEO_MIN_OPACITY
            if is_transparent else
            VIDEO_MAX_OPACITY
        )

        return BackgroundTemplate.color_background(size, [0, 0, 0], duration, fps, opacity)
