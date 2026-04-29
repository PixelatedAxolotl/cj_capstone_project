#!/usr/bin/perl
# TODO: add granular control over percent of each question complete + percent of time option is chosen for specific question

use strict;
use warnings;
use Excel::Writer::XLSX;
use Time::Piece;
use Time::Seconds;
use Data::Dumper qw(Dumper);

# Q1: populate with the numeric school IDs used in the database before running.
my @SCHOOL_IDS = (
    1, 2, 3, 4, 17, 19
);

my @HEADER = (
    qw(StartDate EndDate Status Progress Duration__in_seconds_
       Finished RecordedDate ResponseId DistributionChannel UserLanguage),
    qw(Q1 Q2),
    ( map { "Q3_$_"  } 1..16 ), 'Q3_16_TEXT',
    ( map { "Q4_$_"  } 1..16 ), 'Q4_16_TEXT',
    'Q5',
    ( map { "Q6_$_"  } 1..8  ),
    ( map { "Q7_$_"  } 1..8  ),
    qw(Q7A_1 Q7A_2 Q7A_3 Q7A_7 Q7A_8 Q7A_4 Q7A_5 Q7A_6), 'Q7A_6_TEXT',
    ( map { "Q8_$_"  } 1..19 ),
    ( map { "Q9_$_"  } 1..8  ), 'Q9_7_TEXT',
    'Q10', 'Q10_7_TEXT',
    'Q11', 'Q11_7_TEXT',
    ( map { "Q12_$_"     } 1..7 ),
    ( map { "Q12_${_}_2" } 1..7 ),
    ( map { "Q13_$_"     } 1..7 ),
    qw(Q14 Q15),
    ( map { "Q16_$_" } 1..5 ), 'Q16_5_TEXT',
    'Q18',
    qw(Q20A Q20B Q20C Q20D),
    qw(Q22 Q23),
    ( map { "Q24_0_GROUP_$_" } qw(153 156 157 158 159 171 160 161 162 163 164 165 166 167 168 169 172 170) ),
    ( map { "Q24_1_GROUP_$_" } qw(153 156 157 158 159 171 160 161 162 163 164 165 166 167 168 169 172 170) ),
    ( map { "Q24A_$_"        } 1..18 ),
    qw(Q25 Q25A Q25B Q25C Q25D Q25E Q25F Q25G Q25H Q25I Q25J Q25K Q25L Q25M Q25N Q25O Q25P Q25Q),
    ( map { "Q25R_$_"        } 1..18 ),
    ( map { "Q26_0_GROUP_$_" } qw(1 2 3 4 5 18 6 7 8 9 10 11 12 13 14 15 17 16) ),
    ( map { "Q26_1_GROUP_$_" } qw(1 2 3 4 5 18 6 7 8 9 10 11 12 13 14 15 17 16) ),
    ( map { "Q26_0_${_}_RANK"} qw(1 2 3 4 5 18 6 7 8 9 10 11 12 13 14 15 17 16) ),
    ( map { "Q26_1_${_}_RANK"} qw(1 2 3 4 5 18 6 7 8 9 10 11 12 13 14 15 17 16) ),
    ( map { "Q26A_$_"        } 1..18 ),
    ( map { "SC$_"           } 0..17 ),
    ( map { "Career_${_}_Score" } 1..18 ),
    qw(AwarenessScore ExplorationScore CareerPrepScore),
    qw(Q5R Year Semester Career_Awareness Career_Exploration),
    qw(Q6R Q7R Q6R_Q7R),
    ( map { "Aptitude_$_"    } 1..9  ),
    qw(SC22 SC23 SC24 SC25),
);



# ----------------------------
# Schema Structure:
#    Column Name => {
#        type => 'single' | 'multi' | 'subset_multi' | 'scale' | 'like_dislike'| 'text' | 'system' | 'derived' | 'matrix',
#        values => [ ... ],          # for 'single' type
#        columns => [ ... ],         # for 'multi' and 'scale' types
#        min_select => N,            # for 'multi' type - set min number of selections to ensure question is not left blank - by default chance of entire question being blank is allowed
#        max_select => N,            # for 'multi' type - set max number of selections to handle "pick your top 3" style questions
#        blank_prob => 0.05,         # individual question blanking probability (applies to entire question group for multi/scale types EXCEPT _TEXT cols which have probability set separately)
#        group_ids => [ ... ],       # for 'like_dislike' type - list of item IDs in the group (**NOTE: listed in quoted string instead of with .. because some questions have IDs which are not consecutive)
#
#        prefix_0 => 'Q24_0_GROUP_',  # for 'like_dislike' type - prefix for "like" columns (will be suffixed by group ID)
#        prefix_1 => 'Q24_1_GROUP_',  # for 'like_dislike' type - prefix for "dislike" columns (will be suffixed by group ID)
#
#        trigger_col => 'Q#_##'      # for 'text' type col - identifies 'other, please specify' options for questions
#        trigger_val => '7'          # for 'text' type col - identifies value of the trigger_col (when trigger_col is a single choice question) that will activate this text field (default is any non-blank value)
#
#        conditional_display => 1    # flag for questions that are only displayed in survey based on responses to other questions - they SHOULD NOT be included in the total questions list since they can be blank even if the survey response is 'complete'
#

