# Used accross app for user access control based on user role and affiliation
ROLE_ACCESS_POLICY = {
    'internal': {
        'raw_scope': 'all',
        'aggregate_scopes': ['all'],
    },
    'school_admin': {
        'raw_scope': 'own',
        'aggregate_scopes': ['own', 'group'],
    },
    'sponsor': {
        'raw_scope': 'none',
        'aggregate_scopes': ['group'],
    },
}



# Unified survey column configuration.
# Single source of truth for all column metadata used by the import pipeline,
# dataset detail view, validator, and fixture generation script.
#
# field_type values:
#   metadata  — stored directly on Response model
#   school    — used to resolve Response.school FK from Q1 value
#   calculated — computed by Qualtrics, stored directly on Response model
#   answer    — stored in RespondentAnswer via QuestionColumn
#   discard   — not stored anywhere, excluded from all processing
#
# Optional keys:
#   cast      — type conversion applied during import (metadata only)
#   skip      — True if column should be excluded from RespondentAnswer creation

SURVEY_COLUMNS = {

    # ── Metadata ─────────────────────────────────────────────────────────────
    'StartDate': {
        'field_type': 'metadata',
        'model_field': 'start_date',
        'cast': 'datetime',
    },
    'EndDate': {
        'field_type': 'metadata',
        'model_field': 'end_date',
        'cast': 'datetime',
    },
    'RecordedDate': {
        'field_type': 'metadata',
        'model_field': 'recorded_date',
        'cast': 'datetime',
    },
    'Status': {
        'field_type': 'metadata',
        'model_field': 'status',
        'cast': 'int',
    },
    'Progress': {
        'field_type': 'metadata',
        'model_field': 'progress',
        'cast': 'int',
    },
    'Duration__in_seconds_': {
        'field_type': 'metadata',
        'model_field': 'duration_in_seconds',
        'cast': 'int',
    },
    'Finished': {
        'field_type': 'metadata',
        'model_field': 'finished',
        'cast': 'int',
    },
    'ResponseId': {
        'field_type': 'metadata',
        'model_field': 'response_id',
        'cast': 'str',
    },
    'DistributionChannel': {
        'field_type': 'metadata',
        'model_field': 'distribution_channel',
        'cast': 'str',
    },
    'UserLanguage': {
        'field_type': 'metadata',
        'model_field': 'user_language',
        'cast': 'str',
    },
    'Year': {
        'field_type': 'metadata',
        'model_field': 'year',
        'cast': 'int',
    },
    'Semester': {
        'field_type': 'metadata',
        'model_field': 'semester',
        'cast': 'str',
    },

    # ── School FK ────────────────────────────────────────────────────────────
    'Q1': {
        'field_type': 'school',
        'model_field': 'school',
        'cast': 'int',
    },

    # ── Discard ──────────────────────────────────────────────────────────────
    'Q5R': {
        'field_type': 'discard',
        'model_field': 'Q5R',
        'skip': True,
    },
    'Q6R': {
        'field_type': 'discard',
        'model_field': 'Q6R',
        'skip': True,
    },
    'Q7R': {
        'field_type': 'discard',
        'model_field': 'Q7R',
        'skip': True,
    },
    'Q6R_Q7R': {
        'field_type': 'discard',
        'model_field': 'Q6R_Q7R',
        'skip': True,
    },
    'Q20A': {
        'field_type': 'discard',
        'model_field': 'Q20A',
        'skip': True,
    },
    'Q20B': {
        'field_type': 'discard',
        'model_field': 'Q20B',
        'skip': True,
    },
    'Q20C': {
        'field_type': 'discard',
        'model_field': 'Q20C',
        'skip': True,
    },
    'Q20D': {
        'field_type': 'discard',
        'model_field': 'Q20D',
        'skip': True,
    },

    # ── Answer ───────────────────────────────────────────────────────────────
    'Q2': {
        'field_type': 'answer',
        'model_field': 'Q2',
    },
    'Q3_1': {
        'field_type': 'answer',
        'model_field': 'Q3_1',
    },
    'Q3_2': {
        'field_type': 'answer',
        'model_field': 'Q3_2',
    },
    'Q3_3': {
        'field_type': 'answer',
        'model_field': 'Q3_3',
    },
    'Q3_4': {
        'field_type': 'answer',
        'model_field': 'Q3_4',
    },
    'Q3_5': {
        'field_type': 'answer',
        'model_field': 'Q3_5',
    },
    'Q3_6': {
        'field_type': 'answer',
        'model_field': 'Q3_6',
    },
    'Q3_7': {
        'field_type': 'answer',
        'model_field': 'Q3_7',
    },
    'Q3_8': {
        'field_type': 'answer',
        'model_field': 'Q3_8',
    },
    'Q3_9': {
        'field_type': 'answer',
        'model_field': 'Q3_9',
    },
    'Q3_10': {
        'field_type': 'answer',
        'model_field': 'Q3_10',
    },
    'Q3_11': {
        'field_type': 'answer',
        'model_field': 'Q3_11',
    },
    'Q3_12': {
        'field_type': 'answer',
        'model_field': 'Q3_12',
    },
    'Q3_13': {
        'field_type': 'answer',
        'model_field': 'Q3_13',
    },
    'Q3_14': {
        'field_type': 'answer',
        'model_field': 'Q3_14',
    },
    'Q3_15': {
        'field_type': 'answer',
        'model_field': 'Q3_15',
    },
    'Q3_16': {
        'field_type': 'answer',
        'model_field': 'Q3_16',
    },
    'Q3_16_TEXT': {
        'field_type': 'answer',
        'model_field': 'Q3_16_TEXT',
    },
    'Q4_1': {
        'field_type': 'answer',
        'model_field': 'Q4_1',
    },
    'Q4_2': {
        'field_type': 'answer',
        'model_field': 'Q4_2',
    },
    'Q4_3': {
        'field_type': 'answer',
        'model_field': 'Q4_3',
    },
    'Q4_4': {
        'field_type': 'answer',
        'model_field': 'Q4_4',
    },
    'Q4_5': {
        'field_type': 'answer',
        'model_field': 'Q4_5',
    },
    'Q4_6': {
        'field_type': 'answer',
        'model_field': 'Q4_6',
    },
    'Q4_7': {
        'field_type': 'answer',
        'model_field': 'Q4_7',
    },
    'Q4_8': {
        'field_type': 'answer',
        'model_field': 'Q4_8',
    },
    'Q4_9': {
        'field_type': 'answer',
        'model_field': 'Q4_9',
    },
    'Q4_10': {
        'field_type': 'answer',
        'model_field': 'Q4_10',
    },
    'Q4_11': {
        'field_type': 'answer',
        'model_field': 'Q4_11',
    },
    'Q4_12': {
        'field_type': 'answer',
        'model_field': 'Q4_12',
    },
    'Q4_13': {
        'field_type': 'answer',
        'model_field': 'Q4_13',
    },
    'Q4_14': {
        'field_type': 'answer',
        'model_field': 'Q4_14',
    },
    'Q4_15': {
        'field_type': 'answer',
        'model_field': 'Q4_15',
    },
    'Q4_16': {
        'field_type': 'answer',
        'model_field': 'Q4_16',
    },
    'Q4_16_TEXT': {
        'field_type': 'answer',
        'model_field': 'Q4_16_TEXT',
    },
    'Q5': {
        'field_type': 'answer',
        'model_field': 'Q5',
    },
    'Q6_1': {
        'field_type': 'answer',
        'model_field': 'Q6_1',
    },
    'Q6_2': {
        'field_type': 'answer',
        'model_field': 'Q6_2',
    },
    'Q6_3': {
        'field_type': 'answer',
        'model_field': 'Q6_3',
    },
    'Q6_4': {
        'field_type': 'answer',
        'model_field': 'Q6_4',
    },
    'Q6_5': {
        'field_type': 'answer',
        'model_field': 'Q6_5',
    },
    'Q6_6': {
        'field_type': 'answer',
        'model_field': 'Q6_6',
    },
    'Q6_7': {
        'field_type': 'answer',
        'model_field': 'Q6_7',
    },
    'Q6_8': {
        'field_type': 'answer',
        'model_field': 'Q6_8',
    },
    'Q7_1': {
        'field_type': 'answer',
        'model_field': 'Q7_1',
    },
    'Q7_2': {
        'field_type': 'answer',
        'model_field': 'Q7_2',
    },
    'Q7_3': {
        'field_type': 'answer',
        'model_field': 'Q7_3',
    },
    'Q7_4': {
        'field_type': 'answer',
        'model_field': 'Q7_4',
    },
    'Q7_5': {
        'field_type': 'answer',
        'model_field': 'Q7_5',
    },
    'Q7_6': {
        'field_type': 'answer',
        'model_field': 'Q7_6',
    },
    'Q7_7': {
        'field_type': 'answer',
        'model_field': 'Q7_7',
    },
    'Q7_8': {
        'field_type': 'answer',
        'model_field': 'Q7_8',
    },
    'Q7A_1': {
        'field_type': 'answer',
        'model_field': 'Q7A_1',
    },
    'Q7A_2': {
        'field_type': 'answer',
        'model_field': 'Q7A_2',
    },
    'Q7A_3': {
        'field_type': 'answer',
        'model_field': 'Q7A_3',
    },
    'Q7A_7': {
        'field_type': 'answer',
        'model_field': 'Q7A_7',
    },
    'Q7A_8': {
        'field_type': 'answer',
        'model_field': 'Q7A_8',
    },
    'Q7A_4': {
        'field_type': 'answer',
        'model_field': 'Q7A_4',
    },
    'Q7A_5': {
        'field_type': 'answer',
        'model_field': 'Q7A_5',
    },
    'Q7A_6': {
        'field_type': 'answer',
        'model_field': 'Q7A_6',
    },
    'Q7A_6_TEXT': {
        'field_type': 'answer',
        'model_field': 'Q7A_6_TEXT',
    },
    'Q8_1': {
        'field_type': 'answer',
        'model_field': 'Q8_1',
    },
    'Q8_2': {
        'field_type': 'answer',
        'model_field': 'Q8_2',
    },
    'Q8_3': {
        'field_type': 'answer',
        'model_field': 'Q8_3',
    },
    'Q8_4': {
        'field_type': 'answer',
        'model_field': 'Q8_4',
    },
    'Q8_5': {
        'field_type': 'answer',
        'model_field': 'Q8_5',
    },
    'Q8_6': {
        'field_type': 'answer',
        'model_field': 'Q8_6',
    },
    'Q8_7': {
        'field_type': 'answer',
        'model_field': 'Q8_7',
    },
    'Q8_8': {
        'field_type': 'answer',
        'model_field': 'Q8_8',
    },
    'Q8_9': {
        'field_type': 'answer',
        'model_field': 'Q8_9',
    },
    'Q8_10': {
        'field_type': 'answer',
        'model_field': 'Q8_10',
    },
    'Q8_11': {
        'field_type': 'answer',
        'model_field': 'Q8_11',
    },
    'Q8_12': {
        'field_type': 'answer',
        'model_field': 'Q8_12',
    },
    'Q8_13': {
        'field_type': 'answer',
        'model_field': 'Q8_13',
    },
    'Q8_14': {
        'field_type': 'answer',
        'model_field': 'Q8_14',
    },
    'Q8_15': {
        'field_type': 'answer',
        'model_field': 'Q8_15',
    },
    'Q8_16': {
        'field_type': 'answer',
        'model_field': 'Q8_16',
    },
    'Q8_17': {
        'field_type': 'answer',
        'model_field': 'Q8_17',
    },
    'Q8_18': {
        'field_type': 'answer',
        'model_field': 'Q8_18',
    },
    'Q8_19': {
        'field_type': 'answer',
        'model_field': 'Q8_19',
    },
    'Q9_1': {
        'field_type': 'answer',
        'model_field': 'Q9_1',
    },
    'Q9_2': {
        'field_type': 'answer',
        'model_field': 'Q9_2',
    },
    'Q9_3': {
        'field_type': 'answer',
        'model_field': 'Q9_3',
    },
    'Q9_4': {
        'field_type': 'answer',
        'model_field': 'Q9_4',
    },
    'Q9_5': {
        'field_type': 'answer',
        'model_field': 'Q9_5',
    },
    'Q9_6': {
        'field_type': 'answer',
        'model_field': 'Q9_6',
    },
    'Q9_7': {
        'field_type': 'answer',
        'model_field': 'Q9_7',
    },
    'Q9_8': {
        'field_type': 'answer',
        'model_field': 'Q9_8',
    },
    'Q9_7_TEXT': {
        'field_type': 'answer',
        'model_field': 'Q9_7_TEXT',
    },
    'Q10': {
        'field_type': 'answer',
        'model_field': 'Q10',
    },
    'Q10_7_TEXT': {
        'field_type': 'answer',
        'model_field': 'Q10_7_TEXT',
    },
    'Q11': {
        'field_type': 'answer',
        'model_field': 'Q11',
    },
    'Q11_7_TEXT': {
        'field_type': 'answer',
        'model_field': 'Q11_7_TEXT',
    },
    'Q12_1': {
        'field_type': 'answer',
        'model_field': 'Q12_1',
    },
    'Q12_2': {
        'field_type': 'answer',
        'model_field': 'Q12_2',
    },
    'Q12_3': {
        'field_type': 'answer',
        'model_field': 'Q12_3',
    },
    'Q12_4': {
        'field_type': 'answer',
        'model_field': 'Q12_4',
    },
    'Q12_5': {
        'field_type': 'answer',
        'model_field': 'Q12_5',
    },
    'Q12_6': {
        'field_type': 'answer',
        'model_field': 'Q12_6',
    },
    'Q12_7': {
        'field_type': 'answer',
        'model_field': 'Q12_7',
    },
    'Q12_1_2': {
        'field_type': 'answer',
        'model_field': 'Q12_1_2',
    },
    'Q12_2_2': {
        'field_type': 'answer',
        'model_field': 'Q12_2_2',
    },
    'Q12_3_2': {
        'field_type': 'answer',
        'model_field': 'Q12_3_2',
    },
    'Q12_4_2': {
        'field_type': 'answer',
        'model_field': 'Q12_4_2',
    },
    'Q12_5_2': {
        'field_type': 'answer',
        'model_field': 'Q12_5_2',
    },
    'Q12_6_2': {
        'field_type': 'answer',
        'model_field': 'Q12_6_2',
    },
    'Q12_7_2': {
        'field_type': 'answer',
        'model_field': 'Q12_7_2',
    },
    'Q13_1': {
        'field_type': 'answer',
        'model_field': 'Q13_1',
    },
    'Q13_2': {
        'field_type': 'answer',
        'model_field': 'Q13_2',
    },
    'Q13_3': {
        'field_type': 'answer',
        'model_field': 'Q13_3',
    },
    'Q13_4': {
        'field_type': 'answer',
        'model_field': 'Q13_4',
    },
    'Q13_5': {
        'field_type': 'answer',
        'model_field': 'Q13_5',
    },
    'Q13_6': {
        'field_type': 'answer',
        'model_field': 'Q13_6',
    },
    'Q13_7': {
        'field_type': 'answer',
        'model_field': 'Q13_7',
    },
    'Q14': {
        'field_type': 'answer',
        'model_field': 'Q14',
    },
    'Q15': {
        'field_type': 'answer',
        'model_field': 'Q15',
    },
    'Q16_1': {
        'field_type': 'answer',
        'model_field': 'Q16_1',
    },
    'Q16_2': {
        'field_type': 'answer',
        'model_field': 'Q16_2',
    },
    'Q16_3': {
        'field_type': 'answer',
        'model_field': 'Q16_3',
    },
    'Q16_4': {
        'field_type': 'answer',
        'model_field': 'Q16_4',
    },
    'Q16_5': {
        'field_type': 'answer',
        'model_field': 'Q16_5',
    },
    'Q16_5_TEXT': {
        'field_type': 'answer',
        'model_field': 'Q16_5_TEXT',
    },
    'Q18': {
        'field_type': 'answer',
        'model_field': 'Q18',
    },
    'Q22': {
        'field_type': 'answer',
        'model_field': 'Q22',
    },
    'Q23': {
        'field_type': 'answer',
        'model_field': 'Q23',
    },
    'Q24_0_GROUP_153': {
        'field_type': 'answer',
        'model_field': 'Q24_0_GROUP_153',
    },
    'Q24_0_GROUP_156': {
        'field_type': 'answer',
        'model_field': 'Q24_0_GROUP_156',
    },
    'Q24_0_GROUP_157': {
        'field_type': 'answer',
        'model_field': 'Q24_0_GROUP_157',
    },
    'Q24_0_GROUP_158': {
        'field_type': 'answer',
        'model_field': 'Q24_0_GROUP_158',
    },
    'Q24_0_GROUP_159': {
        'field_type': 'answer',
        'model_field': 'Q24_0_GROUP_159',
    },
    'Q24_0_GROUP_171': {
        'field_type': 'answer',
        'model_field': 'Q24_0_GROUP_171',
    },
    'Q24_0_GROUP_160': {
        'field_type': 'answer',
        'model_field': 'Q24_0_GROUP_160',
    },
    'Q24_0_GROUP_161': {
        'field_type': 'answer',
        'model_field': 'Q24_0_GROUP_161',
    },
    'Q24_0_GROUP_162': {
        'field_type': 'answer',
        'model_field': 'Q24_0_GROUP_162',
    },
    'Q24_0_GROUP_163': {
        'field_type': 'answer',
        'model_field': 'Q24_0_GROUP_163',
    },
    'Q24_0_GROUP_164': {
        'field_type': 'answer',
        'model_field': 'Q24_0_GROUP_164',
    },
    'Q24_0_GROUP_165': {
        'field_type': 'answer',
        'model_field': 'Q24_0_GROUP_165',
    },
    'Q24_0_GROUP_166': {
        'field_type': 'answer',
        'model_field': 'Q24_0_GROUP_166',
    },
    'Q24_0_GROUP_167': {
        'field_type': 'answer',
        'model_field': 'Q24_0_GROUP_167',
    },
    'Q24_0_GROUP_168': {
        'field_type': 'answer',
        'model_field': 'Q24_0_GROUP_168',
    },
    'Q24_0_GROUP_169': {
        'field_type': 'answer',
        'model_field': 'Q24_0_GROUP_169',
    },
    'Q24_0_GROUP_172': {
        'field_type': 'answer',
        'model_field': 'Q24_0_GROUP_172',
    },
    'Q24_0_GROUP_170': {
        'field_type': 'answer',
        'model_field': 'Q24_0_GROUP_170',
    },
    'Q24_1_GROUP_153': {
        'field_type': 'answer',
        'model_field': 'Q24_1_GROUP_153',
    },
    'Q24_1_GROUP_156': {
        'field_type': 'answer',
        'model_field': 'Q24_1_GROUP_156',
    },
    'Q24_1_GROUP_157': {
        'field_type': 'answer',
        'model_field': 'Q24_1_GROUP_157',
    },
    'Q24_1_GROUP_158': {
        'field_type': 'answer',
        'model_field': 'Q24_1_GROUP_158',
    },
    'Q24_1_GROUP_159': {
        'field_type': 'answer',
        'model_field': 'Q24_1_GROUP_159',
    },
    'Q24_1_GROUP_171': {
        'field_type': 'answer',
        'model_field': 'Q24_1_GROUP_171',
    },
    'Q24_1_GROUP_160': {
        'field_type': 'answer',
        'model_field': 'Q24_1_GROUP_160',
    },
    'Q24_1_GROUP_161': {
        'field_type': 'answer',
        'model_field': 'Q24_1_GROUP_161',
    },
    'Q24_1_GROUP_162': {
        'field_type': 'answer',
        'model_field': 'Q24_1_GROUP_162',
    },
    'Q24_1_GROUP_163': {
        'field_type': 'answer',
        'model_field': 'Q24_1_GROUP_163',
    },
    'Q24_1_GROUP_164': {
        'field_type': 'answer',
        'model_field': 'Q24_1_GROUP_164',
    },
    'Q24_1_GROUP_165': {
        'field_type': 'answer',
        'model_field': 'Q24_1_GROUP_165',
    },
    'Q24_1_GROUP_166': {
        'field_type': 'answer',
        'model_field': 'Q24_1_GROUP_166',
    },
    'Q24_1_GROUP_167': {
        'field_type': 'answer',
        'model_field': 'Q24_1_GROUP_167',
    },
    'Q24_1_GROUP_168': {
        'field_type': 'answer',
        'model_field': 'Q24_1_GROUP_168',
    },
    'Q24_1_GROUP_169': {
        'field_type': 'answer',
        'model_field': 'Q24_1_GROUP_169',
    },
    'Q24_1_GROUP_172': {
        'field_type': 'answer',
        'model_field': 'Q24_1_GROUP_172',
    },
    'Q24_1_GROUP_170': {
        'field_type': 'answer',
        'model_field': 'Q24_1_GROUP_170',
    },
    'Q24A_1': {
        'field_type': 'answer',
        'model_field': 'Q24A_1',
    },
    'Q24A_2': {
        'field_type': 'answer',
        'model_field': 'Q24A_2',
    },
    'Q24A_3': {
        'field_type': 'answer',
        'model_field': 'Q24A_3',
    },
    'Q24A_4': {
        'field_type': 'answer',
        'model_field': 'Q24A_4',
    },
    'Q24A_5': {
        'field_type': 'answer',
        'model_field': 'Q24A_5',
    },
    'Q24A_6': {
        'field_type': 'answer',
        'model_field': 'Q24A_6',
    },
    'Q24A_7': {
        'field_type': 'answer',
        'model_field': 'Q24A_7',
    },
    'Q24A_8': {
        'field_type': 'answer',
        'model_field': 'Q24A_8',
    },
    'Q24A_9': {
        'field_type': 'answer',
        'model_field': 'Q24A_9',
    },
    'Q24A_10': {
        'field_type': 'answer',
        'model_field': 'Q24A_10',
    },
    'Q24A_11': {
        'field_type': 'answer',
        'model_field': 'Q24A_11',
    },
    'Q24A_12': {
        'field_type': 'answer',
        'model_field': 'Q24A_12',
    },
    'Q24A_13': {
        'field_type': 'answer',
        'model_field': 'Q24A_13',
    },
    'Q24A_14': {
        'field_type': 'answer',
        'model_field': 'Q24A_14',
    },
    'Q24A_15': {
        'field_type': 'answer',
        'model_field': 'Q24A_15',
    },
    'Q24A_16': {
        'field_type': 'answer',
        'model_field': 'Q24A_16',
    },
    'Q24A_17': {
        'field_type': 'answer',
        'model_field': 'Q24A_17',
    },
    'Q24A_18': {
        'field_type': 'answer',
        'model_field': 'Q24A_18',
    },
    'Q25': {
        'field_type': 'answer',
        'model_field': 'Q25',
    },
    'Q25A': {
        'field_type': 'answer',
        'model_field': 'Q25A',
    },
    'Q25B': {
        'field_type': 'answer',
        'model_field': 'Q25B',
    },
    'Q25C': {
        'field_type': 'answer',
        'model_field': 'Q25C',
    },
    'Q25D': {
        'field_type': 'answer',
        'model_field': 'Q25D',
    },
    'Q25E': {
        'field_type': 'answer',
        'model_field': 'Q25E',
    },
    'Q25F': {
        'field_type': 'answer',
        'model_field': 'Q25F',
    },
    'Q25G': {
        'field_type': 'answer',
        'model_field': 'Q25G',
    },
    'Q25H': {
        'field_type': 'answer',
        'model_field': 'Q25H',
    },
    'Q25I': {
        'field_type': 'answer',
        'model_field': 'Q25I',
    },
    'Q25J': {
        'field_type': 'answer',
        'model_field': 'Q25J',
    },
    'Q25K': {
        'field_type': 'answer',
        'model_field': 'Q25K',
    },
    'Q25L': {
        'field_type': 'answer',
        'model_field': 'Q25L',
    },
    'Q25M': {
        'field_type': 'answer',
        'model_field': 'Q25M',
    },
    'Q25N': {
        'field_type': 'answer',
        'model_field': 'Q25N',
    },
    'Q25O': {
        'field_type': 'answer',
        'model_field': 'Q25O',
    },
    'Q25P': {
        'field_type': 'answer',
        'model_field': 'Q25P',
    },
    'Q25Q': {
        'field_type': 'answer',
        'model_field': 'Q25Q',
    },
    'Q25R_1': {
        'field_type': 'answer',
        'model_field': 'Q25R_1',
    },
    'Q25R_2': {
        'field_type': 'answer',
        'model_field': 'Q25R_2',
    },
    'Q25R_3': {
        'field_type': 'answer',
        'model_field': 'Q25R_3',
    },
    'Q25R_4': {
        'field_type': 'answer',
        'model_field': 'Q25R_4',
    },
    'Q25R_5': {
        'field_type': 'answer',
        'model_field': 'Q25R_5',
    },
    'Q25R_6': {
        'field_type': 'answer',
        'model_field': 'Q25R_6',
    },
    'Q25R_7': {
        'field_type': 'answer',
        'model_field': 'Q25R_7',
    },
    'Q25R_8': {
        'field_type': 'answer',
        'model_field': 'Q25R_8',
    },
    'Q25R_9': {
        'field_type': 'answer',
        'model_field': 'Q25R_9',
    },
    'Q25R_10': {
        'field_type': 'answer',
        'model_field': 'Q25R_10',
    },
    'Q25R_11': {
        'field_type': 'answer',
        'model_field': 'Q25R_11',
    },
    'Q25R_12': {
        'field_type': 'answer',
        'model_field': 'Q25R_12',
    },
    'Q25R_13': {
        'field_type': 'answer',
        'model_field': 'Q25R_13',
    },
    'Q25R_14': {
        'field_type': 'answer',
        'model_field': 'Q25R_14',
    },
    'Q25R_15': {
        'field_type': 'answer',
        'model_field': 'Q25R_15',
    },
    'Q25R_16': {
        'field_type': 'answer',
        'model_field': 'Q25R_16',
    },
    'Q25R_17': {
        'field_type': 'answer',
        'model_field': 'Q25R_17',
    },
    'Q25R_18': {
        'field_type': 'answer',
        'model_field': 'Q25R_18',
    },
    'Q26_0_GROUP_1': {
        'field_type': 'answer',
        'model_field': 'Q26_0_GROUP_1',
    },
    'Q26_0_GROUP_2': {
        'field_type': 'answer',
        'model_field': 'Q26_0_GROUP_2',
    },
    'Q26_0_GROUP_3': {
        'field_type': 'answer',
        'model_field': 'Q26_0_GROUP_3',
    },
    'Q26_0_GROUP_4': {
        'field_type': 'answer',
        'model_field': 'Q26_0_GROUP_4',
    },
    'Q26_0_GROUP_5': {
        'field_type': 'answer',
        'model_field': 'Q26_0_GROUP_5',
    },
    'Q26_0_GROUP_18': {
        'field_type': 'answer',
        'model_field': 'Q26_0_GROUP_18',
    },
    'Q26_0_GROUP_6': {
        'field_type': 'answer',
        'model_field': 'Q26_0_GROUP_6',
    },
    'Q26_0_GROUP_7': {
        'field_type': 'answer',
        'model_field': 'Q26_0_GROUP_7',
    },
    'Q26_0_GROUP_8': {
        'field_type': 'answer',
        'model_field': 'Q26_0_GROUP_8',
    },
    'Q26_0_GROUP_9': {
        'field_type': 'answer',
        'model_field': 'Q26_0_GROUP_9',
    },
    'Q26_0_GROUP_10': {
        'field_type': 'answer',
        'model_field': 'Q26_0_GROUP_10',
    },
    'Q26_0_GROUP_11': {
        'field_type': 'answer',
        'model_field': 'Q26_0_GROUP_11',
    },
    'Q26_0_GROUP_12': {
        'field_type': 'answer',
        'model_field': 'Q26_0_GROUP_12',
    },
    'Q26_0_GROUP_13': {
        'field_type': 'answer',
        'model_field': 'Q26_0_GROUP_13',
    },
    'Q26_0_GROUP_14': {
        'field_type': 'answer',
        'model_field': 'Q26_0_GROUP_14',
    },
    'Q26_0_GROUP_15': {
        'field_type': 'answer',
        'model_field': 'Q26_0_GROUP_15',
    },
    'Q26_0_GROUP_17': {
        'field_type': 'answer',
        'model_field': 'Q26_0_GROUP_17',
    },
    'Q26_0_GROUP_16': {
        'field_type': 'answer',
        'model_field': 'Q26_0_GROUP_16',
    },
    'Q26_1_GROUP_1': {
        'field_type': 'answer',
        'model_field': 'Q26_1_GROUP_1',
    },
    'Q26_1_GROUP_2': {
        'field_type': 'answer',
        'model_field': 'Q26_1_GROUP_2',
    },
    'Q26_1_GROUP_3': {
        'field_type': 'answer',
        'model_field': 'Q26_1_GROUP_3',
    },
    'Q26_1_GROUP_4': {
        'field_type': 'answer',
        'model_field': 'Q26_1_GROUP_4',
    },
    'Q26_1_GROUP_5': {
        'field_type': 'answer',
        'model_field': 'Q26_1_GROUP_5',
    },
    'Q26_1_GROUP_18': {
        'field_type': 'answer',
        'model_field': 'Q26_1_GROUP_18',
    },
    'Q26_1_GROUP_6': {
        'field_type': 'answer',
        'model_field': 'Q26_1_GROUP_6',
    },
    'Q26_1_GROUP_7': {
        'field_type': 'answer',
        'model_field': 'Q26_1_GROUP_7',
    },
    'Q26_1_GROUP_8': {
        'field_type': 'answer',
        'model_field': 'Q26_1_GROUP_8',
    },
    'Q26_1_GROUP_9': {
        'field_type': 'answer',
        'model_field': 'Q26_1_GROUP_9',
    },
    'Q26_1_GROUP_10': {
        'field_type': 'answer',
        'model_field': 'Q26_1_GROUP_10',
    },
    'Q26_1_GROUP_11': {
        'field_type': 'answer',
        'model_field': 'Q26_1_GROUP_11',
    },
    'Q26_1_GROUP_12': {
        'field_type': 'answer',
        'model_field': 'Q26_1_GROUP_12',
    },
    'Q26_1_GROUP_13': {
        'field_type': 'answer',
        'model_field': 'Q26_1_GROUP_13',
    },
    'Q26_1_GROUP_14': {
        'field_type': 'answer',
        'model_field': 'Q26_1_GROUP_14',
    },
    'Q26_1_GROUP_15': {
        'field_type': 'answer',
        'model_field': 'Q26_1_GROUP_15',
    },
    'Q26_1_GROUP_17': {
        'field_type': 'answer',
        'model_field': 'Q26_1_GROUP_17',
    },
    'Q26_1_GROUP_16': {
        'field_type': 'answer',
        'model_field': 'Q26_1_GROUP_16',
    },
    'Q26_0_1_RANK': {
        'field_type': 'answer',
        'model_field': 'Q26_0_1_RANK',
    },
    'Q26_0_2_RANK': {
        'field_type': 'answer',
        'model_field': 'Q26_0_2_RANK',
    },
    'Q26_0_3_RANK': {
        'field_type': 'answer',
        'model_field': 'Q26_0_3_RANK',
    },
    'Q26_0_4_RANK': {
        'field_type': 'answer',
        'model_field': 'Q26_0_4_RANK',
    },
    'Q26_0_5_RANK': {
        'field_type': 'answer',
        'model_field': 'Q26_0_5_RANK',
    },
    'Q26_0_18_RANK': {
        'field_type': 'answer',
        'model_field': 'Q26_0_18_RANK',
    },
    'Q26_0_6_RANK': {
        'field_type': 'answer',
        'model_field': 'Q26_0_6_RANK',
    },
    'Q26_0_7_RANK': {
        'field_type': 'answer',
        'model_field': 'Q26_0_7_RANK',
    },
    'Q26_0_8_RANK': {
        'field_type': 'answer',
        'model_field': 'Q26_0_8_RANK',
    },
    'Q26_0_9_RANK': {
        'field_type': 'answer',
        'model_field': 'Q26_0_9_RANK',
    },
    'Q26_0_10_RANK': {
        'field_type': 'answer',
        'model_field': 'Q26_0_10_RANK',
    },
    'Q26_0_11_RANK': {
        'field_type': 'answer',
        'model_field': 'Q26_0_11_RANK',
    },
    'Q26_0_12_RANK': {
        'field_type': 'answer',
        'model_field': 'Q26_0_12_RANK',
    },
    'Q26_0_13_RANK': {
        'field_type': 'answer',
        'model_field': 'Q26_0_13_RANK',
    },
    'Q26_0_14_RANK': {
        'field_type': 'answer',
        'model_field': 'Q26_0_14_RANK',
    },
    'Q26_0_15_RANK': {
        'field_type': 'answer',
        'model_field': 'Q26_0_15_RANK',
    },
    'Q26_0_17_RANK': {
        'field_type': 'answer',
        'model_field': 'Q26_0_17_RANK',
    },
    'Q26_0_16_RANK': {
        'field_type': 'answer',
        'model_field': 'Q26_0_16_RANK',
    },
    'Q26_1_1_RANK': {
        'field_type': 'answer',
        'model_field': 'Q26_1_1_RANK',
    },
    'Q26_1_2_RANK': {
        'field_type': 'answer',
        'model_field': 'Q26_1_2_RANK',
    },
    'Q26_1_3_RANK': {
        'field_type': 'answer',
        'model_field': 'Q26_1_3_RANK',
    },
    'Q26_1_4_RANK': {
        'field_type': 'answer',
        'model_field': 'Q26_1_4_RANK',
    },
    'Q26_1_5_RANK': {
        'field_type': 'answer',
        'model_field': 'Q26_1_5_RANK',
    },
    'Q26_1_18_RANK': {
        'field_type': 'answer',
        'model_field': 'Q26_1_18_RANK',
    },
    'Q26_1_6_RANK': {
        'field_type': 'answer',
        'model_field': 'Q26_1_6_RANK',
    },
    'Q26_1_7_RANK': {
        'field_type': 'answer',
        'model_field': 'Q26_1_7_RANK',
    },
    'Q26_1_8_RANK': {
        'field_type': 'answer',
        'model_field': 'Q26_1_8_RANK',
    },
    'Q26_1_9_RANK': {
        'field_type': 'answer',
        'model_field': 'Q26_1_9_RANK',
    },
    'Q26_1_10_RANK': {
        'field_type': 'answer',
        'model_field': 'Q26_1_10_RANK',
    },
    'Q26_1_11_RANK': {
        'field_type': 'answer',
        'model_field': 'Q26_1_11_RANK',
    },
    'Q26_1_12_RANK': {
        'field_type': 'answer',
        'model_field': 'Q26_1_12_RANK',
    },
    'Q26_1_13_RANK': {
        'field_type': 'answer',
        'model_field': 'Q26_1_13_RANK',
    },
    'Q26_1_14_RANK': {
        'field_type': 'answer',
        'model_field': 'Q26_1_14_RANK',
    },
    'Q26_1_15_RANK': {
        'field_type': 'answer',
        'model_field': 'Q26_1_15_RANK',
    },
    'Q26_1_17_RANK': {
        'field_type': 'answer',
        'model_field': 'Q26_1_17_RANK',
    },
    'Q26_1_16_RANK': {
        'field_type': 'answer',
        'model_field': 'Q26_1_16_RANK',
    },
    'Q26A_1': {
        'field_type': 'answer',
        'model_field': 'Q26A_1',
    },
    'Q26A_2': {
        'field_type': 'answer',
        'model_field': 'Q26A_2',
    },
    'Q26A_3': {
        'field_type': 'answer',
        'model_field': 'Q26A_3',
    },
    'Q26A_4': {
        'field_type': 'answer',
        'model_field': 'Q26A_4',
    },
    'Q26A_5': {
        'field_type': 'answer',
        'model_field': 'Q26A_5',
    },
    'Q26A_6': {
        'field_type': 'answer',
        'model_field': 'Q26A_6',
    },
    'Q26A_7': {
        'field_type': 'answer',
        'model_field': 'Q26A_7',
    },
    'Q26A_8': {
        'field_type': 'answer',
        'model_field': 'Q26A_8',
    },
    'Q26A_9': {
        'field_type': 'answer',
        'model_field': 'Q26A_9',
    },
    'Q26A_10': {
        'field_type': 'answer',
        'model_field': 'Q26A_10',
    },
    'Q26A_11': {
        'field_type': 'answer',
        'model_field': 'Q26A_11',
    },
    'Q26A_12': {
        'field_type': 'answer',
        'model_field': 'Q26A_12',
    },
    'Q26A_13': {
        'field_type': 'answer',
        'model_field': 'Q26A_13',
    },
    'Q26A_14': {
        'field_type': 'answer',
        'model_field': 'Q26A_14',
    },
    'Q26A_15': {
        'field_type': 'answer',
        'model_field': 'Q26A_15',
    },
    'Q26A_16': {
        'field_type': 'answer',
        'model_field': 'Q26A_16',
    },
    'Q26A_17': {
        'field_type': 'answer',
        'model_field': 'Q26A_17',
    },
    'Q26A_18': {
        'field_type': 'answer',
        'model_field': 'Q26A_18',
    },
    'Aptitude_1': {
        'field_type': 'answer',
        'model_field': 'Aptitude_1',
    },
    'Aptitude_2': {
        'field_type': 'answer',
        'model_field': 'Aptitude_2',
    },
    'Aptitude_3': {
        'field_type': 'answer',
        'model_field': 'Aptitude_3',
    },
    'Aptitude_4': {
        'field_type': 'answer',
        'model_field': 'Aptitude_4',
    },
    'Aptitude_5': {
        'field_type': 'answer',
        'model_field': 'Aptitude_5',
    },
    'Aptitude_6': {
        'field_type': 'answer',
        'model_field': 'Aptitude_6',
    },
    'Aptitude_7': {
        'field_type': 'answer',
        'model_field': 'Aptitude_7',
    },
    'Aptitude_8': {
        'field_type': 'answer',
        'model_field': 'Aptitude_8',
    },
    'Aptitude_9': {
        'field_type': 'answer',
        'model_field': 'Aptitude_9',
    },


    # ── Calculated ───────────────────────────────────────────────────────────
    'SC0': {
        'field_type': 'calculated',
        'model_field': 'score_agriculture',
    },
    'SC1': {
        'field_type': 'calculated',
        'model_field': 'score_architecture',
    },
    'SC2': {
        'field_type': 'calculated',
        'model_field': 'score_arts_av_comm',
    },
    'SC3': {
        'field_type': 'calculated',
        'model_field': 'score_business_mgmt',
    },
    'SC4': {
        'field_type': 'calculated',
        'model_field': 'score_education',
    },
    'SC5': {
        'field_type': 'calculated',
        'model_field': 'score_energy',
    },
    'SC6': {
        'field_type': 'calculated',
        'model_field': 'score_finance',
    },
    'SC7': {
        'field_type': 'calculated',
        'model_field': 'score_government',
    },
    'SC8': {
        'field_type': 'calculated',
        'model_field': 'score_health_sciences',
    },
    'SC9': {
        'field_type': 'calculated',
        'model_field': 'score_hospitality',
    },
    'SC10': {
        'field_type': 'calculated',
        'model_field': 'score_human_services',
    },
    'SC11': {
        'field_type': 'calculated',
        'model_field': 'score_information_tech',
    },
    'SC12': {
        'field_type': 'calculated',
        'model_field': 'score_law_public_safety',
    },
    'SC13': {
        'field_type': 'calculated',
        'model_field': 'score_manufacturing',
    },
    'SC14': {
        'field_type': 'calculated',
        'model_field': 'score_marketing',
    },
    'SC15': {
        'field_type': 'calculated',
        'model_field': 'score_stem',
    },
    'SC16': {
        'field_type': 'calculated',
        'model_field': 'score_telecommunications',
    },
    'SC17': {
        'field_type': 'calculated',
        'model_field': 'score_transportation',
    },
    'SC22': {
        'field_type': 'calculated',
        'model_field': 'score_verbal_aptitude',
    },
    'SC23': {
        'field_type': 'calculated',
        'model_field': 'score_spatial_aptitude',
    },
    'SC24': {
        'field_type': 'calculated',
        'model_field': 'score_cognitive_aptitude',
    },
    'SC25': {
        'field_type': 'calculated',
        'model_field': 'score_numerical_aptitude',
    },
    'Career_1_Score': {
        'field_type': 'calculated',
        'model_field': 'career_score_agriculture',
    },
    'Career_2_Score': {
        'field_type': 'calculated',
        'model_field': 'career_score_architecture',
    },
    'Career_3_Score': {
        'field_type': 'calculated',
        'model_field': 'career_score_arts_av_comm',
    },
    'Career_4_Score': {
        'field_type': 'calculated',
        'model_field': 'career_score_business_mgmt',
    },
    'Career_5_Score': {
        'field_type': 'calculated',
        'model_field': 'career_score_education',
    },
    'Career_6_Score': {
        'field_type': 'calculated',
        'model_field': 'career_score_energy',
    },
    'Career_7_Score': {
        'field_type': 'calculated',
        'model_field': 'career_score_finance',
    },
    'Career_8_Score': {
        'field_type': 'calculated',
        'model_field': 'career_score_government',
    },
    'Career_9_Score': {
        'field_type': 'calculated',
        'model_field': 'career_score_health_sciences',
    },
    'Career_10_Score': {
        'field_type': 'calculated',
        'model_field': 'career_score_hospitality',
    },
    'Career_11_Score': {
        'field_type': 'calculated',
        'model_field': 'career_score_human_services',
    },
    'Career_12_Score': {
        'field_type': 'calculated',
        'model_field': 'career_score_information_tech',
    },
    'Career_13_Score': {
        'field_type': 'calculated',
        'model_field': 'career_score_law_public_safety',
    },
    'Career_14_Score': {
        'field_type': 'calculated',
        'model_field': 'career_score_manufacturing',
    },
    'Career_15_Score': {
        'field_type': 'calculated',
        'model_field': 'career_score_marketing',
    },
    'Career_16_Score': {
        'field_type': 'calculated',
        'model_field': 'career_score_stem',
    },
    'Career_17_Score': {
        'field_type': 'calculated',
        'model_field': 'career_score_telecommunications',
    },
    'Career_18_Score': {
        'field_type': 'calculated',
        'model_field': 'career_score_transportation',
    },
    'AwarenessScore': {
        'field_type': 'calculated',
        'model_field': 'awareness_score',
    },
    'ExplorationScore': {
        'field_type': 'calculated',
        'model_field': 'exploration_score',
    },
    'Q6R_Q7R': {
        'field_type': 'calculated',
        'model_field': 'particip_career_prep_either',
    },
    'Q6R': {
        'field_type': 'calculated',
        'model_field': 'particip_career_prep_awareness',
    },
    'Q7R': {
        'field_type': 'calculated',
        'model_field': 'particip_career_prep_exploration',
    },
}

