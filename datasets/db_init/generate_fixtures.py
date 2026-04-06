"""
SHOULD ONLY BE RUN ONCE FOR INITIAL DB SETUP
utility script to generate Django fixtures for Question, Option, and questionColumn tables.

Deduplication rules:
- 1 Question record per logical question (binary sub-columns consolidated into group)
- 1 Option record per unique display_text (shared across all questions with same option text)
- 1 questionColumn record per raw column header

Usage:
    2. Place question_map.xlsx in the same directory as this file
    4. Run: python generate_fixtures.py
    5. Load: python manage.py loaddata datasets/db_init/structure_gen/questions_and_options.json

Output: datasets/db_init/structure_gen/questions_and_options.json
"""
import sys
import os

# Add Django project root to path so we can import from the project
# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cj_dashboard.settings')



import django
django.setup()

from datasets.constants import SURVEY_COLUMNS

import json
import openpyxl
from collections import Counter




# ─── SINGLE CHOICE OPTION MAPPINGS ────────────────────────────────────────────
# Format: {numeric_value: 'display_text'}
# Numeric values must match exactly what appears in the exported data.
SINGLE_CHOICE_OPTIONS = {

# what grade
    'Q2': {
        1: '7th grade', 2: '8th grade', 3: '9th grade',
        4: 'N/A',
        5: '10th grade', 6: '11th grade', 7: '12th grade',
    },

    # letter grade average
    'Q5': {
        1: 'F', 2: 'D', 3: 'C', 4: 'B', 5: 'A',
    },

    # most time talking about future plans
    'Q10': {
        1: 'Your parent(s) or guardian(s)', 2: 'Other adult family member(s)', 3: 'A schoool guidance counselor',
        4: 'A teachor or coach', 5: 'Your friends', 6: 'Your brother(s) or sister(s)',
        7: 'Someone else (specify)', 8: 'No one',
    },

    # "Of those, who would you say you have spent the most time talking about your future plans?"
    # SAME AS Q10 options
    'Q11': {
        1: 'Your parent(s) or guardian(s)', 2: 'Other adult family member(s)', 3: 'A schoool guidance counselor',
        4: 'A teachor or coach', 5: 'Your friends', 6: 'Your brother(s) or sister(s)',
        7: 'Someone else (specify)', 8: 'No one',
    },

    # "...Living in the area or moving away after highschool?"
    'Q14': {
        1: 'Living in the area', 2: 'Moving away', 3: 'Not sure yet',
        4: 'Moving away for school, then returning',
    },

    # imagine life between ages 22 and 26, what amount of money do you see yourself earning per year?
    'Q15': {
        1: 'Less than $30,000/year', 2: '$30,000-$50,000/year', 3: '$50,000-$70,000/year',
        4: 'Over $70,000/year',
    },

    # how many parents/caregivers do you live with?
    'Q18': {
        1: 'One', 2: 'Two', 3: 'Three', 4: 'Four', 5: 'More than four'
    },

    # What area do you live in?
    'Q22': {
        1: 'Urban', 2: 'Suburban', 3: 'Rural',
    },

    # What type of learner are you?
    'Q23': {
        1: '''I learn best by seeing pictures or images, including graphs and charts.
        I like to seewhat I am learning. I understand and remember things best when I have seen them.''',

        2: '''I learn best by hearing and listening.
        I understand and remember things best when I have heard them.
        I have an easier time understanding spoken instructions than written ones.
        I often read out loud because I have to hear it or speak it in order to know it.''',

        3: '''I learn best by reading and writing. I take notes and re-read them later.
        I have an easier time understanding written instructions than spoken ones.''',

        4: '''I learn best by doing.
        I understand and remember things best when I am active and participate "hands-on".
        I prefer to touch, move, build, or draw what I learn, and sometimes have difficulty sitting still.''',
    },
}


# Scale options for Q25 series (slider 1-5)
SCALE_OPTIONS = {
    1: 'Not good at all',
    2: 'Not very good',
    3: 'Average',
    4: 'Pretty good',
    5: 'Very good',
}

# Aptitude frequency options for Aptitude_1-9
APTITUDE_OPTIONS = {
    1: 'Never',
    2: 'Rarely',
    3: 'Sometimes',
    4: 'Frequently',
    5: 'Always',
}


SINGLE_CHOICE_CATEGORIES = {
    'Q2': 'grade',
    'Q5': 'letter_grade',
    'Q10': 'people',
    'Q11': 'people',
    'Q14': 'location',
    'Q15': 'earnings',
    'Q18': 'caregiver_count',
    'Q22': 'area_type',
    'Q23': 'learning_style',
}


