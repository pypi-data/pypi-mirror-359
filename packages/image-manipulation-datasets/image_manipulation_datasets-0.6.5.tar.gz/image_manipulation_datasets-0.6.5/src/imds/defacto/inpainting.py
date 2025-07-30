import os
from typing import Tuple

import numpy as np

from imds._dataset import _BaseDataset


class Inpainting(_BaseDataset):
    """Digital image forensic has gained a lot of attention as it is becoming easier
    for anyone to make forged images. Several areas are concerned by image
    manipulation: a doctored image can increase the credibility of fake news, impostors
    can use morphed images to pretend being someone else.

    It became of critical importance to be able to recognize the manipulations suffered
    by the images. To do this, the first need is to be able to rely on reliable and
    controlled data sets representing the most characteristic cases encountered. The
    purpose of this work is to lay the foundations of a body of tests allowing both the
    qualification of automatic methods of authentication and detection of manipulations
    and the training of these methods.

    This dataset contains about 25000 object-removal forgeries are available under the
    inpainting directory. Each object-removal is accompanied by two binary masks. One
    under the probemask subdirectory indicates the location of the forgery and one
    under the inpaintmask which is the mask use for the inpainting algorithm.

    To download the dataset, please visit the following link:
    https://defactodataset.github.io

    Note: The dataset has an issue between the image and probe mask sizes. We must be
    careful in how the images and masks are handled. Since the images have manipulation
    statistics embedded in the pixels, any sort of aggregation function could damage or
    destroy the statistics. Therefore, we need to resize the masks to match the images.
    Then we need to crop the images and masks to the provided crop size. This will
    preserve any manipulation statistics while removing issues in the dataset.

    Directory structure:
    Defacto Inpainting
    ├── inpainting_annotations
    │   ├── graph
    │   │   ├── 0_000000000260.json
    │   │   ├── 0_000000000332.json
    │   │   ├── ...
    │   │   └── 9_000000581887.json
    │   ├── inpaint_mask
    │   │   ├── 0_000000000260.tif
    │   │   ├── 0_000000000332.tif
    │   │   ├── ...
    │   │   └── 9_000000581887.tif
    │   └── probe_mask
    │       ├── 0_000000000260.jpg
    │       ├── 0_000000000332.jpg
    │       ├── ...
    │       └── 9_000000581887.jpg
    └── inpainting_img
        └── img
            ├── 0_000000000260.tif
            ├── 0_000000000332.tif
            ├── ...
            └── 9_000000581887.tif

    Args:
        data_dir (str): The directory of the dataset.
        split (str): The split of the dataset. Must be 'train', 'valid', 'test',
            'benchmark', or 'full'.
        crop_size (tuple): The size of the crops.
        pixel_range (tuple): The range of the pixel values of the input images.
            Ex. (0, 1) scales the pixels from [0, 255] to [0, 1].
        shuffle (bool): Whether to shuffle the dataset before splitting.
        download (bool): Whether to download the dataset.
    """

    def __init__(
        self,
        data_dir: str,
        split: str = "full",
        crop_size: Tuple[int, int] = None,
        pixel_range: Tuple[float, float] = (0.0, 1.0),
        shuffle: bool = True,
        download: bool = False,
    ) -> None:
        super().__init__(crop_size, pixel_range)

        if download:
            raise NotImplementedError(
                "Downloading is not implemented yet due to the requirement of a "
                "browser to obtain the dataset. Please refer to the following link "
                "for more information: https://defactodataset.github.io."
            )

        # Fetch the image filenames.
        image_dir = os.path.join(data_dir, "inpainting_img", "img")
        image_files = [
            os.path.abspath(os.path.join(image_dir, f))
            for f in os.listdir(image_dir)
            if f.endswith(".tif") or f.endswith(".jpg")
        ]

        # Shuffle the image files for a random split.
        if shuffle:
            image_files = np.random.permutation(image_files).tolist()

        split_size = len(image_files) // 10

        # Note that the order of the output files is aligned with the input files.
        if split == "train":
            self.image_files = image_files[: split_size * 8]

        elif split == "valid":
            self.image_files = image_files[split_size * 8 : split_size * 9]

        elif split == "test":
            self.image_files = image_files[split_size * 9 :]

        elif split == "benchmark":
            self.image_files = image_files[:1000]

        elif split == "full":
            self.image_files = image_files

        else:
            raise ValueError(f"Unknown split: {split}")

        # Fetch the mask files.
        mask_dir = os.path.join(data_dir, "inpainting_annotations", "probe_mask")

        self.mask_files = []
        for f in self.image_files:
            f = f.split("/")[-1]
            mask_file = os.path.abspath(os.path.join(mask_dir, f))
            if not os.path.exists(mask_file) and mask_file[-3:] == "jpg":
                self.mask_files.append(mask_file.replace(".jpg", ".tif"))
            elif not os.path.exists(mask_file) and mask_file[-3:] == "tif":
                self.mask_files.append(mask_file.replace(".tif", ".jpg"))
            else:
                self.mask_files.append(mask_file)
