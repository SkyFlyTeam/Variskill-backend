import io
import logging
import os
from pathlib import Path
from typing import BinaryIO, Optional, Union
from django.conf import settings

logger = logging.getLogger(__name__)

try:
    import boto3
    from botocore.client import Config
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError:  # pragma: no cover
    boto3 = None
    Config = None
    BotoCoreError = Exception
    ClientError = Exception


def _get_setting(name: str, default: str = '') -> str:
    # Dá prioridade às variáveis do processo/ambiente atual
    if name in os.environ:
        return os.environ[name] or ''
    if settings.configured:
        val = getattr(settings, name, None)
        if val is not None:
            return str(val)
    return default or ''


class BaseStorageService:
    """Interface base para os serviços de armazenamento de assets."""

    def exists(self, s3_key: str) -> bool:
        raise NotImplementedError

    def get_asset_url(self, s3_key: str) -> str:
        raise NotImplementedError

    def upload_asset(
        self,
        file_content: Union[bytes, BinaryIO, io.BytesIO],
        s3_key: str,
        content_type: Optional[str] = None,
    ) -> str:
        raise NotImplementedError



class LocalStorageService(BaseStorageService):
    """
    Modo Offline / Fallback Local.
    Salva e serve arquivos a partir de MEDIA_ROOT (/media/) sem requerer AWS,
    garantindo que testes e ambientes locais funcionem perfeitamente.
    """

    def __init__(self, media_root: Optional[Union[str, Path]] = None, media_url: Optional[str] = None):
        self.media_root = Path(media_root or _get_setting('MEDIA_ROOT', 'media'))
        self.media_url = media_url or _get_setting('MEDIA_URL', '/media/')
        if not self.media_url.endswith('/'):
            self.media_url += '/'

    def _normalize_key(self, s3_key: str) -> str:
        return s3_key.lstrip('/')

    def exists(self, s3_key: str) -> bool:
        clean_key = self._normalize_key(s3_key)
        target_path = self.media_root / clean_key
        return target_path.exists() and target_path.is_file()

    def get_asset_url(self, s3_key: str) -> str:
        clean_key = self._normalize_key(s3_key)
        return f"{self.media_url}{clean_key}"

    def upload_asset(
        self,
        file_content: Union[bytes, BinaryIO, io.BytesIO],
        s3_key: str,
        content_type: Optional[str] = None,
    ) -> str:
        clean_key = self._normalize_key(s3_key)
        target_path = self.media_root / clean_key
        target_path.parent.mkdir(parents=True, exist_ok=True)

        if isinstance(file_content, bytes):
            data = file_content
        elif hasattr(file_content, 'read'):
            data = file_content.read()
        else:
            raise ValueError("O conteúdo do arquivo deve ser bytes ou um stream legível.")

        target_path.write_bytes(data)
        logger.info("Asset salvo localmente em: %s", target_path)
        return self.get_asset_url(clean_key)


