from wsgiref import headers

import openpyxl
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .data_validators import validate_columns
from .constants import METADATA_FIELD_MAP, CALCULATED_FIELD_MAP, SKIP_COLS, EXPECTED_COLUMNS, SURVEY_COLUMNS

from django.db import transaction
from .models import Dataset, Response, RespondentAnswer, QuestionColumn, Option
from accounts.models import School
import base64
import io
from datetime import datetime, timezone

from collections import defaultdict


# Create your views here.

@staff_member_required  # only allow admin users access
def upload_dataset(request):
    print("You are in upload_dataset!")
    context = {}

    if request.method == 'POST' and request.FILES.get('dataset_file'):
        file = request.FILES['dataset_file']

        if not file.name.endswith('.xlsx'):
            messages.error(request, 'Only .xlsx files are supported.')
            return render(request, 'datasets/upload.html', context)

        try:
            # Read file contents and encode as base64 for session storage
            file_contents = file.read()
            request.session['upload_file_data'] = base64.b64encode(file_contents).decode('utf-8')
            request.session['upload_file_name'] = file.name

            # Parse for preview
            wb = openpyxl.load_workbook(io.BytesIO(file_contents), read_only=True, data_only=True)
            ws = wb.active
            rows = list(ws.iter_rows(min_row=1, values_only=True))
            headers = list(rows[0])
            row_count = len(rows) - 1
            data_rows = rows[1:]
            wb.close()

            context = {
                'preview': True,
                'headers': headers,
                'row_count': row_count,
                'data_rows': data_rows[:50], # pass only first 50 rows to preview table FOR NOW - TODO: REMOVE THIS LIMIT LATER
                'validation': validate_columns(headers),
                'file_name': file.name,
            }

        except Exception as e:
            messages.error(request, f'Could not parse file: {str(e)}')

    return render(request, 'datasets/upload.html', context)



# TODO: 
#   disable object printing in delete view
#   make deleted datasets recoverable?
@staff_member_required
def confirm_import(request):

    # Retrieve file data stored in session during upload_dataset step
    file_data = request.session.get('upload_file_data')
    file_name = request.session.get('upload_file_name', '')

    if not file_data:
        messages.error(request, 'No file found. Please upload a file first.')
        return redirect('upload_dataset')

    if request.method == 'POST':
        dataset_name = request.POST.get('dataset_name', '').strip() or file_name

        try:
            with transaction.atomic():  # ensure all-or-nothing import — no partial data is ever committed
                
                # Create the Dataset record first so responses can reference it
                dataset = Dataset.objects.create(
                    name=dataset_name,
                    description='',
                    row_count=0,
                )

                # Decode file from session and parse
                file_contents = base64.b64decode(file_data)
                wb = openpyxl.load_workbook(io.BytesIO(file_contents), read_only=True, data_only=True)
                ws = wb.active
                all_rows = list(ws.iter_rows(min_row=1, values_only=True))
                wb.close()

                headers = list(all_rows[0])
                data_rows = all_rows[1:]

                # Map header name to its column index for lookup during row processing
                header_index = {header: index for index, header in enumerate(headers) if header}

                # Pre-fetch all QuestionColumn records into memory to avoid per-row DB queries
                question_column_map = {
                    question_column.column_header: question_column
                    for question_column in QuestionColumn.objects.select_related('question', 'option').all()
                }

                # fetch schools keyed by survey_index to map Q1 numeric values to school names - done here to avoid per-row queries during import loop
                schools_by_index = {
                    school.survey_index: school
                    for school in School.objects.filter(survey_index__isnull=False)
                }

                # fetch options keyed by (category, numeric_value) for single choice and scale questionlookups - done here to avoid per-row queries during import loop
                option_lookup = {
                    (option.category, option.numeric_value): option
                    for option in Option.objects.filter(category__isnull=False)
                }

                def parse_value(raw, cast):
                    #Convert raw cell values to the appropriate Python type for DB insertion.
                    if raw is None:
                        return None
                    try:
                        if cast == 'datetime':
                            # Assumes Qualtrics export format — update if export format changes
                            # Timestamps stored as UTC
                            return datetime.strptime(raw, "%m/%d/%Y %H:%M:%S").replace(tzinfo=timezone.utc).isoformat()
                        elif cast == 'int':
                            return int(float(raw))
                        elif cast == 'str':
                            return str(raw)
                    except (ValueError, TypeError):
                        return None

                imported_count = 0
                skipped_duplicates = []

                for raw_row in data_rows:
                    # Map each header to its cell value for this row
                    row_data = {headers[i]: raw_row[i] for i in range(len(headers)) if i < len(raw_row)}

                    # Skip rows with no ResponseId
                    response_id = row_data.get('ResponseId')
                    if not response_id or str(response_id).strip() == '':
                        continue

                    # Skip duplicate responses and warn user — ResponseId is unique per survey submission
                    if Response.objects.filter(response_id=str(response_id)).exists():
                        skipped_duplicates.append(str(response_id))
                        continue

                    # Build kwargs for Response and RespondentAnswer creation - use SURVEY_COLUMNS to determine field mapping and handling logic for each column
                    response_kwargs = {'dataset': dataset}
                    answer_kwargs_list = []

                    for column_header, column_config in SURVEY_COLUMNS.items():
                        if column_header not in header_index:
                            continue

                        raw_value = row_data.get(column_header)
                        field_type = column_config['field_type']

                        if field_type in ('metadata', 'calculated'):
                            # set defualts in case cast option isn't set in constants.py
                            cast = column_config.get('cast', 'float' if field_type == 'calculated' else 'str')
                            response_kwargs[column_config['model_field']] = parse_value(raw_value, cast)

                        elif field_type == 'school':
                            # Resolve school FK from Q1 numeric value via survey_index
                            if raw_value is not None:
                                try:
                                    response_kwargs[column_config['model_field']] = schools_by_index.get(parse_value(raw_value, column_config.get('cast', 'int')))
                                except (ValueError, TypeError):
                                    pass

                        elif field_type == 'discard':
                            continue

                        elif field_type == 'answer':
                            # Store in RespondentAnswer — handling varies by question type
                            question_column = question_column_map.get(column_header)
                            if question_column is None:
                                continue
                            question_type = question_column.question.question_type

                            if question_type == 'binary':
                                # Only store if selected (value == 1)
                                if raw_value in (1, '1', 1.0):
                                    answer_kwargs_list.append({
                                        'question_column': question_column,
                                        'option': question_column.option,
                                    })

                            # For free text and rank questions, store raw text value/rank number in the text_value field
                            elif question_type == 'free_text' or question_type == 'rank':
                                if raw_value is not None and str(raw_value).strip():
                                    answer_kwargs_list.append({
                                        'question_column': question_column,
                                        'text_value': str(raw_value),
                                    })

                            elif question_type in ('single_choice', 'scale'):
                                # Look up Option by category and numeric value
                                if raw_value is not None:
                                    option = option_lookup.get((question_column.option_category, int(raw_value)))
                                    if option:
                                        answer_kwargs_list.append({
                                            'question_column': question_column,
                                            'option': option,
                                        })

                    # Create Response first since RespondentAnswer records reference it
                    response = Response.objects.create(**response_kwargs)
                    RespondentAnswer.objects.bulk_create([
                        RespondentAnswer(response=response, **answer_kwargs)
                        for answer_kwargs in answer_kwargs_list
                    ])
                    imported_count += 1 #track num rows sucessfully imported

                # Update dataset row count now that all rows have been processed
                dataset.row_count = imported_count
                dataset.save()

            # Clear session file data on successful import
            del request.session['upload_file_data']
            del request.session['upload_file_name']

            if skipped_duplicates:
                messages.warning(
                    request,
                    f'Import complete. {imported_count} rows imported. '
                    f'{len(skipped_duplicates)} duplicate response IDs were skipped: '
                    f'{",".join(skipped_duplicates[:10])}'
                    f'{"..." if len(skipped_duplicates) > 10 else ""}. '
                    f'You may be uploading a dataset that has already been imported.'
                )
            else:
                messages.success(request, f'Import complete. {imported_count} rows imported successfully.')

            return redirect('admin:datasets_dataset_changelist')

        except Exception as e:
            messages.error(request, f'Import failed: {str(e)}. No data was saved.')
            return render(request, 'datasets/confirm_import.html', {
                'file_name': file_name,
                'dataset_name': file_name,
            })

    # GET — show confirmation form with filename pre-populated as dataset name
    return render(request, 'datasets/confirm_import.html', {
        'file_name': file_name,
        'dataset_name': file_name.replace('.xlsx', ''),
    })



