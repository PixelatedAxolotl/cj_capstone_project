import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Updates the Response.school FK reference in Django's migration state from
    accounts.School to core.School. underlying table was renamed by core.0001_initial.
    """

    dependencies = [
        ('core', '0001_initial'),
        ('datasets', '0010_career_prep_fields_fixes'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterField(
                    model_name='response',
                    name='school',
                    field=models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='responses',
                        to='core.school',
                    ),
                ),
            ],
        ),
    ]
