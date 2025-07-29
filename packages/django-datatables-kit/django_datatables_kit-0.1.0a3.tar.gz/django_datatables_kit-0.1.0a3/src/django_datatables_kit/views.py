import html
import logging
import re
from copy import deepcopy
from typing import Any
from django.conf import settings
from django.db.models import (
    CharField,
    F,
    FileField,
    Manager,
    Q,
    QuerySet,
    TextField,
)
from django.http import HttpRequest, JsonResponse, QueryDict
from django.views import View
from django_helper_kit.utils import tokenize

_logger = logging.getLogger(__name__)


def text_filter(
        global_search_value: str,
        initial_queryset: Manager | QuerySet,
        columns: dict,
        order_by_columns: str | list | None = None,
        offset: int = 0,
        limit: int | None = None,
        global_search_case_insensitive: bool = True,
        silence_unsearchable_columns: bool = True,
):
    global_search_value = str(global_search_value)
    model = initial_queryset.model
    total_count = initial_queryset.count()
    filtered = initial_queryset
    filter_distinct_on = []

    for name, attrs in columns.items():
        attrs["choices"] = None
        attrs["choices_lower"] = None

        if attrs["filter_distinct_on"]:
            filter_distinct_on.append(name)

        if attrs["annotation"]:
            if isinstance(attrs["annotation"], str):
                columns[name]["annotation"] = \
                    F(columns[name]["annotation"])
            if (attrs["global_searchable"]
                    or attrs["column_search_values"]["case_sensitive"]
                    or attrs["column_search_values"]["case_insensitive"]
                    or attrs["column_search_values"]["global_setting"]):
                if not (hasattr(attrs["annotation"], "output_field")
                        and isinstance(attrs["annotation"].output_field,
                                       (CharField, TextField))):
                    if silence_unsearchable_columns:
                        attrs["global_searchable"] = False
                        attrs["column_search_values"]["case_sensitive"] = []
                        attrs["column_search_values"]["case_insensitive"] = []
                        attrs["column_search_values"]["global_setting"] = []
                    else:
                        raise ValueError(f"Annotation `{name}` is not"
                                         f" searchable")
        else:
            if "__" in name:
                field_name, attrs["related_field_name"] = name.split("__")
                attrs["field"] = model._meta.get_field(field_name)
                field = attrs["field"].related_model._meta \
                    .get_field(attrs["related_field_name"])
            else:
                field_name, related_model_field_name = name, None
                attrs["field"] = model._meta.get_field(field_name)
                field = attrs["field"]

            if (attrs["global_searchable"]
                    or attrs["column_search_values"]["case_sensitive"]
                    or attrs["column_search_values"]["case_insensitive"]
                    or attrs["column_search_values"]["global_setting"]):
                if not isinstance(field, (CharField, TextField)):
                    if silence_unsearchable_columns:
                        attrs["global_searchable"] = False
                        attrs["column_search_values"]["case_sensitive"] = []
                        attrs["column_search_values"]["case_insensitive"] = []
                        attrs["column_search_values"]["global_setting"] = []
                    else:
                        raise ValueError(
                            f"Field `{name}` is not CharField or TextField,"
                            f" hence not searchable"
                        )
            if isinstance(field, CharField) and field.choices is not None:
                attrs["choices"] = dict(field.choices)
                if global_search_case_insensitive:
                    attrs["choices_lower"] = {
                        key: str(value).lower()
                        for key, value in attrs["choices"].items()
                    }

    search_filter = Q()
    if global_search_value:
        global_search_tokens = tokenize(string=global_search_value)
        for global_token in global_search_tokens:
            if global_search_case_insensitive:
                global_token = global_token.lower()

            global_filter = Q()
            for name, attrs in columns.items():
                if not attrs["global_searchable"]:
                    continue

                if attrs["choices"]:
                    choices = attrs["choices_lower"] \
                        if global_search_case_insensitive else attrs["choices"]
                    for key, value in choices.items():
                        if global_token in value:
                            global_filter |= Q(**{f"{name}__eq": key})
                else:
                    contains_arg = f"{name}__icontains" \
                        if global_search_case_insensitive \
                        else f"{name}__contains"
                    global_filter |= Q(**{contains_arg: global_token})

            search_filter &= global_filter

    for name, attrs in columns.items():
        column_filter = Q()
        for column_search_type, column_search_case_insensitive \
                in {"case_sensitive": False,
                    "case_insensitive": True,
                    "global_setting": global_search_case_insensitive}.items():
            if not attrs["column_search_values"][column_search_type]:
                for column_search_value \
                        in attrs["column_search_values"][column_search_type]:
                    column_search_value = str(column_search_value)
                    column_search_tokens = tokenize(string=column_search_value)
                    for column_token in column_search_tokens:
                        if attrs["choices"]:
                            column_choices_filter = Q()
                            choices = attrs["choices_lower"] \
                                if column_search_case_insensitive \
                                else attrs["choices"]
                            for key, value in choices.items():
                                if column_token in value:
                                    column_choices_filter |= \
                                        Q(**{f"{name}__eq": key})
                            column_filter &= column_choices_filter
                        else:
                            contains_arg = f"{name}__icontains" \
                                if column_search_case_insensitive \
                                else f"{name}__contains"
                            column_filter &= Q(**{contains_arg: column_token})
            search_filter &= column_filter

    if search_filter:
        filtered = filtered.filter(search_filter)
        if filter_distinct_on:
            filtered = filtered.distinct(*filter_distinct_on)
        filtered_count = filtered.count()
    else:
        filtered_count = total_count

    filtered = filtered.annotate(
        **{name: attrs["annotation"]
           for name, attrs in columns.items()
           if attrs["annotation"]
           and (attrs["select"] or attrs["filter_distinct_on"])})

    if order_by_columns is not None and not order_by_columns == "":
        if not isinstance(order_by_columns, list):
            order_by_columns = [order_by_columns]
        if order_by_columns:
            filtered = filtered.order_by(*order_by_columns)

    if offset or limit >= 1:
        if limit < 1:
            filtered = filtered[offset:]
        else:
            filtered = filtered[offset:offset + limit]

    return filtered, filtered_count, total_count


