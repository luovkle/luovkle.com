import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable

from PIL import Image

BASE_DIR = Path(__file__).parent.parent
IMAGES_DIR = BASE_DIR / "app/static/images/"


def get_input_paths() -> list[Path]:
    """Retrieve all input image paths from the images directory.

    Returns:
        list[Path]: A list of paths pointing to `.png` and `.jpeg` files.
    """
    patterns = ("**/*.png", "**/*.jpeg")
    paths = []
    for pattern in patterns:
        paths.extend(list(IMAGES_DIR.glob(pattern)))
    return paths


def get_webp_output_paths(input_paths: list[Path]) -> list[Path]:
    """Generate output paths for WebP files based on input images.

    Args:
        input_paths (list[Path]): Paths to the original image files.

    Returns:
        list[Path]: A list of corresponding WebP output paths.
    """
    output_paths = []
    for input_path in input_paths:
        output_paths.append(input_path.parent / (input_path.stem + ".webp"))
    return output_paths


def get_avif_output_paths(input_paths: list[Path]) -> list[Path]:
    """Generate output paths for AVIF files based on input images.

    Args:
        input_paths (list[Path]): Paths to the original image files.

    Returns:
        list[Path]: A list of corresponding AVIF output paths.
    """
    output_paths = []
    for input_path in input_paths:
        output_paths.append(input_path.parent / (input_path.stem + ".avif"))
    return output_paths


def img_to_webp(
    input_path: Path, output_path: Path, force_overwrite: bool = False
) -> None:
    """Convert an image to lossless WebP format.

    Args:
        input_path (Path): Path to the source image.
        output_path (Path): Destination path for the WebP file.
        force_overwrite (bool, optional): If True, overwrite the output file even if it
            already exists. Defaults to False.
    """
    if not force_overwrite and output_path.exists():
        return None
    img = Image.open(input_path).convert("RGBA")
    img.save(output_path, format="WEBP", lossless=True)


def img_to_avif(
    input_path: Path, output_path: Path, force_overwrite: bool = False
) -> None:
    """Convert an image to AVIF format with high quality settings.

    Args:
        input_path (Path): Path to the source image.
        output_path (Path): Destination path for the AVIF file.
        force_overwrite (bool, optional): If True, overwrite the output file even if it
            already exists. Defaults to False.
    """
    if not force_overwrite and output_path.exists():
        return None
    img = Image.open(input_path).convert("RGBA")
    img.save(
        output_path,
        format="AVIF",
        quality=90,
        chroma_subsampling="444",
        range="full",
        speed=4,
    )


async def run_blocking_tasks_in_threads(
    funcs_and_args: list[tuple[Callable, tuple]],
) -> None:
    """Run blocking functions concurrently in a thread pool.

    Args:
        funcs_and_args (list[tuple[Callable, tuple]]): List of (function, args) pairs
            to execute in parallel.
    """
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as executor:
        tasks = []
        for func, args in funcs_and_args:
            task = loop.run_in_executor(executor, func, *args)
            tasks.append(task)
        await asyncio.gather(*tasks, return_exceptions=False)


async def main() -> None:
    """Convert all PNG and JPEG images to both WebP and AVIF formats."""
    # Collect all input image paths from the target directory
    input_paths = get_input_paths()
    # Prepare and run tasks to convert images into WebP format
    webp_io_paths = zip(input_paths, get_webp_output_paths(input_paths))
    tasks = [(img_to_webp, io_paths) for io_paths in webp_io_paths]
    await run_blocking_tasks_in_threads(tasks)
    # Prepare and run tasks to convert images into AVIF format
    avif_io_paths = zip(input_paths, get_avif_output_paths(input_paths))
    tasks = [(img_to_avif, io_paths) for io_paths in avif_io_paths]
    await run_blocking_tasks_in_threads(tasks)


if __name__ == "__main__":
    asyncio.run(main())
