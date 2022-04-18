from django.contrib import admin
from django.contrib.admin import SimpleListFilter

from common.models.admin.utils import admin_link


class BaseAdmin(admin.ModelAdmin):
    readonly = False

    def has_add_permission(self, request):
        return super().has_add_permission(request) if not self.readonly else False

    def has_delete_permission(self, request, obj=None):
        return super().has_delete_permission(request) if not self.readonly else False

    def has_change_permission(self, request, obj=None):
        return super().has_change_permission(request, obj) if not self.readonly else False


def AdminLinkMixin(key, name):
    @admin_link(key, name)
    def _inner_func(self, obj):
        return obj

    new_class = type(key.title() + 'Link', (object,), {})
    setattr(new_class, '_' + key, _inner_func)
    return new_class


class SpentTimeFilter(SimpleListFilter):
    title = 'spent'
    parameter_name = 'spent'

    milli_secs = [0, 100, 200, 500, 1000, 2000]

    def lookups(self, request, model_admin):
        choices = []
        for index, ms in enumerate(self.milli_secs):
            if index < len(self.milli_secs) - 1:
                choices.append(
                    (
                        '{}-{}'.format(ms, self.milli_secs[index + 1]),
                        '{}ms < x < {}ms'.format(ms, self.milli_secs[index + 1])
                    )
                )
            else:
                choices.append((str(self.milli_secs[-1]), '> {}ms'.format(self.milli_secs[-1])))
        return choices

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        values = self.value().split('-')
        if len(values) == 1:
            return queryset.filter(spent__gte=int(values[0]))
        else:
            return queryset.filter(spent__gte=int(values[0]), spent__lte=int(values[1]))