class DataTablesMixin:
    model = None
    column_masks = {}
    addon_search_columns = []
    addon_select_columns = []
    filter_distinct_on = []
    annotations = {}
    default_order_by = []
    global_search_case_insensitive = \
        settings.DJDTK_DATATABLES_DEFAULTS["search"]["caseInsensitive"]

    http_method_names = ["post"]

    _DT_KEY_RE = re.compile(r"^(.*?)(\[.*])*$")
    _DT_STACK_RE = re.compile(r"(?<=\[).*?(?=])")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dt_post = None
        self.global_html_escape = False
        if isinstance(self.addon_search_columns, str):
            self.addon_search_columns = [self.addon_search_columns]
        if isinstance(self.addon_select_columns, str):
            self.addon_select_columns = [self.addon_select_columns]

    def _dt_post_to_dict(self, query_dict: QueryDict) -> dict:
        # https://datatables.net/manual/server-side
        body = {}
        for key, value in query_dict.items():
            if key in ["start", "length"]:
                body[key] = int(value)
                continue
            elif value == "true":
                value = True
            elif value == "false":
                value = False
            else:
                try:
                    value = int(value)
                except ValueError:
                    pass

            match = self._DT_KEY_RE.search(key)
            if match:
                key, stack = match.groups()
                stack = ([key]
                         + ([] if stack is None
                            else self._DT_STACK_RE.findall(stack)))
                base = body
                keys_count = len(stack)
                for index, key_ in enumerate(stack):
                    if index == keys_count - 1:
                        base[key_] = value
                    else:
                        if key_ not in base:
                            base[key_] = {}
                        base = base[key_]
        if "order" in body and "columns" in body:
            for attrs in body["order"].values():
                if "data" not in attrs:
                    attrs["data"] = \
                        body["columns"][str(attrs["column"])]["data"]
        return body

    def _html_escape(self, value: str, column_attrs: dict):
        column_html_escape = False
        if isinstance(value, str):
            column_html_escape = column_attrs.get("htmlEscape", None)
            if column_html_escape is None:
                column_html_escape = self.global_html_escape
        return html.escape(value) if column_html_escape else value

    def initial_queryset(self, *args, **kwargs) -> Manager | QuerySet:          # NOQA
        if self.model is None:
            raise NotImplementedError(
                "`model` missing, or override `initial_queryset` method"
            )
        return self.objects.all()

    def _order_by_columns(self):
        return [("-" if order["dir"] == "desc" else "")
                + self.column_masks[order["data"]]
                for order in self.dt_post["order"].values()
                if order["data"] and order["data"] in self.column_masks] \
            if "order" in self.dt_post else self.default_order_by

    def order_by_columns(self):
        return self._order_by_columns()

    def post(self,
             request: HttpRequest,
             *args,                                                             # NOQA
             **kwargs) -> JsonResponse:                                         # NOQA
        self.dt_post = self._dt_post_to_dict(request.POST)
        # column_names = [attrs["data"]
        #     for index, attrs in self.dt_post.get("columns", {}).items()
        # }
        self.global_html_escape = (
                self.dt_post.get("globalSearchHtmlEscape", False)
                or settings.DJDTK_DATATABLES_CONFIG["globalSearchHtmlEscape"]
        )

        column_template = {
            "annotation": None,
            "column_search_values": {"case_sensitive": [],
                                     "case_insensitive": [],
                                     "global_setting": []},
            "field": None,
            "related_field_name": None,
            "global_searchable": False,
            "select": False,
            "filter_distinct_on": False,
            "masked_names": [],
        }

        columns, post_columns = {}, {}
        for column in self.dt_post["columns"].values():
            if column["search"]["regex"]:
                raise ValueError(f"Regex search in `{column["data"]}` is not"
                                 f" supported")
            # column["data"] is empty when DT bases that column on other
            # columns, nothing required from backend
            if not column["data"]:
                continue
            if not column["data"] in self.column_masks.keys():
                post_columns[column["data"]] = None
                continue

            post_columns[column["data"]] = name \
                = self.column_masks[column["data"]]
            columns.setdefault(name, deepcopy(column_template))

            if column["data"] not in columns[name]["masked_names"]:
                columns[name]["masked_names"].append(column["data"])
            columns[name]["select"] = True
            # If column present more than once in dt_post and any one occurrence
            # is "searchable", we make it searchable
            columns[name]["global_searchable"] = \
                columns[name]["global_searchable"] or column["searchable"]
            # If column present more than once in dt_post, and sesarch value
            # is present, we use each column search
            if not column["search"]["value"] == "":
                if ("caseInsensitive" in column["search"]
                        and not column["search"]["caseInsensitive"] == "global"):
                    if column["search"]["caseInsensitive"]:
                        columns[name]["column_search_values"]["case_insensitive"] \
                            .append(column["search"]["value"])
                    else:
                        columns[name]["column_search_values"]["case_sensitive"] \
                            .append(column["search"]["value"])
                else:
                    columns[name]["column_search_values"]["global_setting"] \
                        .append(column["search"]["value"])

        run_text_filter = bool(columns)

        for annot_name, annot in self.annotations.items():
            columns.setdefault(annot_name, column_template.copy())
            columns[annot_name]["annotation"] = annot
        for name in self.addon_select_columns:
            columns.setdefault(name, column_template.copy())
            columns[name]["select"] = True
        for name in self.filter_distinct_on:
            columns.setdefault(name, column_template.copy())
            columns[name]["filter_distinct_on"] = True
        for name in self.addon_search_columns:
            columns.setdefault(name, column_template.copy())
            columns[name]["global_searchable"] = True

        if run_text_filter:
            filtered, filtered_count, total_count = text_filter(
                global_search_value=self.dt_post["search"]["value"],
                initial_queryset=self.initial_queryset(*args, **kwargs),
                columns=columns,
                order_by_columns=self.order_by_columns(),
                offset=self.dt_post["start"],
                limit=self.dt_post["length"],
                global_search_case_insensitive=
                self.global_search_case_insensitive
            )
        else:
            filtered, filtered_count, total_count = \
                self.initial_queryset().none(), 0, 0

        filtered = self.postprocess_filtered(filtered, *args, **kwargs)
        filtered_values = []
        for row in filtered:
            row_dict = {}
            for post_name, name in post_columns.items():
                if name is None:
                    row_dict[post_name] = None
                    continue

                attrs = columns[name]
                if not attrs["select"]:
                    continue

                if attrs["related_field_name"] is None:
                    row_dict[post_name] = self._transform_output(
                        attrs, getattr(row, name)
                    )
                else:
                    if attrs["field"].many_to_many:
                        all_related = getattr(row,
                                              attrs["field"].related_name).all()
                        row_dict[post_name] = [
                            self._transform_output(
                                attrs, getattr(related,
                                               attrs["related_field_name"])
                            ) for related in all_related
                        ]
                    elif attrs["field"].one_to_one:
                        related = getattr(row,
                                          attrs["field"].related_name)
                        row_dict[post_name] = self._transform_output(
                            attrs, getattr(related, attrs["related_field_name"])
                        )

            filtered_values.append(row_dict)

        return JsonResponse({
            "data": self.postprocess_filtered_values(
                filtered_values, *args, **kwargs
            ),
            "draw": self.dt_post["draw"],
            "recordsFiltered": filtered_count,
            "recordsTotal": total_count,
        }, status=200)

    def postprocess_filtered(self, filtered, *args, **kwaargs):                 # NOQA
        return filtered

    def postprocess_filtered_values(self,
                                    filtered_values: list,
                                    *args,
                                    **kwargs) -> list:                          # NOQA
        return filtered_values

    def _transform_output(self, attrs: dict, value) -> Any:
        if attrs["choices"]:
            return {"raw": self._html_escape(value, attrs),
                    "human_readable": attrs["choices"][value]}
        elif isinstance(attrs["field"], FileField):
            return {"url": value.url,
                    "name": value.name.split("/")[-1]}
        else:
            return self._html_escape(value, attrs)


class BaseDataTablesView(DataTablesMixin, View):
    pass
