from csp.constants import NONE

# The readiness/healthz JSON endpoints don't need much,
# so let's set a very restrictive CSP.
#
# Available CSP settings are documented at
# https://django-csp.readthedocs.io/en/latest/configuration.html
CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "base-uri": [NONE],
        "child-src": [NONE],
        "connect-src": [NONE],
        "default-src": [NONE],
        "fenced-frame-src": [NONE],
        "font-src": [NONE],
        "form-action": [NONE],
        "frame-ancestors": [NONE],
        "frame-src": [NONE],
        "img-src": [NONE],
        "manifest-src": [NONE],
        "media-src": [NONE],
        "navigate-to": [NONE],
        "object-src": [NONE],
        "prefetch-src": [NONE],
        "script-src": [NONE],
        "script-src-attr": [NONE],
        "script-src-elem": [NONE],
        "style-src": [NONE],
        "style-src-attr": [NONE],
        "style-src-elem": [NONE],
        "worker-src": [NONE],
        "upgrade-insecure-requests": True,
    }
}
