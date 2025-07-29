import pathlib
from pathlib import Path
import shutil
import subprocess
from dataclasses import dataclass
from PIL import Image
from pprint import pprint as pp  # noqa: F401
import logging
from slugify import slugify

# This is a plugin that adds support for AVIF files until official support has been added
# https://github.com/python-pillow/Pillow/pull/5201
import pillow_avif  # noqa: F401


# Suppress the exifread warning
# https://github.com/ianare/exif-py/issues/167#issuecomment-1359251424
logging.getLogger("exifread").setLevel(logging.ERROR)

# from IPython.core.debugger import set_trace; set_trace()


@dataclass
class ImageData:
    original_image: Path
    compressed_image: Path
    source_image: Path
    original_size: int
    compressed_size: int
    original_dimension: tuple[int, int]
    compressed_dimension: tuple[int, int] | None
    exif_stripped: bool = False


def get_files_by_extension(path: str, wanted_filetypes: list[str]) -> list[Path]:
    """Return a list of image files in the given path that match the image types."""
    image_files: list[Path] = []  # extension
    for image_type in wanted_filetypes:
        image_files.extend(Path(path).glob(f"*.{image_type}"))
    return image_files


def humanize(size: int) -> str:
    """Convert a size in bytes to a human-readable format."""
    units = ["B", "K", "M", "G"]
    index = 0

    # Convert the size to a higher unit until it's less than 1024
    precise_size: float = float(size)
    while precise_size >= 1024 and index < len(units) - 1:
        precise_size = precise_size / 1024
        index += 1

    if index >= 2:
        pretty_size = round(precise_size, 1)
    else:
        pretty_size = round(precise_size)

    return f"{pretty_size}{units[index]}"


def scale_image(image: Path, max_width: int, max_height: int) -> tuple[int, int]:
    """Resize an image to fit within max_width and max_height
    while maintaining aspect ratio."""
    original_size: tuple[int, int]
    new_size: tuple[int, int]
    with Image.open(image) as img:
        original_size = img.size
        # Calculate the new size preserving the aspect ratio
        img.thumbnail((max_width, max_height))
        new_size = img.size
        # Save the resized image to the output path
        img.save(image)
    return new_size


def image_dimensions(image: Path) -> tuple[int, int]:
    """Return the dimensions of an image."""
    with Image.open(image) as img:
        size: tuple[int, int] = img.size
    return size


def convert_image(image: Path, new_format: str) -> Path:
    """Convert an image to a new format."""
    new_image = image.with_suffix(f".{new_format}")
    with Image.open(image) as img:
        img.save(new_image)
    image.unlink()
    return new_image


def trim_image(image: Path, trim: dict[str, int]) -> tuple[int, int]:
    # https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.crop
    # left, upper, right, lower
    with Image.open(image) as img:
        left = trim["l"]
        top = trim["t"]
        right = img.width - trim["r"]
        bottom = img.height - trim["b"]
        img = img.crop((left, top, right, bottom))
        img.save(image)
        new_size: tuple[int, int] = img.size
    return new_size


