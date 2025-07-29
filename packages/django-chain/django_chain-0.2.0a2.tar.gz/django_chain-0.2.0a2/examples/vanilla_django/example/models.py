"""
Test models for integration testing.
"""

import uuid

from django.db import models


class Joke(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    setup = models.CharField(
        max_length=255, null=False, blank=False, help_text="Question to setup joke"
    )
    punchline = models.CharField(
        max_length=255, null=False, blank=False, help_text="Answer to resolve the joke"
    )


class TestChain(models.Model):
    """Test model for chain operations."""

    name = models.CharField(max_length=100)
    chain = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name


class TestSession(models.Model):
    """Test model for session operations."""

    name = models.CharField(max_length=100)
    session = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name
