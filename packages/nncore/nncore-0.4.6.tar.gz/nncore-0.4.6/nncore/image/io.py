# Copyright (c) Ye Liu. Licensed under the MIT License.

import cv2

import nncore

_COLOR_SPACES = {
    'color': cv2.IMREAD_COLOR,
    'grayscale': cv2.IMREAD_GRAYSCALE,
    'unchanged': cv2.IMREAD_UNCHANGED
}


def imread(filename, flag='color', to_rgb=False):
    """
    Read an image from a file.

    Args:
        filename (str): Path to the image file.
        flag (str | int, optional): Flags specifying the color type of the
            loaded image. Currently supported flags include ``color``,
            ``grayscale``, and ``unchanged``. Default: ``color``.
        to_rgb (bool, optional): Whether to convert channel order from ``BGR``
            to ``RGB``. Default: ``False``.

    Returns:
        :obj:`np.ndarray`: The loaded image array.
    """
    if not isinstance(filename, str):
        raise TypeError(
            "filename must be a str, but got '{}'".format(filename))

    nncore.is_file(filename, raise_error=True)

    flag = _COLOR_SPACES[flag] if isinstance(flag, str) else flag
    img = cv2.imread(filename, flag)

    if flag == cv2.IMREAD_COLOR and to_rgb:
        cv2.cvtColor(img, cv2.COLOR_BGR2RGB, img)

    return img


def imwrite(img, filename, overwrite=True, params=None):
    """
    Write an image to a file.

    Args:
        img (:obj:`np.ndarray`): The image array to be written.
        filename (str): Path to the image file.
        params (list | None, optional): Same as the :obj:`cv2.imwrite`
            interface. Default: ``None``.

    Returns:
        bool: Successful or not.
    """
    if nncore.is_file(filename):
        if overwrite:
            nncore.remove(filename)
        else:
            raise FileExistsError("file '{}' exists".format(filename))

    nncore.mkdir(nncore.dir_name(nncore.abs_path(filename)))
    return cv2.imwrite(filename, img, params)
