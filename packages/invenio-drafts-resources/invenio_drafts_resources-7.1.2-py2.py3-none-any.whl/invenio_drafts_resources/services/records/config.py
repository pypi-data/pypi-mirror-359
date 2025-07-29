# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 CERN.
# Copyright (C) 2020 Northwestern University.
# Copyright (C) 2022-2023 Graz University of Technology.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""RecordDraft Service API config."""

from invenio_i18n import lazy_gettext as _
from invenio_indexer.api import RecordIndexer
from invenio_records_resources.services import (
    ConditionalLink,
    RecordLink,
)
from invenio_records_resources.services import (
    RecordServiceConfig as RecordServiceConfigBase,
)
from invenio_records_resources.services import SearchOptions as SearchOptionsBase
from invenio_records_resources.services import (
    pagination_links,
)

from .components import DraftMetadataComponent, PIDComponent
from .permissions import RecordPermissionPolicy
from .schema import ParentSchema, RecordSchema
from .search_params import AllVersionsParam


def is_draft(record, ctx):
    """Shortcut for links to determine if record is a draft."""
    return record.is_draft


def is_record(record, ctx):
    """Shortcut for links to determine if record is a record."""
    return not record.is_draft


@staticmethod
def lock_edit_published_files(service, identity, record=None, draft=None):
    """Should published files be locked from editing in current record version."""
    return True


class SearchOptions(SearchOptionsBase):
    """Search options."""

    sort_options = {
        "bestmatch": dict(
            title=_("Best match"),
            fields=["_score"],  # search defaults to desc on `_score` field
        ),
        "newest": dict(
            title=_("Newest"),
            fields=["-created"],
        ),
        "oldest": dict(
            title=_("Oldest"),
            fields=["created"],
        ),
        "version": dict(
            title=_("Version"),
            fields=["-versions.index"],
        ),
    }

    params_interpreters_cls = [
        AllVersionsParam.factory("versions.is_latest")
    ] + SearchOptionsBase.params_interpreters_cls


class SearchDraftsOptions(SearchOptions):
    """Search options for drafts search."""

    sort_default = "bestmatch"
    sort_default_no_query = "updated-desc"
    sort_options = {
        "bestmatch": dict(
            title=_("Best match"),
            fields=["_score"],  # search defaults to desc on `_score` field
        ),
        "updated-desc": dict(
            title=_("Recently updated"),
            fields=["-updated"],
        ),
        "updated-asc": dict(
            title=_("Least recently updated"),
            fields=["updated"],
        ),
        "newest": dict(
            title=_("Newest"),
            fields=["-created"],
        ),
        "oldest": dict(
            title=_("Oldest"),
            fields=["created"],
        ),
        "version": dict(
            title=_("Version"),
            fields=["-versions.index"],
        ),
    }

    params_interpreters_cls = [
        AllVersionsParam.factory("versions.is_latest_draft")
    ] + SearchOptionsBase.params_interpreters_cls


class SearchVersionsOptions(SearchOptions):
    """Search options for versions search."""

    sort_default = "version"
    sort_default_no_query = "version"
    sort_options = {
        "version": dict(
            title=_("Version"),
            fields=["-versions.index"],
        ),
    }
    facets_options = dict(
        aggs={},
        post_filters={},
    )

    params_interpreters_cls = SearchOptionsBase.params_interpreters_cls


class RecordServiceConfig(RecordServiceConfigBase):
    """Draft Service configuration."""

    # Service configuration
    permission_policy_cls = RecordPermissionPolicy

    # WHY: We want to force user input choice here.
    draft_cls = None

    draft_indexer_cls = RecordIndexer
    draft_indexer_queue_name = f"{RecordServiceConfigBase.indexer_queue_name}-drafts"

    schema = RecordSchema

    schema_parent = ParentSchema

    search = SearchOptions
    search_drafts = SearchDraftsOptions
    search_versions = SearchVersionsOptions

    components = [
        DraftMetadataComponent,
        PIDComponent,
    ]

    default_files_enabled = True
    # we disable by default media files. The feature is only available via REST API
    # and they should be enabled before an upload is made i.e update the draft to
    # set `media_files.enabled` to True
    default_media_files_enabled = False
    lock_edit_published_files = lock_edit_published_files

    links_item = {
        "self": ConditionalLink(
            cond=is_record,
            if_=RecordLink("{+api}/records/{id}"),
            else_=RecordLink("{+api}/records/{id}/draft"),
        ),
        "self_html": ConditionalLink(
            cond=is_record,
            if_=RecordLink("{+ui}/records/{id}"),
            else_=RecordLink("{+ui}/uploads/{id}"),
        ),
        "latest": RecordLink("{+api}/records/{id}/versions/latest"),
        "latest_html": RecordLink("{+ui}/records/{id}/latest"),
        "draft": RecordLink("{+api}/records/{id}/draft", when=is_record),
        "record": RecordLink("{+api}/records/{id}", when=is_draft),
        "publish": RecordLink(
            "{+api}/records/{id}/draft/actions/publish", when=is_draft
        ),
        "versions": RecordLink("{+api}/records/{id}/versions"),
    }

    links_search = pagination_links("{+api}/records{?args*}")

    links_search_drafts = pagination_links("{+api}/user/records{?args*}")

    links_search_versions = pagination_links("{+api}/records/{id}/versions{?args*}")
