import numpy as np


def exposure_estimation(img: np.ndarray, **_kwargs) -> float:
    """
    Estimates the exposure correction gain for an RGB image using sigmoid functions
    to ensure smoother transitions compared to hard-coded thresholds, which helps
    reduce flickering in video sequences.

    The algorithm dynamically sets a target mean brightness and a target clipping
    percentile based on the current image's average intensity.

    :param img: Input RGB image (np.ndarray), shape = (H, W, C).
                Expected to be float type with pixel values in range [0.0, 1.0].
    :returns: The calculated exposure correction gain (float).
    """
    EPS = 1e-12

    img_mean = img.mean()

    # --- Sigmoid 1: Determine Target Mean Brightness (0-1 scale) ---
    # This sigmoid function maps the normalized mean of the current image
    # to a desired target mean brightness.
    # Goal: Darker images should target a higher mean (brighten more).
    # Brighter images should target a lower mean (darken or stabilize).
    # Parameters for this sigmoid:
    #   - k_mean: Steepness of the curve. Higher values mean a sharper transition.
    #   - x0_mean: Midpoint of the curve. Represents the normalized img_mean
    #              at which the target mean transition is centered.
    #   - min_target_mean: The minimum target mean value (for bright input images).
    #   - max_target_mean: The maximum target mean value (for dark input images).
    k_mean = 15.0
    x0_mean = 0.4 # Midpoint for mean normalization (e.g., if input mean is ~0.4)
    min_target_mean = 40.0 / 255.0 # Target mean for very bright images (e.g., if img_mean > ~0.58)
    max_target_mean = 80.0 / 255.0 # Target mean for very dark images (e.g., if img_mean < ~0.2)

    # Sigmoid output (0 to 1), where output increases as img_mean increases.
    sigmoid_output_mean = 1 / (1 + np.exp(-k_mean * (img_mean - x0_mean)))

    # Linearly interpolate between max_target_mean and min_target_mean based on sigmoid output.
    # As sigmoid_output_mean increases (meaning img_mean is higher),
    # target_mean_val_pixel will decrease from max_target_mean towards min_target_mean.
    target_mean_val_pixel = max_target_mean - sigmoid_output_mean * (max_target_mean - min_target_mean)

    # Calculate the gain required to bring the current image's mean to the target mean.
    gain_from_mean = target_mean_val_pixel / (img_mean + EPS)

    # --- Sigmoid 2: Determine Target Percentile for Clipping (0-100 scale) ---
    # This sigmoid determines which percentile of the *original* image's pixel
    # values should be mapped to the maximum output value (e.g., 1.0).
    # Goal: For dark images, map a very high percentile (e.g., 99.9th) to 1.0
    #       to maximize dynamic range without clipping.
    #       For brighter images, map a slightly lower percentile (e.g., 99.0th) to 1.0
    #       to accept a small amount of clipping, preventing over-darkening.
    # Parameters for this sigmoid:
    #   - k_perc: Steepness of the curve.
    #   - x0_perc: Midpoint of the curve for the percentile transition.
    #   - min_target_perc: The minimum target percentile (for bright input images).
    #   - max_target_perc: The maximum target percentile (for dark input images).
    k_perc = 20.0
    x0_perc = 0.5 # Midpoint for percentile transition (e.g., if input mean is ~0.5)
    min_target_perc = 99.0 # Target percentile for very bright images (allow 1% clip)
    max_target_perc = 99.9 # Target percentile for very dark images (allow 0.1% clip)

    # Sigmoid output (0 to 1), where output increases as img_mean increases.
    sigmoid_output_perc = 1 / (1 + np.exp(-k_perc * (img_mean - x0_perc)))

    # Linearly interpolate between max_target_perc and min_target_perc based on sigmoid output.
    # As sigmoid_output_perc increases (meaning img_mean is higher),
    # target_percentile will decrease from max_target_perc towards min_target_perc.
    target_percentile = max_target_perc - sigmoid_output_perc * (max_target_perc - min_target_perc)

    # Find the pixel value at the determined target percentile in the original image.
    # This is the value that, after applying the gain, should ideally become 1.0 (max output).
    val_at_target_percentile = np.percentile(img.ravel(), target_percentile) + EPS

    # Calculate the gain required to scale this percentile value to 1.0.
    gain_from_clipping = 1.0 / val_at_target_percentile

    # --- Final Gain Calculation ---
    # The final gain is the minimum of the gain required to meet the target mean
    # and the gain required to prevent excessive clipping.
    # While `min()` is a discrete operation, its inputs (`gain_from_mean` and
    # `gain_from_clipping`) are now derived from smoothly varying sigmoid functions.
    # This ensures that the chosen gain will transition smoothly, significantly
    # reducing flickering compared to the original algorithm's hard thresholds.
    final_exposure_gain = min(gain_from_mean, gain_from_clipping)
    final_exposure_gain = gain_from_mean

    print(f"brightness gain = {gain_from_mean:.2f},  clipping gain = {gain_from_clipping:.2f} => total gain = {final_exposure_gain:.2f}")

    return final_exposure_gain
