create table if not exists {{ table.schema }}.{{ table.name }} ( 
    {% for column in table.columns %}
    "{{ column.name }}" {{ column.type }} {% if not loop.last %},{% endif %}
    {% endfor %}
)
{% if table.partition_by is defined and table.partition_by|length > 0 %}
partition by (
    {% for column in table.columns %}
    "{{ column.name }}"{% if not loop.last %},{% endif %}
    {% endfor %}
)
{% endif %}
;