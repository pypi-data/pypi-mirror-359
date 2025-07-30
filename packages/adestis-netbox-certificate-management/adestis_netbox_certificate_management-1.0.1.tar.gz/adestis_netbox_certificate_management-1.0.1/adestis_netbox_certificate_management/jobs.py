from adestis_netbox_certificate_management.models import Certificate
import logging

from core.choices import JobIntervalChoices
from netbox.jobs import JobRunner, system_job
import cert_utils 

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import ExtensionOID
from django.utils.translation import gettext_lazy as _

    
# @system_job(interval=JobIntervalChoices.INTERVAL_MINUTELY)
class CertificateMetadataExtractorJob(JobRunner):
    class Meta:
        name = "Zertifikats-Metadaten extrahieren"
        model = Certificate 
        
    def run(self, *args, **kwargs):
        logger = logging.getLogger('CertificateMetadataExtractorJob')
        
        logger.warning("Starting to import certificates")
        
        for certificate in Certificate.objects.all():
                x509cert = x509.load_pem_x509_certificate(certificate.certificate.encode('utf-8'), default_backend())
                # logger.warning(f"type(certificate): {type(certificate)}")
                # logger.warning(f"type(certificate.certificate): {type(certificate.certificate)}")
                # logger.warning(f"certificate.certificate: {certificate.certificate}")
                        
                subject_key_identifier = x509cert.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_KEY_IDENTIFIER)
                subject_hex = subject_key_identifier.value.digest.hex()
                        
                authority_key_identifier = x509cert.extensions.get_extension_for_oid(ExtensionOID.AUTHORITY_KEY_IDENTIFIER)
                authority_hex = authority_key_identifier.value.key_identifier.hex()
                
                certificate.subject_key_identifier = subject_hex
                issuer_parent_certificate = Certificate.objects.filter(
                subject_key_identifier=authority_hex
                ).first()
                
                cert_data = cert_utils.parse_cert(certificate.certificate)
                issuer = cert_data["issuer"].replace("\n", ";").strip()
                common_name = cert_data["subject"]
                for name,value in [ (pair.split("=")) for pair in cert_data["subject"].split("\n") ]:
                    if name == "CN":
                        common_name=value

                certificate.valid_from=cert_data["startdate"].date()
                certificate.valid_to=cert_data["enddate"].date()
                issuer=issuer
                certificate.subject=common_name
                certificate.authority_key_identifier = issuer_parent_certificate
                certificate.key_technology=cert_data["key_technology"]
                certificate.subject_alternative_name=cert_data.get("SubjectAlternativeName", "")

                
                certificate.save(update_fields=["subject_key_identifier", "authority_key_identifier", "valid_from", "valid_to", "subject", "issuer", "subject_alternative_name", "key_technology"])

                # logger.warning(subject_hex)
                # logger.warning(authority_hex)