# Derived convenience sets — computed from SURVEY_COLUMNS - any changes should be made to SURVEY_COLUMNS ONLY!
EXPECTED_COLUMNS = list(SURVEY_COLUMNS.keys())

SKIP_COLS = {
    col for col, cfg in SURVEY_COLUMNS.items()
    if cfg.get('skip') or cfg['field_type'] in ('metadata', 'calculated', 'school')
}

# Most cols are stored in DB with the same name as the survey column header, but some are changed to be more meaningful/consistent in the DB
#     These must be mapped back to match them to the original column header in the survey dataset import files
METADATA_FIELD_MAP = {
    cfg['model_field']: col
    for col, cfg in SURVEY_COLUMNS.items()
    if cfg['field_type'] == 'metadata'
}

CALCULATED_FIELD_MAP = {
    cfg['model_field']: col
    for col, cfg in SURVEY_COLUMNS.items()
    if cfg['field_type'] == 'calculated'
}


# Columns that indicate career awareness participation (Q6_8 is "None of the above" — excluded)
Q6_PARTICIPATION_COLS = ['Q6_1', 'Q6_2', 'Q6_3', 'Q6_4', 'Q6_5', 'Q6_6', 'Q6_7']

# Columns that indicate career exploration participation (Q7_8 is "None of the above" — excluded)
# All Q7A columns are valid participation indicators (no "None of the above" in Q7A)
Q7_PARTICIPATION_COLS = [
    'Q7_1', 'Q7_2', 'Q7_3', 'Q7_4', 'Q7_5', 'Q7_6', 'Q7_7',
    'Q7A_1', 'Q7A_2', 'Q7A_3', 'Q7A_4', 'Q7A_5', 'Q7A_6', 'Q7A_7', 'Q7A_8',
]