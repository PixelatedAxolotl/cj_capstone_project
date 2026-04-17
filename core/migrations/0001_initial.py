from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Moves School and User_Group from the accounts app to core.

    DB operations: renames the three existing accounts_* tables to core_*.
    State operations: registers the models under core so Django's ORM points
    at the new table names going forward.
    """

    initial = True

    dependencies = [
        ('accounts', '0004_make_school_survey_index_unique'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL('ALTER TABLE accounts_user_group RENAME TO core_user_group'),
                migrations.RunSQL('ALTER TABLE accounts_school RENAME TO core_school'),
                migrations.RunSQL('ALTER TABLE accounts_school_groups RENAME TO core_school_groups'),
            ],
            state_operations=[
                migrations.CreateModel(
                    name='User_Group',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('name', models.CharField(max_length=255, unique=True)),
                        ('date_added', models.DateField(auto_now_add=True)),
                        ('notes', models.TextField(blank=True)),
                        ('group_type', models.CharField(
                            choices=[('region', 'Region'), ('demographic', 'Demographic Group')],
                            max_length=20,
                        )),
                    ],
                ),
                migrations.CreateModel(
                    name='School',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('name', models.CharField(max_length=255, unique=True)),
                        ('date_added', models.DateField(auto_now_add=True)),
                        ('notes', models.TextField(blank=True)),
                        ('groups', models.ManyToManyField(blank=True, related_name='schools', to='core.User_Group')),
                        ('survey_index', models.IntegerField(blank=True, null=True, unique=True)),
                    ],
                ),
            ],
        ),
    ]
