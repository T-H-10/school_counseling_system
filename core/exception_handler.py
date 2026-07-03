"""Uniform, detail-free handling of unexpected API errors.

DRF's default handler covers expected API exceptions (validation, auth,
permissions, 404...) and those pass through untouched. Anything else — a code
crash, a DB error — is logged server-side with its full traceback and returned
to the client as a generic JSON 500, so internal paths, table names, and stack
traces never leak in a response body.
"""

import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if response is not None:
        return response
    logger.exception("Unhandled exception in %s", context.get("view"), exc_info=exc)
    return Response(
        {"error": "אירעה שגיאה פנימית"},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
