from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    bucket_name = '5fdd6f1f-media'
    location = 'media'


class StaticStorage(S3Boto3Storage):
    bucket_name = '5fdd6f1f-media'
    location = 'static'
