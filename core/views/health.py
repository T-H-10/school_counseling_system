from django.http import JsonResponse


def health_check(request):
    """Unauthenticated liveness probe for uptime monitors and keep-alive pings.

    A plain Django view (not DRF) on purpose: it skips authentication,
    throttling, and the database entirely, so a ping every few minutes costs
    nothing and can't be rate-limited away from the monitor. It only proves
    the process is up — deeper checks (DB reachable) belong in the monitor's
    alerting on real endpoints, not in a hot keep-alive path.
    """
    return JsonResponse({"status": "ok"})
