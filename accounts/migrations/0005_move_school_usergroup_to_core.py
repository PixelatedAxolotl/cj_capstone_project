import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Removes School and User_Group from the accounts migration state now that
    they live in core. updates the User.school FK to reference core.School.
    tables were renamed by core.0001_initial.
    """

    dependencies = [
        ('accounts', '0004_make_school_survey_index_unique'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterField(
                    model_name='user',
                    name='school',
                    field=models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='administrators',
                        to='core.school',
                    ),
                ),
                migrations.DeleteModel(name='School'),
                migrations.DeleteModel(name='User_Group'),
            ],
        ),
    ]
