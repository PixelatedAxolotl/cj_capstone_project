from .constants import EXPECTED_COLUMNS

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


def validate_schools(data_rows, q1_col_index, known_survey_indices):
    """Checks that every Q1 (school) value in the data maps to a known school.
    Args:
        data_rows (list): Raw rows from the spreadsheet (excluding the header row)
        q1_col_index (int): Index of the Q1 column in each row
        known_survey_indices (set): Set of survey_index values that exist in the DB
    Returns:
        dict: {
            'unknown_indices': sorted list of Q1 values with no matching school,
            'rejected': True if any unknown indices were found
        }
    """
    unknown = set()
    for row in data_rows:
        if q1_col_index >= len(row):
            continue
        raw = row[q1_col_index]
        if raw is None or str(raw).strip() == '':
            continue
        try:
            index_val = int(float(raw))
        except (ValueError, TypeError):
            continue
        if index_val not in known_survey_indices:
            unknown.add(index_val)

    return {
        'unknown_indices': sorted(unknown),
        'rejected': len(unknown) > 0,
    }