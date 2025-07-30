import datetime
import json
import logging

from dateutil import parser
from flask import current_app
from flask_appbuilder.exceptions import ApplyFilterException
from flask_appbuilder.models.filters import (
    BaseFilter,
    BaseFilterConverter,
    FilterRelation,
)
from flask_babel import lazy_gettext
from sqlalchemy import and_, cast, func, or_, select
from sqlalchemy import types as sa_types
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import BadRequest

log = logging.getLogger(__name__)

__all__ = [
    "SQLAFilterConverter",
    "FilterEqual",
    "FilterNotStartsWith",
    "FilterStartsWith",
    "FilterContains",
    "FilterNotEqual",
    "FilterEndsWith",
    "FilterEqualFunction",
    "FilterInFunction",
    "FilterGreater",
    "FilterNotEndsWith",
    "FilterRelationManyToManyEqual",
    "FilterRelationOneToManyEqual",
    "FilterRelationOneToManyNotEqual",
    "FilterSmaller",
    "FilterGreaterEqual",
    "FilterSmallerEqual",
]


def get_field_setup_query(query, model, column_name):
    """
    Help function for SQLA filters, checks for dot notation on column names.
    If it exists, will join the query with the model
    from the first part of the field name.

    example:
        Contact.created_by: if created_by is a User model,
        it will be joined to the query.
    """
    if not hasattr(model, column_name):
        # it's an inner obj attr
        rel_model = getattr(model, column_name.split(".")[0]).mapper.class_
        query = query.join(rel_model)
        return query, getattr(rel_model, column_name.split(".")[1])
    else:
        return query, getattr(model, column_name)


def set_value_to_type(datamodel, column_name, value):
    if datamodel.is_integer(column_name):
        try:
            return int(value)
        except Exception:
            return None
    elif datamodel.is_float(column_name):
        try:
            return float(value)
        except Exception:
            return None
    elif datamodel.is_boolean(column_name):
        if value == "y":
            return True
    elif datamodel.is_date(column_name) and not isinstance(value, datetime.date):
        try:
            return parser.parse(value).date()
        except Exception:
            return None
    elif datamodel.is_datetime(column_name) and not isinstance(
        value, datetime.datetime
    ):
        try:
            return parser.parse(value)
        except Exception:
            return None
    return value


class BaseFilterTextContains(BaseFilter):
    def _handle_relation_contains(self, col: str, value: str):
        concat = []
        rel_interface = self.datamodel.get_related_interface(col)
        for col_name in rel_interface.list_columns.keys():
            rel_col = getattr(rel_interface.obj, col_name)
            concat.append(cast(rel_col, sa_types.String))
            concat.append(" ")

        rel_obj = rel_interface.obj
        rel_pks = rel_interface.get_pk_name()
        if not isinstance(rel_pks, list):
            rel_pks = [rel_pks]

        rel_statements = [
            select(getattr(rel_obj, pk)).filter(
                func.concat(*concat).ilike("%" + value + "%")
            )
            for pk in rel_pks
        ]
        rel_statements = [
            getattr(rel_obj, pk).in_(stmt) for pk, stmt in zip(rel_pks, rel_statements)
        ]
        filter = (
            getattr(self.datamodel.obj, col).any
            if self.datamodel.is_relation_one_to_many(col)
            or self.datamodel.is_relation_many_to_many(col)
            else getattr(self.datamodel.obj, col).has
        )
        return filter(*rel_statements)


class FilterTextContains(BaseFilterTextContains):
    name = lazy_gettext("Text contains")
    arg_name = "tc"

    def apply(self, query, value):
        SEPARATOR = current_app.config.get("TEXT_FILTER_SEPARATOR", ";")
        value = [v.strip() for v in value.split(SEPARATOR) if v]
        filters = []
        query, field = get_field_setup_query(query, self.model, self.column_name)

        for val in value:
            if self.datamodel.is_relation(self.column_name):
                filters.append(self._handle_relation_contains(self.column_name, val))
            else:
                filters.append(cast(field, sa_types.String).ilike("%" + val + "%"))
        return query.filter(and_(*filters))


class FilterStartsWith(BaseFilter):
    name = lazy_gettext("Starts with")
    arg_name = "sw"

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        return query.filter(field.ilike(value + "%"))


class FilterNotStartsWith(BaseFilter):
    name = lazy_gettext("Not Starts with")
    arg_name = "nsw"

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        return query.filter(~field.ilike(value + "%"))


class FilterEndsWith(BaseFilter):
    name = lazy_gettext("Ends with")
    arg_name = "ew"

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        return query.filter(field.ilike("%" + value))


class FilterNotEndsWith(BaseFilter):
    name = lazy_gettext("Not Ends with")
    arg_name = "new"

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        return query.filter(~field.ilike("%" + value))


class FilterContains(BaseFilter):
    name = lazy_gettext("Contains")
    arg_name = "ct"

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        return query.filter(field.ilike("%" + value + "%"))