# ----------------------------
my %schema = (

    # ----------------------------
    # SYSTEM / METADATA
    # ----------------------------
    StartDate             => { type => 'system' },
    EndDate               => { type => 'system' },
    Status                => { type => 'system' },
    Progress              => { type => 'system' },
    Duration__in_seconds_ => { type => 'system' },
    Finished              => { type => 'system' },
    RecordedDate          => { type => 'system' },
    ResponseId            => { type => 'system' },
    DistributionChannel   => { type => 'system' },
    UserLanguage          => { type => 'system' },
    Year     => { type => 'system', values => [1..4],},
    Semester => { type => 'system', values => [1, 2],},

    # ----------------------------
    # SINGLE-CHOICE QUESTIONS
    # ----------------------------
    Q1  => { type => 'single', values => \@SCHOOL_IDS,  blank_prob => 0 },
    Q2  => { type => 'single', values => [1..7],         blank_prob => 0.03 },
    Q5  => { type => 'single', values => [1..5],         blank_prob => 0.03 },
    Q14 => { type => 'single', values => [1..4],         blank_prob => 0.03 },
    Q15 => { type => 'single', values => [1..4],         blank_prob => 0.03 },
    Q18 => { type => 'single', values => [1..5],         blank_prob => 0.03 },
    Q22 => { type => 'single', values => [1..3],         blank_prob => 0.03 },
    Q23 => { type => 'single', values => [1..4],         blank_prob => 0.03 },



    # ----------------------------
    # SCALE QUESTIONS
    # Q25-Q25Q: 18 items each rated 1-5
    # ----------------------------
    Q25_SCALE => {
        type       => 'scale',
        columns    => [qw(Q25 Q25A Q25B Q25C Q25D Q25E Q25F Q25G
                          Q25H Q25I Q25J Q25K Q25L Q25M Q25N Q25O Q25P Q25Q)],
        min        => 1,
        max        => 5,
        blank_prob => 0.05,
    },
    Aptitude => {
        type       => 'scale',
        columns    => [ map { "Aptitude_$_" } 1..9 ],
        min        => 1,
        max        => 5,
        blank_prob => 0.05,
    },

    # ----------------------------
    # MULTI-SELECT (WIDE BINARY)
    # ----------------------------
    Q3 => {
        type => 'multi',
        columns => [ map { "Q3_$_" } 1..16 ],
        min_select => 0,
        max_select => 6,
        blank_prob => 0.05,
    },

    Q6 => {
        type => 'multi',
        columns => [ map { "Q6_$_" } 1..8 ],
        min_select => 0,
        max_select => 4,
        blank_prob => 0.05,
    },

    Q7 => {
        type => 'multi',
        columns => [ map { "Q7_$_" } 1..8 ],
        min_select => 0,
        max_select => 4,
        blank_prob => 0.05,
    },

    Q7A => {
        type => 'multi',
        columns => [ qw(Q7A_1 Q7A_2 Q7A_3 Q7A_4 Q7A_5 Q7A_6 Q7A_7 Q7A_8) ],
        min_select => 0,
        max_select => 4,
        blank_prob => 0.05,
        conditional_display => 1,  # Q7A questions are only displayed based on responses to Q7, so they should not be counted for completeness calc
    },

    Q8 => {
        type => 'multi',
        columns => [ map { "Q8_$_" } 1..19 ],
        min_select => 0,
        max_select => 6,
        blank_prob => 0.05,
    },

    Q9 => {
        type => 'multi',
        columns => [ map { "Q9_$_" } 1..8 ],
        min_select => 0,
        max_select => 4,
        blank_prob => 0.05,
    },

    Q12 => {
        type => 'multi',
        columns => [ map { "Q12_$_" } 1..7 ],
        min_select => 0,
        max_select => 4,
        blank_prob => 0.05,
    },

    Q12_2 => {
        type => 'multi',
        columns => [ map { "Q12_${_}_2" } 1..7 ],
        min_select => 0,
        max_select => 4,
        blank_prob => 0.05,
    },

    Q13 => {
        type => 'multi',
        columns => [ map { "Q13_$_" } 1..7 ],
        min_select => 0,
        max_select => 4,
        blank_prob => 0.05,
    },

    Q16 => {
        type => 'multi',
        columns => [ map { "Q16_$_" } 1..5 ],
        min_select => 0,
        max_select => 3,
        blank_prob => 0.05,
    },

    # ----------------------------
    # MULI-SELECT WITH DEPENDENT OPTIONS (SUBSET_MULTI)
    #     Q4_1-16 depend on Q3_1-16 (only shown if parent item selected)
    #     Q10_7 and Q11_7 depend on Q10 and Q11 response of 7 respectively (only shown if parent response is 7)
    #     Q25R_1-18 depend on Q25-Q25R responses of 4 or 5 (only shown if parent item rated 4 or 5)
    #         For these, build a pool of eligible options from selectd parent opts, then randomly select from that pool.
    # ----------------------------
    Q4 => {
        type        => 'subset_multi',
        parent      => 'Q3',
        parent_cols => [ map { "Q3_$_" } 1..16 ],
        columns     => [ map { "Q4_$_" } 1..16 ],
        max_select  => 3,
        conditional_display => 1,  # Q4 questions are only displayed based on responses to Q3, so they should not be counted for completeness calc
    },
    Q10 => {
        type       => 'subset_multi',
        parent     => 'Q9',
        parent_cols => [ map { "Q9_$_" } 1..7 ],  # exclude Q9_8 "No one"
        blank_if   => 'Q9_8',
        output_col => 'Q10',
        max_select => 1,
        conditional_display => 1,  # Q10 is only displayed based on responses to Q9, so it should not be counted for completeness calc
    },

    Q11 => {
        type       => 'subset_multi',
        parent     => 'Q9',
        parent_cols => [ map { "Q9_$_" } 1..7 ],
        blank_if   => 'Q9_8',
        output_col => 'Q11',
        max_select => 1,
        conditional_display => 1,  # Q11 is only displayed based on responses to Q9, so it should not be counted for completeness calc
    },
    Q25R => {
        type        => 'subset_multi',
        parent      => 'Q25_SCALE',
        parent_cols => [qw(Q25 Q25A Q25B Q25C Q25D Q25E Q25F Q25G
                        Q25H Q25I Q25J Q25K Q25L Q25M Q25N Q25O Q25P Q25Q)],
        columns     => [ map { "Q25R_$_" } 1..18 ],
        max_select  => 3,
        min_score   => 4,
        map_suffix_manually => 1,  # flag to indicate question is a super special lil' guy.  -_-   parent suffixes are letters but Q25R suffixes are numbers + first parent option does not have suffix
                                   #    Suffix mapping logic is handled manually since this is such a weird case.
        conditional_display => 1,  # Q25R questions are only displayed based on responses to Q25-Q25Q, so they should not be counted for completeness calc
    },

    # ----------------------------
    # FREE TEXT FIELDS
    # ----------------------------
    Q3_16_TEXT  => { type => 'text', trigger_col => 'Q3_16'  },
    Q4_16_TEXT  => { type => 'text', trigger_col => 'Q4_16'  },
    Q7A_6_TEXT  => { type => 'text', trigger_col => 'Q7A_6'  },
    Q9_7_TEXT   => { type => 'text', trigger_col => 'Q9_7'   },
    Q10_7_TEXT  => { type => 'text', trigger_col => 'Q10', trigger_val => '7' },
    Q11_7_TEXT  => { type => 'text', trigger_col => 'Q11', trigger_val => '7' },
    Q16_5_TEXT  => { type => 'text', trigger_col => 'Q16_5'  },

    # ----------------------------
    # LIKE/DISLIKE GROUPS
    # Q24: 18 items, like (0-group=1) or dislike (1-group=1), never both.
    # Q26: same structure, plus unique ranks assigned to selected items.
    # Q24A/Q26A (top-3 from liked items) are populated by generate_like_dislike().
    # ----------------------------
    Q24_GROUP => {
        type        => 'like_dislike',
        group_ids   => [qw(153 156 157 158 159 171 160 161 162 163 164 165 166 167 168 169 172 170)],
        prefix_0    => 'Q24_0_GROUP_',
        prefix_1    => 'Q24_1_GROUP_',
        topn_prefix => 'Q24A_',
        ranked      => 0,
    },

    Q26_GROUP => {
        type          => 'like_dislike',
        group_ids     => [qw(1 2 3 4 5 18 6 7 8 9 10 11 12 13 14 15 17 16)],
        prefix_0      => 'Q26_0_GROUP_',
        prefix_1      => 'Q26_1_GROUP_',
        topn_prefix   => 'Q26A_',
        rank_prefix_0 => 'Q26_0_',
        rank_prefix_1 => 'Q26_1_',
        ranked        => 1,
    },

    # ----------------------------
    # DERIVED / CALCULATED — initially blank - filled in later dependent on other columns
    # NOTE: Forumulas do not match those used on the real data - these are just meant to give plausible values for testing!
    # ----------------------------
    ( map { ( "SC$_"              => { type => 'derived' } ) } (0..17, 22..25) ),
    ( map { ( "Career_${_}_Score" => { type => 'derived' } ) } 1..18           ),
    AwarenessScore     => { type => 'derived' },
    ExplorationScore   => { type => 'derived' },
    CareerPrepScore    => { type => 'derived' },
    Career_Awareness   => { type => 'derived' },
    Career_Exploration => { type => 'derived' },
    Q5R     => { type => 'derived' },
    Q6R     => { type => 'derived' },
    Q7R     => { type => 'derived' },
    Q6R_Q7R => { type => 'derived' },
);



# ----------------------------
# DERIVED/CALCULATED FIELD CONTROLS
# ----------------------------

# Maps raw point totals to final 1-5 career cluster scores.
# Each entry is [max_points, score]
my @SCORE_SCALE = (
    [0,  0],
    [2,  1],
    [4,  2],
    [6,  3],
    [8,  4],
    [99, 5],  # 9+ points
);


