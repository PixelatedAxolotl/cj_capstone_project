# datasets/crosstabs.py

from collections import defaultdict
from .models import QuestionColumn, RespondentAnswer

def build_crosstab(
    x_question_id,
    base_queryset,
    y_question_ids=None,
    derived_field_map=None,
    pct_type='total',
):
    """
    Build crosstab data for one X question crossed against N Y questions,
    including derived fields stored on related models.

    Args:
        x_question_id (int):
            Question pk for the X axis (columns). Must exist in RespondentAnswer.

        base_queryset:
            Pre-filtered Response queryset. Auth and school scoping must be
            applied by the caller before passing in.

        y_question_ids (list[int] | None):
            Question pks for Y axes sourced from RespondentAnswer.

        derived_field_map (dict | None):
            Y axes sourced from model fields rather than RespondentAnswer.
            Keys are sentinel IDs (use negative integers to avoid clashing
            with real Question pks). Values are dicts:
            {
                'source': 'response' | 'school',  # which model to read from
                'field':  'field_name',            # model field name
                'label':  'Display Label',         # shown in chart/table
            }
            For 'school' source, the Response must have a school FK.

            Example:
                derived_field_map={
                    -1: {'source': 'response', 'field': 'participated_awareness',   'label': 'Career Awareness'},
                    -2: {'source': 'response', 'field': 'participated_exploration', 'label': 'Career Exploration'},
                    -3: {'source': 'response', 'field': 'participated_either',      'label': 'Career Preparedness'},
                }

        pct_type (str): 'total' | 'row' | 'column'

    Returns:
        list[dict] — one dict per Y question/derived field:
        {
            'x_question_id', 'x_label',
            'y_question_id', 'y_label',
            'x_options': list[str],
            'y_options': list[str],
            'counts':      { y_option: { x_option: int } },
            'percentages': { y_option: { x_option: float } },
            'total': int,
            'pct_type': str,
        }
    """
    y_question_ids   = list(y_question_ids or [])
    derived_field_map = derived_field_map or {}

    # use QuestionColumns to load any related questions and options for X and any real Y questions
    all_real_question_ids = [x_question_id] + y_question_ids

    columns = (
        QuestionColumn.objects
        .filter(question_id__in=all_real_question_ids)
        .select_related('question', 'option')
    )

    cols_by_question   = defaultdict(list)
    col_to_question_id = {}
    for col in columns:
        cols_by_question[col.question_id].append(col)
        col_to_question_id[col.id] = col.question_id

    # Fetch RespondentAnswers for X and real Y questions (one query)
    answers = (
        RespondentAnswer.objects
        .filter(
            response__in=base_queryset,
            question_column_id__in=col_to_question_id.keys(),
        )
        .select_related('option')
    )

    # Pivot: response_id -> question_id -> [labels]
    response_answers = defaultdict(lambda: defaultdict(list))
    for ans in answers:
        label = ans.option.display_text if ans.option_id else ans.text_value
        if label:
            response_answers[ans.response_id][col_to_question_id[ans.question_column_id]].append(label)

    # ------------------------------------------------------------------
    # Populate derived field values into the same pivot structure
    #
    #    Uses values() to flatten both 'response' and 'school' sources
    #    into a single query regardless of how many derived fields exist.
    #    To add a new source (e.g. 'district'), add an elif branch below
    #    that maps sentinel_id -> dotted field path for values().
    # ------------------------------------------------------------------
    if derived_field_map:
        fetch_fields = {'id': 'id'}  # maps sentinel_id -> values() field path

        for sentinel_id, config in derived_field_map.items():
            source = config['source']
            field  = config['field']
            if source == 'response':
                fetch_fields[sentinel_id] = field
            elif source == 'school':
                fetch_fields[sentinel_id] = f'school__{field}'
            # add future sources here

        field_path_map = {sid: path for sid, path in fetch_fields.items() if sid != 'id'}

        for row in base_queryset.values('id', *field_path_map.values()):
            for sentinel_id, field_path in field_path_map.items():
                val = row.get(field_path)
                if val is not None:
                    response_answers[row['id']][sentinel_id].append(str(val))

    # ------------------------------------------------------------------
    # 4. Build one result dict per Y axis (real + derived)
    # ------------------------------------------------------------------
    x_cols           = cols_by_question.get(x_question_id, [])
    x_question_label = x_cols[0].question.label if x_cols else ''

    all_y_ids = y_question_ids + list(derived_field_map.keys())
    results   = []

    for y_qid in all_y_ids:
        is_derived = y_qid in derived_field_map

        if is_derived:
            y_label = derived_field_map[y_qid]['label']
            y_cols  = []
        else:
            y_cols = cols_by_question.get(y_qid)
            if not y_cols:
                continue
            y_label = y_cols[0].question.label

        pair_counts = defaultdict(lambda: defaultdict(int))
        x_seen = {}  # label -> numeric_value for ordering
        y_seen = {}
        total  = 0

        for q_answers in response_answers.values():
            x_labels = q_answers.get(x_question_id)
            y_labels = q_answers.get(y_qid)
            if not x_labels or not y_labels:
                continue
            x_label, y_label_val = x_labels[0], y_labels[0]
            pair_counts[y_label_val][x_label] += 1
            x_seen.setdefault(x_label, None)
            y_seen.setdefault(y_label_val, None)
            total += 1

        # Use numeric_value for stable ordering when available (real questions only)
        for col in x_cols:
            if col.option and col.option.display_text in x_seen:
                x_seen[col.option.display_text] = col.option.numeric_value
        for col in y_cols:
            if col.option and col.option.display_text in y_seen:
                y_seen[col.option.display_text] = col.option.numeric_value

        def sort_key(item):
            label, num = item
            return (num is None, num if num is not None else 0, label)

        x_options = [l for l, _ in sorted(x_seen.items(), key=sort_key)]
        y_options = [l for l, _ in sorted(y_seen.items(), key=sort_key)]

        counts = {
            yopt: {xopt: pair_counts[yopt].get(xopt, 0) for xopt in x_options}
            for yopt in y_options
        }


        # Calculate percentages based on the specified pct_type
        #   row: each cell is percentage of its row total
        #   column: each cell is percentage of its column total
        #   total: each cell is percentage of the grand total
        denom = total or 1
        if pct_type == 'row':
            percentages = {
                yopt: {xopt: round(counts[yopt][xopt] / (sum(counts[yopt].values()) or 1) * 100, 1) for xopt in x_options}
                for yopt in y_options
            }
        elif pct_type == 'column':
            col_totals = {xopt: sum(counts[yopt][xopt] for yopt in y_options) for xopt in x_options}
            percentages = {
                yopt: {xopt: round(counts[yopt][xopt] / (col_totals[xopt] or 1) * 100, 1) for xopt in x_options}
                for yopt in y_options
            }
        else:  # 'total'
            percentages = {
                yopt: {xopt: round(counts[yopt][xopt] / denom * 100, 1) for xopt in x_options}
                for yopt in y_options
            }

        results.append({
            'x_question_id': x_question_id,
            'x_label':       x_question_label,
            'y_question_id': y_qid,
            'y_label':       y_label,
            'x_options':     x_options,
            'y_options':     y_options,
            'counts':        counts,
            'percentages':   percentages,
            'total':         total,
            'pct_type':      pct_type,
        })

    return results