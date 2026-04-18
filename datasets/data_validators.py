from .constants import EXPECTED_COLUMNS

# TODO: add validation rules for:
# - school id that does not exist in the DB

# check for missing cols or unexpected cols in input and set rejection flag if too many are missing (25% or more)
def validate_columns(file_columns):
    """Validates uploaded dataset
    Args:
        file_columns (list): List of column headers in the uploaded file
    Returns:
        dict: {
            'missing': list of missing columns,
            'unexpected': list of unexpected columns,
            'missing_count': number of missing columns,
            'missing_percent': percentage of missing columns,
            'rejected': boolean flag indicating whether to reject the file based on missing columns
        }
    """

    expected_set = set(EXPECTED_COLUMNS)
    file_set = set(file_columns)

    missing = expected_set - file_set
    unexpected = file_set - expected_set
    missing_percent = (len(missing) / len(EXPECTED_COLUMNS)) * 100

    return {
        'missing': sorted(missing),
        'unexpected': sorted(unexpected),
        'missing_count': len(missing),
        'missing_percent': missing_percent,
        'rejected': missing_percent > 25,
    }