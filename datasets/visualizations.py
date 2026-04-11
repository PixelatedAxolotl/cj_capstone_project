import plotly.graph_objects as go
from collections import defaultdict
from django.db.models import Count
from .models import RespondentAnswer, QuestionColumn
from .constants import Q6_PARTICIPATION_COLS, Q7_PARTICIPATION_COLS


def make_slug(text):
    """
        Convert a display label of option into a URL/filename-safe slug.
        Icon image filenames all based on display labels
    """
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


# ---------------------------------------------------------------------------
# Visual constants
# Note: applyPlotlyTheme() in plotly_config.js overrides these at render time
# using CSS variables, so they serve as SSR defaults only.
# Table cell fill_color arrays are not overridable by a simple relayout, so
# the JS rebases them explicitly — see applyPlotlyTheme in plotly_config.js.
# ---------------------------------------------------------------------------

# TODO: get these constants out of the python side and into js/css with the rest of them
# Table layout (px)
COL_WIDTH_LABEL = 150
COL_WIDTH_DATA  = 140
ROW_HEIGHT_PX   = 25
TABLE_MARGIN_PX = 60  # top margin (40) + bottom padding (20)

# Heatmap cell shading — base RGB kept in sync with --plotly-table-heatmap (#265790)
HEATMAP_RGB   = (38, 87, 144)
HEATMAP_ALPHA = 0.55

# Bar chart fill — overridden client-side by --plotly-bar-1
COLOR_BAR = '#265790'


# TODO: map/combine old career clusters to new clusters for analysis
CAREER_CLUSTER_FIELDS = [
    ('career_score_agriculture',       'Agriculture, Food & Natural Resources'),
    ('career_score_architecture',      'Architecture & Construction'),
    ('career_score_arts_av_comm',      'Arts, A/V Technology & Communications'),
    ('career_score_business_mgmt',     'Business Management & Administration'),
    ('career_score_education',         'Education & Training'),
    ('career_score_energy',            'Energy'),
    ('career_score_finance',           'Finance'),
    ('career_score_government',        'Government & Public Administration'),
    ('career_score_health_sciences',   'Health Care and Human Services'),
    ('career_score_hospitality',       'Hospitality & Tourism'),
    ('career_score_human_services',    'Human Services'),
    ('career_score_information_tech',  'Information Technology'),
    ('career_score_law_public_safety', 'Law, Public Safety, Corrections & Security'),
    ('career_score_manufacturing',     'Manufacturing'),
    ('career_score_marketing',         'Marketing'),
    ('career_score_stem',              'Science, Technology, Engineering & Mathematics'),
    ('career_score_telecommunications','Telecommunications'),
    ('career_score_transportation',    'Transportation, Distribution & Logistics Services'),
]


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


def build_grouped_bar(result, mode, title=None, legend_title=None, x_axis_title=None, y_axis_title=None):
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
        title=title or dict(text=f"{result['y_label']}", font=dict(size=15), x=0.5, xanchor='center'),
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
    fig = go.Figure([go.Bar(x=grades, y=y_vals, marker_color=COLOR_BAR)])
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
            response__particip_career_prep_either=True,
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


def build_aptitude_summary(qs):
    """
    Return average aptitude scores (out of 20) across all responses in qs.

    Returns a dict:
        { 'verbal': float, 'spatial': float, 'cognitive': float, 'numerical': float }
    """
    result = qs.aggregate(
        verbal=Avg('score_verbal_aptitude'),
        spatial=Avg('score_spatial_aptitude'),
        cognitive=Avg('score_cognitive_aptitude'),
        numerical=Avg('score_numerical_aptitude'),
    )
    return {
        'verbal':    round(result['verbal']    or 0, 2),
        'spatial':   round(result['spatial']   or 0, 2),
        'cognitive': round(result['cognitive'] or 0, 2),
        'numerical': round(result['numerical'] or 0, 2),
    }

