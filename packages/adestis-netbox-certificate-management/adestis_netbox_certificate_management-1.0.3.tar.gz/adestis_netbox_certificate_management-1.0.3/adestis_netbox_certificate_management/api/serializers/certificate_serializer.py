from rest_framework import serializers
from adestis_netbox_certificate_management.models.certificate import Certificate, ContactAssignment, DeviceAssignment, ClusterAssignment, ClusterGroupAssignment, VirtualMachineAssignment
from netbox.api.serializers import NetBoxModelSerializer

from tenancy.models import *
from tenancy.api.serializers import *
from dcim.api.serializers import *
from dcim.models import *
from virtualization.api.serializers import *

class CertificateSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:adestis_netbox_certificate_management-api:certificate-detail'
    )
    

    class Meta:
        model = Certificate
        fields = ('id', 'tags', 'custom_fields', 'display', 'url', 'created', 'last_updated',
                  'custom_field_data', 'status', 'comments', 'certificate', 'tenant', 'tenant_group', 'valid_from', 'valid_to', 'subject', 'subject_alternative_name', 'key_technology', 'device', 'virtual_machine', 'cluster', 'cluster_group', 'contact', 'contact_group', 'issuer_parent_certificate', 'issuer', 'contact_group', 'predecessor_certificate')
        brief_fields = ('id', 'tags', 'custom_fields', 'display', 'url', 'created', 'last_updated',
                        'custom_field_data', 'status','certificate', 'tenant', 'tenant_group', 'valid_from', 'valid_to', 'subject', 'subject_alternative_name', 'key_technology', 'device', 'virtual_machine', 'cluster', 'cluster_group', 'contact', 'contact_group', 'issuer_parent_certificate', 'issuer', 'contact_group',  'predecessor_certificate', 'comments')

class DeviceAssignmentSerializer(NetBoxModelSerializer):
    certificate = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = DeviceAssignment
        fields = ('id', 'certificate', 'device')
        
class ClusterAssignmentSerializer(NetBoxModelSerializer):
    certificate = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = ClusterAssignment
        fields = ('id', 'certificate', 'cluster')
        
class ClusterGroupAssignmentSerializer(NetBoxModelSerializer):
    certificate = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = ClusterGroupAssignment
        fields = ('id', 'certificate', 'cluster_group')
        
class VirtualMachineAssignmentSerializer(NetBoxModelSerializer):
    certificate = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = VirtualMachineAssignment
        fields = ('id', 'certificate', 'virtual_machine')
        
class ContactAssignmentSerializer(NetBoxModelSerializer):
    certificate = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = ContactAssignment
        fields = ('id', 'certificate', 'contact')
        
# class ApplicationAssignmentSerializer(NetBoxModelSerializer):
#     certificate = serializers.PrimaryKeyRelatedField(read_only=True)
#     class Meta:
#         model = ApplicationAssignment
#         fields = ('id', 'certificate', 'installedapplication')