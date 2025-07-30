from django.db import models 
from django.urls import reverse
# from fieldsignals import pre_save_changed
from netbox.models import NetBoxModel
from core.choices import JobIntervalChoices

from utilities.choices import ChoiceSet
from tenancy.models import *
from dcim.models import *
from virtualization.models import *
from adestis_netbox_applications.models import InstalledApplication
import datetime
from taggit.managers import TaggableManager

__all__ = (
    'CertificateStatusChoices',
    'Certificate',
    # 'fieldsignals',
)

class CertificateStatusChoices(ChoiceSet):
    key = 'Certificates.status'

    STATUS_ACTIVE = 'active'
    STATUS_INACTIVE = 'inactive'

    CHOICES = [
        (STATUS_ACTIVE, 'Active', 'green'),
        (STATUS_INACTIVE, 'Inactive', 'red'),
    ]
class Certificate(NetBoxModel):

    status = models.CharField(
        max_length=50,
        choices=CertificateStatusChoices,
        verbose_name='Status',
        help_text='Status'
    )

    comments = models.TextField(
        blank=True
    )
    
    name = models.CharField(
        max_length=150
    )
    
    description = models.CharField(
        max_length=500,
        blank = True
    )
    
    subject = models.CharField(
        max_length=2000,
        verbose_name='Common Name',
        blank=True
    )
    
    supplier_product = models.CharField(
        max_length=2000,
        verbose_name='Supplier Product',
        blank=True
    )
    
    issuer = models.CharField(
        max_length=2000,
        verbose_name='Issuer',
        blank=True
    )
    
    issuer_parent_certificate = models.ForeignKey(
        'self',
        verbose_name='Issuer (Parent Certificate)',
        on_delete = models.CASCADE,
        null=True,
        related_name='issued_certificates'
    )
    
    authority_key_identifier = models.ForeignKey(
        'self',
        verbose_name='Parent Certificate',
        on_delete = models.CASCADE,
        null=True,
        blank=True,
        related_name='authority_certificates'
    )
    
    subject_key_identifier = models.CharField(
        max_length=40,
        unique=True,
        null=False,
        blank=False
    )
    
    key_technology = models.CharField(
        max_length=2000,
        verbose_name='Key Technology',
        blank=True
    )
    
    subject_alternative_name = models.CharField(
        max_length=2000,
        verbose_name='Subject Alternative Names',
        blank=True,
        null=True
    )
    
    valid_from = models.DateField(
        null=True,
        blank=True,
        verbose_name='Valid from',
        help_text='Start of validity'
    )
    
    valid_to = models.DateField(
        null=True,
        blank=True,
        verbose_name='Valid to',
        help_text='End of validity'
    )
    
    contact_group = models.ForeignKey(
        to = 'tenancy.ContactGroup',
        on_delete = models.PROTECT,
        related_name='certificate',
        verbose_name='Supplier',
        blank = True,
        null = True,
    )
    
    certificate = models.CharField(
        verbose_name='Certificate',
        help_text='The certificate to be linked to the certificate chain',
        unique=True,
        max_length=10000,
    )
    
    virtual_machine = models.ManyToManyField(
        to='virtualization.VirtualMachine',
        through='VirtualMachineAssignment',
        related_name= 'certificate',
        verbose_name='Virtual Machines',
        blank = True
    )
    
    device = models.ManyToManyField(
        to = 'dcim.Device',
        through='DeviceAssignment',
        related_name= 'certificate',
        verbose_name='Devices',
        blank = True
    )
    
    tenant = models.ForeignKey(
         to = 'tenancy.Tenant',
         on_delete = models.PROTECT,
         related_name = 'certificate_tenant',
         null = True,
         verbose_name='Tenant',
         blank = True
     )
    
    tenant_group = models.ForeignKey(
        to= 'tenancy.TenantGroup',
        on_delete= models.PROTECT,
        related_name='certificate_tenant_group',
        null = True,
        verbose_name= 'Tenant Group',
        blank = True
    )
    
    installedapplication = models.ManyToManyField(
        'adestis_netbox_applications.InstalledApplication',
        # through='ApplicationAssignment',
        related_name='certificate_application',
        verbose_name='Applications',
        blank = True
    ) 
    
    contact = models.ManyToManyField(
        to = 'tenancy.Contact',
        through='ContactAssignment',
        related_name='certificate',
        verbose_name='Contacts',
        blank = True
    )
    
    cluster = models.ManyToManyField(
        to = 'virtualization.Cluster',
        through='ClusterAssignment',
        related_name = 'certificate',
        verbose_name='Clusters',
        blank = True
    )
    
    cluster_group = models.ManyToManyField(
        to = 'virtualization.ClusterGroup',
        through='ClusterGroupAssignment',
        related_name = 'certificate',
        verbose_name='Cluster Groups',
        blank = True
    )
    
    predecessor_certificate = models.ManyToManyField(
        'self',
        related_name = 'certificate',
        verbose_name='Predecessor Certificate',
        blank=True
    )
    
    successor_certificates = models.ManyToManyField(
        'self',
        related_name = 'certificate',
        verbose_name='Successor Certificate',
        blank=True
    )
    
    class Meta:
        verbose_name_plural = "Certificates"
        verbose_name = 'Certificate'

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('plugins:adestis_netbox_certificate_management:certificate', args=[self.pk])

    def get_status_color(self):
        return CertificateStatusChoices.colors.get(self.status)
    
    def save(self, *args, **kwargs):
        from adestis_netbox_certificate_management.jobs import CertificateMetadataExtractorJob
        CertificateMetadataExtractorJob.enqueue_once()
        return super().save(*args, **kwargs)

    def sync(self):
        from adestis_netbox_certificate_management.jobs import CertificateMetadataExtractorJob
        CertificateMetadataExtractorJob.enqueue()

