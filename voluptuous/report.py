"""Batch validation reporting helpers.

Validates many documents against a single ``Schema`` and aggregates the
failures into a flat, operator-friendly report where every error carries
the index of the offending document and a dotted field path.
"""

import typing

from voluptuous import error as er
from voluptuous.schema_builder import Schema


class Report:
    """Aggregate result of validating many documents.

    :attr errors: A list of ``{'index', 'path', 'msg'}`` dicts, one per
        individual validation failure, in document order.
    :attr ok: ``True`` when every document validated cleanly.
    """

    def __init__(self, errors: typing.List[typing.Dict[str, typing.Any]]) -> None:
        self.errors = errors
        self.ok = not errors

    def __repr__(self) -> str:
        return 'Report(ok=%r, errors=%r)' % (self.ok, self.errors)


def _format_path(path: typing.Sequence[typing.Hashable]) -> str:
    """Render an error path as ``name`` / ``tags[0]`` / ``a.b[2].c``."""
    out = ''
    for part in path:
        if isinstance(part, int):
            out += '[%d]' % part
        else:
            out += ('.' if out else '') + str(part)
    return out


def validate_many(schema: Schema, docs: typing.Iterable[typing.Any]) -> Report:
    """Validate each document in ``docs`` against ``schema``.

    Returns a :class:`Report` whose ``errors`` locate each failure by
    document ``index`` and field ``path``; documents are validated
    independently so one bad document does not affect the others.
    """
    errors: typing.List[typing.Dict[str, typing.Any]] = []
    for index, doc in enumerate(docs):
        try:
            schema(doc)
        except er.MultipleInvalid as exc:
            for err in exc.errors:
                errors.append(
                    {
                        'index': index,
                        'path': _format_path(err.path),
                        'msg': err.msg,
                    }
                )
        except er.Invalid as exc:
            errors.append(
                {
                    'index': index,
                    'path': _format_path(exc.path),
                    'msg': exc.msg,
                }
            )
    return Report(errors)
