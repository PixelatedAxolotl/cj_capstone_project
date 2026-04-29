# datasets/crosstabs.py

from collections import defaultdict
from .models import QuestionColumn, RespondentAnswer, Question

def build_crosstab(
    x_question_id,
    base_queryset,
    y_question_ids=None,
    pct_type='total',
):
    """
    Build crosstab data for one X question crossed against N Y questions.
    Y axes may include questions of type 'calculated', which are read directly
    from Response model fields rather than RespondentAnswer records.

    Args:
        x_question_id (int):
            Question pk for the X axis (columns). Must exist in RespondentAnswer.

        base_queryset:
            Pre-filtered Response queryset. Auth and school scoping must be
            applied by the caller before passing in.

        y_question_ids (list[int] | None):
            Question pks for Y axes. Questions with question_type='calculated'
            are handled automatically via their label field (Response field name).

        pct_type (str): 'total' | 'row' | 'column'

    Returns:
        list[dict] — one dict per Y question:
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
    y_question_ids = list(y_question_ids or [])

    # Separate calculated questions (read from Response fields) from survey
    # questions (read from RespondentAnswer records via QuestionColumn).
    y_question_objects = Question.objects.filter(id__in=y_question_ids).in_bulk()
    calculated_qs  = {q.id: q for q in y_question_objects.values() if q.question_type == 'calculated'}
    real_y_ids     = [i for i in y_question_ids if i not in calculated_qs]

    # Load QuestionColumns for X and all real Y questions
    columns = (
        QuestionColumn.objects
        .filter(question_id__in=[x_question_id] + real_y_ids)
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

    # Populate calculated field values into the same pivot structure using
    # a single values() query across all calculated fields at once.
    if calculated_qs:
        fetch_fields = {q.id: q.label for q in calculated_qs.values()}

        for row in base_queryset.values('id', *fetch_fields.values()):
            for question_id, field_name in fetch_fields.items():
                val = row.get(field_name)
                if val is not None:
                    response_answers[row['id']][question_id].append(str(val))

    # Build one result dict per Y axis
    x_cols           = cols_by_question.get(x_question_id, [])
    x_question_label = (x_cols[0].question.crosstab_label or x_cols[0].question.label) if x_cols else ''

    results = []

    for y_qid in y_question_ids:
        if y_qid in calculated_qs:
            y_label = calculated_qs[y_qid].crosstab_label
            y_cols  = []
        else:
            y_cols = cols_by_question.get(y_qid)
            if not y_cols:
                continue
            y_label = y_cols[0].question.crosstab_label or y_cols[0].question.label

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
