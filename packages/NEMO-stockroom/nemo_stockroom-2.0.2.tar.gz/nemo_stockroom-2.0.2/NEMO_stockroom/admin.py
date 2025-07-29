from django.contrib import admin
from django.utils.safestring import mark_safe

from NEMO_stockroom.models import ConsumableRequest, ConsumableDetails, QuantityModification


@admin.register(ConsumableRequest)
class ConsumableRequestAdmin(admin.ModelAdmin):
    list_display = ("customer", "consumable", "quantity", "project", "date")


@admin.register(QuantityModification)
class QuantityModificationAdmin(admin.ModelAdmin):
    list_display = ("consumable", "old_qty", "new_qty", "modifier")


@admin.register(ConsumableDetails)
class ConsumableDetailsAdmin(admin.ModelAdmin):
    list_display = ("consumable", "get_image", "has_warning_message")

    @admin.display(boolean=True, description="Has warning message")
    def has_warning_message(self, obj: ConsumableDetails):
        return bool(obj.warning_message)

    @admin.display(description="Image", ordering="image")
    def get_image(self, obj: ConsumableDetails):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" height="75px" />')
        return None
