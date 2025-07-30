from __future__ import annotations

from typing import Any, Dict

from ckan.logic.schema import validator_args

from ckanext.ap_support.model import Ticket

Schema = Dict[str, Any]
STATUSES = [
    Ticket.Status.opened,
    Ticket.Status.closed,
]


@validator_args
def ticket_search(ignore_missing, unicode_safe, one_of) -> Schema:
    return {"status": [ignore_missing, unicode_safe, one_of(STATUSES)]}


@validator_args
def ticket_create(
    not_missing,
    unicode_safe,
    user_id_or_name_exists,
    ap_support_category_validator,
) -> Schema:
    return {
        "subject": [not_missing, unicode_safe],
        "category": [not_missing, unicode_safe, ap_support_category_validator],
        "text": [not_missing, unicode_safe],
        "author_id": [not_missing, unicode_safe, user_id_or_name_exists],
    }


@validator_args
def ticket_show(ignore_missing, unicode_safe, ticket_id_exists) -> Schema:
    return {"id": [ignore_missing, unicode_safe, ticket_id_exists]}


@validator_args
def ticket_delete(ignore_missing, unicode_safe, ticket_id_exists) -> Schema:
    return {"id": [ignore_missing, unicode_safe, ticket_id_exists]}


@validator_args
def ticket_update(
    not_missing, ignore_missing, unicode_safe, ignore, one_of, ticket_id_exists
) -> Schema:
    return {
        "id": [not_missing, unicode_safe, ticket_id_exists],
        "status": [ignore_missing, unicode_safe, one_of(STATUSES)],
        "text": [ignore_missing, unicode_safe],
        "__extras": [ignore],
        "__junk": [ignore],
    }
