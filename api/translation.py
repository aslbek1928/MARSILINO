from modeltranslation.translator import register, TranslationOptions
from .models import Tag, Restaurant

@register(Tag)
class TagTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Restaurant)
class RestaurantTranslationOptions(TranslationOptions):
    fields = ('name', 'description')
