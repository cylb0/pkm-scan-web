from django.contrib import admin
from nested_admin import NestedModelAdmin, NestedTabularInline, NestedStackedInline
from ..models import (
    CardVariant,
    Card,
    CardPrinting,
    LocalizedCard,
    LocalizedAttack,
    AttackCost,
    Attack,
    LocalizedAbility,
    Ability,
)
from aws_shared.languages import SupportedLanguage


class LocalizedAttackInline(NestedTabularInline):
    model = LocalizedAttack
    extra = 1


class AttackCostInline(NestedTabularInline):
    model = AttackCost
    extra = 1


class AttackInline(NestedTabularInline):
    model = Attack
    extra = 1
    inlines = [AttackCostInline, LocalizedAttackInline]


class LocalizedAbilityInline(NestedTabularInline):
    model = LocalizedAbility
    extra = 1


class AbilityInline(NestedStackedInline):
    model = Ability
    extra = 1
    inlines = [LocalizedAbilityInline]
    readonly_fields = ("id",)
    fields = ("id",)


class LocalizedCardInline(NestedTabularInline):
    model = LocalizedCard
    extra = 1
    fields = ("language", "name", "number", "total_cards_override", "description")
    verbose_name = "Translation and Numbering"
    verbose_name_plural = "Translations and Numberings"


class CardPrintingInline(NestedTabularInline):
    model = CardPrinting
    extra = 1
    inlines = [LocalizedCardInline]
    fields = ("variant", "rarity", "master_image")
    verbose_name = "Printing variation"
    verbose_name_plural = "Printing variations"


@admin.register(Card)
class CardAdmin(NestedModelAdmin):
    list_display = ("get_name", "expansion", "supertype", "subtype", "hp")
    list_filter = ("expansion", "supertype", "subtype", "types")
    search_fields = ("localizations__name", "expansion__code", "slug")

    inlines = [AbilityInline, AttackInline, CardPrintingInline]

    def get_name(self, instance):
        loc = instance.localizations.filter(language=SupportedLanguage.EN).first()
        name = loc.name if loc else "No default english name"
        return name

    get_name.short_description = "Name (EN)"

    fieldsets = (
        (
            "General information",
            {
                "fields": (
                    "expansion",
                    "slug",
                    "supertype",
                    "subtype",
                    "hp",
                    "retreat_cost",
                )
            },
        ),
        ("Types and energy", {"fields": ("types",)}),
        (
            "Weakness & Resistance",
            {
                "fields": (
                    ("weak_type", "weak_value"),
                    ("resist_type", "resist_value"),
                )
            },
        ),
    )


@admin.register(CardVariant)
class CardVariantAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