# Maps each of the 18 career clusters (by index 0-17) to the Q8, Q24A, Q25R
# and Q26A columns that contribute points toward that cluster score.
my @CLUSTER_INPUTS = (
    # 0: Agriculture, Food & Natural Resources
    { q8 => 'Q8_1',
      q24a => [qw(Q24A_1 Q24A_2 Q24A_16 Q24A_17)],
      q25r => [qw(Q25R_14)],
      q26a => [qw(Q26A_1 Q26A_14)] },

    # 1: Architecture & Construction
    { q8 => 'Q8_2',
      q24a => [qw(Q24A_2 Q24A_14)],
      q25r => [qw(Q25R_18)],
      q26a => [qw(Q26A_18)] },

    # 2: Arts, A/V Technology & Communications
    { q8 => 'Q8_3',
      q24a => [qw(Q24A_3)],
      q25r => [qw(Q25R_15)],
      q26a => [] },

    # 3: Business, Management & Administration
    { q8 => 'Q8_4',
      q24a => [qw(Q24A_4 Q24A_8 Q24A_15)],
      q25r => [qw(Q25R_1 Q25R_4 Q25R_6 Q25R_8 Q25R_15 Q25R_18)],
      q26a => [qw(Q26A_3 Q26A_5 Q26A_7 Q26A_18)] },

    # 4: Education & Training
    { q8 => 'Q8_5',
      q24a => [qw(Q24A_5 Q24A_6 Q24A_11)],
      q25r => [qw(Q25R_3 Q25R_5 Q25R_10)],
      q26a => [qw(Q26A_2 Q26A_4 Q26A_9)] },

    # 5: Energy
    { q8 => 'Q8_6',
      q24a => [qw(Q24A_17)],
      q25r => [],
      q26a => [qw(Q26A_1)] },

    # 6: Finance
    { q8 => 'Q8_7',
      q24a => [qw(Q24A_7)],
      q25r => [qw(Q25R_7 Q25R_9 Q25R_11 Q25R_16)],
      q26a => [qw(Q26A_12 Q26A_16)] },

    # 7: Government & Public Administration
    { q8 => 'Q8_8',
      q24a => [qw(Q24A_4 Q24A_8 Q24A_13)],
      q25r => [qw(Q25R_3 Q25R_4 Q25R_6 Q25R_17 Q25R_18)],
      q26a => [qw(Q26A_5 Q26A_8 Q26A_17)] },

    # 8: Health Sciences
    { q8 => 'Q8_9',
      q24a => [qw(Q24A_1 Q24A_5 Q24A_9 Q24A_11 Q24A_16)],
      q25r => [qw(Q25R_5 Q25R_9 Q25R_14)],
      q26a => [qw(Q26A_4 Q26A_9 Q26A_11)] },

    # 9: Hospitality & Tourism
    { q8 => 'Q8_10',
      q24a => [qw(Q24A_8 Q24A_10)],
      q25r => [qw(Q25R_10)],
      q26a => [qw(Q26A_10)] },

    # 10: Human Services
    { q8 => 'Q8_11',
      q24a => [qw(Q24A_5 Q24A_9 Q24A_11)],
      q25r => [qw(Q25R_5 Q25R_17)],
      q26a => [qw(Q26A_8 Q26A_9 Q26A_11)] },

    # 11: Information Technology
    { q8 => 'Q8_12',
      q24a => [qw(Q24A_7 Q24A_12)],
      q25r => [qw(Q25R_1 Q25R_11 Q25R_16)],
      q26a => [qw(Q26A_6 Q26A_16)] },

    # 12: Law, Public Safety, Corrections & Security
    { q8 => 'Q8_13',
      q24a => [qw(Q24A_13)],
      q25r => [qw(Q25R_8 Q25R_12 Q25R_14)],
      q26a => [qw(Q26A_3 Q26A_13 Q26A_14 Q26A_15 Q26A_17)] },

    # 13: Manufacturing
    { q8 => 'Q8_14',
      q24a => [qw(Q24A_2 Q24A_14)],
      q25r => [qw(Q25R_2 Q25R_7 Q25R_9 Q25R_13)],
      q26a => [qw(Q26A_12)] },

    # 14: Marketing
    { q8 => 'Q8_15',
      q24a => [qw(Q24A_3 Q24A_10 Q24A_15)],
      q25r => [qw(Q25R_3 Q25R_8 Q25R_10)],
      q26a => [qw(Q26A_7 Q26A_10 Q26A_15)] },

    # 15: Science, Technology, Engineering & Mathematics
    { q8 => 'Q8_16',
      q24a => [qw(Q24A_1 Q24A_6 Q24A_7 Q24A_16 Q24A_17)],
      q25r => [qw(Q25R_1 Q25R_11 Q25R_12 Q25R_16)],
      q26a => [qw(Q26A_2 Q26A_6 Q26A_12)] },

    # 16: Telecommunications
    { q8 => 'Q8_17',
      q24a => [qw(Q24A_12)],
      q25r => [],
      q26a => [] },

    # 17: Transportation, Distribution & Logistics
    { q8 => 'Q8_18',
      q24a => [qw(Q24A_2 Q24A_14 Q24A_18)],
      q25r => [qw(Q25R_2 Q25R_13)],
      q26a => [qw(Q26A_13)] },
);

# Maps each aptitude SC score to its contributing aptitude columns.
my %APTITUDE_GROUPS = (
    SC22 => [qw(Aptitude_1 Aptitude_2 Aptitude_5 Aptitude_8)],  # Verbal
    SC23 => [qw(Aptitude_2 Aptitude_3 Aptitude_4 Aptitude_9)],  # Spatial
    SC24 => [qw(Aptitude_1 Aptitude_5 Aptitude_6 Aptitude_8)],  # Cognitive
    SC25 => [qw(Aptitude_5 Aptitude_6 Aptitude_7 Aptitude_8)],  # Numerical
);

my $APTITUDE_MIN = 4;   # 4 aptitudes x min score of 1
my $APTITUDE_MAX = 20;  # 4 aptitudes x max score of 5



