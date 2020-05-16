from django.utils.translation import gettext_lazy as _
import django_filters


class UserFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(
        label=_('Vorname'),
        lookup_expr='icontains',
    )
    last_name = django_filters.CharFilter(
        label=_('Nachname'),
        lookup_expr='icontains',
    )
    username = django_filters.CharFilter(
        label=_('Benutzername'),
        lookup_expr='icontains',
    )
    email = django_filters.CharFilter(
        label=_('E-Mail'),
        lookup_expr='icontains',
    )


class UserStatisticsFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(
        label=_('Vorname'),
        lookup_expr='icontains',
    )
    last_name = django_filters.CharFilter(
        label=_('Nachname'),
        lookup_expr='icontains',
    )
