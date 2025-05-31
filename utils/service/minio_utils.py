from minio import Minio
from io import BytesIO
import uuid
import os
from django.core.exceptions import ValidationError
from django.conf import settings

# 初始化MinIO客户端
minio_client = Minio(
    settings.MINIO_STORAGE_ENDPOINT,
    access_key=settings.MINIO_STORAGE_ACCESS_KEY,
    secret_key=settings.MINIO_STORAGE_SECRET_KEY,
    secure=settings.MINIO_STORAGE_USE_HTTPS
)


def validate_image_file(file):
    """验证图片文件"""
    allowed_types = ['image/jpeg', 'image/png', 'image/gif']
    if file.content_type not in allowed_types:
        raise ValidationError("只支持JPEG/PNG/GIF格式的图片")

    # 验证文件大小（最大5MB）
    max_size = settings.MINIO_MAX_UPLOAD_SIZE
    if file.size > max_size:
        raise ValidationError("图片大小不能超过5MB")


def upload_competition_image_to_minio(uploaded_files, bucket_name=settings.MINIO_STORAGE_MEDIA_BUCKET_NAME, prefix=settings.MINIO_STORAGE_MEDIA_COMPETITIONS):
    """
    上传多张图片到MinIO并返回URL列表
    :param uploaded_files: 一个包含InMemoryUploadedFile对象的列表
    :param bucket_name: 存储桶名称
    :param prefix: 存储路径前缀
    :return: 图片访问URL列表
    """
    image_urls = []
    for uploaded_file in uploaded_files:
        # 验证图片
        validate_image_file(uploaded_file)

        # 生成唯一文件名
        ext = os.path.splitext(uploaded_file.name)[1].lower()
        object_name = f"{prefix}/{uuid.uuid4().hex}{ext}"

        # 确保存储桶存在
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)

        # 读取文件内容
        file_data = uploaded_file.read()

        # 上传到MinIO
        minio_client.put_object(
            bucket_name=bucket_name,
            object_name=object_name,
            data=BytesIO(file_data),
            length=len(file_data),
            content_type=uploaded_file.content_type
        )

        # 构造图片的访问 URL
        image_url = f"{settings.MINIO_STORAGE_ENDPOINT}/{bucket_name}/{object_name}"
        image_urls.append(image_url)

    return image_urls


def validate_pdf_file(file):
    """验证PDF文件"""
    if file.content_type != 'application/pdf':
        raise ValidationError("只支持PDF格式的文件")

    # 验证文件大小（最大10MB）
    max_size = settings.MINIO_MAX_UPLOAD_SIZE
    if file.size > max_size:
        raise ValidationError("文件大小不能超过10MB")

def upload_patent_file_to_minio(uploaded_file, bucket_name=settings.MINIO_STORAGE_MEDIA_BUCKET_NAME, prefix=settings.MINIO_STORAGE_MEDIA_PATENTS):
    """
    上传专利文件到MinIO并返回URL
    :param uploaded_file: InMemoryUploadedFile对象
    :param bucket_name: 存储桶名称
    :param prefix: 存储路径前缀
    :return: 文件访问URL
    """
    # 验证文件
    validate_pdf_file(uploaded_file)

    # 生成唯一文件名
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    object_name = f"{prefix}/{uuid.uuid4().hex}{ext}"

    # 确保存储桶存在
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)

    # 读取文件内容
    file_data = uploaded_file.read()

    # 上传到MinIO
    minio_client.put_object(
        bucket_name=bucket_name,
        object_name=object_name,
        data=BytesIO(file_data),
        length=len(file_data),
        content_type=uploaded_file.content_type
    )

    # 构造文件的访问 URL
    return f"{settings.MINIO_STORAGE_ENDPOINT}/{bucket_name}/{object_name}"


def upload_paper_file_to_minio(uploaded_file, bucket_name=settings.MINIO_STORAGE_MEDIA_BUCKET_NAME, prefix=settings.MINIO_STORAGE_MEDIA_PAPERS):
    """
    上传专利文件到MinIO并返回URL
    :param uploaded_file: InMemoryUploadedFile对象
    :param bucket_name: 存储桶名称
    :param prefix: 存储路径前缀
    :return: 文件访问URL
    """
    # 验证文件
    validate_pdf_file(uploaded_file)

    # 生成唯一文件名
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    object_name = f"{prefix}/{uuid.uuid4().hex}{ext}"

    # 确保存储桶存在
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)

    # 读取文件内容
    file_data = uploaded_file.read()

    # 上传到MinIO
    minio_client.put_object(
        bucket_name=bucket_name,
        object_name=object_name,
        data=BytesIO(file_data),
        length=len(file_data),
        content_type=uploaded_file.content_type
    )

    # 构造文件的访问 URL
    return f"{settings.MINIO_STORAGE_ENDPOINT}/{bucket_name}/{object_name}"


def delete_files_from_minio(file_urls, bucket_name=settings.MINIO_STORAGE_MEDIA_BUCKET_NAME):
    """删除MinIO上的文件"""
    # 分割出URL中的文件名
    if ',' not in file_urls:
        # 直接处理单个文件
        object_name = file_urls.split('media/')[-1]
        try:
            minio_client.remove_object(bucket_name, object_name)
        except Exception as e:
            raise ValidationError(f"删除文件 {object_name} 时出错: {e}")
    else:
        # 如果是多个文件的 URL
        object_names = file_urls.split(",")
        for object_name in object_names:
            # 找到 URL 中 `/media/` 之后的部分，即需要保留的路径
            object_name = object_name.split('media/')[-1]
            try:
                minio_client.remove_object(bucket_name, object_name)
            except Exception as e:
                raise ValidationError(f"删除文件 {object_name} 时出错: {e}")