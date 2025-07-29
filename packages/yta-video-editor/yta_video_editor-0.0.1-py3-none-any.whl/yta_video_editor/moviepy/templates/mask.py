from yta_video_editor.moviepy.validator import validate_duration, validate_fps, validate_opacity, validate_size
from yta_multimedia_core.parser import VideoParser
from yta_multimedia_core.video.frame import VideoFrame
from yta_constants.multimedia import DEFAULT_SCENE_SIZE
from moviepy import ColorClip, VideoClip
from moviepy.Clip import Clip


class MaskTemplate:

    @staticmethod
    def uniform_mask(
        size: tuple = DEFAULT_SCENE_SIZE,
        duration: float = 1 / 60,
        fps: float = 60.0,
        opacity: float = 1.0
    ):
        """
        Get a moviepy ColorClip with the 'opacity' provided,
        where 1.0 indicates full opaque and 0.0 full
        transparent, to be used as a mask.
        
        This is called uniform because it uses a ColorClip
        that doesn't change along its duration time.
        """
        validate_size(size)
        validate_duration(duration)
        validate_fps(fps)
        validate_opacity(opacity)
        
        return ColorClip(size, opacity, is_mask = True, duration = duration).with_fps(fps)
    
    @staticmethod
    def uniform_opaque_mask(
        size: tuple = DEFAULT_SCENE_SIZE,
        duration: float = 1 / 60,
        fps: float = 60.0
    ):
        """
        Get a moviepy ColorClip full opaque to be used as
        the mask of a normal clip.
        
        This is called uniform because it uses a ColorClip
        that doesn't change along its duration time.
        """
        return MaskTemplate.uniform_mask(size, duration, fps, 1.0)
    
    @staticmethod
    def uniform_transparent_mask(
        size: tuple = DEFAULT_SCENE_SIZE,
        duration: float = 1 / 60,
        fps: float = 60.0
    ):
        """
        Get a moviepy ColorClip full transparent to be
        used as the mask of a normal clip.
        
        This is called uniform because it uses a ColorClip
        that doesn't change along its duration time.
        """
        return MaskTemplate.uniform_mask(size, duration, fps, 0.0)
    
    @staticmethod
    def video_to_mask(
        video: Clip
    ):
        """
        Turn the provided 'video' into a mask Clip that
        can be set as the mask of any other normal clip.

        This method will apply a mask conversion
        strategy to turn the original clip into a mask.
        """
        video = VideoParser.to_moviepy(video)

        # TODO: This is ok but very slow I think...
        mask_clip_frames = [
            VideoFrame(frame).as_mask()
            for frame in video.iter_frames()
        ]

        return VideoClip(lambda t: mask_clip_frames[int(t * video.fps)], is_mask = True).with_fps(video.fps)
