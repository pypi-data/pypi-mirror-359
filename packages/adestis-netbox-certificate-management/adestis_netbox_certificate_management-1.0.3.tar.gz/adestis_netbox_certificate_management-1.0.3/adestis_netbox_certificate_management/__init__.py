from netbox.plugins import PluginConfig
default_app_config = 'adestis_netbox_certificate_management.AdestisCertificateManagementConfig'



class AdestisCertificateManagementConfig(PluginConfig):
    name = 'adestis_netbox_certificate_management'
    verbose_name = 'Certificate Management'
    description = 'A NetBox plugin for managing certficates.'
    version = '1.0.3'
    author = 'ADESTIS GmbH'
    author_email = 'pypi@adestis.de'
    base_url = 'certificates'
    required_settings = []
    default_settings = {
        'top_level_menu' : True,
    }
    
    def ready(self):
        super().ready()
        from adestis_netbox_certificate_management.jobs import CertificateMetadataExtractorJob

config = AdestisCertificateManagementConfig
