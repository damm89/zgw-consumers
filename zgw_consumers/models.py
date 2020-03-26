import uuid
from typing import Optional
from urllib.parse import urljoin, urlsplit, urlunsplit

from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import Length
from django.utils.translation import ugettext_lazy as _

from zds_client import ClientAuth

from .client import ZGWClient, get_client_class
from .constants import APITypes, AuthTypes


class Service(models.Model):
    label = models.CharField(_("label"), max_length=100)
    api_type = models.CharField(_("type"), max_length=20, choices=APITypes.choices)
    api_root = models.CharField(_("api root url"), max_length=255, unique=True)

    extra = JSONField(
        _("extra configuration"),
        default=dict,
        help_text=_("Extra configuration that's service-specific"),
        blank=True,
    )

    # credentials for the API
    client_id = models.CharField(max_length=255, blank=True)
    secret = models.CharField(max_length=255, blank=True)
    auth_type = models.CharField(
        _("authorization type"),
        max_length=20,
        choices=AuthTypes,
        default=AuthTypes.jwt,
    )
    header_key = models.CharField(_("header key"), max_length=100, blank=True)
    header_value = models.CharField(_("header value"), max_length=255, blank=True)
    oas = models.URLField(
        _("OAS"), max_length=255, help_text=_("Path to OAS yaml file")
    )

    class Meta:
        verbose_name = _("service")
        verbose_name_plural = _("services")

    def __str__(self):
        return f"[{self.get_api_type_display()}] {self.label}"

    def save(self, *args, **kwargs):
        if not self.api_root.endswith("/"):
            self.api_root = f"{self.api_root}/"

        if not self.oas:
            self.oas = urljoin(self.api_root, "schema/openapi.yaml")

        super().save(*args, **kwargs)

    def clean(self):
        super().clean()

        if self.api_type == APITypes.ztc:
            main_catalogus_uuid = self.extra.get("main_catalogus_uuid")
            if main_catalogus_uuid is None:
                raise ValidationError(
                    {"extra": _("Expected a 'main_catalogus_uuid' extra config")}
                )

            try:
                uuid.UUID(main_catalogus_uuid)
            except ValueError:
                raise ValidationError(
                    {
                        "extra": _(
                            "'main_catalogus_uuid' does not look like a valid UUID4"
                        )
                    }
                )

    def build_client(self, **claims):
        """
        Build an API client from the service configuration.
        """
        _uuid = uuid.uuid4()
        dummy_detail_url = f"{self.api_root}dummy/{_uuid}"
        Client = get_client_class()
        client = Client.from_url(dummy_detail_url)
        client.schema_url = self.oas

        if self.auth_type == AuthTypes.jwt:
            client.auth = ClientAuth(
                client_id=self.client_id, secret=self.secret, **claims
            )
        elif self.auth_type == AuthTypes.token:
            client.auth_value = {self.header_key: self.header_value}
        return client

    @classmethod
    def get_client(cls, url: str, **kwargs) -> Optional[ZGWClient]:
        split_url = urlsplit(url)
        scheme_and_domain = urlunsplit(split_url[:2] + ("", "", ""))

        candidates = (
            cls.objects.filter(api_root__startswith=scheme_and_domain)
            .annotate(api_root_length=Length("api_root"))
            .order_by("-api_root_length")
        )

        # select the one matching
        for candidate in candidates.iterator():
            if url.startswith(candidate.api_root):
                credentials = candidate
                break
        else:
            return None

        client = credentials.build_client(**kwargs)

        return client

    @classmethod
    def get_auth_header(cls, url: str, **kwargs) -> Optional[dict]:
        client = cls.get_client(url, **kwargs)
        if not client:
            return None

        return client.auth_header
