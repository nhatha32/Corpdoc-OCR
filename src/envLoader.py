###################### LIBRARY ###################################

from dotenv import load_dotenv
import os

##################################################################
##################################################################

load_dotenv()

s3_region = os.environ.get("STORAGE_AWS_REGION")
s3_access_key_id = os.environ.get("STORAGE_AWS_ACCESS_KEY_ID")
s3_secret_access_key = os.environ.get("STORAGE_AWS_SECRET_ACCESS_KEY")
s3_file_bucket = os.environ.get("S3_FILE_BUCKET_NAME")
asset_path = os.environ.get("ASSET_PATH")
poppler_path = os.environ.get("POPPLER_PATH")
gg_api = os.environ.get("GOOGLE_API")
amqp_protocol = os.environ.get("AMQP_PROTOCOL")
amqp_username = os.environ.get("AMQP_USERNAME")
amqp_password = os.environ.get("AMQP_PASSWORD")
amqp_hostname = os.environ.get("AMQP_HOSTNAME")
amqp_vhost = os.environ.get("AMQP_VHOST")
amqp_ocr_queue = os.environ.get("AMQP_OCR_QUEUE")
amqp_langchain_queue = os.environ.get("AMQP_LANGCHAIN_QUEUE")