from django.db import models
from core.models import School

# Create your models here.
class Dataset(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date_added = models.DateField(auto_now_add=True)
    row_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name

# model for survey questions
class Question(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('binary', 'Binary'),
        ('single_choice', 'Single Choice'),
        ('free_text', 'Free Text'),
        ('scale', 'Scale'),
        ('rank', 'Rank'),
    ]

    label = models.TextField(blank=True)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES)
    can_crosstab = models.BooleanField(default=False)
    crosstab_label = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.label


# model for survey question options
class Option(models.Model):
    numeric_value = models.FloatField(null=True, blank=True)
    display_text = models.TextField()
    category = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        unique_together = ('category', 'numeric_value')

    def __str__(self):
        return self.display_text



# maps dataset column headers to questions and options in the db
# option is nullable for single choice questions since numeric value decides how it maps to the options
class QuestionColumn(models.Model):
    column_header = models.CharField(max_length=100, unique=True)
    question = models.ForeignKey(
        Question,
        on_delete=models.PROTECT,
        related_name='column_mappings'
    )
    option = models.ForeignKey(
        Option,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='column_mappings'
    )
    option_category = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.column_header



# model for survey responses - each response = 1 row in the dataset
# includes metadata fields and computed score fields
# connected to RespondentAnswer model which stores the actual answers to each question by response_id
class Response(models.Model):
    dataset = models.ForeignKey(
        Dataset,
        on_delete=models.CASCADE,
        related_name='responses'
    )

    school = models.ForeignKey(
        School,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='responses'
    )

    # Metadata fields
    response_id = models.CharField(max_length=100, unique=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    recorded_date = models.DateTimeField(null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    semester = models.CharField(max_length=20, blank=True)
    status = models.IntegerField(null=True, blank=True)
    progress = models.IntegerField(null=True, blank=True)
    duration_in_seconds = models.IntegerField(null=True, blank=True)
    finished = models.IntegerField(null=True, blank=True)
    distribution_channel = models.CharField(max_length=100, blank=True)
    user_language = models.CharField(max_length=10, blank=True)

    # Computed score fields
    # Career cluster scores
    score_agriculture = models.IntegerField(null=True, blank=True)
    score_architecture = models.IntegerField(null=True, blank=True)
    score_arts_av_comm = models.IntegerField(null=True, blank=True)
    score_business_mgmt = models.IntegerField(null=True, blank=True)
    score_education = models.IntegerField(null=True, blank=True)
    score_energy = models.IntegerField(null=True, blank=True)
    score_finance = models.IntegerField(null=True, blank=True)
    score_government = models.IntegerField(null=True, blank=True)
    score_health_sciences = models.IntegerField(null=True, blank=True)
    score_hospitality = models.IntegerField(null=True, blank=True)
    score_human_services = models.IntegerField(null=True, blank=True)
    score_information_tech = models.IntegerField(null=True, blank=True)
    score_law_public_safety = models.IntegerField(null=True, blank=True)
    score_manufacturing = models.IntegerField(null=True, blank=True)
    score_marketing = models.IntegerField(null=True, blank=True)
    score_stem = models.IntegerField(null=True, blank=True)
    score_telecommunications = models.IntegerField(null=True, blank=True)
    score_transportation = models.IntegerField(null=True, blank=True)

    # Aptitude scores
    score_verbal_aptitude = models.IntegerField(null=True, blank=True)
    score_spatial_aptitude = models.IntegerField(null=True, blank=True)
    score_cognitive_aptitude = models.IntegerField(null=True, blank=True)
    score_numerical_aptitude = models.IntegerField(null=True, blank=True)

    # Career composite scores
    career_score_agriculture = models.IntegerField(null=True, blank=True)
    career_score_architecture = models.IntegerField(null=True, blank=True)
    career_score_arts_av_comm = models.IntegerField(null=True, blank=True)
    career_score_business_mgmt = models.IntegerField(null=True, blank=True)
    career_score_education = models.IntegerField(null=True, blank=True)
    career_score_energy = models.IntegerField(null=True, blank=True)
    career_score_finance = models.IntegerField(null=True, blank=True)
    career_score_government = models.IntegerField(null=True, blank=True)
    career_score_health_sciences = models.IntegerField(null=True, blank=True)
    career_score_hospitality = models.IntegerField(null=True, blank=True)
    career_score_human_services = models.IntegerField(null=True, blank=True)
    career_score_information_tech = models.IntegerField(null=True, blank=True)
    career_score_law_public_safety = models.IntegerField(null=True, blank=True)
    career_score_manufacturing = models.IntegerField(null=True, blank=True)
    career_score_marketing = models.IntegerField(null=True, blank=True)
    career_score_stem = models.IntegerField(null=True, blank=True)
    career_score_telecommunications = models.IntegerField(null=True, blank=True)
    career_score_transportation = models.IntegerField(null=True, blank=True)

    # Overall scores
    awareness_score = models.FloatField(null=True, blank=True)      # Raw score: 1pt per awareness question marked "yes"
    exploration_score = models.FloatField(null=True, blank=True)    # Raw score: 1pt per exploration question marked "yes"
    career_prep_score = models.FloatField(null=True, blank=True)    # Raw score: sum of awareness + exploration scores

    particip_career_prep_awareness   = models.BooleanField(null=True, blank=True)  # whether they participated in any awareness activities
    particip_career_prep_exploration = models.BooleanField(null=True, blank=True)  # whether they participated in any exploration activities
    particip_career_prep_either      = models.BooleanField(null=True, blank=True)  # whether they participated in either awareness or exploration activities


    def __str__(self):
        return self.response_id



class RespondentAnswer(models.Model):

    # If a response is deleted, all associated answers should also be deleted.
    # Protect question and option deletions so that responses remain intact and questions/options can't be deleted if they have associated answers
    response = models.ForeignKey(
        Response,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    question_column = models.ForeignKey(
        QuestionColumn,
        on_delete=models.PROTECT,
        related_name='answers'
    )
    option = models.ForeignKey(
        Option,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='answers'
    )
    # store free text answers here - only applicable for free text questions, otherwise null
    text_value = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.response.response_id} - {self.question_column.column_header}'