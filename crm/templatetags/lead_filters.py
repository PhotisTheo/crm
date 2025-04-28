from django import template

register = template.Library()


@register.filter
def filter_by_category_and_status(leads, arg):
    try:
        category, status = arg.split(":")
        return [
            lead
            for lead in leads
            if lead.lead_type == category and lead.status == status
        ]
    except ValueError:
        return []


@register.simple_tag
def count_leads_by_category_status(leads, category, status):
    return len(
        [lead for lead in leads if lead.lead_type == category and lead.status == status]
    )
