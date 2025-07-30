from typing import IO, Literal, NotRequired, TypedDict, assert_never

from pptx.opc.constants import CONTENT_TYPE
from pptx.shapes.picture import Movie as PptxMovie
from pptx.shapes.picture import Picture as PptxPicture

from tppt.types import FilePath, Length, LiteralLength

from . import BaseShape, RangeProps


class PictureProps(TypedDict):
    """Picture properties."""

    left: Length | LiteralLength
    top: Length | LiteralLength
    width: NotRequired[Length | LiteralLength]
    height: NotRequired[Length | LiteralLength]


class PictureData(PictureProps):
    """Picture data."""

    type: Literal["picture"]

    image_file: FilePath | IO[bytes]


class Picture(BaseShape[PptxPicture]):
    """Picture data class."""

    def __init__(
        self,
        pptx_obj: PptxPicture,
        data: PictureData | None = None,
        /,
    ) -> None:
        self._pptx = pptx_obj


MOVIE_MIME_TYPE = Literal[
    "video/x-ms-asf",
    "video/avi",
    "video/quicktime",
    "video/mp4",
    "video/mpeg",
    "video/msvideo",
    "video/x-ms-wmv",
    "video/x-msvideo",
]


def to_pptx_movie_mime_type(mime_type: MOVIE_MIME_TYPE) -> str:
    """Convert movie mime type to pptx movie mime type."""
    match mime_type:
        case "video/x-ms-asf":
            return CONTENT_TYPE.ASF
        case "video/avi":
            return CONTENT_TYPE.AVI
        case "video/quicktime":
            return CONTENT_TYPE.MOV
        case "video/mp4":
            return CONTENT_TYPE.MP4
        case "video/mpeg":
            return CONTENT_TYPE.MPG
        case "video/msvideo":
            return CONTENT_TYPE.MS_VIDEO
        case "video/x-ms-wmv":
            return CONTENT_TYPE.WMV
        case "video/x-msvideo":
            return CONTENT_TYPE.X_MS_VIDEO
        case _:
            assert_never(mime_type)


class MovieProps(RangeProps):
    """Movie properties."""

    poster_frame_image: NotRequired[FilePath | IO[bytes]]

    mime_type: MOVIE_MIME_TYPE
    """
    Mime type of the movie.

    NOTE: The Movie shape is an experimental feature of python-pptx, and specifying the mime_type is recommended.
    """


class MovieData(MovieProps):
    """Movie data."""

    type: Literal["movie"]

    movie_file: FilePath | IO[bytes]


class Movie(BaseShape[PptxMovie]):
    """Movie data class."""

    def __init__(
        self,
        pptx_obj: PptxMovie,
        data: MovieData | None = None,
        /,
    ) -> None:
        self._pptx = pptx_obj
