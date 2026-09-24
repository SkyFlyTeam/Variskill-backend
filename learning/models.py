import uuid

from django.db import models


class Module(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Content(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    explanatory_text = models.TextField()
    estimated_minutes = models.PositiveIntegerField()
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Activity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module = models.ForeignKey(Module, related_name='activities', on_delete=models.CASCADE)
    content = models.ForeignKey(Content, related_name='activities', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    evaluation_context = models.CharField(max_length=64)
    xp_reward = models.PositiveIntegerField(default=0)
    order = models.PositiveIntegerField()
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    activity = models.ForeignKey(Activity, related_name='questions', on_delete=models.CASCADE)
    exercise_type = models.CharField(max_length=64)
    statement = models.TextField()
    code_snippet = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField()
    expected_answer = models.TextField(blank=True, default='')
    explanation = models.TextField(blank=True, default='')
    conceptual_hint = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.statement[:50]


class Option(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.text
