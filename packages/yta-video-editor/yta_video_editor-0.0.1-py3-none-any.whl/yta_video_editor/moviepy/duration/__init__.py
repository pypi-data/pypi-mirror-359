"""
Module to modify the duration of a moviepy
native and basic clip.
"""

# TODO: This is the basic video editor, but
# some imports here sound too advanced...
# Check it and make a decision
from yta_video_editor.moviepy.duration.enums import ExtendVideoMode, EnshortVideoMode
from yta_multimedia.video.parser import VideoParser
from yta_multimedia.video.frames.video_frame_extractor import VideoFrameExtractor
from yta_multimedia.video.utils import generate_video_from_image
from yta_multimedia.video.edition.effect.fit_duration_effect import FitDurationEffect
from yta_multimedia.video.edition.effect.moviepy.mask import ClipGenerator
from yta_validation.parameter import ParameterValidator
from moviepy import VideoClip, concatenate_videoclips
from typing import Union


def set_video_duration(
    video: Union[str, VideoClip],
    duration = float,
    extend_mode: ExtendVideoMode = ExtendVideoMode.LOOP,
    enshort_mode: EnshortVideoMode = EnshortVideoMode.CROP
):
    """
    This method will return a copy of the provided 'video' with the desired
    'duration' by applying crops, loops or different strategies according
    to the provided 'extend_mode' and 'enshort_mode' parameters. If the
    provided 'duration' is lower than the actual 'video' duration, it will
    be shortened by applying the 'enshort_mode'. If it is greater, it will
    be extended until we reach the desired 'duration' by applying the 
    'extend_mode' provided.

    This method makes a 'video.copy()' internally to work and avoid problems
    with references.

    If you pay attention to the options available, you can obtain a video 
    which duration doesn't fit the provided as the 'duration' parameter
    because there are some options that actually don't modify the video
    duration.
    """
    ParameterValidator.validate_mandatory_positive_number('duration', duration, do_include_zero = False)
    
    video = VideoParser.to_moviepy(video)
    extend_mode = (
        ExtendVideoMode.to_enum(extend_mode)
        if extend_mode is not None else
        ExtendVideoMode.default()
    )
    enshort_mode = (
        EnshortVideoMode.to_enum(enshort_mode)
        if extend_mode is not None else
        EnshortVideoMode.default()
    )

    final_video = video.copy()

    if video.duration > duration:
        # We need to enshort it
        if enshort_mode == EnshortVideoMode.CROP:
            final_video = final_video.with_subclip(0, duration)
        elif enshort_mode == EnshortVideoMode.SPEED_UP:
            final_video = FitDurationEffect().apply(video, duration)
            #final_video = final_video.with_effects([MultiplySpeed(final_duration = duration)])
            # TODO: Remove this below when effects reviewed and
            # functionality is working perfectly
            #final_video = ChangeSpeedVideoEffect.apply(final_video, duration)
        elif enshort_mode == EnshortVideoMode.DONT_ENSHORT:
            # Intentionally written because it does not change
            pass
    elif video.duration < duration:
        # We need to enlarge it
        remaining_time = duration % video.duration

        if extend_mode == ExtendVideoMode.LOOP:
            times_to_loop = (int) (duration / video.duration) - 1
            for _ in range(times_to_loop):
                final_video = concatenate_videoclips([
                    final_video,
                    video
                ])
            final_video = concatenate_videoclips([final_video, video.with_subclip(0, remaining_time)])
        elif extend_mode == ExtendVideoMode.FREEZE_LAST_FRAME:
            remaining_time = duration - video.duration
            frame = VideoFrameExtractor.get_frame_by_t(video, video.duration)
            frame_freezed_video = generate_video_from_image(frame, remaining_time, fps = video.fps)
            final_video = concatenate_videoclips([
                video,
                frame_freezed_video
            ])
        elif extend_mode == ExtendVideoMode.SLOW_DOWN:
            final_video = FitDurationEffect().apply(video, duration)
            #final_video = final_video.with_effects([MultiplySpeed(final_duration = duration)])
            # TODO: Remove this below when effects reviewed and
            # functionality is working perfectly
            #final_video = ChangeSpeedVideoEffect.apply(final_video, duration)
        elif extend_mode == ExtendVideoMode.BLACK_TRANSPARENT_BACKGROUND:
            final_video = concatenate_videoclips([
                video,
                ClipGenerator.get_default_background_video(size = video.size, duration = remaining_time, fps = video.fps)
            ])
        elif extend_mode == ExtendVideoMode.DONT_ENLARGE:
            # Intentionally written because it does not change
            pass

    return final_video