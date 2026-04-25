from whitenoise.storage import CompressedManifestStaticFilesStorage


class NonStrictCompressedManifestStaticFilesStorage(CompressedManifestStaticFilesStorage):
    """Manifest storage that falls back to original paths when missing entries exist."""

    manifest_strict = False
