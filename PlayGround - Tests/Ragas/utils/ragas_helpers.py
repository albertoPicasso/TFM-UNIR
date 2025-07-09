from typing import Dict, List, Any
from datetime import datetime
import os
import re
import json
from typing import List, Dict, Iterator, Any, Union
from ast import literal_eval


def parse_line(line: str, source_file: str = "") -> Dict[str, str]:
    """
    Parse a single line from the dataset into a dictionary.

    Args:
        line: A string in the format "type#id#question#answer"
        source_file: Name of the file this entry came from (optional)

    Returns:
        Dictionary with parsed components
    """
    # Split the line by '#' character
    parts = line.strip().split('#')

    # Ensure we have exactly 4 parts
    if len(parts) != 4:
        raise ValueError(f"Invalid line format: {line}")

    # Create and return a dictionary
    return {
        "type": parts[0],
        "id": parts[1],
        "question": parts[2],
        "answer": parts[3],
        "source_file": source_file
    }


def read_qa_file(file_path: str) -> List[Dict[str, str]]:
    """
    Read a question-answer dataset file and parse each line.

    Args:
        file_path: Path to the dataset file

    Returns:
        List of dictionaries with parsed entries
    """
    entries = []
    filename = os.path.basename(file_path)

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if line.strip():  # Skip empty lines
                    try:
                        entry = parse_line(line, filename)
                        entries.append(entry)
                    except ValueError as e:
                        print(f"Skipping invalid line in {filename}: {e}")
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")

    return entries


def process_qa_folder(folder_path: str, file_extension: str = ".txt") -> List[Dict[str, str]]:
    """
    Process all question-answer dataset files in a folder.

    Args:
        folder_path: Path to the folder containing the datasets
        file_extension: File extension to filter for (default: .txt)

    Returns:
        List of dictionaries with parsed entries from all files
    """
    all_entries = []

    try:
        # List all files in the directory
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))
                 and f.endswith(file_extension)]

        if not files:
            print(f"No {file_extension} files found in {folder_path}")
            return all_entries

        # Process each file
        for filename in files:
            file_path = os.path.join(folder_path, filename)
            print(f"Processing file: {filename}")
            file_entries = read_qa_file(file_path)
            all_entries.extend(file_entries)
            print(f"Added {len(file_entries)} entries from {filename}")

    except Exception as e:
        print(f"Error processing folder {folder_path}: {e}")

    return all_entries