# ----------------------------
# GRADE-CONDITIONAL RESPONSE PROBABILITIES
#
# Controls how a respondent's letter grade (Q5: 1=A, 2=B, 3=C, 4=D, 5=F)
# affects the probability of selecting each option in a question.
# allows for dataset gen with logic such as "B students are 25% more likely to be interested in STEM careers than A students"
#
# Two-layer system per question:
#   1. col_probs:         Base probability of an option being selected (independent of grade)
#   2. grade_multipliers: Q5-keyed scalar multiplied onto col_probs (each question has its own)
#   Optional column_overrides: absolute probability for a specific (Q5, column) pair —
#                              bypasses col_probs and grade_multipliers entirely for that cell
#
# Question types and their format:
#
#   MULTI-SELECT (Q3, Q6, Q7, Q7A, Q8, Q9, Q12, Q12_2, Q13, Q16):
#       col_probs => { 'ColName' => 0.0..1.0, ... }
#       grade_multipliers => { 1 => mult, 2 => mult, 3 => mult, 4 => mult, 5 => mult }
#       column_overrides  => { q5_val => { 'ColName' => absolute_prob } }   # optional
#
#   SCALE (Q25_SCALE, Aptitude):  *** Note: schema key is Q25_SCALE, not Q25 ***
#       col_probs         => { 'ColName' => [w1, w2, w3, w4, w5] }  # one weight per value 1-5
#       grade_value_shift => { 1 => N, ... }    # +N pushes toward higher values, -N toward lower
#
#   LIKE/DISLIKE (Q24_GROUP, Q26_GROUP):
#       col_probs         => { item_id => [like_prob, dislike_prob] }
#       grade_multipliers => { 1 => mult, ... }  # applied to like_prob only
#       column_overrides  => { q5_val => { item_id => absolute_like_prob } }  # optional
#
# Leave the hash body empty for uniform-random behavior.
# Uncomment questions to configure specific probabilities.
# ----------------------------
my %CONDITIONAL_PROBS = (

    # ----------------------------
    # SINGLE-CHOICE QUESTIONS
    # val_probs:         value => weight  (weights are normalized, so ratios matter not sum)
    # grade_value_shift: Q5 => integer shift applied to val_probs (+N toward higher values)
    #                    Omit grade_value_shift for Q5 itself since it IS the grade field.
    # ----------------------------

    # Q5: Letter grade average — set the target distribution of grades in the dataset
    # 1=F, 2=D, 3=C, 4=B, 5=A
    Q5 => {
        val_probs => { 1=>0.083, 2=>0.016, 3=>0.11, 4=>0.4, 5=>0.46 },
    },

    # Q2: Grade level — 1=7th through 7=12th
    Q2 => {
        val_probs => { 1=>0.007, 2=>0.65, 3=>0.16, 4=>0.06, 5=>0.06, 6=>0.05, 7=>0.008 },
    },

    # Q14: Response options 1-4
    # val_probs is used as the fallback when Q5 is blank.
    Q14 => {
        val_probs       => { 1=>0.25, 2=>0.25, 3=>0.25, 4=>0.25 },
        grade_val_probs => {
            1 => { 1=>0.63,  2=>1.03,  3=>0.51,  4=>0.34  },   # A students
            2 => { 1=>2.06,  2=>1.81,  3=>1.11,  4=>0.45  },   # B students
            3 => { 1=>10.76, 2=>10.75, 3=>11.09, 4=>4.93  },   # C students
            4 => { 1=>41.35, 2=>35.51, 3=>36.61, 4=>33.97 },   # D students
            5 => { 1=>36.50, 2=>41.27, 3=>42.78, 4=>51.23 },   # F students
        },
    },

    # Q15: Response options 1-4
    Q15 => {
        val_probs         => { 1=>0.20, 2=>0.35, 3=>0.30, 4=>0.15 },
        grade_value_shift => { 1=>+1, 2=>0, 3=>0, 4=>-1, 5=>-1 },
    },

    # Q18: Response options 1-5
    Q18 => {
        val_probs         => { 1=>0.05, 2=>0.15, 3=>0.35, 4=>0.30, 5=>0.15 },
        grade_value_shift => { 1=>+1, 2=>0, 3=>0, 4=>-1, 5=>-1 },
    },

    # Q22: Response options 1-3
    Q22 => {
        val_probs         => { 1=>0.30, 2=>0.45, 3=>0.25 },
        grade_value_shift => { 1=>+1, 2=>0, 3=>0, 4=>-1, 5=>-1 },
    },

    # Q23: Response options 1-4
    Q23 => {
        val_probs         => { 1=>0.20, 2=>0.35, 3=>0.30, 4=>0.15 },
        grade_value_shift => { 1=>+1, 2=>0, 3=>0, 4=>-1, 5=>-1 },
    },

    # ----------------------------
    # MULTI-SELECT QUESTIONS
    # col_probs:         base probability per column (0.0-1.0)
    # grade_multipliers: Q5 value (1=A, 2=B, 3=C, 4=D, 5=F) => multiplier on col_probs
    # column_overrides:  optional absolute prob for a specific (Q5, col) pair
    # ----------------------------

    # Q6: Career awareness activities -- A students participate more
    Q6 => {
        col_probs => {
            Q6_1 => 0.45, Q6_2 => 0.38, Q6_3 => 0.30,
            Q6_4 => 0.25, Q6_5 => 0.20, Q6_6 => 0.18,
            Q6_7 => 0.22, Q6_8 => 0.42,   # Q6_8 = "None of the above"
        },
        grade_multipliers => { 1=>0.90, 2=>.70, 3=>0.6, 4=>0.2, 5=>0.2 },
        column_overrides => {
            3 => { Q6_8 => 0.45 },  # C
            2 => { Q6_8 => 0.55 },  # D
            1 => { Q6_8 => 0.60 },  # F
        },
    },

    # Q7: Career exploration activities -- A students participate more
    Q7 => {
        col_probs => {
            Q7_1 => 0.40, Q7_2 => 0.35, Q7_3 => 0.30,
            Q7_4 => 0.25, Q7_5 => 0.20, Q7_6 => 0.18,
            Q7_7 => 0.22, Q7_8 => 0.42,
        },
        #grade_multipliers => { 1=>0.90, 2=>.70, 3=>0.6, 4=>0.2, 5=>0.2 },
        # C/D/F students are more likely to have done none of these activities
        column_overrides => {
            3 => { Q7_8 => 0.45 },  # C
            2 => { Q7_8 => 0.55 },  # D
            1 => { Q7_8 => 0.60 },  # F
        },
    },

    # Q8: Career cluster interests -- slight engagement gradient across grades
    Q8 => {
        col_probs => {
            Q8_1  => 0.25, Q8_2  => 0.25, Q8_3  => 0.25,
            Q8_4  => 0.25, Q8_5  => 0.25, Q8_6  => 0.25,
            Q8_7  => 0.25, Q8_8  => 0.25, Q8_9  => 0.25,
            Q8_10 => 0.25, Q8_11 => 0.25, Q8_12 => 0.25,
            Q8_13 => 0.25, Q8_14 => 0.25, Q8_15 => 0.25,
            Q8_16 => 0.25, Q8_17 => 0.25, Q8_18 => 0.25,
            Q8_19 => 0.25,
        },
        grade_multipliers => { 1=>1.20, 2=>1.10, 3=>1.00, 4=>0.90, 5=>0.75 },
        # To boost specific clusters for specific grades, uncomment and adjust:
        # column_overrides => { 2 => { Q8_16 => 0.55 }, 3 => { Q8_16 => 0.50 } },
    },

    # ----------------------------
    # SCALE QUESTIONS
    # col_probs:         per-column weight array [w_val1, w_val2, w_val3, w_val4, w_val5]
    # grade_value_shift: Q5 => integer shift (+N toward higher values, -N toward lower)
    # ----------------------------

    # Q25_SCALE: Career interest ratings -- A students rate interests slightly higher
    Q25_SCALE => {
        col_probs => {
            # [weight for 1, weight for 2, weight for 3, weight for 4, weight for 5]
            Q25  => [0.05, 0.10, 0.30, 0.35, 0.20],
            Q25A => [0.05, 0.10, 0.30, 0.35, 0.20],
            Q25B => [0.05, 0.10, 0.30, 0.35, 0.20],
            Q25C => [0.05, 0.10, 0.30, 0.35, 0.20],
            Q25D => [0.05, 0.10, 0.30, 0.35, 0.20],
            Q25E => [0.05, 0.10, 0.30, 0.35, 0.20],
            Q25F => [0.05, 0.10, 0.30, 0.35, 0.20],
            Q25G => [0.05, 0.10, 0.30, 0.35, 0.20],
            Q25H => [0.05, 0.10, 0.30, 0.35, 0.20],
            Q25I => [0.05, 0.10, 0.30, 0.35, 0.20],
            Q25J => [0.05, 0.10, 0.30, 0.35, 0.20],
            Q25K => [0.05, 0.10, 0.30, 0.35, 0.20],
            Q25L => [0.05, 0.10, 0.30, 0.35, 0.20],
            Q25M => [0.05, 0.10, 0.30, 0.35, 0.20],
            Q25N => [0.05, 0.10, 0.30, 0.35, 0.20],
            Q25O => [0.05, 0.10, 0.30, 0.35, 0.20],
            Q25P => [0.05, 0.10, 0.30, 0.35, 0.20],
            Q25Q => [0.05, 0.10, 0.30, 0.35, 0.20],
        },
        grade_value_shift => { 1=>+1, 2=>0, 3=>0, 4=>-1, 5=>-1 },
    },

    # Aptitude: A and B students score higher
    Aptitude => {
        col_probs => {
            Aptitude_1 => [0.00, 0.00, 0.02, 0.08, 0.90],  # Verbal/Cognitive — very high
            Aptitude_2 => [0.70, 0.20, 0.06, 0.02, 0.02],  # Verbal/Spatial — low (pulls SC22 down)
            Aptitude_3 => [0.00, 0.00, 0.01, 0.06, 0.93],  # Spatial — high
            Aptitude_4 => [0.00, 0.00, 0.01, 0.06, 0.93],  # Spatial — high
            Aptitude_5 => [0.07, 0.11, 0.23, 0.38, 0.21],  # Verbal/Cognitive/Numerical — medium
            Aptitude_6 => [0.12, 0.26, 0.27, 0.23, 0.12],  # Cognitive/Numerical — medium-low
            Aptitude_7 => [0.75, 0.03, 0.01, 0.01, 0.30],  # Numerical only — very low (pulls SC25 down)
            Aptitude_8 => [0.08, 0.13, 0.25, 0.34, 0.20],  # Verbal/Cognitive/Numerical — medium
            Aptitude_9 => [0.00, 0.00, 0.01, 0.06, 0.93],  # Spatial — high
        },
        grade_value_shift => { 1=>-1, 2=>-1, 3=>0, 4=>+1, 5=>+1 },
    },


    # ----------------------------
    # LIKE/DISLIKE QUESTIONS
    # col_probs:         item_id => [like_prob, dislike_prob]  (neither = 1 - like - dislike)
    # grade_multipliers: Q5 => multiplier applied to like_prob only
    # ----------------------------

    # Q24_GROUP: Career activity like/dislike -- A students like more activities
    Q24_GROUP => {
        col_probs => {
            153 => [0.40, 0.20], 156 => [0.35, 0.25], 157 => [0.35, 0.25],
            158 => [0.38, 0.22], 159 => [0.30, 0.30], 171 => [0.35, 0.25],
            160 => [0.32, 0.28], 161 => [0.33, 0.27], 162 => [0.36, 0.24],
            163 => [0.34, 0.26], 164 => [0.37, 0.23], 165 => [0.33, 0.27],
            166 => [0.31, 0.29], 167 => [0.35, 0.25], 168 => [0.38, 0.22],
            169 => [0.36, 0.24], 172 => [0.34, 0.26], 170 => [0.32, 0.28],
        },
        grade_multipliers => { 1=>1.30, 2=>1.15, 3=>1.00, 4=>0.87, 5=>0.72 },
    },

    # Q26_GROUP: Career cluster like/dislike -- same gentle A>F gradient
    Q26_GROUP => {
        col_probs => {
             1 => [0.38, 0.22],  2 => [0.35, 0.25],  3 => [0.32, 0.28],
             4 => [0.36, 0.24],  5 => [0.34, 0.26], 18 => [0.30, 0.30],
             6 => [0.33, 0.27],  7 => [0.35, 0.25],  8 => [0.37, 0.23],
             9 => [0.34, 0.26], 10 => [0.31, 0.29], 11 => [0.35, 0.25],
            12 => [0.33, 0.27], 13 => [0.36, 0.24], 14 => [0.38, 0.22],
            15 => [0.35, 0.25], 17 => [0.32, 0.28], 16 => [0.34, 0.26],
        },
        grade_multipliers => { 1=>1.25, 2=>1.12, 3=>1.00, 4=>0.88, 5=>0.74 },
    },
);



