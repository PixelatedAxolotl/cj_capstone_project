import plotly.graph_objects as go
from collections import defaultdict
from django.db.models import Count
from .models import RespondentAnswer, QuestionColumn
from .constants import Q6_PARTICIPATION_COLS, Q7_PARTICIPATION_COLS


# ---------------------------------------------------------------------------
# Crosstab renderers — consume dicts produced by build_crosstab()
# ---------------------------------------------------------------------------


def build_crosstab_table(result, mode='counts'):
    """
    Single Y question as a Plotly Table with heatmap cell shading.

    Args:
        result (dict): One element from build_crosstab()'s return value.
        mode (str):    'counts' | 'percentages'
    """
    x_options = result['x_options']
    y_options = result['y_options']
    data      = result[mode] if mode in result else result['counts']
    suffix    = '%' if mode == 'percentages' else ''

    flat_vals = [data[yopt][xopt] for yopt in y_options for xopt in x_options]
    max_val   = max(flat_vals) if flat_vals else 1

    cell_values = [
        [f"{data[yopt][xopt]}{suffix}" for yopt in y_options]
        for xopt in x_options
    ]
    colors = [
        [f"rgba(38, 87, 144, {data[yopt][xopt] / max_val * 0.55})" if max_val else 'white'
         for yopt in y_options]
        for xopt in x_options
    ]

    fig = go.Figure(data=[go.Table(
        columnwidth=[220] + [140] * len(x_options),
        header=dict(values=[result['y_label']] + x_options, fill_color='#e8edf2', align='left'),
        cells=dict(
            values=[y_options] + cell_values,
            fill_color=[['white'] * len(y_options)] + colors,
            align='left',
        ),
    )])

    row_px = 30  # approximate px per table row (header + each data row)
    height = row_px * (1 + len(y_options)) + 60  # rows + top margin (40) + bottom padding (20)

    fig.update_layout(
        title=dict(text=f"{result['y_label']} × {result['x_label']}", font=dict(size=13)),
        width=220 + 140 * len(x_options),
        height=height,
        autosize=False,
        margin=dict(l=10, r=10, t=40, b=10),
    )

    return fig


def build_combined_crosstab_table(results, mode='counts'):
    """
    All Y questions stacked into one wide horizontally-scrolling Plotly Table.
    Section header rows separate each Y question group.

    Args:
        results (list[dict]): Full return value of build_crosstab().
        mode (str):           'counts' | 'percentages'

    returns:
        Plotly Figure dict
    """
    if not results:
        return go.Figure()

    suffix   = '%' if mode == 'percentages' else ''
    data_key = mode if mode in results[0] else 'counts'

    # Union of x_options across all results
    seen_x = set()
    x_options = []
    for r in results:
        for xopt in r['x_options']:
            if xopt not in seen_x:
                x_options.append(xopt)
                seen_x.add(xopt)

    all_vals = [
        r[data_key][yopt].get(xopt, 0)
        for r in results
        for yopt in r['y_options']
        for xopt in x_options
    ]
    global_max = max(all_vals) if all_vals else 1

    # One row per (y_question, y_option) pair; one column per x_option
    # Section header rows are inserted before each y question group.
    SECTION_COLOR = "#539de6"
    BORDER_COLOR  = "#dde3ea"  # consistent neutral border for all cells

    row_labels      = []
    label_colors    = []
    col_data_by_x   = [[] for _ in x_options]
    col_colors_by_x = [[] for _ in x_options]

    for result in results:
        data = result[data_key]

        # Section header row — spans full width visually via background color
        row_labels.append(result['y_label'])
        label_colors.append(SECTION_COLOR)
        for i in range(len(x_options)):
            col_data_by_x[i].append('')
            col_colors_by_x[i].append(SECTION_COLOR)

        # Data rows for this y question
        for yopt in result['y_options']:
            row_labels.append(f"  {yopt}")
            label_colors.append('white')
            for i, xopt in enumerate(x_options):
                val = data[yopt].get(xopt, 0)
                col_data_by_x[i].append(f"{val}{suffix}")
                col_colors_by_x[i].append(
                    f"rgba(38, 87, 144, {val / global_max * 0.55})" if global_max else 'white'
                )

    fig = go.Figure(data=[go.Table(
        columnwidth=[220] + [140] * len(x_options),
        header=dict(values=[''] + x_options, fill_color='#e8edf2', align='left',
                    line_color=BORDER_COLOR),
        cells=dict(
            values=[row_labels] + col_data_by_x,
            fill_color=[label_colors] + col_colors_by_x,
            align='left',
            line_color=BORDER_COLOR,
        ),
    )])

    fig.update_layout(
        title=dict(text=f"Crosstab: {results[0]['x_label']}", font=dict(size=13)),
        width=220 + 140 * len(x_options),
        autosize=False,
        margin=dict(l=10, r=10, t=40, b=10),
    )

    return fig


