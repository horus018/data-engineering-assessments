{% test accepted_range(model, column_name, min_value=None, max_value=None) %}

SELECT *
FROM {{ model }}
WHERE {{ column_name }} IS NOT NULL
  AND (
    {% if min_value is not none %}
      {{ column_name }} < {{ min_value }}
    {% else %}
      FALSE
    {% endif %}
    OR
    {% if max_value is not none %}
      {{ column_name }} > {{ max_value }}
    {% else %}
      FALSE
    {% endif %}
  )

{% endtest %}

