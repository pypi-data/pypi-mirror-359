..
    Copyright (C) 2020-2025 CERN.
    Copyright (C) 2020 Northwestern University.
    Copyright (C) 2024-2025 Graz University of Technology.

    Invenio-Drafts-Resources is free software; you can redistribute it and/or
    modify it under the terms of the MIT License; see LICENSE file for more
    details.

Changes
=======

Version v7.1.2 (released 2025-07-01)

- fix: Bug in import files from published record permissions

Version v7.1.1 (released 2025-06-25)

- auditlog: fix context injection
- fix: translation only applied on app start

Version v7.1.0 (released 2025-06-11)

- services: added `errors` in read_draft components

Version 7.0.0 (release 2025-06-03)

- setup: bump major dependencies
- tests: Added tests for remote transfer type
  * Whole lifecycle - create draft, add remote file, publish, create new
  version, import files from the previous, add a new remote file, publish,
  check files are ok
- fix: remove obsolete code in favour of transfer checks
- feat: file transfer registry update
  * Implementation of RFC 0072 - Pluggable Transfer Types for Record Files


Version 6.2.0 (release 2025-05-23)

- auditlog: actions: update entrypoint registration
- auditlog: context: Add context resolvers for User, Record and Resource

Version 6.1.1 (release 2025-05-06)

- installation: fix installation directive (audit-logs)

Version 6.1.0 (release 2025-05-06)

- i18n: mark strings for translation
- versions: dump UUIDs as string
- global: add audit logs to basic record and draft actions
          (experimental, behind a feature flag)

Version 6.0.0 (release 2024-12-10)

- setup: change to reusable workflows
- setup: bump major dependencies
- i18n:push translations


Version 5.1.0 (released 2024-08-09)

- resources: use and adjust vnd.inveniordm.v1+json http accept header

Version 5.0.0 (released 2024-07-04)

- services: return DraftNotCreatedError on read_draft when no draft available
            (on published record)

Version 4.0.0 (released 2024-06-04)

- installation: bump invenio-records-resources

Version 3.1.1 (released 2024-05-17)

- services: fix permission for file edit

Version 3.1.0 (released 2024-05-03)

- media-files: prevent copying to new version

Version 3.0.0 (released 2024-01-31)

- installation: bump dependencies
- uow: add "bulk_index" param on ParentRecordCommmitOp

Version 2.0.2 (2023-11-07)

- components: change cleanup method (backwards compatible, performance optimisation)

Version 2.0.1 (2023-10-26)

- fix: TypeError multiple values for record

Version 2.0.0 (2023-10-19)

- service: lock files conditionally (breaking change `#267`)

Version 1.13.1 (2023-10-19)

- service: handle soft-deleted drafts

Version 1.13.0 (2023-10-16)

- media files: create missing buckets on new publish

Version 1.12.2 (2023-10-15)

- service: change from NoResultFound to PIDDoesNotExistsError for consistency
  in service.read_draft() - affects errors for published records without a
  draft

Version 1.12.1 (2023-10-10)

- service: allow passing permission_action in kwargs for search versions

Version 1.12.0 (2023-10-09)

- versions: set the next index to the max index of all record versions

Version 1.11.2 (2023-10-02)

- components: handle disabled state on draft delete action

Version 1.11.1 (2023-10-02)

- components: replace ambiguous error on publish

Version 1.11.0 (2023-09-21)

- resources: add etag headers
- resources: add search request param to schema

Version 1.10.1 (2023-09-18)

- models: avoid flushing when getting records

Version 1.10.0 (2023-09-05)

- uow: add ParentRecordCommitOp uow

Version 1.9.0 (2023-09-05)

- service: allow passing of 'extra_filter' via kwargs to searches

Version 1.8.1 (2023-08-25)

- tasks: add margin time window for search to purge deleted documents
- services: move reindex latest records from records-resources

Version 1.8.0 (2023-08-16)

- components: conditional lock of files
- components: refactor file workflow

Version 1.7.1 (2023-08-14)

- fix an issue where the next version of the draft is incorrectly set

Version 1.7.0 (2023-08-10)

- records: read_latest method now accepts parent_id and it
  will return the latest version of a record also by parent_id
- change error message when publishing with missing files,
  depending if the record can be metadata only

Version 1.6.0 (2023-07-21)

- Add parent id resolver

Version 1.5.0 (2023-07-11)

- add media files components

Version 1.4.2 (2023-07-05)

- transifex: update config
- components: add default files enabled variable

Version 1.4.1 (2023-06-06)

- fix permission check for managing files

Version 1.4.0 (2023-04-25)

- upgrade invenio-records-resources
- ensure testing of file indexing

Version 1.3.0 (2023-04-20)

- upgrade invenio-records-resources

Version 1.2.0 (2023-03-24)

- bump invenio-records-resources to v2.0.0

Version 1.1.1 (2023-03-03)

- permissions: add can manage files permission to the draft

Version 1.1.0 (2023-03-02)

- remove deprecated flask-babelex dependency and imports
- install invenio-i18n explicitly

Version 1.0.4 (2023-02-22)

- service: allow to ignore field-level permission checks in validate_draft
- files: publishing files pending download from Fetch

Version 1.0.3 (2022-12-02)

- Fix rebuild index memory usage

Version 1.0.2 (2022-11-25)

- Add i18n translations.

Version 1.0.1 (2022-11-15)

- Use bulk indexing for service `rebuild_index` method.

Version 1.0.0 (2022-11-04)

- Bump invenio-records-resources version

Version 0.2.2 (2020-08-19)

- Fix support for Elasticsearch 6 and 7

Version 0.2.1 (2020-08-18)

- Initial public release.