def strip_exif(image: Path) -> bool:
    cmd = ["exiftool", "-overwrite_original_in_place", "-all=", str(image)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    metadata_removed = False
    if "1 image files updated" in result.stdout:
        metadata_removed = True
    return metadata_removed


class Compress:
    """A class to compress a single image using specified quality settings.

    This class supports JPEG, PNG, and WEBP formats, utilizing
    external tools (jpegoptim, pngquant, webp) for compression.
    These tools must be installed and accessible in the system's
    PATH.
    """

    types: dict[str, str] = {
        "png": "png",
        "jpeg": "jpeg",
        "jpg": "jpeg",
        "webp": "webp",
        "avif": "avif",
    }

    def __init__(self, source_image: pathlib.Path, quality: int, output_dir: str):
        self.do_compress: bool = True
        self.source_image = source_image
        self.quality: int = quality
        self.output_dir = output_dir
        self.dest_extra_name: str = ""
        self.source_extra_name: str = ""
        self.size: tuple[int, int] = (0, 0)
        self.convert: str | None = ""
        self.trim: dict[str, int] = {}
        self.strip_exif: bool = False
        self.slugify: bool = False

    def get_type(self, image: Path) -> str:
        image_type: str = image.suffix
        image_type = image_type[1:].lower()  # remove the leading dot
        if image_type in self.types:
            return self.types[image_type]
        else:
            raise ValueError(f"Unsupported image type: {image_type}")

    def compress_jpeg(self, image: Path) -> None:
        """Compresses a JPEG image to a specified quality and moves it to the
        output directory with a new name.

        jpegoptim doesn't allow renaming of the file when compressing, so we
        need to use a temporary directory to store the compressed image before
        moving it to the output directory and renaming.

        Raises:
            subprocess.CalledProcessError: If the `jpegoptim` command fails.
        """
        # fmt: off
        cmd = [
            "jpegoptim", "--quiet", "--overwrite", "--strip-exif",
            "--max", str(self.quality),
            str(image),
        ]
        # fmt: on
        self.run_cmd(cmd)

    def compress_png(self, image: Path) -> None:
        quality: str = f"0-{self.quality}"
        # fmt: off
        cmd = [
            "pngquant", "--force",
            "--quality", quality,
            "--output", str(image),
            str(image),
        ]
        # fmt: on
        self.run_cmd(cmd)

    def compress_webp(self, image: Path) -> None:
        # fmt: off
        cmd = [
            "cwebp",
            "-q", str(self.quality),
            "-o", str(image),
            str(image),
        ]
        # fmt: on
        self.run_cmd(cmd)

    def compress_avif(self, image: Path) -> None:
        # fmt: off
        cmd = [
            'avif',
            '--input', str(image),
            '--quality', str(self.quality),
            '--overwrite',
        ]
        # fmt: on

    @staticmethod
    def run_cmd(cmd: list[str]) -> None:
        cmd = [str(i) for i in cmd]
        subprocess.run(cmd, capture_output=True)

    def create_new_name(self, dest_dir: Path, suffix: str) -> Path:
        name = self.source_image
        base_name = name.stem
        if self.slugify:
            base_name = slugify(name.stem)
        base_name = base_name + suffix + name.suffix
        new_name = Path(name.parent, dest_dir, base_name)
        return new_name

    def make_filenames(self, output_dir: Path) -> tuple[Path, Path]:
        """Create new file names for the destination and new source name."""
        source_new_name: Path = None
        # dest_name: Path = None
        source_name = self.source_image
        if self.source_extra_name:
            here = source_name.parent
            source_new_name = self.create_new_name(here, self.source_extra_name)
        dest_name = self.create_new_name(output_dir, self.dest_extra_name)
        return dest_name, source_new_name

    def copy_move(self, dest_name: Path, source_new_name: Path) -> None:
        try:
            if source_new_name and dest_name:
                self.source_image.rename(source_new_name)
                shutil.copy(source_new_name, dest_name)
            elif dest_name:
                shutil.copy(self.source_image, dest_name)
        except shutil.SameFileError:
            raise shutil.SameFileError(
                f"The source and destination files are the same, {dest_name}"
            )

    def compress(self) -> ImageData:
        """
        Compresses the source image using the specified quality setting.

        This method determines the image type (JPEG, PNG, or WEBP) of the
        source image, applies the appropriate compression command, and
        saves the compressed image to the output directory.

        The compression process is performed using external tools
        (`jpegoptim` for JPEGs, `pngquant` for PNGs, and `webp` for WEBP
        images), which must be installed and accessible in the system's
        PATH.

        The method calculates the original and compressed sizes of the
        image, returning both values for further use.

        Raises:
            ValueError: If the image type is unsupported or if the external
                        compression tool encounters an error.
            Exception: If the subprocess call to the external compression tool fails.

        Returns:
            tuple: A tuple containing the original size and compressed
                   size of the image, both in bytes.
        """

        # SVG cleaner - https://github.com/scour-project/scour

        original_size: int = self.source_image.stat().st_size

        # create the output dir if it doesn't exist
        output_dir = Path(self.source_image.parent / "kompressor")
        if self.output_dir:
            output_dir = Path(self.source_image.parent, self.output_dir)
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
            except FileExistsError:
                # in multi-threaded environments, this directory
                # may have been created in another thread.
                pass

        compressed_image, renamed_source_image = self.make_filenames(output_dir)
        self.copy_move(compressed_image, renamed_source_image)
        original_dimensions = image_dimensions(compressed_image)
        size = None

        if self.trim:
            size = trim_image(compressed_image, self.trim)

        if self.convert:
            compressed_image = convert_image(compressed_image, self.convert)
            size = image_dimensions(compressed_image)

        if self.size != (0, 0):
            size = scale_image(compressed_image, self.size[0], self.size[1])

        if self.do_compress:
            image_type: str = self.get_type(compressed_image)
            if image_type == "jpeg":
                self.compress_jpeg(compressed_image)
            elif image_type == "png":
                self.compress_png(compressed_image)
            elif image_type == "webp":
                self.compress_webp(compressed_image)
            elif image_type == "avif":
                self.compress_avif(compressed_image)
            else:
                raise ValueError(f"Unsupported image type: {image_type}")

        stripped = False
        if self.strip_exif:
            stripped = strip_exif(compressed_image)

        compressed_size: int = compressed_image.stat().st_size

        data = ImageData(
            original_image=self.source_image,
            compressed_image=compressed_image,
            source_image=self.source_image,
            original_size=original_size,
            compressed_size=compressed_size,
            original_dimension=original_dimensions,
            compressed_dimension=size,
            exif_stripped=stripped,
        )
        return data