@staff_member_required
def dataset_detail(request, dataset_id):
    
    dataset = Dataset.objects.get(pk=dataset_id)

    # Handle dataset name/description edits
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        if name:
            dataset.name = name
            dataset.description = description
            dataset.save()
            messages.success(request, 'Dataset updated successfully.')

    # Fetch all RespondentAnswer records for dataset
    # select_related prevents additional queries when accessing related fields.
    answers = (
        RespondentAnswer.objects
        .filter(response__dataset=dataset)
        .select_related('response', 'question_column', 'question_column__question', 'option')
    )

    # Construct dictionary keyed by response ID
    # For each answer, store either the free text value, the numeric option value,
    # or 1 for binary questions (which only create a record when selected).
    response_answers = defaultdict(dict)
    for respondent_answer in answers:
        
        column_header = respondent_answer.question_column.column_header

        if respondent_answer.text_value is not None:
            response_answers[respondent_answer.response.id][column_header] = respondent_answer.text_value

        elif respondent_answer.option and respondent_answer.option.numeric_value is not None:
            response_answers[respondent_answer.response.id][column_header] = respondent_answer.option.numeric_value

        else:
            response_answers[respondent_answer.response.id][column_header] = 1

    # Fetch Response records to get metadata, calculated score, and school fields
    # select_related used to avoid additional queries when accessing related school field
    responses = list(Response.objects.filter(dataset=dataset).select_related('school'))
    for response in responses:
        response_id = response.id

        for column_header, column_config in SURVEY_COLUMNS.items():
            field_type = column_config['field_type']

            if field_type in ('metadata', 'calculated'):
                response_answers[response_id][column_header] = getattr(response, column_config['model_field'], '')

            elif field_type == 'school':
                response_answers[response_id][column_header] = response.school.name if response.school else ''

    # Build header list from SURVEY_COLUMNS, excluding discarded columns.
    # Column order is determined by the order of entries in SURVEY_COLUMNS.
    headers = [column_header for column_header, column_config in SURVEY_COLUMNS.items() 
               if column_config['field_type'] != 'discard']

    # Build rows in column order for display in template.
    # Missing values default to empty string.
    data_rows = [
        [response_answers[response.id].get(column_header, '') for column_header in headers]
        for response in responses
    ]

    # pass dataset info, headers, and data rows to template for rendering
    context = {
        'dataset': dataset,
        'headers': headers,
        'data_rows': data_rows,
        'row_count': len(data_rows),
    }
    return render(request, 'datasets/dataset_detail.html', context)

