from django.contrib.staticfiles.storage import ManifestStaticFilesStorage


class NonStrictManifestStaticFilesStorage(ManifestStaticFilesStorage):
    """Manifest storage that falls back to original paths when entries are missing.

    Using Django's ManifestStaticFilesStorage directly (not whitenoise's subclass)
    avoids a whitenoise version dependency and works with any whitenoise >= 5.x.
    WhiteNoise handles compression at serve time; this class handles URL hashing.
    """

    manifest_strict = False