def build_grouped_bar(result, mode, legend_title=None, x_axis_title=None, y_axis_title=None):
    """
    Single Y question as a grouped bar chart.
    X axis = X question options. One bar group per Y question option.
    Allows for both count and percentage modes

    Args:
        result (dict): One element from build_crosstab()'s return value.
        mode (str):    'counts' | 'percentages'
    """
    data      = result[mode] if mode in result else result['counts']
    x_options = result['x_options']
    total     = result.get('total') or 1

    # helper to add total count or percentage to each legend label
    def legend_label(yopt):
        row_count = sum(result['counts'][yopt].values())
        if mode == 'percentages':
            pct = round(row_count / total * 100, 1)
            return f"{yopt}: {pct}%"
        return f"{yopt}: {row_count}"

    fig = go.Figure([
        go.Bar(name=legend_label(yopt), x=x_options, y=[data[yopt][xopt] for xopt in x_options])
        for yopt in result['y_options']
    ])

    fig.update_layout(
        barmode='group',
        title=dict(text=f"{result['y_label']}", font=dict(size=13)),
        xaxis_title=x_axis_title or result['x_label'],
        yaxis_title='Percentage of Students' if mode == 'percentages' else 'Number of Students',
        xaxis=dict(type='category'),
        template='plotly_white',
        legend_title=legend_title or result['y_label'],
        legend=dict(
            font=dict(size=14),
            itemsizing='constant',
        ),
        **(dict(yaxis=dict(ticksuffix='%')) if mode == 'percentages' else {}),
    )

    return fig



def build_participation_chart(qs, grade_q, mode):
    """
    Build a participation by grade chart and activity breakdown.
    Returns data for both raw count and percentage modes
    Args:
        qs:       Pre-filtered Response queryset.
        grade_q:  QuestionColumn for the grade question (Q5).
        mode:     'percentages' or 'counts' — whether to display percentages or raw counts in the chart.

    Returns a dict with:
        'figure':    Plotly figure dict — one bar per grade showing % who participated
        'total_pct': float — overall participation rate across all respondents
        'grade_pcts': dict — participation rate per grade e.g. {'9th': 12.3, '10th': 45.6, ...}
        'grade_counts': dict — number of participants per grade e.g. {'9th': 123, '10th': 456, ...}
        'breakdown': {
            'awareness':   [{'label': str, 'pct': float}, ...],  # Q6 activities, sorted desc
            'exploration': [{'label': str, 'pct': float}, ...],  # Q7 activities, sorted desc
        }
    """
    total_responses = qs.count()
    if not total_responses:
        return None

    # Fetch grade label + participation status for all responses
    grade_answers = (
        RespondentAnswer.objects
        .filter(response__in=qs, question_column=grade_q)
        .select_related('response', 'option')
    )

    # Map response_id -> (grade_label, participated)
    response_grades = {}
    for ans in grade_answers:
        if ans.option:
            response_grades[ans.response_id] = {
                'grade':         ans.option.display_text,
                'participated':  ans.response.particip_career_prep_either
            }

    # Count per grade
    grade_totals       = defaultdict(int)
    grade_participated = defaultdict(int)

    for row in response_grades.values():
        grade = row['grade']
        grade_totals[grade] += 1
        if row['participated']:
            grade_participated[grade] += 1

    # Overall participation rate
    total_participants = sum(grade_participated.values())
    total_pct          = round(total_participants / total_responses * 100, 1)

    # Build bar chart — one bar per grade, height = % participated within that grade
    grades = sorted(grade_totals.keys())

    # build y values as either raw counts or percentage based on mode
    y_vals = [
        round(grade_participated[g] / grade_totals[g] * 100, 1) if grade_totals[g] else 0
        for g in grades
    ] if mode == 'percentages' else [
        grade_participated[g] for g in grades
    ]

    # TODO: change to palette colors
    fig = go.Figure([go.Bar(x=grades, y=y_vals, marker_color='#4a7fb5')])
    fig.update_layout(
        title=dict(text='Career Preparation Participation by Average Grade', font=dict(size=13)),
        xaxis_title='Average Grade',
        yaxis_title='Percentage of Students' if mode == 'percentages' else 'Students',
        xaxis=dict(type='category'),
        template='plotly_white',
        yaxis=dict(ticksuffix='%', range=[0, 100]) if mode == 'percentages' else {},
        showlegend=False,
    )


    # Activity breakdown — % of participants who did each activity.
    #    Denominator = total_participants (the 'either' group).

    # Load all options for exploration and awareness activities
    all_activity_cols = Q6_PARTICIPATION_COLS + Q7_PARTICIPATION_COLS
    col_map = {
        qc.column_header: qc
        for qc in QuestionColumn.objects.filter(
            column_header__in=all_activity_cols
        ).select_related('option')
    }

    activity_answers = (
        RespondentAnswer.objects
        .filter(
            response__in=qs,
            response__particip_career_prep_either='Yes',
            question_column__in=col_map.values(),
        )
        .values_list('question_column__column_header', flat=True)
    )

    # Count how many participants selected each activity column
    activity_counts = defaultdict(int)
    for col_header in activity_answers:
        activity_counts[col_header] += 1

    # helper to build breakdown list of options
    def _activity_breakdown(col_list):
        items = []

        if not total_participants:
            return []

        for col_header in col_list:
            qc = col_map.get(col_header)
            if not qc or not qc.option:
                continue
            count = activity_counts.get(col_header, 0)
            items.append({
                'label': qc.option.display_text,
                'pct':   round(count / total_participants * 100, 1),
                'count': count,
            })
        return sorted(items, key=lambda x: x['pct'], reverse=True)

    return {
        'figure':    fig.to_dict(),
        'total_pct': total_pct,
        'total_count': total_participants,
        'grade_pcts': {g: y_vals[i] for i, g in enumerate(grades)},
        'grade_counts': dict(grade_participated),
        'breakdown': {
            'awareness':   _activity_breakdown(Q6_PARTICIPATION_COLS),
            'exploration': _activity_breakdown(Q7_PARTICIPATION_COLS),
        },
    }