# TODO: fix ordering to be based on average grade
def build_career_cluster_top3(qs):
    """
    Return the top 3 career clusters by average composite score, with grade-group callouts.

    For each grade group (from Q5), determines which cluster is most commonly #1
    per respondent. Then annotates each of the overall top 3 with the grade groups
    that have it as their most popular cluster.

    Returns a list of 3 dicts:
        [
            {
                'label':          str,    # display name of the cluster
                'avg_score':      float,  # average career composite score
                'grade_callouts': list,   # grade labels for which this is the #1 cluster
                'slug':           str,    # field suffix, e.g. 'telecommunications'
            },
            ...
        ]
    """
    career_field_names = [f for f, _ in CAREER_CLUSTER_FIELDS]

    # Average composite score per cluster across all responses
    agg = qs.aggregate(**{field: Avg(field) for field in career_field_names})

    ranked = sorted(
        [(field, label, agg.get(field) or 0) for field, label in CAREER_CLUSTER_FIELDS],
        key=lambda x: x[2],
        reverse=True,
    )
    top3 = ranked[:3]
    top3_fields = {field for field, _, _ in top3}
    grade_callouts = {field: [] for field in top3_fields}

    # Grade-segmented callouts: for each grade group, find the most commonly #1 cluster
    try:
        grade_q = QuestionColumn.objects.get(column_header='Q5')
    except QuestionColumn.DoesNotExist:
        grade_q = None

    if grade_q:
        # Map response pk -> grade label
        grade_answers = (
            RespondentAnswer.objects
            .filter(response__in=qs, question_column=grade_q)
            .select_related('option')
        )
        response_grade = {
            ans.response_id: ans.option.display_text
            for ans in grade_answers if ans.option
        }

        # For each response, count how many respondents per grade have each cluster as their #1
        responses_scores = qs.values('id', *career_field_names)
        cluster_grade_counts = defaultdict(Counter)
        for row in responses_scores:
            grade = response_grade.get(row['id'])
            if not grade:
                continue
            best_field = max(career_field_names, key=lambda f: row.get(f) or 0)
            cluster_grade_counts[best_field][grade] += 1

        # For each top-3 cluster, find the single grade that most frequently had it as #1
        for field in top3_fields:
            if cluster_grade_counts[field]:
                best_grade = cluster_grade_counts[field].most_common(1)[0][0]
                grade_callouts[field] = [best_grade]

    return [
        {
            'label':          label,
            'avg_score':      round(avg, 1),
            'grade_callouts': sorted(grade_callouts.get(field, [])),
            'slug':           field.replace('career_score_', ''),
        }
        for field, label, avg in top3
    ]


def build_post_hs_conversations(qs):
    """
    Return statistics about who students talked to regarding their post-high-school plans.

    Q9_*: binary multi-select "Who have you spent time talking with about your plans
          for after high school?"
    Q10:  single_choice "Of those, who have you spent the most time talking with?"
    Q11:  single_choice "Who would you say has had the greatest influence on your future plans?"

    Returns a dict:
        {
            'talked_pct':         float  — % of all respondents who talked to at least one person
            'talked_count':       int    — raw count of those respondents
            'who_talked_to':      list   — top 2 [{label, pct, count}] from Q9_* (excl. "No one")
            'most_time':          list   — top 2 [{label, pct, count}] from Q10
            'biggest_influence':  list   — top 2 [{label, pct, count}] from Q11
        }
    or None if qs is empty.
    """
    total = qs.count()
    if not total:
        return None

    # Q9_* binary columns — who they talked to; exclude "No one" (Q9_8) and free-text field
    q9_cols = list(
        QuestionColumn.objects
        .filter(column_header__startswith='Q9_')
        .exclude(column_header__in={'Q9_8', 'Q9_7_TEXT'})
        .select_related('option')
    )

    # % talked to at least one person (any Q9_* selection except "No one")
    talked_count = (
        RespondentAnswer.objects
        .filter(response__in=qs, question_column__in=q9_cols)
        .values('response_id')
        .distinct()
        .count()
    )
    talked_pct = round(talked_count / total * 100, 1)

    # Top 2 Q9_* options by selection count
    q9_answer_counts = (
        RespondentAnswer.objects
        .filter(response__in=qs, question_column__in=q9_cols)
        .values('question_column__column_header')
        .annotate(count=Count('id'))
    )
    q9_count_map = {row['question_column__column_header']: row['count'] for row in q9_answer_counts}
    q9_col_map   = {col.column_header: col for col in q9_cols}

    who_talked_to = sorted(
        [
            {
                'label': col.option.display_text,
                'pct':   round(q9_count_map.get(header, 0) / total * 100, 1),
                'count': q9_count_map.get(header, 0),
            }
            for header, col in q9_col_map.items()
            if col.option
        ],
        key=lambda x: x['pct'],
        reverse=True,
    )[:2]

    # Helper: top 2 options for a single_choice question column
    def _top2_single(col_header):
        try:
            qc = QuestionColumn.objects.get(column_header=col_header)
        except QuestionColumn.DoesNotExist:
            return []
        rows = (
            RespondentAnswer.objects
            .filter(response__in=qs, question_column=qc)
            .values('option__display_text')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        return [
            {
                'label': row['option__display_text'],
                'pct':   round(row['count'] / total * 100, 1),
                'count': row['count'],
            }
            for row in rows[:2]
            if row['option__display_text']
        ]

    return {
        'talked_pct':        talked_pct,
        'talked_count':      talked_count,
        'who_talked_to':     who_talked_to,
        'most_time':         _top2_single('Q10'),
        'biggest_influence': _top2_single('Q11'),
    }


def build_top_selections(qs, col_prefix, top_n=3, exclude_cols=None):
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
                'slug':  make_slug(col.option.display_text),
            }
            for header, col in col_map.items()
        ],
        key=lambda x: x['pct'],
        reverse=True,
    )

    return ranked[:top_n]