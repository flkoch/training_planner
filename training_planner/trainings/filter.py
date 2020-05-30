from django.forms.widgets import CheckboxSelectMultiple
from django.utils.translation import gettext_lazy as _
import django_filters
from members.models import trainer
from .models import TargetGroup, Training


class TrainingFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(
        label=_('Title'),
        lookup_expr='icontains',
    )
    main_instructor = django_filters.ModelMultipleChoiceFilter(
        label=_('Main Instructor'),
        queryset=trainer(),
    )
    target_group = django_filters.ModelMultipleChoiceFilter(
        queryset=TargetGroup.objects.all(), label=_('Target Group'),
        widget=CheckboxSelectMultiple(
            attrs={'class': 'list-group list-group-horizontal'},
        ),
    )


class TrainingAdminFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(
        label=_('Title'),
        lookup_expr='icontains',
    )
    start = django_filters.DateFromToRangeFilter(
        label=_("Date"),
    )
    main_instructor = django_filters.ModelMultipleChoiceFilter(
        label=_('Main Instructor'),
        queryset=trainer(),
    )
    target_group = django_filters.ModelMultipleChoiceFilter(
        queryset=TargetGroup.objects.all(), label=_('Target Group'),
        widget=CheckboxSelectMultiple(
            attrs={'class': 'list-group list-group-horizontal'},
        ),
    )

    class Meta:
        model = Training
        exclude = [
            'coordinator',
            'registered_participants',
            'participants',
            'registration_open',
            'registration_close',
        ]
