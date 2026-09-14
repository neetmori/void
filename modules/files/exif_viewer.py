from pathlib import Path

from PIL import ExifTags, Image
from rich.table import Table

from core.logger import save_log
from core.ui import console, module_header, pause


def rational_to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError, ZeroDivisionError):
        return None


def gps_to_decimal(values, ref):
    if not values or len(values) != 3:
        return None
    parts = [rational_to_float(item) for item in values]
    if any(item is None for item in parts):
        return None
    decimal = parts[0] + parts[1] / 60 + parts[2] / 3600
    if ref in {"S", "W"}:
        decimal *= -1
    return decimal


def serialize_value(value):
    if isinstance(value, bytes):
        return value.hex()
    if isinstance(value, tuple):
        return [serialize_value(item) for item in value]
    if isinstance(value, list):
        return [serialize_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): serialize_value(item) for key, item in value.items()}
    try:
        return str(value)
    except Exception:
        return repr(value)


def run():
    module_header("EXIF Viewer", "Files")
    raw = console.input("[bold white]Image path:[/bold white] ").strip().strip('"')
    path = Path(raw).expanduser()
    if not path.is_file():
        console.print("[red]Image not found.[/red]")
        pause()
        return

    try:
        with Image.open(path) as image:
            exif = image.getexif()
            metadata = {
                "format": image.format,
                "mode": image.mode,
                "width": image.width,
                "height": image.height,
                "animated": bool(getattr(image, "is_animated", False)),
                "frames": int(getattr(image, "n_frames", 1)),
                "info": {str(key): serialize_value(value) for key, value in image.info.items() if key not in {"icc_profile", "exif"}},
            }
            decoded = {}
            gps_raw = None
            for tag_id, value in exif.items():
                name = ExifTags.TAGS.get(tag_id, str(tag_id))
                if name == "GPSInfo":
                    try:
                        gps_raw = exif.get_ifd(tag_id)
                    except Exception:
                        gps_raw = value
                decoded[name] = serialize_value(value)
    except Exception as exc:
        console.print(f"[red]Could not read image metadata: {exc}[/red]")
        pause()
        return

    gps = {}
    if isinstance(gps_raw, dict):
        named_gps = {ExifTags.GPSTAGS.get(key, str(key)): value for key, value in gps_raw.items()}
        latitude = gps_to_decimal(named_gps.get("GPSLatitude"), named_gps.get("GPSLatitudeRef"))
        longitude = gps_to_decimal(named_gps.get("GPSLongitude"), named_gps.get("GPSLongitudeRef"))
        gps = {key: serialize_value(value) for key, value in named_gps.items()}
        if latitude is not None:
            gps["LatitudeDecimal"] = latitude
        if longitude is not None:
            gps["LongitudeDecimal"] = longitude

    summary = Table(title="Image Metadata", show_header=False, border_style="red")
    summary.add_column("Field", style="bold red")
    summary.add_column("Value", style="white")
    for key in ["format", "mode", "width", "height", "animated", "frames"]:
        summary.add_row(key.title(), str(metadata[key]))
    summary.add_row("EXIF Tags", str(len(decoded)))
    if gps.get("LatitudeDecimal") is not None and gps.get("LongitudeDecimal") is not None:
        summary.add_row("GPS Coordinates", f"{gps['LatitudeDecimal']}, {gps['LongitudeDecimal']}")
    console.print(summary)

    if decoded:
        table = Table(title="EXIF Tags", border_style="red")
        table.add_column("Tag", style="bold red")
        table.add_column("Value", style="white")
        for key in sorted(decoded):
            table.add_row(key, str(decoded[key]))
        console.print(table)

    if gps:
        gps_table = Table(title="GPS Metadata", border_style="red")
        gps_table.add_column("Field", style="bold red")
        gps_table.add_column("Value", style="white")
        for key, value in gps.items():
            gps_table.add_row(str(key), str(value))
        console.print(gps_table)

    log_path = save_log("exif_viewer", str(path.resolve()), {"image": metadata, "exif": decoded, "gps": gps})
    console.print(f"[dim]Log saved to {log_path}[/dim]")
    pause()
