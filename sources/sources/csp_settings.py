from csp.constants import NONE

# The readiness/healthz JSON endpoints don't need much,
# so let's set a very restrictive CSP.
#
# Available CSP settings are documented at
# https://django-csp.readthedocs.io/en/latest/configuration.html
CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": [NONE],
        "script-src": [NONE],
        "img-src": [NONE],
        "object-src": [NONE],
        "media-src": [NONE],
        "frame-src": [NONE],
        "font-src": [NONE],
        "connect-src": [NONE],
        "style-src": [NONE],
        "base-uri": [NONE],
        "child-src": [NONE],
        "frame-ancestors": [NONE],
        "navigate-to": [NONE],
        "form-action": [NONE],
        "manifest-src": [NONE],
        "worker-src": [NONE],
        "upgrade-insecure-requests": True,
    }
}
