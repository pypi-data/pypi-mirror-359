from loguru import logger
from slugify import slugify

from komora_syncer.helpers.utils import build_tenant_name, clean_organization_name
from komora_syncer.models.netbox.NetboxBase import NetboxBase
from komora_syncer.models.netbox.NetboxCache import NetboxCache


class NbTenant(NetboxBase):
    def __init__(self, komora_obj=None):
        super().__init__()

        self.name = build_tenant_name(komora_obj.clientId, komora_obj.name)
        self.slug = slugify(self.name) if slugify(self.name) else komora_obj.id
        self.description = (
            " / ".join(komora_obj.keywords) if isinstance(komora_obj.keywords, list) else komora_obj.keywords
        )

        try:
            komora_vip_note = komora_obj.vipNote.strip()
        except AttributeError:
            komora_vip_note = ""

        self.custom_fields = {
            "client_id": komora_obj.clientId,
            "komora_id": komora_obj.id,
            "client_name": clean_organization_name(komora_obj.name),
            "komora_is_customer": komora_obj.isCustomer,
            "komora_is_supplier": komora_obj.isSupplier,
            "komora_is_vip": komora_obj.isVip,
            "komora_is_actual": komora_obj.isActual,
            "komora_is_member": komora_obj.isMember,
            "komora_vip_note": komora_vip_note,
        }

        self.api_object = None

    def find_or_create(self):
        self.find()
        if not self.api_object:
            self.create()

        return self.api_object

    def find(self):
        komora_id = self.custom_fields.get("komora_id")
        tenant_cache = NetboxCache.get_tenant_cache()

        try:
            if komora_id in tenant_cache:
                netbox_tenant = tenant_cache[komora_id]
            else:
                netbox_tenant = self.nb.tenancy.tenants.get(cf_komora_id=komora_id)

            if netbox_tenant:
                self.api_object = netbox_tenant
        except Exception:
            logger.exception(f"Unable to find tenant by komora_id: {komora_id}")
            netbox_tenant = None

        if not netbox_tenant:
            try:
                netbox_tenant = self.nb.tenancy.tenants.get(name__ie=self.name)

                if netbox_tenant:
                    logger.warning(f"komora_id: {str(komora_id)} was not found, but Tenant {self.name} already exists")
                    self.api_object = netbox_tenant
            except Exception:
                logger.exception(f"Unable to find tenant by name: {self.name}")
                raise

        return self.api_object

    def create(self):
        try:
            params = self.params
            netbox_tenant = self.nb.tenancy.tenants.create(params)

            logger.info(f"Region: {self.name} created successfully")
            self.api_object = netbox_tenant
        except Exception:
            logger.exception(f"Unable to create netbox tenant: {self.name}")
            raise

        return self.api_object

    def update(self, nb_tenant):
        try:
            # TODO: HotFix: Ensure slug is never empty
            if not self.params["slug"]:
                komora_id = self.params["custom_fields"].get("komora_id")
                if komora_id:
                    self.slug = komora_id
                else:
                    # Fallback if komora_id is also empty
                    self.slug = f"tenant-{self.name}"[:63]
            if nb_tenant.update(self.params):
                self.api_object = nb_tenant
                logger.info(f"Tenant: {self.name} updated successfully")
        except Exception:
            logger.exception(f"Unable to update tenant: {self.name} {nb_tenant.id}", exc_info=False)

    def synchronize(self):
        tenant = self.find()

        if tenant:
            self.update(tenant)
        else:
            self.create()

    @property
    def params(self):
        return {
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "custom_fields": self.custom_fields,
        }
