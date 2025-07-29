from yta_constants.enum import YTAEnum as Enum


class ExtendVideoMode(Enum):
    """
    The strategy we want to apply to extend the
    duration of a video.
    """

    LOOP = 'loop'
    """
    This mode will make the video loop (restart from the begining)
    until it reaches the expected duration.
    """
    FREEZE_LAST_FRAME = 'freeze_last_frame'
    """
    This mode will freeze the last frame of the video and extend 
    it until it reaches the expected duration.
    """
    SLOW_DOWN = 'slow_down'
    """
    This mode will change the speed of the provided video to make
    it fit the needed duration by deccelerating it. As you should
    know, this method changes the whole video duration so the 
    result could be unexpected. Use it carefully.
    """
    BLACK_TRANSPARENT_BACKGROUND = 'black_background'
    """
    This mode will add a black and transparent background clip
    the time needed to fulfill the required duration. This is
    useful when we need to composite different clips with non
    similar durations so we can force all of them to have the
    same duration.
    """
    DONT_ENLARGE = 'dont_enlarge'
    """
    This mode will not touch the video duration when we need
    to enlarge it to fit the provided duration. This option
    must be chosen when we don't want to enlarge the video.
    It is interesting when combined with an enshort option
    that is modifying the video because we only want it
    modified if we need to enshort it.
    """

class EnshortVideoMode(Enum):
    """
    The strategy we want to apply to enshort the
    duration of a video.
    """
    
    CROP = 'crop'
    """
    This mode will make a subclip of the clip and remove
    the remaining part to fit the expected duration time.
    """
    SPEED_UP = 'speed_up'
    """
    This mode will change the speed of the clip by speeding
    it up. This is useful to make clips shorter when we need
    it, but be careful when you use it. Could be a good 
    choice for transitions that you need to apply in a
    specific amount of time.
    """
    DONT_ENSHORT = 'dont_enshort'
    """
    This mode will not touch the video duration when we need
    to enshort it to fit the provided duration. This option
    must be chosen when we don't want to enshort the video.
    It is interesting when combined with an enlarge option
    that is modifying the video because we only want it
    modified if we need to enlarge it.
    """