def build_top_selections(qs, col_prefix, top_n=3, exclude_cols=None):
    import re
    """
    Return the top N most-selected binary options for a given question prefix.

    Args:
        qs:            Pre-filtered Response queryset.
        col_prefix:    Column header prefix to filter on (e.g. 'Q3_', 'Q25R_').
        top_n:         Number of top results to return (default 3).
        exclude_cols:  Set of column headers to exclude (e.g. {'Q3_16', 'Q3_16_TEXT'}).

    Returns:
        list of dicts, length top_n:
        [
            {
                'label': str,   # Option.display_text
                'pct':   float, # % of respondents who selected this option
                'count': int,   # Number of respondents who selected this option
                'slug':  str,   # image filename slug e.g. 'solving-problems'
            },
            ...
        ]
    """
    exclude_cols  = exclude_cols or set()
    total         = qs.count()

    if not total:
        return []

    # Fetch all relevant QuestionColumns
    cols = (
        QuestionColumn.objects
        .filter(column_header__startswith=col_prefix)
        .exclude(column_header__in=exclude_cols)
        .exclude(option__display_text__isnull=True)
        .select_related('option')
    )

    # Count selections per column — binary answers exist in RespondentAnswer only when selected
    # count = number of RespondentAnswer rows per column
    answer_counts = (
        RespondentAnswer.objects
        .filter(response__in=qs, question_column__in=cols)
        .values('question_column__column_header')
        .annotate(count=Count('id'))
    )

    count_map = {row['question_column__column_header']: row['count'] for row in answer_counts}
    col_map   = {col.column_header: col for col in cols}

    # Build ranked list
    ranked = sorted(
        [
            {
                'label': col.option.display_text,
                'pct':   round(count_map.get(header, 0) / total * 100, 1),
                'count': count_map.get(header, 0),
                'slug':  re.sub(r'[^a-z0-9]+', '-', col.option.display_text.lower()).strip('-'), # construct filename from option text
            }
            for header, col in col_map.items()
        ],
        key=lambda x: x['pct'],
        reverse=True,
    )

    return ranked[:top_n]