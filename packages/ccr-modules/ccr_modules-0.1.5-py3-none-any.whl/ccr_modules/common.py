import datetime
import json
import re
from typing import Optional, Union

import pandas as pd
from loguru import logger

date_formats = {
    "short": "%Y-%m-%d",
    "long": "%Y-%m-%d %H:%M:%S",
}


def read_json(file_path: str) -> dict:
    """
    Reads settings from a JSON file.
    Args:
        file_path (str): The path to the JSON file.
    Returns:
        dict: Settings loaded from the JSON file.
    """
    if not file_path.endswith(".json"):
        raise ValueError("File path must end with .json")
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from file: {file_path}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise
    if not isinstance(data, dict):
        logger.error(f"Data in {file_path} is not a valid JSON object.")
        raise ValueError(f"Data in {file_path} is not a valid JSON object.")
    logger.info(f"Settings loaded from {file_path}")
    logger.debug(f"Settings: {data}")
    return data


def append_to_json(filename: str, new_data: Union[dict, list]) -> None:
    """
    Appends new data to a JSON file. If the file does not exist, it creates it.
    If the file contains a JSON object, it updates it with the new data.
    If the file contains a JSON array, it appends the new data to the array.
    Args:
        filename (str): The path to the JSON file.
        new_data (dict or list): The data to append or update in the JSON file.
    """
    try:
        with open(filename, "r+") as file:
            file_data = json.load(file)
            if isinstance(file_data, list):
                file_data.append(new_data)
            elif isinstance(file_data, dict):
                file_data.update(new_data)
            file.seek(0)
            json.dump(file_data, file, indent=4)
    except FileNotFoundError:
        with open(filename, "w") as file:
            json.dump(
                [new_data] if not isinstance(new_data, dict) else new_data,
                file,
                indent=4,
            )
    except json.JSONDecodeError:
        with open(filename, "w") as file:
            json.dump(
                [new_data] if not isinstance(new_data, dict) else new_data,
                file,
                indent=4,
            )


def date_datetime(date: Union[str, pd.Timestamp]) -> Optional[pd.Timestamp]:
    """
    Converts a date string to a pandas Timestamp.
    Args:
        date (str): The date to convert.
    Returns:
        pd.Timestamp: The converted date as a pandas Timestamp, or None if conversion fails.
    """
    # .strftime(date_formats["short"])
    if isinstance(date, str):
        try:
            ts = pd.to_datetime(date, errors="coerce")
            if pd.isna(ts):
                return None
            return ts
        except ValueError:
            return None  # Return None if conversion fails
    elif isinstance(date, pd.Timestamp):
        return date

    else:
        raise ValueError("Input must be a string or pandas Timestamp.")


def date_string(
    date: Union[str, pd.Timestamp, datetime.date],
    format: str = "long",
    date_formats: dict = date_formats,
) -> str:
    """
    Converts a date string to a standardized format.
    Args:
        date (str): The date to format.
    Returns:
        str: The formatted date string.
    """

    format = format.lower()

    # Check if format is valid
    if format not in date_formats and format != "iso":
        raise ValueError("Invalid format specified. Use 'short', 'long', or 'iso'.")
    # Convert date to pandas Timestamp
    if isinstance(date, pd.Timestamp):
        ts = date
    if isinstance(date, str):
        ts = date_datetime(date)
    elif isinstance(date, datetime.date):
        ts = pd.Timestamp(date)
    if ts is not None:
        return ts.strftime(date_formats[format])
    else:
        # If the date is not a valid string or Timestamp, return it as is
        raise ValueError(
            f"Invalid date input: {date}. Must be a string or pandas Timestamp."
        )


def extract_date(filename: str) -> str:
    """
    Extracts a date from a filename in YYYY-MM-DD format.
    """
    date_pattern = r"\d{4}-\d{2}-\d{2}"  # Matches YYYY-MM-DD
    match = re.search(date_pattern, filename)

    if match:
        date_str = match.group(0)
        extracted_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        return date_str
    else:
        logger.warning(f"No date found in filename: {filename}")
        raise ValueError(
            f"No date found in filename: {filename}. Ensure the filename contains a date in YYYY-MM-DD format."
        )


# Example usage:
# filename = "data.json"
# new_data = {"item": "New Item", "price": 19.99}
# append_to_json(filename, new_data)
