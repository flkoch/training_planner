import django_filters
from django.forms.widgets import CheckboxSelectMultiple
from members.models import trainer
from .models import TargetGroup


class TrainingFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(
        label="Bezeichnung", lookup_expr="icontains")
    main_instructor = django_filters.ModelChoiceFilter(
        queryset=trainer())
    # start = django_filters.DateFromToRangeFilter(label="Datum")
    target_group = django_filters.ModelMultipleChoiceFilter(
        queryset=TargetGroup.objects.all(), label="Zielgruppe",
        widget=CheckboxSelectMultiple(
            attrs={'class': 'list-group list-group-horizontal'})
    )
