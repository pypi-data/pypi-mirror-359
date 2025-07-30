from netbox.tables import NetBoxTable, ChoiceFieldColumn, columns
from adestis_netbox_certificate_management.models.certificate import *
from adestis_netbox_certificate_management.filtersets import *
import django_tables2 as tables
from dcim.models import *
from virtualization.models import *
from tenancy.models import *
from adestis_netbox_applications.models import *


class CertificateTable(NetBoxTable):
    status = ChoiceFieldColumn()

    comments = columns.MarkdownColumn()

    tags = columns.TagColumn()
    
    name = columns.MarkdownColumn(
        linkify=True
    )
    
    description = columns.MarkdownColumn()
    
    valid_from = columns.DateColumn()
    
    valid_to = columns.DateColumn()
    
    tenant = tables.Column(
        linkify = True
    )
    
    tenant_group = tables.Column(
        linkify = True
    )
    
    certificate = tables.Column(
        linkify=True
    )
    
    installedapplication = tables.Column(
        linkify=True
    )
    
    contact = tables.Column(
        linkify=True
    )
    
    virtual_machine = tables.Column(
        linkify=True
    )
    
    cluster_group = tables.Column(
        linkify=True
    )
        
    cluster = tables.Column(
        linkify=True
    )
        
    device = tables.Column(
        linkify=True
    )
    
    predecessor_certificate = tables.Column(
        linkify=True
    )
    
    successor_certificates = tables.Column(
        linkify=True
    )
    
    issuer_parent_certificate = tables.Column(
        linkify=True
    )
    
    authority_key_identifier = tables.Column(
        linkify=True
    )

    class Meta(NetBoxTable.Meta):
        model = Certificate
        fields = [ 'name', 'pk', 'id', 'status', 'comments', 'actions', 'tags', 'created', 'last_updated', 'valid_from', 'valid_to', 'contact_group', 'authority_key_identifier', 'issuer_parent_certificate', 'subject', 'subject_alternative_name', 'key_technology', 'tenant', 'installedapplication', 'version', 'url', 'description', 'tags', 'tenant_group', 'cluster', 'cluster_group', 'virtual_machine', 'device', 'contact', 'successor_certificates', 'predecessor_certificate', 'certificate']
        default_columns = ['name', 'tenant', 'status', 'valid_from', 'valid_to', 'authority_key_identifier']
