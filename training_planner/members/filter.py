from django.utils.translation import gettext_lazy as _
import django_filters


class UserFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(
        label=_('First name'),
        lookup_expr='icontains',
    )
    last_name = django_filters.CharFilter(
        label=_('Last name'),
        lookup_expr='icontains',
    )
    username = django_filters.CharFilter(
        label=_('Username'),
        lookup_expr='icontains',
    )
    email = django_filters.CharFilter(
        label=_('E-mail'),
        lookup_expr='icontains',
    )


class UserStatisticsFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(
        label=_('First name'),
        lookup_expr='icontains',
    )
    last_name = django_filters.CharFilter(
        label=_('Last name'),
        lookup_expr='icontains',
    )
