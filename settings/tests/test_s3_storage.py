import io
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
import boto3
from botocore.exceptions import ClientError, EndpointConnectionError

from settings.s3_storage import (
    BaseStorageService,
    LocalStorageService,
    S3StorageService,
)

pytestmark = [pytest.mark.unit]


class TestLocalStorageService:
    def test_get_asset_url(self, tmp_path):
        service = LocalStorageService(media_root=tmp_path, media_url="/media/")
        url = service.get_asset_url("badges/streak_7.png")
        assert url == "/media/badges/streak_7.png"

    def test_get_asset_url_with_leading_slash(self, tmp_path):
        service = LocalStorageService(media_root=tmp_path, media_url="/media/")
        url = service.get_asset_url("/avatars/dev_python.png")
        assert url == "/media/avatars/dev_python.png"

    def test_upload_asset_from_bytes(self, tmp_path):
        service = LocalStorageService(media_root=tmp_path, media_url="/media/")
        content = b"fake-png-content"
        url = service.upload_asset(content, "cosmeticos/borda_ouro.png", content_type="image/png")

        assert url == "/media/cosmeticos/borda_ouro.png"
        file_path = tmp_path / "cosmeticos" / "borda_ouro.png"
        assert file_path.exists()
        assert file_path.read_bytes() == content

    def test_upload_asset_from_stream(self, tmp_path):
        service = LocalStorageService(media_root=tmp_path, media_url="/media/")
        content = b"fake-stream-data"
        stream = io.BytesIO(content)
        url = service.upload_asset(stream, "conquistas/primeiro_passo.svg")

        assert url == "/media/conquistas/primeiro_passo.svg"
        file_path = tmp_path / "conquistas" / "primeiro_passo.svg"
        assert file_path.exists()
        assert file_path.read_bytes() == content


class TestS3StorageService:
    def test_unconfigured_service_falls_back_to_local_storage(self, tmp_path):
        fallback = LocalStorageService(media_root=tmp_path, media_url="/media/")
        service = S3StorageService(
            bucket_name="",
            aws_access_key_id="",
            aws_secret_access_key="",
            fallback_service=fallback,
        )

        assert service.is_configured is False
        assert service.s3_client is None

        # URL generation fallback
        assert service.get_asset_url("avatars/bot.png") == "/media/avatars/bot.png"

        # Upload fallback
        content = b"fallback-content"
        url = service.upload_asset(content, "avatars/bot.png")
        assert url == "/media/avatars/bot.png"
        assert (tmp_path / "avatars" / "bot.png").read_bytes() == content

    def test_configured_service_with_iam_role(self):
        with patch.dict("os.environ", {"AWS_USE_IAM_ROLE": "True"}):
            service = S3StorageService(
                bucket_name="variskill-assets",
                aws_access_key_id="",
                aws_secret_access_key="",
            )
            assert service.is_configured is True
            assert service.s3_client is not None


    def test_configured_service_url_standard_s3(self):
        service = S3StorageService(
            bucket_name="variskill-assets",
            aws_access_key_id="test-key",
            aws_secret_access_key="test-secret",
            region_name="us-east-1",
        )
        assert service.is_configured is True
        url = service.get_asset_url("badges/python_master.png")
        assert url == "https://variskill-assets.s3.amazonaws.com/badges/python_master.png"

    def test_configured_service_url_regional_s3(self):
        service = S3StorageService(
            bucket_name="variskill-assets",
            aws_access_key_id="test-key",
            aws_secret_access_key="test-secret",
            region_name="sa-east-1",
        )
        url = service.get_asset_url("badges/python_master.png")
        assert url == "https://variskill-assets.s3.sa-east-1.amazonaws.com/badges/python_master.png"

    def test_configured_service_url_custom_domain_cloudfront(self):
        service = S3StorageService(
            bucket_name="variskill-assets",
            aws_access_key_id="test-key",
            aws_secret_access_key="test-secret",
            custom_domain="cdn.variskill.com.br",
        )
        url = service.get_asset_url("avatars/hero.png")
        assert url == "https://cdn.variskill.com.br/avatars/hero.png"

    def test_configured_service_upload_success(self):
        service = S3StorageService(
            bucket_name="variskill-assets",
            aws_access_key_id="test-key",
            aws_secret_access_key="test-secret",
            custom_domain="https://cdn.variskill.com.br",
        )
        mock_client = MagicMock()
        service._s3_client = mock_client

        content = b"test-image-data"
        url = service.upload_asset(content, "cosmeticos/titulo_mestre.png", content_type="image/png")

        assert url == "https://cdn.variskill.com.br/cosmeticos/titulo_mestre.png"
        mock_client.upload_fileobj.assert_called_once()
        call_kwargs = mock_client.upload_fileobj.call_args[1]
        assert call_kwargs["Bucket"] == "variskill-assets"
        assert call_kwargs["Key"] == "cosmeticos/titulo_mestre.png"
        assert call_kwargs["ExtraArgs"] == {"ContentType": "image/png"}

    def test_configured_service_upload_failure_triggers_fallback(self, tmp_path):
        fallback = LocalStorageService(media_root=tmp_path, media_url="/media/")
        service = S3StorageService(
            bucket_name="variskill-assets",
            aws_access_key_id="test-key",
            aws_secret_access_key="test-secret",
            fallback_service=fallback,
        )
        mock_client = MagicMock()
        mock_client.upload_fileobj.side_effect = EndpointConnectionError(endpoint_url="https://s3.amazonaws.com")
        service._s3_client = mock_client

        content = b"offline-emergency-content"
        url = service.upload_asset(content, "offline/asset.png")

        assert url == "/media/offline/asset.png"
        assert (tmp_path / "offline" / "asset.png").read_bytes() == content

    def test_emulated_s3_end_to_end_with_moto(self):
        """Teste ponta a ponta simulando provisionamento de bucket e upload real via boto3/moto."""
        try:
            from moto import mock_aws
        except ImportError:
            pytest.skip("moto not installed")

        with mock_aws():
            bucket_name = "test-e2e-bucket"
            region = "us-east-1"
            client = boto3.client("s3", region_name=region, aws_access_key_id="mock", aws_secret_access_key="mock")
            client.create_bucket(Bucket=bucket_name)

            service = S3StorageService(
                bucket_name=bucket_name,
                aws_access_key_id="mock",
                aws_secret_access_key="mock",
                region_name=region,
            )

            test_data = b"avatar-bytes-content"
            stream = io.BytesIO(test_data)
            url = service.upload_asset(stream, "avatars/dev.png", content_type="image/png")

            assert url == f"https://{bucket_name}.s3.amazonaws.com/avatars/dev.png"

            # Valida que o objeto está fisicamente no bucket emulado
            obj = client.get_object(Bucket=bucket_name, Key="avatars/dev.png")
            assert obj["Body"].read() == test_data
            assert obj["ContentType"] == "image/png"

