import json
import yaml

from pathlib import Path
from typing import Literal, Final, TypeAlias, Dict, Any, List, Tuple
from pydantic import BaseModel, field_validator, ValidationError, model_validator

# Type aliases
ChannelCount: TypeAlias = Literal[3, 4]  # RGB or RGBN
ImageShape = tuple[ChannelCount, int, int]

# Valid constants
VALID_PIXEL_SIZES: Final = (0.2, 0.4, 0.8, 1.6, 3.2, 6.4, 12.8, 25.6, 51.2, 102.4, 204.8)
VALID_MASK_LABELS: Final = (40, 41, 42, 48, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 72, 83, 84, 87, 88, 92, 95, 96)
VALID_DOWNLOADS_METHODS: Final = ('sequential', 'parallel')


class ConfigManager(BaseModel):
    data_path: Path | str
    pixel_size: float
    shape: ImageShape
    outpath: Path | str
    mask_label: List[int] | Tuple[int] | int

    outfile_prefixes: Dict[str, str] = {"raster": "input", "vector": "target"}
    resample_size: float | int | None = None
    download_method: str = 'sequential'
    create_gpkg: bool = False
    verbose: bool = False
    nodata_mode: str = 'flag'
    nodata_value: int = 0
    mask_remapping: Dict[int, Any] | None = None  # mapping FROM - TO

    class Config:
        frozen = True  # Make instances immutable

    @property
    def config_data(self) -> Dict[str, Any]:
        """Return all fields as a dict including defaults and validated data."""
        return self.model_dump()

    @field_validator("outfile_prefixes")
    @classmethod
    def validate_outfile_prefixes(cls, value: Dict[str, str]) -> Dict[str, str]:
        prefixes = ['raster', 'vector']
        if len(value) != 2:
            raise ValueError(f"Irregular Prefix Dictionary length of {len(value)}")
        for k in value.keys():
            if k not in prefixes:
                raise ValueError(f"Prefix '{k}' must match to ['raster', 'vector'].")
        return value

    @field_validator("nodata_mode")
    @classmethod
    def validate_nodata_mode(cls, value: str) -> str:
        if value not in {"flag", "remove"}:
            raise ValueError("Operation mode must be either 'flag' or 'remove'")
        return value

    @field_validator("resample_size")
    @classmethod
    def validate_resample_size(cls, value: float | int | None) -> float | None:
        if value is None:
            return value
        elif isinstance(value, (float, int)) and value > 0:
            return float(value)
        else:
            raise ValueError("Provide as float, int or None - null in rgb.yml")

    @field_validator("shape")
    @classmethod
    def validate_shape(cls, value: ImageShape) -> ImageShape:
        if len(value) != 3 or value[0] not in (3, 4) or any(dim <= 0 for dim in value):
            raise ValueError("Invalid shape: (channels, height, width) required with channels 3 or 4.")
        return value

    @field_validator("outpath")
    @classmethod
    def validate_outpath(cls, value: Path | str) -> Path:
        path = Path(value)
        # create folder structure
        Path(path).mkdir(parents=True, exist_ok=True)
        Path(path / 'input').mkdir(parents=True, exist_ok=True)
        Path(path / 'target').mkdir(parents=True, exist_ok=True)
        if not path.exists() or not path.is_dir():
            raise ValueError(f"Output path is invalid: {path}")
        return path

    @field_validator("data_path")
    @classmethod
    def validate_data_path(cls, value: Path | str) -> Path:
        path = Path(value)
        if not path.exists():
            raise ValueError(f"data_path path is invalid: {path}")
        return path

    @field_validator("pixel_size")
    @classmethod
    def validate_pixel_size(cls, value: float) -> float:
        if value not in VALID_PIXEL_SIZES:
            raise ValueError(f"Invalid pixel size: {value}. Must be one of {VALID_PIXEL_SIZES}")
        return value

    @field_validator("mask_label")
    @classmethod
    def validate_mask_label(cls, value: List[int] | Tuple[int] | int) -> list[int]:
        if isinstance(value, int):
            value = [value]
        if not all(val in VALID_MASK_LABELS for val in value):
            raise ValueError(f"Invalid mask labels: {value}. Must be within {VALID_MASK_LABELS}")
        else:
            return value

    @field_validator("mask_remapping", mode="before")
    @classmethod
    def validate_mask_remapping(cls, value: Dict[int, Any]) -> Dict[int, List[int]]:
        # optional value
        if value is None:
            return None

        # invert mapping dict to have FROM - TO
        new = {}
        for k, v in value.items():
            if isinstance(v, int):
                new[v] = k
            else:
                for vv in v:
                    new[vv] = k

        if not all(val in VALID_MASK_LABELS for val in new.keys()):
            raise ValueError(f"Invalid mask label {v} in mask_remapping {value}. "
                             f"Must be within {VALID_MASK_LABELS}")

        return new

    @field_validator("download_method")
    @classmethod
    def validate_download_method(cls, value: str) -> str:
        if value not in VALID_DOWNLOADS_METHODS:
            raise ValueError(f"Invalid download method: {value}. Must be one of {VALID_DOWNLOADS_METHODS}")
        return value

    @model_validator(mode="after")
    def check_pixel_resampling_size(self):
        if self.resample_size is not None:
            if self.resample_size <= self.pixel_size:
                raise ValueError(f"resample_size {self.resample_size} must be larger than pixel_size {self.pixel_size}")
            elif self.resample_size >= VALID_PIXEL_SIZES[VALID_PIXEL_SIZES.index(self.pixel_size)+1]:
                raise ValueError(f"resample_size {self.resample_size} must be smaller than next largest available pixel size: {VALID_PIXEL_SIZES[VALID_PIXEL_SIZES.index(self.pixel_size)+1]}")
            else:
                return self
        else:
            return self

    @classmethod
    def from_config_file(cls, file_path: str | Path) -> "ConfigManager":
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        with open(path, "r", encoding="utf-8") as file:
            if path.suffix.lower() == ".json":
                config_data = json.load(file)
            elif path.suffix.lower() in {".yaml", ".yml"}:
                config_data = yaml.safe_load(file)
            else:
                raise ValueError("Unsupported config file format. Use JSON or YAML.")

        # Ensure all parameters are loaded, using defaults if necessary
        default_values = {
            "resample_size": None,
            "create_gpkg": False,
            "nodata_mode": "flag",
            "verbose": False,
            "nodata_value": 0,
            "download_method": "sequential",
            "outfile_prefixes": {"raster": "input", "vector": "target"},
            "mask_remapping": None,
        }
        config_data = {**default_values, **config_data}  # Merge defaults with provided values

        try:
            return cls(**config_data)
        except ValidationError as e:
            raise ValueError(f"Invalid configuration: {e}")
