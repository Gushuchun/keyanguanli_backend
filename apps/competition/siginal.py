from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import CompetitionMemberConfirm, Competition
from apps.team.models import Team


@receiver(post_save, sender=CompetitionMemberConfirm)
def update_competition_status(sender, instance, **kwargs):
    """
    使用select_for_update解决竞态条件问题
    """
    with transaction.atomic():
        competition = Competition.objects.get(sn=instance.sn)

        if competition.status != 'confirmed':
            unconfirmed_exists = CompetitionMemberConfirm.objects.filter(
                sn=competition.sn,
                status='pending',
                is_cap=False
            ).exists()

            unconfirmed_exists_1 = CompetitionMemberConfirm.objects.filter(
                sn=competition.sn,
                is_cap=False,
                state=1
            ).exists()

            if not unconfirmed_exists_1 :
                return

            if not unconfirmed_exists:
                competition.status = 'confirmed'
                competition.save()
                team = Team.objects.get(sn=competition.team_id)
                team.race_num += 1
                if competition.score != '无':
                    team.prize_num += 1
                team.save()
