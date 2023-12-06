from django import template

register = template.Library()

@register.filter(name='bootstrap')
def bootstrap_form(element):
    return element.as_widget(attrs={'class': 'form-control'})