{#-- TODO: move to dbt-adapters --#}
{% macro get_show_sql(compiled_code, sql_header, limit) -%}
{%- set language = model['language'] %}
{%- if language == 'sql' %}
    {%- if sql_header -%}
      {{ sql_header }}
    {%- endif -%}
    {%- if limit is not none and language == "sql" -%}
      {{ get_limit_subquery_sql(compiled_code, limit) }}
    {%- else -%}
      {{ compiled_code }}
    {%- endif -%}
{%- endif -%}

{% elif language == "python" %}

{% set preview_code %}

{{ compiled_code }}

def main(session):
    dbt = dbtObj(session.table)
    try:
        df = model(dbt, session)
    except Exception as e:
        raise Exception(f"""While running {dbt.this}, encountered an error:
{e}
Logs: {dbt.logs}
"""
)
    {% if limit is not none %}
    df.limit({{ limit }})
    {% endif %}
    return df

{% endset %}

{#-- TODO: generalize this & use Capability / adapter.supports() --#}
{{ adapter.get_snowpark_sproc_sql(model, preview_code, "TABLE()") }}

{%- else -%}

  {{ exceptions.raise_compiler_error("Unrecognized model language " ~ language) }}

{%- endif -%}

{% endmacro %}
