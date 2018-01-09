{{ fullname }} package
{% for item in range(8 + fullname|length) -%}={%- endfor %}

.. automodule:: {{ fullname }}
    {% if members -%}
    :show-inheritance:
    {%- endif %}

{% if submodules %}
    .. rubric:: Submodules

    .. toctree::
       :maxdepth: 2
{% for item in submodules %}
       {{ fullname }}.{{ item }}
       {%- endfor %}
    {%- endif -%}

{% if subpackages %}
    .. rubric:: Subpackages

    .. toctree::
       :maxdepth: 2
{% for item in subpackages %}
       {{ fullname }}.{{ item }}
       {%- endfor %}
    {%- endif %}

{% if members %}

    Summary
    -------

    {%- if exceptions %}

    .. rubric:: Exceptions

    .. autosummary::
        :nosignatures:
{% for item in exceptions %}
        {{ item }}
{%- endfor %}
    {%- endif %}

    {%- if classes %}

    .. rubric:: Classes

    .. autosummary::
        :nosignatures:
{% for item in classes %}
        {{ item }}
{%- endfor %}
    {%- endif %}

    {%- if functions %}

    .. rubric:: Functions

    .. autosummary::
        :nosignatures:
{% for item in functions %}
        {{ item }}
{%- endfor %}
    {%- endif %}
{%- endif %}

    {%- if data %}

    .. rubric:: Data

    .. autosummary::
        :nosignatures:
{% for item in data %}
        {{ item }}
{%- endfor %}
    {%- endif %}

{% if all_refs %}
    ``__all__``: {{ all_refs|join(", ") }}
{%- endif %}

{% if members %}

    {%- if exceptions %}

{% for item in exceptions %}

    {{ item }}
    {% for underline in range(item|length) -%}-{%- endfor %}
    .. autoexception:: {{ item }}
        :members:
        :undoc-members:
        :show-inheritance:
        :member-order: bysource
{%- endfor %}
    {%- endif %}


    {%- if classes %}
{% for item in classes %}

    {{ item }}
    {% for underline in range(item|length) -%}-{%- endfor %}
    .. autoclass:: {{ item }}
        :members:
        :undoc-members:
        :show-inheritance:
        :member-order: bysource
{%- endfor %}
    {%- endif %}


    {%- if functions %}
{% for item in functions %}

    {{ item }}
    {% for underline in range(item|length) -%}-{%- endfor %}
    .. autofunction:: {{ item }}
{%- endfor %}
    {%- endif %}


    {%- if data %}
{% for item in data %}

    {{ item }}
    {% for underline in range(item|length) -%}-{%- endfor %}
    .. autodata:: {{ item }}
{%- endfor %}
    {%- endif %}

{%- endif %}

