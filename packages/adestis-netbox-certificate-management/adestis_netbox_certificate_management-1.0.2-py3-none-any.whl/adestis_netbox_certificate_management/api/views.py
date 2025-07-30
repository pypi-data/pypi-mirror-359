from adestis_netbox_certificate_management.models.certificate import Certificate
from adestis_netbox_certificate_management.filtersets import *

from netbox.api.viewsets import NetBoxModelViewSet
from .serializers import CertificateSerializer


class CertificateViewSet(NetBoxModelViewSet):
    queryset = Certificate.objects.prefetch_related(
        'tags', 'cluster', 'cluster_group', 'virtual_machine', 'device', 'contact',
    )

    serializer_class = CertificateSerializer
    filterset_class = CertificateFilterSet
    # def post_queryset(self):
    #     certificate = certificate.objects.all()
    #     return certificate
    