# ─── COLUMN SETS ──────────────────────────────────────────────────────────────

METADATA_COLS = {
    'StartDate', 'EndDate', 'Status', 'Progress', 'Duration__in_seconds_',
    'Finished', 'RecordedDate', 'ResponseId', 'DistributionChannel',
    'UserLanguage', 'Year', 'Semester', 'StartMonth',
}

SCHOOL_COL = {'Q1'}

CALCULATED_COLS = {
    'SC0', 'SC1', 'SC2', 'SC3', 'SC4', 'SC5', 'SC6', 'SC7', 'SC8', 'SC9',
    'SC10', 'SC11', 'SC12', 'SC13', 'SC14', 'SC15', 'SC16', 'SC17',
    'SC22', 'SC23', 'SC24', 'SC25',
    'Career_1_Score', 'Career_2_Score', 'Career_3_Score', 'Career_4_Score',
    'Career_5_Score', 'Career_6_Score', 'Career_7_Score', 'Career_8_Score',
    'Career_9_Score', 'Career_10_Score', 'Career_11_Score', 'Career_12_Score',
    'Career_13_Score', 'Career_14_Score', 'Career_15_Score', 'Career_16_Score',
    'Career_17_Score', 'Career_18_Score',
    'AwarenessScore', 'ExplorationScore', 'CareerPrepScore',
    'Career_Awareness', 'Career_Exploration',
}

DISCARDED_COLS = {'Q5R', 'Q6R', 'Q7R', 'Q6R_Q7R', 'Q20A', 'Q20B', 'Q20C', 'Q20D'}

SKIP_COLS = METADATA_COLS | SCHOOL_COL | CALCULATED_COLS | DISCARDED_COLS

FREE_TEXT_COLS = {
    'Q3_16_TEXT', 'Q4_16_TEXT', 'Q7A_6_TEXT', 'Q9_7_TEXT',
    'Q10_7_TEXT', 'Q11_7_TEXT', 'Q16_5_TEXT',
}

SCALE_COLS = {
    'Q25', 'Q25A', 'Q25B', 'Q25C', 'Q25D', 'Q25E', 'Q25F', 'Q25G',
    'Q25H', 'Q25I', 'Q25J', 'Q25K', 'Q25L', 'Q25M', 'Q25N', 'Q25O',
    'Q25P', 'Q25Q',
}

APTITUDE_COLS = {f'Aptitude_{i}' for i in range(1, 10)}

SINGLE_CHOICE_COLS = set(SINGLE_CHOICE_OPTIONS.keys())

# ─── BINARY GROUP DEFINITIONS ─────────────────────────────────────────────────
# Format: group_key -> (question_label, [column_headers in survey order])
# The group_key becomes the column_header on the Question record.

