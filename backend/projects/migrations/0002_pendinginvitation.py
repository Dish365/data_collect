# Generated by Django 5.2.4 on 2025-07-26 16:31

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="PendingInvitation",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        help_text="Email of the person being invited", max_length=254
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("member", "Member"),
                            ("analyst", "Analyst"),
                            ("collaborator", "Collaborator"),
                            ("viewer", "Viewer"),
                        ],
                        default="member",
                        max_length=20,
                    ),
                ),
                (
                    "permissions",
                    models.TextField(
                        default="view_project,view_responses",
                        help_text="Comma-separated list of permissions",
                    ),
                ),
                (
                    "invitation_token",
                    models.CharField(
                        help_text="Unique token for invitation link",
                        max_length=100,
                        unique=True,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("accepted", "Accepted"),
                            ("expired", "Expired"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "expires_at",
                    models.DateTimeField(help_text="When invitation expires"),
                ),
                ("accepted_at", models.DateTimeField(blank=True, null=True)),
                (
                    "invited_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sent_pending_invitations",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="pending_invitations",
                        to="projects.project",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="received_pending_invitations",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(
                        fields=["email", "status"], name="projects_pe_email_2feb3d_idx"
                    ),
                    models.Index(
                        fields=["invitation_token"],
                        name="projects_pe_invitat_a2d8a8_idx",
                    ),
                    models.Index(
                        fields=["status", "expires_at"],
                        name="projects_pe_status_f7b4fd_idx",
                    ),
                ],
                "unique_together": {("project", "email")},
            },
        ),
    ]