class FilterNotContains(BaseFilter):
    name = lazy_gettext("Not Contains")
    arg_name = "nct"

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        return query.filter(~field.ilike("%" + value + "%"))


class FilterEqual(BaseFilter):
    name = lazy_gettext("Equal to")
    arg_name = "eq"

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        if value == "NULL":
            return query.filter(field.is_(None))
        value = set_value_to_type(self.datamodel, self.column_name, value)
        return query.filter(field == value)


class FilterNotEqual(BaseFilter):
    name = lazy_gettext("Not Equal to")
    arg_name = "neq"

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        value = set_value_to_type(self.datamodel, self.column_name, value)
        if value == "NULL":
            return query.filter(field.is_not(None))
        return query.filter(field != value)


class FilterGreater(BaseFilter):
    name = lazy_gettext("Greater than")
    arg_name = "gt"

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        value = set_value_to_type(self.datamodel, self.column_name, value)

        if value is None:
            return query

        return query.filter(field > value)


class FilterSmaller(BaseFilter):
    name = lazy_gettext("Smaller than")
    arg_name = "lt"

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        value = set_value_to_type(self.datamodel, self.column_name, value)

        if value is None:
            return query

        return query.filter(field < value)


class FilterRelationOneToManyEqual(FilterRelation):
    name = lazy_gettext("Relation")
    arg_name = "rel_o_m"

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        try:
            rel_obj = self.datamodel.get_related_obj(self.column_name, value)
        except SQLAlchemyError as exc:
            logging.warning(
                "Filter exception for %s with value %s, will not apply", field, value
            )
            self.datamodel.session.rollback()
            raise ApplyFilterException(exception=exc)
        return query.filter(field == rel_obj)


class FilterRelationOneToManyNotEqual(FilterRelation):
    name = lazy_gettext("No Relation")
    arg_name = "nrel_o_m"

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        try:
            rel_obj = self.datamodel.get_related_obj(self.column_name, value)
        except SQLAlchemyError as exc:
            logging.warning(
                "Filter exception for %s with value %s, will not apply", field, value
            )
            self.datamodel.session.rollback()
            raise ApplyFilterException(exception=exc)
        return query.filter(field != rel_obj)


class FilterRelationManyToManyEqual(FilterRelation):
    name = lazy_gettext("Relation as Many")
    arg_name = "rel_m_m"

    def apply_item(self, query, field, value_item):
        """
        Get object by column_name and value_item, then apply filter if object exists
        Query with new filter applied
        """
        try:
            rel_obj = self.datamodel.get_related_obj(self.column_name, value_item)
        except SQLAlchemyError as exc:
            logging.warning(
                "Filter exception for %s with value %s, will not apply",
                field,
                value_item,
            )
            self.datamodel.session.rollback()
            raise ApplyFilterException(exception=exc)

        if rel_obj:
            return query.filter(field.contains(rel_obj))
        else:
            log.error(
                "Related object for column: %s, value: %s return Null",
                self.column_name,
                value_item,
            )

        return query

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)

        if isinstance(value, list):
            for value_item in value:
                query = self.apply_item(query, field, value_item)
            return query

        return self.apply_item(query, field, value)


class FilterEqualFunction(BaseFilter):
    name = "Filter view with a function"
    arg_name = "eqf"

    def apply(self, query, func):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        return query.filter(field == func())


class FilterInFunction(BaseFilter):
    name = "Filter view where field is in a list returned by a function"
    arg_name = "inf"

    def apply(self, query, func):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        filter_ = func()
        if not filter_:
            return query
        return query.filter(field.in_(filter_))


class FilterGreaterEqual(BaseFilter):
    name = lazy_gettext("Greater equal")
    arg_name = "ge"

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        value = set_value_to_type(self.datamodel, self.column_name, value)

        if value is None:
            return query

        return query.filter(field >= value)


class FilterSmallerEqual(BaseFilter):
    name = lazy_gettext("Smaller equal")
    arg_name = "le"

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        value = set_value_to_type(self.datamodel, self.column_name, value)

        if value is None:
            return query

        return query.filter(field <= value)


class FilterIn(BaseFilter):
    name = lazy_gettext("One of")
    arg_name = "in"

    def apply(self, query, value):
        values = json.loads(value)
        if not values:
            return query
        query, field = get_field_setup_query(query, self.model, self.column_name)
        return query.filter(field.in_(values))


