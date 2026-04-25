import smtplib

from django.core.mail.backends.smtp import EmailBackend as DjangoSMTPEmailBackend
from django.core.mail.backends.smtp import DNS_NAME


class CompatibleSMTPEmailBackend(DjangoSMTPEmailBackend):
    """SMTP backend that tolerates Python 3.12+ starttls signature changes."""

    def open(self):
        try:
            return super().open()
        except TypeError as exc:
            if "starttls" not in str(exc):
                raise

            if self.connection:
                try:
                    self.connection.close()
                except OSError:
                    pass
                finally:
                    self.connection = None

            connection_class = smtplib.SMTP_SSL if self.use_ssl else smtplib.SMTP

            try:
                self.connection = connection_class(
                    self.host,
                    self.port,
                    local_hostname=DNS_NAME.get_fqdn(),
                    timeout=self.timeout,
                )

                if not self.use_ssl and self.use_tls:
                    self.connection.starttls()
                    self.connection.ehlo()

                if self.username and self.password:
                    self.connection.login(self.username, self.password)

                return True
            except (OSError, smtplib.SMTPException):
                if not self.fail_silently:
                    raise
                return False
