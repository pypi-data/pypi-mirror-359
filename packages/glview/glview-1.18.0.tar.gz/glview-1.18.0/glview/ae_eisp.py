import numpy as np


def exposure_estimation(rgb_image: np.ndarray,
                        **_kwargs) -> float:
    """
    :param rgb_image: input rgb image, shape = (H, W, C)
    :returns: exposure correction gain
    """
    eps = 1e-12

    # maximum value before AEC, all color components included
    hi_val_no_clip = rgb_image.max() + eps

    # make histogram of input data
    counts, bin_locations = matlab_imhist(rgb_image / hi_val_no_clip)
    cum_hist = np.cumsum(counts)
    cum_hist = cum_hist / max(cum_hist)

    # average value before AEC
    avg_val = np.mean(rgb_image)

    # Parameters: How many % of pixels allowed to clip,
    # different level accepted depending on if the mean brightness
    # is going to be very low, or just a bit dark, etc.
    clip_margin_lo = 1 - 0.01
    clip_margin_me = 1 - 0.03
    clip_margin_hi = 1 - 0.07

    # Get pixel value/level which would let % of pixels to clip
    # according different clip levels of parameters
    first = lambda idx: idx[0][0]

    hi_val_lo_clip_idx = first(np.where(cum_hist >= clip_margin_lo))
    hi_val_me_clip_idx = first(np.where(cum_hist >= clip_margin_me))
    hi_val_hi_clip_idx = first(np.where(cum_hist >= clip_margin_hi))

    hi_val_lo_clip = hi_val_no_clip * bin_locations[hi_val_lo_clip_idx] + eps
    hi_val_me_clip = hi_val_no_clip * bin_locations[hi_val_me_clip_idx] + eps
    hi_val_hi_clip = hi_val_no_clip * bin_locations[hi_val_hi_clip_idx] + eps

    # Parameters: Define average target range matching to different
    # allowed clip levels, high clip would let the average
    # brightness go lower, i.e. avoid clip by lowering average brightness
    avg_tgt_min_hi_clip = 15/255
    avg_tgt_min_me_clip = 25/255
    avg_tgt_min_lo_clip = 35/255
    avg_tgt_min_no_clip = 55/255
    avg_tgt = 70/255 # Average target when there is no risk of clipping

    # Calculate gains that would scale data so that average goes to
    # the different targets
    gain_avg_tgt = avg_tgt / avg_val
    gain_avg_tgt_min_hi_clip = avg_tgt_min_hi_clip / avg_val
    gain_avg_tgt_min_me_clip = avg_tgt_min_me_clip / avg_val
    gain_avg_tgt_min_lo_clip = avg_tgt_min_lo_clip / avg_val
    gain_avg_tgt_min_no_clip = avg_tgt_min_no_clip / avg_val

    # Calculate gains that would scale data so that only allowed % of
    # pixels is clipped, but keeping the brightness above allowed
    # minimum value matching each clip level
    gain_hi_clip = max(gain_avg_tgt_min_hi_clip, 1/hi_val_hi_clip)
    gain_me_clip = max(gain_avg_tgt_min_me_clip, 1/hi_val_me_clip)
    gain_lo_clip = max(gain_avg_tgt_min_lo_clip, 1/hi_val_lo_clip)
    gain_no_clip = max(gain_avg_tgt_min_no_clip, 1/hi_val_no_clip)

    # Final gain is a minimum of clipping prevention gains,
    # and gain putting the average to the defined target
    # i.e. saving as many pixels
    # from clipping, but keeping the brightness target as well
    # as possible, allowing some darkening for avoiding clipping
    gain_aec = min([ gain_avg_tgt, gain_hi_clip, gain_me_clip, gain_lo_clip, gain_no_clip ])
    return gain_aec


def matlab_imhist(image: np.ndarray, n_bins: int=256) -> tuple[np.ndarray, np.ndarray]:
    """
    matlab's version of imhist
    """
    bin_center = np.linspace(0, 1.0, num=n_bins)

    bin_edges = bin_center[:-1] + np.diff(bin_center)/2
    bin_edges = [ float('-inf'), *bin_edges, float('inf') ]

    count, _ = np.histogram(image.ravel(), bins=bin_edges)
    return count, bin_center