my %multi_column_to_group;

for my $key (keys %schema) {
    my $rule = $schema{$key};
    next unless ref $rule eq 'HASH';
    my $type = $rule->{type} // '';
    if ( $type eq 'multi' || $type eq 'scale' || $type eq 'subset_multi' ) {
        for my $col (@{ $rule->{columns} // [] }) {
            $multi_column_to_group{$col} = $key;
        }
    }
    elsif ( $type eq 'like_dislike' ) {
        # Only the _0_GROUP_ columns are used as triggers; all other columns
        # produced by generate_like_dislike() are written and skipped via %filled.
        for my $id (@{ $rule->{group_ids} }) {
            $multi_column_to_group{ "$rule->{prefix_0}$id" } = $key;
        }
    }

    # subset_multi rules that output a single column instead of a columns list
    if ( $type eq 'subset_multi' && $rule->{output_col} ) {
        $multi_column_to_group{ $rule->{output_col} } = $key;
    }

}


# ----------------------------
# GENERATE DATA
# ----------------------------
my $NUM_ROWS = $ARGV[0] || 500;
# 0.76 is about the average completeness rate of the real dataset
my $PERCENT_COMPLETE = 0.76;  # overall percentage of rows that should be "complete" (i.e. no blank answers to non-conditional questions).
my $OUTPUT_FILE = $ARGV[1] || 'synthetic_survey_data.xlsx';
my @rows;


for (1 .. $NUM_ROWS) {
    my $row = generate_row(\%schema);
    calculate_scores($row);     # calculate derived fields after other row data is generated

    push @rows, $row;   # Add to @rows array for final printing to excel file
}


write_xlsx(\@HEADER, \@rows, $OUTPUT_FILE);
# That's it Chris!



# ----------------------------
# FUNCTIONS
# ----------------------------

# Generates a row based on provided schema rules.
# $schema: reference to the schema hash which defines generation rules for each column
# %row: hash to hold generated column values for this row
# %context: hash to hold intermediate values and states used during generation (e.g. conditional logic for "of your answers to question X, what are your top 3?")
# %filled: hash to track which columns have been filled in the row
sub generate_row {
    my ($schema) = @_;

    my %row;
    my %context;
    my %filled;

    # ---- PRE-GENERATE SEMESTER/YEAR (needed for date range) ----
    # year_val is 1-4 mapping to the start year of the survey 2022-2025
    # sem_val is 1 or 2, mapping to Fall (Aug-Dec) or Spring (Jan-May) semesters respectively
    # **NOTE: startdate is decided based on these semester and year values
    # ***NOTE: startdate must be generated before question cols since some should/not be filled based on when survey was taken
    my $year_val = (1..4)[ int rand 4 ];
    my $sem_val  = (1, 2)[ int rand 2 ];
    $context{year}     = $year_val;
    $context{semester} = $sem_val;

    # ---- PRE-GENERATE TIME SYSTEM FIELDS ----
    my $cal_year = 2021 + $year_val;
    my ($mo_lo, $mo_hi) = $sem_val == 1 ? (8, 12) : (1, 5);
    my $mo = $mo_lo + int rand($mo_hi - $mo_lo + 1);
    my $dy = 1 + int rand(28);
    my $hr = 8 + int rand(13);
    my $mi = int rand(60);
    my $sc = int rand(60);

    my $start = Time::Piece->strptime(
        sprintf("%04d-%02d-%02d %02d:%02d:%02d", $cal_year, $mo, $dy, $hr, $mi, $sc),
        "%Y-%m-%d %H:%M:%S"
    );

    # Generate survey duration in seconds (2 minutes to ~1.5 hours) and use duration to calculate EndDate time
    $context{Duration}     = 120 + int rand(5600);
    $context{StartDateObj} = $start;
    $context{EndDateObj}   = $start + $context{Duration};

    my $delay = (rand() < 0.7) ? 0 : int(rand(120));
    $context{RecordedDateObj} = $context{EndDateObj} + $delay;

    # For tracking progress and completion status
    my $questions_total    = 0;
    my $questions_answered = 0;

    $context{is_complete_row} = (rand() < $PERCENT_COMPLETE) ? 1 : 0;

    # True only for year=1 (2022), semester=2 (Spring) — i.e. before Sept 2022
    # accounts for Q12/Q13 questions that were changed in Sept 2022
    #     Pre Sept 2022: Q13_1-7 shown, Q12_1_2-_7_2 not shown (always blank)
    #     Post Sept 2022: Q13_1-7 not shown (always blank), Q12_1_2-Q12_7_2 shown
    my $is_pre_sept_2022 = ($year_val == 1 && $sem_val == 2) ? 1 : 0;

    # 2024 = year 3, 2 = spring semester. Aptitude questions were added after spring 2024 so if survey was taken before that all aptitude cols should be blank.
    my $is_pre_spring_2024 = $year_val < 3 || ($year_val == 3 && $sem_val == 2) ? 1 : 0;



    for my $col (@HEADER) {

        next if $filled{$col};

        # ---- GROUP-DISPATCHED COLUMN (multi, scale, or like_dislike) ----
        if (exists $multi_column_to_group{$col}) {
            my $group = $multi_column_to_group{$col};
            my $rule  = $schema->{$group};
            my $type  = $rule->{type};

            my $result;


            # Q7A should be blank if both Q6 and Q7 had only "None of the above" or were blank
            if ($group eq 'Q7A') {
                my $q6 = $context{results}{Q6} // {};
                my $q7 = $context{results}{Q7} // {};
                my $q6_active = grep { ($q6->{"Q6_$_"} // '') eq '1' } 1..7;
                my $q7_active = grep { ($q7->{"Q7_$_"} // '') eq '1' } 1..7;
                unless ($q6_active || $q7_active) {
                    $result = { map { $_ => '' } @{ $rule->{columns} } };
                    $context{results}{Q7A} = $result;
                    @row{keys %$result}    = values %$result;
                    @filled{keys %$result} = (1) x scalar keys %$result;
                    # No questions_total++ — question was never shown to this respondent
                    next;
                }
            }

            # Q13 is only shown in surveys before Sept 2022
            if ($group eq 'Q13' && !$is_pre_sept_2022) {
                $result = { map { $_ => '' } @{ $rule->{columns} } };
                @row{keys %$result}    = values %$result;
                @filled{keys %$result} = (1) x scalar keys %$result;
                # Do NOT increment questions_total — this question didn't exist for this respondent
                next;
            }

            # Q12_2 is only shown in surveys from Sept 2022 onwards
            if ($group eq 'Q12_2' && $is_pre_sept_2022) {
                $result = { map { $_ => '' } @{ $rule->{columns} } };
                @row{keys %$result}    = values %$result;
                @filled{keys %$result} = (1) x scalar keys %$result;
                 # Do NOT increment questions_total — this question didn't exist for this respondent
                next;
            }

            # Aptitude questions were added in Spring 2024
            if  ($group eq 'Aptitude' && $is_pre_spring_2024) {
                $result = { map { $_ => '' } @{ $rule->{columns} } };
                @row{keys %$result}    = values %$result;
                @filled{keys %$result} = (1) x scalar keys %$result;
                # Do NOT increment questions_total — these questions didn't exist for this respondent
                next;
            }


            if    ($type eq 'multi')        { $result = generate_multi($rule, \%context, $group)        }
            elsif ($type eq 'scale')        { $result = generate_scale($rule, \%context, $group)        }
            elsif ($type eq 'like_dislike') { $result = generate_like_dislike($rule, \%context, $group) }
            elsif ($type eq 'subset_multi') { $result = generate_subset_multi($rule, \%context)         }

            # Store result in context so dependent questions can reference it
            $context{results}{$group} = $result;

            @row{keys %$result}    = values %$result;
            @filled{keys %$result} = (1) x scalar keys %$result;


            # Count as ONE question for progress tracking
            # Dependent questions are only counted if they were actually shown
            # (i.e. their result has at least one non-blank value).
            my $answered = grep { defined $_ && $_ ne '' } values %$result;
            unless ($rule->{conditional_display} && !$answered) {
                $questions_total++;
                $questions_answered++ if $answered;
            }

            next;
        }

        # ---- DIRECT SCHEMA MATCH [single choice, text, system] (1 col = 1 outer key) ----
        if (exists $schema->{$col}) {
            my $rule = $schema->{$col};

            if ($rule->{type} eq 'single') {
                $questions_total++;

                my $val = generate_single($rule, \%context, $col);
                $row{$col} = $val;
                $context{Q5} = $val if $col eq 'Q5';   # make grade available to subsequent generators

                if (defined $val && $val ne '') {
                    $questions_answered++;
                }
            }
            elsif ($rule->{type} eq 'text') {
                # TEXT fields should only be filled if their "Other" trigger option was selected
                my $trigger = $rule->{trigger_col};
                my $trigger_val;
                $trigger_val = $row{$trigger} // '' if $trigger;
                #print "\nProcessing text field $col with trigger $trigger (value: '$trigger_val')\n";

                # For single-choice triggers (Q10, Q11), the trigger fires when value == 7
                # For binary triggers (Q3_16, Q4_16 etc.), the trigger fires when value eq '1'
                my $triggered = $trigger
                    ? ($rule->{trigger_val}
                        ? $trigger_val eq $rule->{trigger_val}
                        : $trigger_val eq '1')
                    : 0;

                $row{$col} = $triggered ? 'Sample text' : '';
            }
            elsif ($rule->{type} eq 'system') {
                $row{$col} = generate_system($col, \%context);
            }
            elsif ($rule->{type} =~ /^(derived|matrix)$/) {
                $row{$col} = '';
            }
            else {
                warn "Unknown type '$rule->{type}' for column $col\n";
                $row{$col} = '';
            }
        }
        else {
            $row{$col} = '';
        }
    }


    # ---- Progress Calc ----
    my $progress = 0;

    if ($questions_total > 0) {
        $progress = int(($questions_answered / $questions_total) * 100);
    }

    $row{Progress} = $progress;
    $row{Finished} = ($progress == 100) ? 1 : 0;

    if ($row{Finished} == 1 && $row{Progress} != 100) {
        die "You Got Problems: Finished=1 but Progress=$row{Progress}";
    }

    return \%row;
}

# helper function to determine whether to leave a question blank based on blank_prob and context (e.g. is_complete_row for entire row blanking)
sub maybe_blank {
    my ($prob, $context) = @_;
    return 0 if $context && $context->{is_complete_row};
    return rand() < $prob;
}

# Resolve the effective Bernoulli probability for a column given the conditional config and Q5.
# Priority: column_overrides{q5}{col} > col_probs{col} * grade_multipliers{q5}
sub _resolve_prob {
    my ($cond, $col, $q5) = @_;
    return $cond->{column_overrides}{$q5}{$col}
        if $q5 && exists $cond->{column_overrides}{$q5}{$col};
    my $p = $cond->{col_probs}{$col} // 0.30;
    $p *= $cond->{grade_multipliers}{$q5}
        if $q5 && exists $cond->{grade_multipliers}{$q5};
    return $p < 0.01 ? 0.01 : $p > 0.95 ? 0.95 : $p;
}

# Pick a value starting at $min_val using a weight array (one weight per possible value).
# Weights need not sum to 1 — they are treated as relative frequencies.
sub _weighted_pick {
    my ($min_val, $weights) = @_;
    my $total = 0;
    $total += $_ for @$weights;
    return $min_val unless $total > 0;
    my $r = rand() * $total;
    my $cumul = 0;
    for my $i (0 .. $#$weights) {
        $cumul += $weights->[$i];
        return $min_val + $i if $r < $cumul;
    }
    return $min_val + $#$weights;
}

# Shift a weight distribution toward higher (+) or lower (-) values by $shift steps.
# Each weight moves to an adjacent bucket; out-of-range weights accumulate at the boundary.
sub _apply_value_shift {
    my ($weights, $shift) = @_;
    return @$weights unless $shift;
    my @w   = @$weights;
    my $n   = scalar @w;
    my @new = (0) x $n;
    for my $i (0 .. $n - 1) {
        my $j = $i + $shift;
        $j = 0     if $j < 0;
        $j = $n-1  if $j >= $n;
        $new[$j] += $w[$i];
    }
    return @new;
}

# generate values for single choice questions based on provided rules and context
sub generate_single {
    my ($rule, $context, $col) = @_;
    return '' if maybe_blank($rule->{blank_prob}, $context);
    my @vals = @{ $rule->{values} };
    return '' unless @vals;

    if ($col && exists $CONDITIONAL_PROBS{$col}) {
        my $cond = $CONDITIONAL_PROBS{$col};
        my $q5   = $context->{Q5} // '';
        my @weights;

        # grade_val_probs: full per-grade conditional table (highest priority).
        # Each grade entry maps value => weight; weights are normalized automatically.
        if ($q5 && exists $cond->{grade_val_probs}{$q5}) {
            @weights = map { $cond->{grade_val_probs}{$q5}{$_} // 0 } @vals;
        }
        # val_probs: base distribution, optionally shifted by grade level.
        elsif (exists $cond->{val_probs}) {
            @weights = map { $cond->{val_probs}{$_} // 1 } @vals;
            if ($q5 && exists $cond->{grade_value_shift}{$q5}) {
                @weights = _apply_value_shift(\@weights, $cond->{grade_value_shift}{$q5});
            }
        }

        if (@weights) {
            # Weighted index pick — works for any value array, consecutive or not
            my $total = 0; $total += $_ for @weights;
            if ($total > 0) {
                my $r = rand() * $total;
                my $cumul = 0;
                for my $i (0 .. $#weights) {
                    $cumul += $weights[$i];
                    return $vals[$i] if $r < $cumul;
                }
                return $vals[-1];
            }
        }
    }

    return $vals[ int rand @vals ];
}

# generate values for multi-select questions based on provided rules and context
sub generate_multi {
    my ($rule, $context, $group) = @_;
    my %row;

    # If this row is incomplete, roll against blank_prob to skip the entire
    # question group — all columns come back empty and we return early.
    if (maybe_blank($rule->{blank_prob}, $context)) {
        $row{$_} = '' for @{ $rule->{columns} };
        return \%row;
    }

    # Grade-conditional per-column Bernoulli: if this question group has an entry in
    # %CONDITIONAL_PROBS, draw independently for each column using the configured probabilities
    # scaled by the respondent's letter grade (Q5).
    if ($group && exists $CONDITIONAL_PROBS{$group}) {
        my $cond = $CONDITIONAL_PROBS{$group};
        my $q5   = $context->{Q5} // '';
        for my $col (@{ $rule->{columns} }) {
            $row{$col} = rand() < _resolve_prob($cond, $col, $q5) ? 1 : '';
        }
        # Honour is_complete_row: ensure at least one column is selected.
        unless (grep { ($row{$_} // '') eq '1' } @{ $rule->{columns} }) {
            if ($context->{is_complete_row}) {
                my @cols = @{ $rule->{columns} };
                $row{ $cols[ int rand @cols ] } = 1;
            }
        }
        # "None of the above" mutual exclusivity: if Q?_8 is selected, clear Q?_1..7
        if ($group && ($group eq 'Q6' || $group eq 'Q7')) {
            if (($row{"${group}_8"} // '') eq '1') {
                $row{"${group}_$_"} = '' for 1..7;
            }
        }
        return \%row;
    }

    # Start with the schema's minimum selections (usually 0). For complete
    # rows, bump the floor to 1 so every group has at least one answer.
    my $min = $rule->{min_select} // 0;
    if ($context->{is_complete_row}) {
        $min = 1;
    }

    # Pick a random number of selections between $min and max_select.
    my $n_pick = $min + int rand($rule->{max_select} - $min + 1);

    # Shuffle the column list and take the first $n_pick as the selected ones.
    my @shuffled = sort { rand() <=> rand() } @{ $rule->{columns} };
    my %picked = map { $_ => 1 } @shuffled[0 .. $n_pick - 1];

    # Write 1 for selected columns and '' for unselected ones.
    for my $col (@{ $rule->{columns} }) {
        $row{$col} = $picked{$col} ? 1 : '';
    }

    # "None of the above" mutual exclusivity: if Q?_8 is selected, clear Q?_1..7
    if ($group && ($group eq 'Q6' || $group eq 'Q7')) {
        if (($row{"${group}_8"} // '') eq '1') {
            $row{"${group}_$_"} = '' for 1..7;
        }
    }

    return \%row;
}

# Handle generating multi-select questions whose eligible options depend on parent question responses.
# "Of those, select your top 3"/"Of those, you said you are good at, which ones are you best at?" style questions
sub generate_subset_multi {
    my ($rule, $context) = @_;

    # Get the parent group's results from context
    my $parent_results = $context->{results}{ $rule->{parent} } // {};

    # Build the eligible_col_pool of eligible parent columns based on the rule type
    my @eligible_col_pool;
    if ($rule->{min_score}) {
        # Q25R: eligible_col_pool is parent columns that scored >= min_score
        @eligible_col_pool = grep { ($parent_results->{$_} || 0) >= $rule->{min_score} }
                @{ $rule->{parent_cols} };
    } else {
        # Q4, Q10/Q11: eligible_col_pool is parent columns that were selected (value eq '1')
        @eligible_col_pool = grep { ($parent_results->{$_} // '') eq '1' }
                @{ $rule->{parent_cols} };
    }
    # print "\nELIGIBLE COLS: \n";
    # print Dumper(@eligible_col_pool);

    my %result;

    # If blank_if is set, check if that column was selected in parent results
    # e.g. Q9_8 "No one" — if selected, leave this question blank
    if ($rule->{blank_if} && ($parent_results->{ $rule->{blank_if} } // '') eq '1') {
        $result{ $rule->{output_col} } = '' if $rule->{output_col};
        $result{$_} = '' for @{ $rule->{columns} // [] };
        return \%result;
    }

    # If the eligible_col_pool is empty, return all blank
    unless (@eligible_col_pool) {
        $result{ $rule->{output_col} } = '' if $rule->{output_col};
        $result{$_} = '' for @{ $rule->{columns} // [] };
        return \%result;
    }

    # Shuffle and pick up to max_select from the eligible_col_pool
    my @shuffled  = sort { rand() <=> rand() } @eligible_col_pool;
    my $take      = $rule->{max_select} < scalar @shuffled
                        ? $rule->{max_select} : scalar @shuffled;
    my @chosen    = @shuffled[0 .. $take - 1];
    my %chosen    = map { $_ => 1 } @chosen;


    my $suffix_pattern = qr/([A-Z0-9]+)$/;  # pattern to extract suffix from column names - matches either numeric suffixes (e.g. Q9_3) or Q25A-Q25Q style suffixes
    if ($rule->{output_col}) {
        # Single output column (Q10, Q11): extract numeric suffix from chosen col
        # e.g. 'Q9_3' -> 3
        my ($val) = $chosen[0] =~ $suffix_pattern;
        $result{ $rule->{output_col} } = $val // '';
    } else {
        # Multi column output (Q4, Q25R): extract the numeric suffix from each
        # chosen parent column and use it to mark the corresponding output column
        # print "CHOSEN COLS: \n";
        # print Dumper(\@chosen);

        my %chosen_suffixes;

        # handle the special lil' guy Q25R whose parent suffixes are letters but output suffixes are numbers (and first parent option doesn't have a suffix at all)
        if ($rule->{map_suffix_manually}) {
            # loop through @chosen to match and grab the letter suffix
            # if letter suffix doesn't exist (Q25) map suffix to 1
            # otherwise use the ASCII values of the letter returned by ord to map A-Q to 2-18 (since Q25 corresponds to 1 and doesn't have a suffix)
            %chosen_suffixes = map {
                                /\d([A-Q])$/;
                                $1 ? ord($1)  - ord('A') + 2 : 1 => 1} @chosen;
        }
        else {  # normal suffix extraction and matching
            %chosen_suffixes = map { /$suffix_pattern/; $1 => 1 } @chosen;
        }


        for my $col (@{ $rule->{columns} }) {
            my ($suffix) = $col =~ /$suffix_pattern/m;
            $result{$col} = $chosen_suffixes{$suffix} ? 1 : '';
            # print "MATCHING OUTPUT COL: $col SUFFIX: $suffix CHOSEN? " . ($chosen_suffixes{$suffix} ? "YES" : "NO") . "\n";
        }
    }

    return \%result;
}


# generate scale questions by randomly picking a value between min and max for each column, with optional blanking of the entire group based on blank_prob
sub generate_scale {
    my ($rule, $context, $group) = @_;
    my %answers;

    # accounts for chance that respondent skipped question entirely
    if (maybe_blank($rule->{blank_prob}, $context)) {
        $answers{$_} = '' for @{ $rule->{columns} };
        return \%answers;
    }

    # Grade-conditional weighted distribution: if this scale group has an entry in
    # %CONDITIONAL_PROBS, use per-column weight arrays optionally shifted by Q5 grade.
    if ($group && exists $CONDITIONAL_PROBS{$group}) {
        my $cond  = $CONDITIONAL_PROBS{$group};
        my $q5    = $context->{Q5} // '';
        my $shift = ($q5 && exists $cond->{grade_value_shift}{$q5})
                        ? $cond->{grade_value_shift}{$q5} : 0;
        for my $col (@{ $rule->{columns} }) {
            my $base = $cond->{col_probs}{$col}
                // [(1) x ($rule->{max} - $rule->{min} + 1)];
            my @weights = $shift ? _apply_value_shift($base, $shift) : @$base;
            $answers{$col} = _weighted_pick($rule->{min}, \@weights);
        }
        return \%answers;
    }

    for my $col (@{ $rule->{columns} }) {
        $answers{$col} = $rule->{min} + int rand($rule->{max} - $rule->{min} + 1);
    }
    return \%answers;
}


# generate like/dislike groups by iterating through each item and randomly assigning
# like (1 in prefix_0 column),
# dislike (1 in prefix_1 column),
# or neither (blank in both columns) based on specified probabilities.
# Then shuffle list of likes and pick top 3 for "pick your top 3" follow up questions
sub generate_like_dislike {
    my ($rule, $context, $group) = @_;

    my @ids = @{ $rule->{group_ids} };
    my $n   = scalar @ids;
    my %result;

    my (@like, @dislike);

    for my $i (0 .. $#ids) {
        my $like_p    = 0.40;
        my $dislike_p = 0.30;

        # Grade-conditional probabilities: if this group has an entry in %CONDITIONAL_PROBS,
        # look up per-item base probs and apply the grade multiplier (Q5) to like_prob.
        if ($group && exists $CONDITIONAL_PROBS{$group}) {
            my $cond = $CONDITIONAL_PROBS{$group};
            my $id   = $ids[$i];
            my $q5   = $context->{Q5} // '';

            if (exists $cond->{col_probs}{$id}) {
                ($like_p, $dislike_p) = @{ $cond->{col_probs}{$id} };
            }
            if ($q5 && exists $cond->{column_overrides}{$q5}{$id}) {
                $like_p = $cond->{column_overrides}{$q5}{$id};
            } elsif ($q5 && exists $cond->{grade_multipliers}{$q5}) {
                $like_p *= $cond->{grade_multipliers}{$q5};
                $like_p  = 0.95 if $like_p > 0.95;
            }
            # Prevent like + dislike from exceeding 1.0
            if ($like_p + $dislike_p > 0.99) {
                my $scale = 0.99 / ($like_p + $dislike_p);
                $like_p    *= $scale;
                $dislike_p *= $scale;
            }
        }

        my $r = rand();
        if    ($r < $like_p)               { push @like, 1;  push @dislike, ''  }
        elsif ($r < $like_p + $dislike_p)  { push @like, ''; push @dislike, 1   }
        else                               { push @like, ''; push @dislike, ''   }
    }

    for my $i (0 .. $#ids) {
        $result{ "$rule->{prefix_0}$ids[$i]" } = $like[$i];
        $result{ "$rule->{prefix_1}$ids[$i]" } = $dislike[$i];
    }

    # Ranks for Q26: assign unique ranks to liked and disliked items separately
    if ($rule->{ranked}) {
        my @like_pos    = grep { $like[$_]    eq '1' } 0 .. $#like;
        my @dislike_pos = grep { $dislike[$_] eq '1' } 0 .. $#dislike;

        my @like_ranks    = sort { rand() <=> rand() } 1 .. scalar @like_pos;
        my @dislike_ranks = sort { rand() <=> rand() } 1 .. scalar @dislike_pos;

        # Default all rank columns to blank
        for my $id (@ids) {
            $result{ "$rule->{rank_prefix_0}${id}_RANK" } = '';
            $result{ "$rule->{rank_prefix_1}${id}_RANK" } = '';
        }
        for my $i (0 .. $#like_pos) {
            $result{ "$rule->{rank_prefix_0}$ids[$like_pos[$i]]_RANK" } = $like_ranks[$i];
        }
        for my $i (0 .. $#dislike_pos) {
            $result{ "$rule->{rank_prefix_1}$ids[$dislike_pos[$i]]_RANK" } = $dislike_ranks[$i];
        }
    }

    # Top-3 follow-up: randomly pick up to 3 of the liked items
    my @liked_pos = grep { $like[$_] eq '1' } 0 .. $#like;
    my @shuffled  = sort { rand() <=> rand() } @liked_pos;
    my $take      = @shuffled < 3 ? scalar @shuffled : 3;
    my %top3      = map { $_ => 1 } @shuffled[0 .. $take - 1];

    for my $i (0 .. $#ids) {
        $result{ "$rule->{topn_prefix}" . ($i + 1) } = $top3{$i} ? 1 : '';
    }

    return \%result;
}


# Generate system fields - constraints like user language 'EN', distribution channel 'anonymous' are based on actual data being emulated
sub generate_system {
    my ($col, $context) = @_;

    if ($col eq 'StartDate') {
        return $context->{StartDateObj}->strftime("%m/%d/%Y %H:%M:%S");
    }
    elsif ($col eq 'Duration__in_seconds_') {
        return $context->{Duration};
    }
    elsif ($col eq 'EndDate') {
        return $context->{EndDateObj}->strftime("%m/%d/%Y %H:%M:%S");
    }
    elsif ($col eq 'RecordedDate') {
        return $context->{RecordedDateObj}->strftime("%m/%d/%Y %H:%M:%S");
    }
    elsif ($col eq 'Finished') {
        return 1;
    }
    elsif ($col eq 'Progress') {
        return 100;
    }
    elsif ($col eq 'Status') {
        return 0;
    }
    elsif ($col eq 'ResponseId') {
        my @chars = ('A'..'Z', 'a'..'z', 0..9);
        return 'R_' . join '', map { $chars[rand @chars] } 1..15;
    }
    elsif ($col eq 'DistributionChannel') {
        return 'anonymous';
    }
    elsif ($col eq 'UserLanguage') {
        return 'EN';
    }
    elsif ($col eq 'Year') {
        return $context->{year};
    }
    if ($col eq 'Semester') {
        return $context->{semester};
    }

    return '';
}


# calculate derived fields based on previously generated data for the row.
# Calculations are NOT going for accuracy - just meant to reflect the general patterns of the real data
sub calculate_scores {
    my ($row) = @_;

    for my $i (0 .. $#CLUSTER_INPUTS) {
        my $inputs = $CLUSTER_INPUTS[$i];
        my $points = 0;

        # Q8: direct interest in this cluster
        $points++ if ($row->{ $inputs->{q8} } // '') eq '1';

        # Q24A, Q25R, Q26A: each selected option mapping to this cluster = 1 point
        for my $col (@{ $inputs->{q24a} }) {
            $points++ if ($row->{$col} // '') eq '1';
        }
        for my $col (@{ $inputs->{q25r} }) {
            $points++ if ($row->{$col} // '') eq '1';
        }
        for my $col (@{ $inputs->{q26a} }) {
            $points++ if ($row->{$col} // '') eq '1';
        }

        # Convert raw points to 0-5 score using the scale
        my $score = 5;
        for my $tier (@SCORE_SCALE) {
            if ($points <= $tier->[0]) {
                $score = $tier->[1];
                last;
            }
        }

        # SC scores are formatted as X.00, Career scores are plain integers
        my $sc_col      = 'SC' . $i;
        my $career_col  = 'Career_' . ($i + 1) . '_Score';
        $row->{$sc_col}     = sprintf("%.2f", $score);
        $row->{$career_col} = $score;
    }

    # AwarenessScore: count of Q6 options selected excluding Q6_8 "None of the above"
    my $awareness = scalar grep { ($row->{"Q6_$_"} // '') eq '1' } 1..7;

    # ExplorationScore: count of Q7 options selected excluding Q7_8 "None of the above"
    my $exploration = scalar grep { ($row->{"Q7_$_"} // '') eq '1' } 1..7;

    $row->{AwarenessScore}   = $awareness;
    $row->{ExplorationScore} = $exploration;
    $row->{CareerPrepScore}  = $awareness + $exploration;

    # Career_Awareness and Career_Exploration mirror the above but are blank
    # for surveys taken before Sept 2022
    my $pre = ($row->{Year} == 1 && $row->{Semester} == 2) ? 1 : 0;
    $row->{Career_Awareness}   = $pre ? '' : $awareness;
    $row->{Career_Exploration} = $pre ? '' : $exploration;

    # Aptitude scores: average of the 4 contributing aptitude question scores for each aptitude type, rounded to nearest whole number
    # SC22-25: normalize sum to 1-20 scale
    # Formula: (sum - min) / (max - min) * 20, rounded to nearest whole, min 1
    for my $sc (qw(SC22 SC23 SC24 SC25)) {
        my $sum = 0;

        for my $col (@{ $APTITUDE_GROUPS{$sc} }) {
            # check if aptitude question was answered (not blank) before adding to sum
            if (defined $row->{$col} && $row->{$col} ne '') {
                $sum += $row->{$col};
            }
        }

        my $normalized = int(
            ($sum - $APTITUDE_MIN) / ($APTITUDE_MAX - $APTITUDE_MIN) * 20 + 0.5
        );
        $normalized = 1 if $normalized < 1;

        # format as X.00
        $row->{$sc} = sprintf("%.2f", $normalized);
    }
}


# Write generated rows to XLSX Excel file
sub write_xlsx {
    my ($header, $rows, $outfile) = @_;

    my $wb  = Excel::Writer::XLSX->new($outfile)
        or die "Cannot create '$outfile': $!\n";
    my $ws  = $wb->add_worksheet('Survey Data');
    my $fmt = $wb->add_format(bold => 1);

    $ws->write(0, $_, $header->[$_], $fmt) for 0 .. $#$header;

    my %col_idx;
    $col_idx{ $header->[$_] } = $_ for 0 .. $#$header;

    for my $r (0 .. $#$rows) {
        for my $col (@$header) {
            my $val = $rows->[$r]{$col} // '';
            $ws->write($r + 1, $col_idx{$col}, $val);
        }
    }

    $wb->close();
    printf "Done - wrote %s rows to '%s'\n", scalar @$rows, $outfile;
}