BINARY_GROUPS = {
    'Q3': (
        'What types of activities do you do in your free time? Please select ALL that apply.',
        ['Q3_1','Q3_2','Q3_3','Q3_4','Q3_5','Q3_6','Q3_7','Q3_8',
         'Q3_9','Q3_10','Q3_11','Q3_12','Q3_13','Q3_14','Q3_15','Q3_16'],
    ),
    'Q4': (
        'Of those activities, which two do you enjoy doing the most?',
        ['Q4_1','Q4_2','Q4_3','Q4_4','Q4_5','Q4_6','Q4_7','Q4_8',
         'Q4_9','Q4_10','Q4_11','Q4_12','Q4_13','Q4_14','Q4_15','Q4_16'],
    ),
    'Q6': (
        'What type of career awareness activities have you done? Please check ALL that apply.',
        ['Q6_1','Q6_2','Q6_3','Q6_4','Q6_5','Q6_6','Q6_7','Q6_8'],
    ),
    'Q7': (
        'What type of career exploration activities have you done? Please check ALL that apply.',
        ['Q7_1','Q7_2','Q7_3','Q7_4','Q7_5','Q7_6','Q7_7','Q7_8'],
    ),
    'Q7A': (
        'Where have you participated in career awareness or exploration activities? Please check ALL that apply.',
        ['Q7A_1','Q7A_2','Q7A_3','Q7A_7','Q7A_8','Q7A_4','Q7A_5','Q7A_6'],
    ),
    'Q8': (
        'What industry or career areas interest you most? Please check ALL that apply.',
        ['Q8_1','Q8_2','Q8_3','Q8_4','Q8_5','Q8_6','Q8_7','Q8_8','Q8_9',
         'Q8_10','Q8_11','Q8_12','Q8_13','Q8_14','Q8_15','Q8_16','Q8_17','Q8_18','Q8_19'],
    ),
    'Q9': (
        'Who have you spent time talking with about your plans for after high school? Please select ALL that apply.',
        ['Q9_1','Q9_2','Q9_3','Q9_4','Q9_5','Q9_6','Q9_7','Q9_8'],
    ),
    'Q12_student': (
        'Imagining your life after graduating high school, which of the following do you want to do? Please select ALL that apply.',
        ['Q12_1','Q12_2','Q12_3','Q12_4','Q12_5','Q12_6','Q12_7'],
    ),
    'Q12_caregiver': (
        'Imagining your life after graduating high school, what does your caregiver want you to do? Please select ALL that apply.',
        ['Q12_1_2','Q12_2_2','Q12_3_2','Q12_4_2','Q12_5_2','Q12_6_2','Q12_7_2'],
    ),
    'Q13': (
        'Imagining your life after graduating high school, which of the following do you plan to do? Please select ALL that apply.',
        ['Q13_1','Q13_2','Q13_3','Q13_4','Q13_5','Q13_6','Q13_7'],
    ),
    'Q16': (
        'Who do you live with? Please check ALL that apply.',
        ['Q16_1','Q16_2','Q16_3','Q16_4','Q16_5'],
    ),
    'Q24_like': (
        'This next set of questions will ask about your interest in a variety of areas. Please mark whether you LIKE that activity.',
        ['Q24_0_GROUP_153','Q24_0_GROUP_156','Q24_0_GROUP_157','Q24_0_GROUP_158',
         'Q24_0_GROUP_159','Q24_0_GROUP_171','Q24_0_GROUP_160','Q24_0_GROUP_161',
         'Q24_0_GROUP_162','Q24_0_GROUP_163','Q24_0_GROUP_164','Q24_0_GROUP_165',
         'Q24_0_GROUP_166','Q24_0_GROUP_167','Q24_0_GROUP_168','Q24_0_GROUP_169',
         'Q24_0_GROUP_172','Q24_0_GROUP_170'],
    ),
    'Q24_dislike': (
        'This next set of questions will ask about your interest in a variety of areas. Please mark whether you DISLIKE that activity.',
        ['Q24_1_GROUP_153','Q24_1_GROUP_156','Q24_1_GROUP_157','Q24_1_GROUP_158',
         'Q24_1_GROUP_159','Q24_1_GROUP_171','Q24_1_GROUP_160','Q24_1_GROUP_161',
         'Q24_1_GROUP_162','Q24_1_GROUP_163','Q24_1_GROUP_164','Q24_1_GROUP_165',
         'Q24_1_GROUP_166','Q24_1_GROUP_167','Q24_1_GROUP_168','Q24_1_GROUP_169',
         'Q24_1_GROUP_172','Q24_1_GROUP_170'],
    ),
    'Q24A': (
        'Of those activities you like, please select your top activities. Please select up to THREE activities.',
        ['Q24A_1','Q24A_2','Q24A_3','Q24A_4','Q24A_5','Q24A_6','Q24A_7','Q24A_8',
         'Q24A_9','Q24A_10','Q24A_11','Q24A_12','Q24A_13','Q24A_14','Q24A_15',
         'Q24A_16','Q24A_17','Q24A_18'],
    ),
    'Q25R': (
        'Of the skills you are good at, please select up to THREE activities you are the BEST at.',
        ['Q25R_1','Q25R_2','Q25R_3','Q25R_4','Q25R_5','Q25R_6','Q25R_7','Q25R_8',
         'Q25R_9','Q25R_10','Q25R_11','Q25R_12','Q25R_13','Q25R_14','Q25R_15',
         'Q25R_16','Q25R_17','Q25R_18'],
    ),
    'Q26_true': (
        'Please finish this sentence: "I am the type of person who is/is a _____." Select all that apply. - This IS true about me.',
        ['Q26_0_GROUP_1','Q26_0_GROUP_2','Q26_0_GROUP_3','Q26_0_GROUP_4',
         'Q26_0_GROUP_5','Q26_0_GROUP_18','Q26_0_GROUP_6','Q26_0_GROUP_7',
         'Q26_0_GROUP_8','Q26_0_GROUP_9','Q26_0_GROUP_10','Q26_0_GROUP_11',
         'Q26_0_GROUP_12','Q26_0_GROUP_13','Q26_0_GROUP_14','Q26_0_GROUP_15',
         'Q26_0_GROUP_17','Q26_0_GROUP_16'],
    ),
    'Q26_false': (
        'Please finish this sentence: "I am the type of person who is/is a _____." Select all that apply. - This is NOT true about me.',
        ['Q26_1_GROUP_1','Q26_1_GROUP_2','Q26_1_GROUP_3','Q26_1_GROUP_4',
         'Q26_1_GROUP_5','Q26_1_GROUP_18','Q26_1_GROUP_6','Q26_1_GROUP_7',
         'Q26_1_GROUP_8','Q26_1_GROUP_9','Q26_1_GROUP_10','Q26_1_GROUP_11',
         'Q26_1_GROUP_12','Q26_1_GROUP_13','Q26_1_GROUP_14','Q26_1_GROUP_15',
         'Q26_1_GROUP_17','Q26_1_GROUP_16'],
    ),
    'Q26A': (
        'Of those characteristics that describe you, please select up to THREE that describe you best.',
        ['Q26A_1','Q26A_2','Q26A_3','Q26A_4','Q26A_5','Q26A_6','Q26A_7','Q26A_8',
         'Q26A_9','Q26A_10','Q26A_11','Q26A_12','Q26A_13','Q26A_14','Q26A_15',
         'Q26A_16','Q26A_17','Q26A_18'],
    ),
}

