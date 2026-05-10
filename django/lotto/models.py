from django.db import models
from django.contrib.auth.models import User


class Draw(models.Model):
    round = models.IntegerField(unique=True)
    numbers = models.CharField(max_length=50, blank=True)
    bonus = models.IntegerField(null=True, blank=True)
    drawn_at = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-round']

    def __str__(self):
        return f"{self.round}회차"

    def get_numbers_list(self):
        if self.numbers:
            return [int(n) for n in self.numbers.split(',')]
        return []


class Ticket(models.Model):
    MODE_CHOICES = [
        ('manual', '수동'),
        ('auto', '자동'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    draw = models.ForeignKey(Draw, on_delete=models.CASCADE, related_name='tickets')
    numbers = models.CharField(max_length=50)
    mode = models.CharField(max_length=10, choices=MODE_CHOICES)
    purchased_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.draw.round}회차 [{self.mode}]"

    def get_numbers_list(self):
        return [int(n) for n in self.numbers.split(',')]


class WinResult(models.Model):
    draw = models.ForeignKey(Draw, on_delete=models.CASCADE, related_name='results')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='results')
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE, related_name='result')
    rank = models.IntegerField()
    confirmed_at = models.DateTimeField(auto_now_add=True)

    RANK_PRIZE = {
        1: '1등 (전액)',
        2: '2등',
        3: '3등 (1,500,000원)',
        4: '4등 (50,000원)',
        5: '5등 (5,000원)',
        0: '낙첨',
    }

    def get_rank_display_custom(self):
        return self.RANK_PRIZE.get(self.rank, '낙첨')

    def __str__(self):
        return f"{self.user.username} - {self.rank}등"
    