from imageio.v3 import imread
from skimage.color import rgb2lab, lab2rgb
from scipy.cluster.vq import kmeans
import numpy as np
from numpy.typing import NDArray


def colour_palette(path: str, k: int, samples: int) -> list[tuple[int, int, int]]:
    """Returns a colour palette obtained by clustering the colours in an image file.

    Args:
        path (str): Path to the image file.
        k (int): Number of colours in the palette.
        samples (int): Number of samples to take from the image.

    Returns:
       list[tuple[int, int, int]]: Colour palette comprised of a list of
        RGB colours.
    """

    # Read the image to an array, flatten, and then downsample
    image: NDArray[np.float32] = read_image_rgb(path)
    flat_image = flatten(image)
    samples = sample(flat_image, samples)

    # Divide by 255 to normalise to range [0, 1] for colour space conversion.
    samples /= 255
    # Convert to CIE-LAB colour space.
    samples = rgb2lab(samples)

    # Perform k-means clustering on the colours in the image
    centroids = clusters(samples, k)

    # Convert the obtained centroids back to integer RGB values
    colours: NDArray[int] = round_rgb(255 * lab2rgb(centroids))

    return [tuple(col) for col in colours]


def read_image_rgb(path: str) -> NDArray[np.float32]:
    return imread(path).astype(np.float32)


def flatten(image: NDArray) -> NDArray:
    return image.reshape(-1, 3)


# Take n evenly spaced samples from the flattened image array.
def sample(data: NDArray, n_samples: int) -> NDArray:
    compression = data.shape[0] // n_samples
    return data[::compression]


# Cluster the RGB values using the kmeans algorithm.
def clusters(data: NDArray, k: int) -> NDArray:
    centroids, distortion = kmeans(data, k)
    return centroids


def round_rgb(colours: NDArray[np.floating]) -> NDArray[int]:
    return np.rint(colours).astype(int)


def brightness(rgb: tuple[int, int, int]):
    r, g, b = rgb

    # Perceived brightness formula (ITU-R BT.601)

    return 0.299 * r + 0.587 * g + 0.114 * b