class DeviceAssignment(NetBoxModel):
    
    device = models.ForeignKey(
        to='dcim.Device',
        on_delete=models.CASCADE,
        related_name="certificate_device_assignments",
        verbose_name="Device"
    )
    
    tags = TaggableManager(related_name='certificate_deviceassignment_tags')
    
    certificate = models.ForeignKey('Certificate', on_delete=models.CASCADE)
    
class ClusterAssignment(NetBoxModel):
    
    cluster = models.ForeignKey(
        to='virtualization.Cluster',
        on_delete=models.CASCADE,
        related_name="certificate_cluster_assignments",
        verbose_name="Cluster"
    )
    
    tags = TaggableManager(related_name='certificate_clusterassignment_tags')
    
    certificate = models.ForeignKey('Certificate', on_delete=models.CASCADE)
      
class ClusterGroupAssignment(NetBoxModel):
    
    cluster_group = models.ForeignKey(
        to='virtualization.ClusterGroup',
        on_delete=models.CASCADE,
        related_name="certificate_cluster_group_assignments",
        verbose_name="Cluster Group"
    )
    
    tags = TaggableManager(related_name='certificate_clustergroupassignment_tags')
    
    certificate = models.ForeignKey('Certificate', on_delete=models.CASCADE)
    
class VirtualMachineAssignment(NetBoxModel):
    
    virtual_machine = models.ForeignKey(
        to='virtualization.VirtualMachine',
        on_delete=models.CASCADE,
        related_name="certificate_virtual_machine_assignments",
        verbose_name="Cluster"
    )
    
    tags = TaggableManager(related_name='certificate_virtualmachineassignment_tags')
    
    certificate = models.ForeignKey('Certificate', on_delete=models.CASCADE)
    
# class ApplicationAssignment(NetBoxModel):
    
#     installedapplication = models.ForeignKey(
#         to= 'adestis_netbox_applications.InstalledApplication',
#         on_delete=models.CASCADE,
#         related_name="certificate_application_assignments",
#         verbose_name="Application"
#     )

#     certificate = models.ForeignKey('Certificate', on_delete=models.CASCADE)
    
#     class Meta:
#         unique_together = ('certificate', 'installedapplication')
class ContactAssignment(NetBoxModel):
    
    contact = models.ForeignKey(
        to = 'tenancy.Contact',
        on_delete=models.CASCADE,
        related_name="certificate_contact_assignment",
        verbose_name="Contact"
    )
    
    certificate = models.ForeignKey('Certificate', on_delete=models.CASCADE)
    
    tags = TaggableManager(related_name='certificate_contactassignment_tags')          