# ─── RANK GROUP DEFINITIONS ───────────────────────────────────────────────────

RANK_GROUPS = {
    'Q26_0_RANK': (
        'Please finish this sentence: "I am the type of person who is/is a _____." - Selection order - This IS true about me.',
        ['Q26_0_1_RANK','Q26_0_2_RANK','Q26_0_3_RANK','Q26_0_4_RANK',
         'Q26_0_5_RANK','Q26_0_18_RANK','Q26_0_6_RANK','Q26_0_7_RANK',
         'Q26_0_8_RANK','Q26_0_9_RANK','Q26_0_10_RANK','Q26_0_11_RANK',
         'Q26_0_12_RANK','Q26_0_13_RANK','Q26_0_14_RANK','Q26_0_15_RANK',
         'Q26_0_17_RANK','Q26_0_16_RANK'],
    ),
    'Q26_1_RANK': (
        'Please finish this sentence: "I am the type of person who is/is a _____." - Selection order - This is NOT true about me.',
        ['Q26_1_1_RANK','Q26_1_2_RANK','Q26_1_3_RANK','Q26_1_4_RANK',
         'Q26_1_5_RANK','Q26_1_18_RANK','Q26_1_6_RANK','Q26_1_7_RANK',
         'Q26_1_8_RANK','Q26_1_9_RANK','Q26_1_10_RANK','Q26_1_11_RANK',
         'Q26_1_12_RANK','Q26_1_13_RANK','Q26_1_14_RANK','Q26_1_15_RANK',
         'Q26_1_17_RANK','Q26_1_16_RANK'],
    ),
}


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def read_mapping_file():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        'question_map.xlsx')
    if not os.path.exists(path):
        raise FileNotFoundError(
            f'Could not find mapping file at:\n  {path}\n'
            'Place question_map.xlsx in your project root.'
        )
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb.active
    rows = {row[0]: row for row in ws.iter_rows(min_row=2, values_only=True) if row[0]}
    wb.close()
    return rows


def parse_display_text(value_string):
    """Parse display text from '{1, Some text}...' format."""
    if not value_string or str(value_string) == 'None':
        return None
    s = str(value_string).strip()
    if s.startswith('{'):
        inner = s[1:s.find('}')]
        parts = inner.split(', ', 1)
        if len(parts) == 2:
            return parts[1].strip()
    return None


# ─── GENERATE ─────────────────────────────────────────────────────────────────

