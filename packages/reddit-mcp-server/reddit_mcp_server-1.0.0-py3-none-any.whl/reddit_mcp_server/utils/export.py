"""Data export utilities."""

import csv
import io
import json
from typing import Any, Dict, List


def export_data(data: Any, format: str = "json") -> str:
    """
    Export data in the specified format.

    Args:
        data: Data to export (list of dicts, dict, or any JSON-serializable data)
        format: Export format ('json' or 'csv')

    Returns:
        Formatted string of the exported data
    """
    if format.lower() == "json":
        return json.dumps(data, indent=2, ensure_ascii=False)

    elif format.lower() == "csv":
        if isinstance(data, list) and data and isinstance(data[0], dict):
            # List of dictionaries - perfect for CSV
            return _list_of_dicts_to_csv(data)
        elif isinstance(data, dict):
            # Single dictionary - convert to list with one item
            return _list_of_dicts_to_csv([data])
        else:
            # Not suitable for CSV, return JSON instead
            return json.dumps(data, indent=2, ensure_ascii=False)

    else:
        raise ValueError(f"Unsupported format: {format}. Use 'json' or 'csv'.")


def _list_of_dicts_to_csv(data: List[Dict[str, Any]]) -> str:
    """Convert a list of dictionaries to CSV format."""
    if not data:
        return ""

    # Get all unique keys from all dictionaries
    all_keys = set()
    for item in data:
        all_keys.update(item.keys())

    # Sort keys for consistent output
    fieldnames = sorted(all_keys)

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)

    # Write header
    writer.writeheader()

    # Write rows
    for item in data:
        # Flatten nested structures
        flattened = _flatten_dict(item)
        writer.writerow(flattened)

    return output.getvalue()


def _flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
    """Flatten nested dictionary structures."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(_flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # Convert lists to strings
            items.append((new_key, str(v)))
        else:
            items.append((new_key, v))
    return dict(items)
