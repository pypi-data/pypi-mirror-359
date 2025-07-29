from collections.abc import Sequence
import enum
import os
from typing import Optional, overload


class ImageMetadata:
    @overload
    def __init__(self, image_height: int, image_width: int, title: Optional[str] = None, description: Optional[str] = None, region_info: Optional[RegionInfo] = None, orientation: Optional[ExifOrientation] = None, keyword_info: Optional[KeywordInfo] = None, country: Optional[str] = None, city: Optional[str] = None, state: Optional[str] = None, location: Optional[str] = None) -> None: ...

    @overload
    def __init__(self, path: str | os.PathLike) -> None: ...

    def __eq__(self, arg: ImageMetadata, /) -> bool: ...

    def __ne__(self, arg: ImageMetadata, /) -> bool: ...

    def __repr__(self) -> str: ...

    def to_file(self, new_path: Optional[str | os.PathLike] = None) -> None:
        """
        If `new_path` is provided, the original image is copied to the new location and the metadata is written to the new file. Otherwise, it overwrites the original file with the updated metadata.
        """

    @property
    def image_height(self) -> int: ...

    @property
    def image_width(self) -> int: ...

    @property
    def title(self) -> Optional[str]: ...

    @title.setter
    def title(self, arg: str, /) -> None: ...

    @property
    def description(self) -> Optional[str]: ...

    @description.setter
    def description(self, arg: str, /) -> None: ...

    @property
    def region_info(self) -> Optional[RegionInfo]: ...

    @region_info.setter
    def region_info(self, arg: RegionInfo, /) -> None: ...

    @property
    def orientation(self) -> Optional[ExifOrientation]: ...

    @orientation.setter
    def orientation(self, arg: ExifOrientation, /) -> None: ...

    @property
    def keyword_info(self) -> Optional[KeywordInfo]: ...

    @keyword_info.setter
    def keyword_info(self, arg: KeywordInfo, /) -> None: ...

    @property
    def country(self) -> Optional[str]: ...

    @country.setter
    def country(self, arg: str, /) -> None: ...

    @property
    def city(self) -> Optional[str]: ...

    @city.setter
    def city(self, arg: str, /) -> None: ...

    @property
    def state(self) -> Optional[str]: ...

    @state.setter
    def state(self, arg: str, /) -> None: ...

    @property
    def location(self) -> Optional[str]: ...

    @location.setter
    def location(self, arg: str, /) -> None: ...

class ExifOrientation(enum.IntEnum):
    def __str__(self) -> str:
        """String representation"""

    def __repr__(self) -> str:
        """String representation"""

    Undefined = 0
    """Set but not a valid value"""

    Horizontal = 1
    """Normal (0° rotation)"""

    TopLeft = 1
    """Normal (0° rotation)"""

    MirrorHorizontal = 2
    """Horizontal flip"""

    TopRight = 2
    """Horizontal flip"""

    Rotate180 = 3
    """180° rotation"""

    BottomRight = 3
    """180° rotation"""

    MirrorVertical = 4
    """Vertical flip"""

    BottomLeft = 4
    """Vertical flip"""

    MirrorHorizontalAndRotate270CW = 5
    """90° CCW rotation + horizontal flip"""

    LeftTop = 5
    """90° CCW rotation + horizontal flip"""

    Rotate90CW = 6
    """90° CW rotation"""

    RightTop = 6
    """90° CW rotation"""

    MirrorHorizontalAndRotate90CW = 7
    """90° CW rotation + horizontal flip"""

    RightBottom = 7
    """90° CW rotation + horizontal flip"""

    Rotate270CW = 8
    """90° CCW rotation"""

    LeftBottom = 8
    """90° CCW rotation"""

    def to_exif_value(self) -> int:
        """Convert to EXIF orientation value"""

    def __int__(self) -> int:
        """Convert to integer"""

    @staticmethod
    def from_exif_value(arg: int, /) -> ExifOrientation:
        """Create from EXIF orientation value"""

    @staticmethod
    def from_int(arg: int, /) -> ExifOrientation:
        """Create from integer"""

class XmpArea:
    def __init__(self, h: float, w: float, x: float, y: float, unit: str, d: Optional[float] = None) -> None: ...

    def __eq__(self, arg: XmpArea, /) -> bool: ...

    def __ne__(self, arg: XmpArea, /) -> bool: ...

    def __repr__(self) -> str: ...

    @property
    def h(self) -> float: ...

    @h.setter
    def h(self, arg: float, /) -> None: ...

    @property
    def w(self) -> float: ...

    @w.setter
    def w(self, arg: float, /) -> None: ...

    @property
    def x(self) -> float: ...

    @x.setter
    def x(self, arg: float, /) -> None: ...

    @property
    def y(self) -> float: ...

    @y.setter
    def y(self, arg: float, /) -> None: ...

    @property
    def d(self) -> Optional[float]: ...

    @d.setter
    def d(self, arg: float, /) -> None: ...

    @property
    def unit(self) -> str: ...

    @unit.setter
    def unit(self, arg: str, /) -> None: ...