class FilterBetween(BaseFilter):
    name = lazy_gettext("Between")
    arg_name = "bw"

    first_value = None
    second_value = None

    def apply(self, query, value):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        value = self.add_value(value)
        if not value:
            return query
        self.clear_values()

        if len(value) != 2:
            raise BadRequest("Between filter requires two values")

        value = [set_value_to_type(self.datamodel, self.column_name, v) for v in value]
        if value[0] is None or value[1] is None:
            return query

        return query.filter(field.between(value[0], value[1]))

    def add_value(self, value):
        """
        Add a value to the filter. This is used to add the first and second values
        for the between filter.
        """
        if self.first_value is None:
            self.first_value = value
            return None
        elif self.second_value is None:
            self.second_value = value
            return [self.first_value, self.second_value]
        elif self.first_value is not None and self.second_value is not None:
            raise BadRequest("Between filter can only have two values")

    def clear_values(self):
        """
        Clear the values for the filter. This is used to reset the filter
        after it has been applied.
        """
        self.first_value = None
        self.second_value = None


class FilterGlobal(BaseFilterTextContains):
    name = lazy_gettext("Global Filter")
    arg_name = "global"

    def apply(self, query, value):
        SEPARATOR = current_app.config.get("TEXT_FILTER_SEPARATOR", ";")
        list_cols, value = value
        value = [v.strip() for v in value.split(SEPARATOR) if v]
        filters = []
        list_cols = [x for x in list_cols if x in self.datamodel.list_properties]

        for val in value:
            concat_arr = []
            rel_filter_arr = []
            for col in list_cols:
                query, field = get_field_setup_query(query, self.model, col)
                if self.datamodel.is_relation(col):
                    rel_filter_arr.append(self._handle_relation_contains(col, val))
                else:
                    concat_arr.extend([cast(field, sa_types.String), " "])
            filters.append(
                or_(*rel_filter_arr, func.concat(*concat_arr).ilike("%" + val + "%"))
            )

        return query.filter(and_(*filters))


class SQLAFilterConverter(BaseFilterConverter):
    """
    Class for converting columns into a supported list of filters
    specific for SQLAlchemy.

    """

    conversion_table = (
        (
            "is_relation_many_to_one",
            [
                FilterRelationOneToManyEqual,
                FilterRelationOneToManyNotEqual,
                FilterTextContains,
            ],
        ),
        (
            "is_relation_one_to_one",
            [
                FilterRelationOneToManyEqual,
                FilterRelationOneToManyNotEqual,
                FilterTextContains,
            ],
        ),
        (
            "is_relation_many_to_many",
            [FilterRelationManyToManyEqual, FilterTextContains],
        ),
        (
            "is_relation_one_to_many",
            [FilterRelationManyToManyEqual, FilterTextContains],
        ),
        (
            "is_enum",
            [
                FilterTextContains,
                FilterEqual,
                FilterNotEqual,
                FilterIn,
            ],
        ),
        (
            "is_text",
            [
                FilterTextContains,
                FilterStartsWith,
                FilterEndsWith,
                FilterContains,
                FilterEqual,
                FilterNotStartsWith,
                FilterNotEndsWith,
                FilterNotContains,
                FilterNotEqual,
                FilterIn,
            ],
        ),
        (
            "is_binary",
            [
                FilterTextContains,
                FilterStartsWith,
                FilterEndsWith,
                FilterContains,
                FilterEqual,
                FilterNotStartsWith,
                FilterNotEndsWith,
                FilterNotContains,
                FilterNotEqual,
                FilterIn,
            ],
        ),
        (
            "is_string",
            [
                FilterTextContains,
                FilterStartsWith,
                FilterEndsWith,
                FilterContains,
                FilterEqual,
                FilterNotStartsWith,
                FilterNotEndsWith,
                FilterNotContains,
                FilterNotEqual,
                FilterIn,
            ],
        ),
        (
            "is_integer",
            [
                FilterBetween,
                FilterTextContains,
                FilterEqual,
                FilterGreater,
                FilterSmaller,
                FilterNotEqual,
                FilterSmallerEqual,
                FilterGreaterEqual,
                FilterIn,
            ],
        ),
        (
            "is_float",
            [
                FilterBetween,
                FilterTextContains,
                FilterEqual,
                FilterGreater,
                FilterSmaller,
                FilterNotEqual,
                FilterSmallerEqual,
                FilterGreaterEqual,
                FilterIn,
            ],
        ),
        (
            "is_numeric",
            [
                FilterBetween,
                FilterTextContains,
                FilterEqual,
                FilterGreater,
                FilterSmaller,
                FilterNotEqual,
                FilterSmallerEqual,
                FilterGreaterEqual,
                FilterIn,
            ],
        ),
        (
            "is_date",
            [
                FilterBetween,
                FilterTextContains,
                FilterEqual,
                FilterGreater,
                FilterSmaller,
                FilterNotEqual,
                FilterSmallerEqual,
                FilterGreaterEqual,
                FilterIn,
            ],
        ),
        (
            "is_boolean",
            [
                FilterEqual,
                FilterNotEqual,
                FilterTextContains,
            ],
        ),
        (
            "is_datetime",
            [
                FilterBetween,
                FilterTextContains,
                FilterEqual,
                FilterGreater,
                FilterSmaller,
                FilterNotEqual,
                FilterSmallerEqual,
                FilterGreaterEqual,
                FilterIn,
            ],
        ),
    )