def get_entries_by_file(entries: List[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
    """
    Group entries by their source file.

    Args:
        entries: List of entry dictionaries

    Returns:
        Dictionary mapping filenames to lists of entries
    """
    file_entries = {}

    for entry in entries:
        source_file = entry.get("source_file", "")
        if source_file not in file_entries:
            file_entries[source_file] = []
        file_entries[source_file].append(entry)

    return file_entries


def iterate_qa_entries(entries: List[Dict[str, str]]) -> Iterator[Dict[str, str]]:
    """
    Generator function to iterate through QA entries.
    Useful for processing large datasets without loading everything into memory.

    Args:
        entries: List of entry dictionaries

    Yields:
        Entry dictionaries one by one
    """
    for entry in entries:
        yield entry


def parse_llm_response(response_str: str) -> dict:
    """
    Parse an LLM response string and extract content, additional_kwargs, and response_metadata.

    Args:
        response_str: The raw response string from the LLM

    Returns:
        Dictionary with extracted content, additional_kwargs, and response_metadata
    """
    result = {}

    # Extract content (everything between content=' and the next property)
    content_match = re.search(
        r"content='(.*?)' additional_kwargs", response_str, re.DOTALL)
    if content_match:
        result['content'] = content_match.group(1)
    else:
        result['content'] = ""

    # Extract additional_kwargs
    additional_kwargs_match = re.search(
        r"additional_kwargs=(\{.*?\}) response_metadata", response_str, re.DOTALL)
    if additional_kwargs_match:
        # Try to parse as JSON if possible
        try:
            kwargs_str = additional_kwargs_match.group(1).replace("'", '"')
            result['additional_kwargs'] = json.loads(kwargs_str)
        except json.JSONDecodeError:
            # If JSON parsing fails, keep as string
            result['additional_kwargs'] = additional_kwargs_match.group(1)
    else:
        result['additional_kwargs'] = {}

    # Extract response_metadata
    metadata_match = re.search(
        r"response_metadata=(\{.*?\}) id=", response_str, re.DOTALL)
    if metadata_match:
        # Try to parse as JSON if possible
        try:
            metadata_str = metadata_match.group(1).replace("'", '"')
            result['response_metadata'] = json.loads(metadata_str)
        except json.JSONDecodeError:
            # If JSON parsing fails, keep as string
            result['response_metadata'] = metadata_match.group(1)
    else:
        result['response_metadata'] = {}

    return result


def _parse_llm_response_robust(response_str: Union[str, Any]) -> Dict[str, Any]:
    """
    Parse an LLM response string and extract content, additional_kwargs, and response_metadata
    using a more robust approach with better error handling.

    Args:
        response_str: The raw response string from the LLM or response object

    Returns:
        Dictionary with extracted content, additional_kwargs, and response_metadata
    """
    result = {
        'content': "",
        'additional_kwargs': {},
        'response_metadata': {}
    }

    # Check if response_str is a string
    if not isinstance(response_str, str):
        try:
            # If it's an object with attributes, try to access them directly
            if hasattr(response_str, 'content'):
                result['content'] = response_str.content
            if hasattr(response_str, 'additional_kwargs'):
                result['additional_kwargs'] = response_str.additional_kwargs
            if hasattr(response_str, 'response_metadata'):
                result['response_metadata'] = response_str.response_metadata
            return result
        except Exception:
            # If it's not a string and we can't extract attributes, convert to string
            try:
                response_str = str(response_str)
            except Exception:
                print("Error: Could not convert input to string")
                return result

    try:
        # Extract content
        content_pattern = r"content=['\"]?(.*?)['\"]? additional_kwargs"
        content_match = re.search(content_pattern, response_str, re.DOTALL)
        if content_match:
            result['content'] = content_match.group(1).strip("'\"")

        # Extract additional_kwargs
        kwargs_pattern = r"additional_kwargs=(\{.*?\}) response_metadata"
        kwargs_match = re.search(kwargs_pattern, response_str, re.DOTALL)
        if kwargs_match:
            try:
                # Use literal_eval for safer parsing of Python literals
                result['additional_kwargs'] = literal_eval(
                    kwargs_match.group(1))
            except (ValueError, SyntaxError):
                result['additional_kwargs'] = kwargs_match.group(1)

        # Extract response_metadata
        metadata_pattern = r"response_metadata=(\{.*?\}) id="
        metadata_match = re.search(metadata_pattern, response_str, re.DOTALL)
        if metadata_match:
            try:
                # Use literal_eval for safer parsing of Python literals
                result['response_metadata'] = literal_eval(
                    metadata_match.group(1))
            except (ValueError, SyntaxError):
                result['response_metadata'] = metadata_match.group(1)
    except Exception as e:
        print(f"Error parsing response: {e}")

    return result


def save_evaluation_data_to_json(data_to_evaluate: Dict[str, List[Any]],
                                 output_dir: str = "evaluation_results",
                                 filename: str = None) -> str:
    """
    Save evaluation data to a plain JSON file.

    Args:
        data_to_evaluate: Dictionary containing evaluation data with arrays
        output_dir: Directory where the JSON file will be saved (default: "evaluation_results")
        filename: Custom filename (optional). If None, a timestamp-based name will be used

    Returns:
        Path to the saved JSON file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Generate filename with timestamp if not provided
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"evaluation_data_{timestamp}.json"

    # Ensure filename has .json extension
    if not filename.endswith('.json'):
        filename += '.json'

    # Full path to output file
    output_path = os.path.join(output_dir, filename)

    try:
        # Validate that all arrays have the same length
        array_lengths = {key: len(
            value) for key, value in data_to_evaluate.items() if isinstance(value, list)}
        if len(set(array_lengths.values())) > 1:
            print(f"Warning: Arrays have different lengths: {array_lengths}")

        # Write data to JSON file with proper formatting
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_evaluate, f, ensure_ascii=False, indent=2)

        print(f"Evaluation data successfully saved to {output_path}")
        return output_path

    except Exception as e:
        print(f"Error saving evaluation data to JSON: {e}")
        # Try to save with a different name if there was an error
        if "permission denied" in str(e).lower():
            alt_filename = f"evaluation_data_alt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            alt_path = os.path.join(output_dir, alt_filename)
            try:
                with open(alt_path, 'w', encoding='utf-8') as f:
                    json.dump(data_to_evaluate, f,
                              ensure_ascii=False, indent=2)
                print(f"Evaluation data saved to alternative path: {alt_path}")
                return alt_path
            except Exception as e2:
                print(f"Failed to save to alternative path: {e2}")

        return None