class Dimensions:
    def __init__(self, h: float, w: float, unit: str) -> None: ...

    def __eq__(self, arg: Dimensions, /) -> bool: ...

    def __ne__(self, arg: Dimensions, /) -> bool: ...

    def __hash__(self) -> int: ...

    def __repr__(self) -> str: ...

    @property
    def h(self) -> float: ...

    @h.setter
    def h(self, arg: float, /) -> None: ...

    @property
    def w(self) -> float: ...

    @w.setter
    def w(self, arg: float, /) -> None: ...

    @property
    def unit(self) -> str: ...

    @unit.setter
    def unit(self, arg: str, /) -> None: ...

class Region:
    def __init__(self, area: XmpArea, name: str, type_: str, description: Optional[str] = None) -> None: ...

    def __eq__(self, arg: Region, /) -> bool: ...

    def __ne__(self, arg: Region, /) -> bool: ...

    def __repr__(self) -> str: ...

    @property
    def area(self) -> XmpArea: ...

    @area.setter
    def area(self, arg: XmpArea, /) -> None: ...

    @property
    def name(self) -> str: ...

    @name.setter
    def name(self, arg: str, /) -> None: ...

    @property
    def type(self) -> str: ...

    @type.setter
    def type(self, arg: str, /) -> None: ...

    @property
    def description(self) -> Optional[str]: ...

    @description.setter
    def description(self, arg: str, /) -> None: ...

class RegionInfo:
    def __init__(self, applied_to_dimensions: Dimensions, region_list: Sequence[Region]) -> None: ...

    def __eq__(self, arg: RegionInfo, /) -> bool: ...

    def __ne__(self, arg: RegionInfo, /) -> bool: ...

    def __repr__(self) -> str: ...

    @property
    def applied_to_dimensions(self) -> Dimensions: ...

    @applied_to_dimensions.setter
    def applied_to_dimensions(self, arg: Dimensions, /) -> None: ...

    @property
    def region_list(self) -> list[Region]: ...

    @region_list.setter
    def region_list(self, arg: Sequence[Region], /) -> None: ...

class Keyword:
    def __init__(self, keyword: str, children: Sequence[Keyword], applied: Optional[bool] = None) -> None: ...

    def __lt__(self, arg: Keyword, /) -> bool: ...

    def __le__(self, arg: Keyword, /) -> bool: ...

    def __gt__(self, arg: Keyword, /) -> bool: ...

    def __ge__(self, arg: Keyword, /) -> bool: ...

    def __eq__(self, arg: Keyword, /) -> bool: ...

    def __ne__(self, arg: Keyword, /) -> bool: ...

    def __repr__(self) -> str: ...

    @property
    def keyword(self) -> str: ...

    @keyword.setter
    def keyword(self, arg: str, /) -> None: ...

    @property
    def applied(self) -> Optional[bool]: ...

    @applied.setter
    def applied(self, arg: bool, /) -> None: ...

    @property
    def children(self) -> list[Keyword]: ...

    @children.setter
    def children(self, arg: Sequence[Keyword], /) -> None: ...

class KeywordInfo:
    @overload
    def __init__(self, hierarchy: Sequence[Keyword]) -> None: ...

    @overload
    def __init__(self, delimited_strings: Sequence[str]) -> None: ...

    @overload
    def __init__(self, delimited_strings: Sequence[str], delimiter: str) -> None: ...

    def __eq__(self, arg: KeywordInfo, /) -> bool: ...

    def __ne__(self, arg: KeywordInfo, /) -> bool: ...

    def __or__(self, arg: KeywordInfo, /) -> KeywordInfo: ...

    def __ior__(self, arg: KeywordInfo, /) -> KeywordInfo: ...

    def __repr__(self) -> str: ...

    @property
    def hierarchy(self) -> list[Keyword]: ...

    @hierarchy.setter
    def hierarchy(self, arg: Sequence[Keyword], /) -> None: ...

EXIV2_VERSION: str = '0.28.5'

EXPAT_VERSION: str = 'expat_2.7.1'

class ExifMwgBaseError(Exception):
    pass

class FileAccessError(ExifMwgBaseError):
    pass

class Exiv2Error(ExifMwgBaseError):
    pass

class InvalidStructureError(ExifMwgBaseError):
    pass

class MissingFieldError(InvalidStructureError):
    pass
