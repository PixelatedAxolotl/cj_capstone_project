from django.shortcuts import render
import openpyxl
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.contrib import messages
from .data_validators import validate_columns

# Create your views here.

@staff_member_required  # only allow admin users access
def upload_dataset(request):
    context = {}

    if request.method == 'POST' and request.FILES.get('dataset_file'):
        file = request.FILES['dataset_file']

        if not file.name.endswith('.xlsx'):
            messages.error(request, 'Only .xlsx files are supported.')
            return render(request, 'datasets/upload.html', context)

        try:
            wb = openpyxl.load_workbook(file, read_only=True, data_only=True)
            ws = wb.active
            rows = list(ws.iter_rows(min_row=1, values_only=True))
            headers = list(rows[0])
            row_count = len(rows) - 1
            data_rows = rows[1:]
            wb.close()

            validation = validate_columns(headers)

            context = {
                'preview': True,
                'headers': headers,
                'row_count': row_count,
                'data_rows': data_rows[:50], # pass only first 50 rows to preview table FOR NOW - TO DO: REMOVE THIS LIMIT LATER
                'validation': validation,
                'file_name': file.name,
            }

        except Exception as e:
            messages.error(request, f'Could not parse file: {str(e)}')

    return render(request, 'datasets/upload.html', context)