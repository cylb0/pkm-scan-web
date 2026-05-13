from django.db import models
from django.utils.text import slugify
from .expansion import Expansion
from .energy_type import EnergyType
from aws_shared.languages import SupportedLanguage


class CardVariant(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.CharField(max_length=50, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Card(models.Model):
    class SuperType(models.TextChoices):
        POKEMON = "pokemon", "Pokemon"
        TRAINER = "trainer", "Trainer"
        ENERGY = "energy", "Energy"

    class SubType(models.TextChoices):
        BASIC = "basic", "Basic"
        STAGE_1 = "stage-1", "Stage 1"
        STAGE_2 = "stage-2", "Stage 2"
        TRAINER = "trainer", "Trainer"
        STADIUM = "stadium", "Stadium"
        SPECIAL = "special", "Special"

    supertype = models.CharField(
        max_length=20, choices=SuperType.choices, default=SuperType.POKEMON
    )
    subtype = models.CharField(max_length=20, choices=SubType.choices, blank=True)
    expansion = models.ForeignKey(
        Expansion, on_delete=models.CASCADE, related_name="cards"
    )
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    hp = models.IntegerField(null=True, blank=True)
    retreat_cost = models.IntegerField(default=0)
    types = models.ManyToManyField(EnergyType, related_name="cards", blank=True)
    weak_type = models.ForeignKey(
        EnergyType,
        on_delete=models.PROTECT,
        related_name="cards_with_weakness",
        blank=True,
        null=True,
    )
    weak_value = models.CharField(max_length=10, blank=True, help_text="e.g. x2, +20")
    resist_type = models.ForeignKey(
        EnergyType,
        on_delete=models.PROTECT,
        related_name="cards_with_resistance",
        blank=True,
        null=True,
    )
    resist_value = models.CharField(max_length=10, blank=True, help_text="e.g. -20")

    def __str__(self):
        loc = self.localizations.filter(language=SupportedLanguage.EN).first()
        name = loc.name if loc else "Unknown"
        return f"{name} - {self.expansion.code}"

    def save(self, *args, **kwargs):
        if self.pk is None:
            super().save(*args, **kwargs)

        if not self.slug:
            self.slug = slugify(f"{self.expansion.code}-{self.pk}")
            super().save(update_fields=["slug"])
        else:
            super().save(*args, **kwargs)


class CardPrinting(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name="printings")
    variant = models.ForeignKey(
        CardVariant, on_delete=models.PROTECT, related_name="printings"
    )
    rarity = models.CharField(max_length=50)
    master_image = models.ImageField(upload_to="cards/master/", null=True, blank=True)

    def __str__(self):
        return f"{self.card} - {self.variant.name}"


class LocalizedCard(models.Model):
    printing = models.ForeignKey(
        CardPrinting, on_delete=models.CASCADE, related_name="localizations"
    )
    language = models.CharField(
        max_length=2,
        choices=SupportedLanguage.to_choices(),
        default=SupportedLanguage.EN,
    )
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=10, help_text="e.g. 'H28', '40'")
    total_cards_override = models.IntegerField(
        null=True,
        blank=True,
        help_text="Specific total for a group (e.g. 32 for Aquapolis Holos)",
    )
    description = models.TextField(blank=True, null=True)

    def get_full_number(self, expansion_total):
        total = self.total_cards_override or expansion_total
        return f"{self.number}/{total}"

    class Meta:
        unique_together = ("printing", "language")

    def __str__(self):
        return f"{self.name} ({self.number}) - {self.language.upper()}"
