from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.


class Training(models.Model):
    title = models.CharField(max_length=200)
    start = models.DateTimeField()
    duration = models.IntegerField(validators=[MinValueValidator(1),
                                               MaxValueValidator(240)])

    def __str__(self):
        starttime = self.start.strftime('%a') + self.start.strftime('%H%M')
        return f"{starttime}: {self.title}"