def generate():
    rows = read_mapping_file()

    questions = []   # datasets.question records
    options = []     # datasets.option records
    mappings = []    # datasets.questionColumn records

    # Deduplication caches
    # option_cache: display_text -> pk
    option_cache = {}

    question_pk = 1
    option_pk = 1
    mapping_pk = 1
    mapped_cols = set()
    warnings = []

    def get_or_create_option(display_text, category=None, numeric_value=None):
        nonlocal option_pk
        key = (category, display_text)
        if key in option_cache:
            return option_cache[key]
        pk = option_pk
        options.append({
            'model': 'datasets.option',
            'pk': pk,
            'fields': {
                'numeric_value': numeric_value,
                'display_text': display_text,
                'category': category,
            },
        })
        option_cache[key] = pk
        option_pk += 1
        return pk

    def create_question(label, question_type):
        nonlocal question_pk
        pk = question_pk
        questions.append({
            'model': 'datasets.question',
            'pk': pk,
            'fields': {
                'label': label,
                'question_type': question_type,
                'is_active': True,
            },
        })
        question_pk += 1
        return pk

    def create_mapping(column_header, question_pk, option_pk=None, option_category=None):
        nonlocal mapping_pk
        mappings.append({
            'model': 'datasets.questioncolumn',
            'pk': mapping_pk,
            'fields': {
                'column_header': column_header,
                'question': question_pk,
                'option': option_pk,
                'option_category': option_category,
            },
        })
        mapping_pk += 1
        mapped_cols.add(column_header)

    # ── Pre-create shared options ───────────────────────────────────────────────
    # These are created upfront so they exist before any question references them.
    # get_or_create_option handles deduplication so calling it here just registers them.

    for num_val, display in sorted(SCALE_OPTIONS.items()):
        get_or_create_option(display, category='skill_level', numeric_value=float(num_val))

    for num_val, display in sorted(APTITUDE_OPTIONS.items()):
        get_or_create_option(display, category='frequency', numeric_value=float(num_val))

    # ── Binary groups ───────────────────────────────────────────────────────────
    for group_key, (question_label, col_headers) in BINARY_GROUPS.items():
        q_pk = create_question(question_label, 'binary')

        for col in col_headers:
            row = rows.get(col)
            if not row:
                warnings.append(f'Column {col} not found in mapping file')
                continue

            display_text = parse_display_text(row[2])
            if not display_text:
                warnings.append(f'Could not parse display text for {col} — using column header as fallback')
                display_text = col

            opt_pk = get_or_create_option(display_text)
            create_mapping(col, q_pk, opt_pk)

    # ── Rank groups ─────────────────────────────────────────────────────────────
    for group_key, (question_label, col_headers) in RANK_GROUPS.items():
        q_pk = create_question(question_label, 'rank')
        for col in col_headers:
            create_mapping(col, q_pk, None, option_category='rank')  # rank position stored as text_value at import

    # ── Scale questions ─────────────────────────────────────────────────────────
    for col in sorted(SCALE_COLS):
        row = rows.get(col)
        label = row[1] if row else ''
        q_pk = create_question(label or '', 'scale')
        create_mapping(col, q_pk, None, option_category='skill_level')  # cell value determines option at import

    # ── Aptitude questions ──────────────────────────────────────────────────────
    for col in sorted(APTITUDE_COLS):
        row = rows.get(col)
        label = row[1] if row else ''
        q_pk = create_question(label or '', 'single_choice')
        create_mapping(col, q_pk, None, option_category='frequency')  # cell value determines option at import

    # ── Single choice questions ─────────────────────────────────────────────────
    for col in sorted(SINGLE_CHOICE_COLS):
        row = rows.get(col)
        label = row[1] if row else ''
        q_pk = create_question(label or '', 'single_choice')
        option_set = SINGLE_CHOICE_OPTIONS.get(col, {})
        if not option_set:
            warnings.append(
                f'No options defined for single_choice question {col}'
            )
        else:
            category = SINGLE_CHOICE_CATEGORIES.get(col)
            for numeric_val, display in option_set.items():
                get_or_create_option(display, category=category, numeric_value=float(numeric_val))
        create_mapping(col, q_pk, None, option_category=SINGLE_CHOICE_CATEGORIES.get(col))

    # ── Free text questions ─────────────────────────────────────────────────────
    for col in sorted(FREE_TEXT_COLS):
        row = rows.get(col)
        label = row[1] if row else ''
        q_pk = create_question(label or '', 'free_text')
        create_mapping(col, q_pk, None)

    # ── Check for unaccounted columns ───────────────────────────────────────────
    unaccounted = [
        col for col in rows
        if col not in SKIP_COLS and col not in mapped_cols
    ]
    if unaccounted:
        warnings.append(
            f'{len(unaccounted)} columns in mapping file not accounted for:\n' +
            '\n'.join(f'  {col}' for col in unaccounted)
        )

    # ── Combine and summarise ───────────────────────────────────────────────────
    fixture = questions + options + mappings

    type_counts = Counter(q['fields']['question_type'] for q in questions)
    print(f'\nGenerated:')
    print(f'  {len(questions)} Question records')
    for t, count in sorted(type_counts.items()):
        print(f'    {t}: {count}')
    print(f'  {len(options)} Option records (deduplicated by display_text)')
    print(f'  {len(mappings)} questionColumn records')
    print(f'  {len(mapped_cols)} columns mapped total')

    if warnings:
        print(f'\nWarnings ({len(warnings)}):')
        for w in warnings:
            print(f'  {w}')

    return fixture


# ─── MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    fixture = generate()

    output_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'structure_gen'
    )
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'questions_and_options.json')

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(fixture, f, indent=2, ensure_ascii=False)

    print(f'\nFixture written to:\n  {output_path}')