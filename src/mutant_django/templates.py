from jinja2 import Template


DJANGO_FILE_TEMPLATE = Template("""
from django.db import models
{% for line in imports -%}
{{ line }}
{% endfor %}

{% for entity in entities -%}
{{ entity.render() }}{% if not loop.last %}

{% endif %}
{% endfor -%}
""".lstrip())


DJANGO_MODEL_TEMPLATE = Template("""
class {{ name }}(models.Model):
    class Meta:
      {%- for option in model_meta %}
        {{ option }}
      {%- endfor %}
{% for field in fields -%}
    {{ field.render_choices() }}
  {%- endfor -%}
  {%- for field in fields -%}
    {{ field.render() }}
  {%- endfor -%}
""".lstrip())


DJANGO_FIELD_TEMPLATE = Template("""
    {{ field_name }} = {{ field_type.django_field }}(
      {%- for value in field_type.django_positional -%}
        {{ value }}
        {%- if not loop.last %}, {% endif -%}
      {%- endfor -%}
      {%- for name, value in field_type.django_attributes -%}
        {%- if loop.first and field_type.django_positional %}, {% endif -%}
        {{ name }}={{ value }}
        {%- if not loop.last %}, {% endif -%}
      {%- endfor -%}
    )
""")
