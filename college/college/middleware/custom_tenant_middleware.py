from django_tenants.middleware.main import TenantMainMiddleware
from django_tenants.utils import get_tenant_model, get_public_schema_name
from django.db import connection
from django.http import Http404

EXCLUDED_DOMAINS = ['super.localhost', 'localhost', '127.0.0.1']


class CustomTenantMiddleware(TenantMainMiddleware):
    def process_request(self, request):
        hostname = self.hostname_from_request(request)
        TenantModel = get_tenant_model()

        if hostname in EXCLUDED_DOMAINS:
            print(f"[CustomTenantMiddleware] Skipping tenant load for: {hostname}")
            try:
                tenant = TenantModel.objects.get(schema_name=get_public_schema_name())
                request.tenant = tenant
                connection.set_schema_to_public()
                return  # Skip tenant loading
            except TenantModel.DoesNotExist:
                raise Http404("Public tenant not found.")

        # Default behavior for tenant domains
        return super().process_request(request)
