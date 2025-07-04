# Generated by Django 5.2.3 on 2025-06-26 21:04

from django.db import migrations
import uuid


def create_respondents_from_existing_responses(apps, schema_editor):
    """Create Respondent records from existing Response data"""
    Response = apps.get_model('responses', 'Response')
    Respondent = apps.get_model('responses', 'Respondent')
    
    # Get all unique respondent_id values from existing responses
    unique_respondent_ids = Response.objects.values_list('legacy_respondent_id', 'project').distinct()
    
    created_respondents = {}
    
    for legacy_id, project_id in unique_respondent_ids:
        if legacy_id and project_id:  # Skip null values
            # Create a new Respondent record
            respondent = Respondent.objects.create(
                respondent_id=legacy_id,
                project_id=project_id,
                is_anonymous=True,
                consent_given=True,  # Assume consent since they already responded
            )
            created_respondents[(legacy_id, project_id)] = respondent
            
    # Update Response records to link to the new Respondent records
    for response in Response.objects.all():
        if response.legacy_respondent_id and response.project_id:
            key = (response.legacy_respondent_id, response.project_id)
            if key in created_respondents:
                response.respondent = created_respondents[key]
                response.save(update_fields=['respondent'])


def reverse_respondent_migration(apps, schema_editor):
    """Reverse the respondent migration"""
    Response = apps.get_model('responses', 'Response')
    Respondent = apps.get_model('responses', 'Respondent')
    
    # Copy respondent_id back to legacy_respondent_id
    for response in Response.objects.all():
        if response.respondent:
            response.legacy_respondent_id = response.respondent.respondent_id
            response.save(update_fields=['legacy_respondent_id'])
    
    # Delete all Respondent records
    Respondent.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("responses", "0002_respondent_and_more"),
    ]

    operations = [
        migrations.RunPython(
            create_respondents_from_existing_responses,
            reverse_respondent_migration
        ),
    ]
