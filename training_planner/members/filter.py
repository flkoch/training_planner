import django_filters


class UserFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(
        label='Vorname', lookup_expr='icontains')
    last_name = django_filters.CharFilter(
        label='Nachname', lookup_expr='icontains')
    username = django_filters.CharFilter(
        label='Benutzername', lookup_expr='icontains')
    email = django_filters.CharFilter(
        label='E-Mail', lookup_expr='icontains')