class S3StorageService(BaseStorageService):
    """
    Serviço centralizado de armazenamento na AWS S3 com suporte a CloudFront/Custom Domain.
    Se as credenciais AWS não estiverem configuradas, delega automaticamente para LocalStorageService.
    """

    def __init__(
        self,
        bucket_name: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None,
        region_name: Optional[str] = None,
        custom_domain: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        use_iam_role: Optional[bool] = None,
        fallback_service: Optional[BaseStorageService] = None,
    ):
        self.bucket_name = bucket_name if bucket_name is not None else _get_setting('AWS_STORAGE_BUCKET_NAME', '')
        self.aws_access_key_id = aws_access_key_id if aws_access_key_id is not None else _get_setting('AWS_ACCESS_KEY_ID', '')
        self.aws_secret_access_key = aws_secret_access_key if aws_secret_access_key is not None else _get_setting('AWS_SECRET_ACCESS_KEY', '')
        self.aws_session_token = aws_session_token if aws_session_token is not None else _get_setting('AWS_SESSION_TOKEN', '')
        self.region_name = region_name if region_name is not None else _get_setting('AWS_S3_REGION_NAME', 'us-east-1')
        self.custom_domain = custom_domain if custom_domain is not None else _get_setting('AWS_S3_CUSTOM_DOMAIN', '')
        self.endpoint_url = endpoint_url if endpoint_url is not None else _get_setting('AWS_ENDPOINT_URL', '')
        self.use_iam_role = (
            use_iam_role
            if use_iam_role is not None
            else _get_setting('AWS_USE_IAM_ROLE', 'False').lower() in ('true', '1', 'yes')
        )
        self.fallback_service = fallback_service or LocalStorageService()

        self._s3_client = None

    @property
    def is_configured(self) -> bool:
        """
        Indica se o armazenamento na nuvem AWS S3 está ativo:
        1. Se bucket_name e as chaves de acesso (access_key + secret) estiverem preenchidas;
        2. OU se bucket_name estiver preenchido e use_iam_role for True (EC2/ECS).
        """
        if not boto3 or not self.bucket_name:
            return False

        if self.aws_access_key_id and self.aws_secret_access_key:
            return True

        return bool(self.use_iam_role)

    @property
    def s3_client(self):
        if not self.is_configured:
            return None
        if self._s3_client is None:
            client_kwargs = {
                'service_name': 's3',
                'region_name': self.region_name,
                'config': Config(signature_version='s3v4') if Config else None,
            }
            # Se forneceu chaves explicitamente, utiliza-as; caso contrário o boto3 usa a IAM Role automaticamente
            if self.aws_access_key_id and self.aws_secret_access_key:
                client_kwargs['aws_access_key_id'] = self.aws_access_key_id
                client_kwargs['aws_secret_access_key'] = self.aws_secret_access_key
            if self.aws_session_token:
                client_kwargs['aws_session_token'] = self.aws_session_token
            if self.endpoint_url:
                client_kwargs['endpoint_url'] = self.endpoint_url

            self._s3_client = boto3.client(**client_kwargs)
        return self._s3_client

    def _normalize_key(self, s3_key: str) -> str:
        return s3_key.lstrip('/')

    def exists(self, s3_key: str) -> bool:
        """Verifica se o objeto realmente existe no bucket S3 (ou no fallback local)."""
        if not self.is_configured:
            return self.fallback_service.exists(s3_key)

        clean_key = self._normalize_key(s3_key)
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=clean_key)
            return True
        except (ClientError, BotoCoreError):
            return False

    def get_asset_url(self, s3_key: str) -> str:
        """
        Retorna a URL pública direta:
        1. Via CloudFront / Domínio customizado (se AWS_S3_CUSTOM_DOMAIN estiver preenchido).
        2. Via endpoint direto do bucket S3.
        3. Caso não configurado na AWS, delega para fallback local.
        """
        if not self.is_configured:
            return self.fallback_service.get_asset_url(s3_key)

        clean_key = self._normalize_key(s3_key)

        if self.custom_domain:
            domain = self.custom_domain.rstrip('/')
            if not (domain.startswith('http://') or domain.startswith('https://')):
                domain = f"https://{domain}"
            return f"{domain}/{clean_key}"

        # Endpoint S3 padrão da AWS
        if self.region_name and self.region_name != 'us-east-1':
            return f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{clean_key}"
        return f"https://{self.bucket_name}.s3.amazonaws.com/{clean_key}"

    def upload_asset(
        self,
        file_content: Union[bytes, BinaryIO, io.BytesIO],
        s3_key: str,
        content_type: Optional[str] = None,
    ) -> str:
        """
        Realiza upload com permissão de leitura pública (ACL public-read quando suportado).
        Caso AWS não esteja configurada ou ocorra erro crítico de credencial, recorre ao fallback local.
        """
        if not self.is_configured:
            logger.info("AWS S3 não configurado. Utilizando fallback local para upload do asset: %s", s3_key)
            return self.fallback_service.upload_asset(file_content, s3_key, content_type)

        clean_key = self._normalize_key(s3_key)

        if isinstance(file_content, bytes):
            body_stream = io.BytesIO(file_content)
        elif hasattr(file_content, 'read'):
            body_stream = file_content
        else:
            raise ValueError("O conteúdo do arquivo deve ser bytes ou um stream legível.")

        extra_args = {}
        if content_type:
            extra_args['ContentType'] = content_type

        try:
            # Tenta upload direto para o bucket S3
            self.s3_client.upload_fileobj(
                Fileobj=body_stream,
                Bucket=self.bucket_name,
                Key=clean_key,
                ExtraArgs=extra_args if extra_args else None,
            )
            logger.info("Asset enviado com sucesso para S3: bucket=%s, key=%s", self.bucket_name, clean_key)
            return self.get_asset_url(clean_key)
        except (BotoCoreError, ClientError) as exc:
            logger.error("Falha ao realizar upload para S3 (%s). Acionando fallback local: %s", exc, clean_key)
            # Reseta o cursor do stream caso possível antes de tentar o fallback local
            if hasattr(body_stream, 'seek'):
                try:
                    body_stream.seek(0)
                except Exception:
                    pass
            return self.fallback_service.upload_asset(body_stream, clean_key, content_type)


# Instância singleton padrão para conveniência
default_storage_service = S3StorageService()
