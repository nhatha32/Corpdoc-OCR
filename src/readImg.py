from tempfile import TemporaryDirectory
from PIL import Image
import pytesseract
import cv2
import os
from pdf2image import convert_from_path
import numpy as np
from dotenv import load_dotenv
import platform
from pathlib import Path

# Load variables from .env file
load_dotenv()
s3_region = os.environ.get("STORAGE_AWS_REGION")
s3_access_key_id = os.environ.get("STORAGE_AWS_ACCESS_KEY_ID")
s3_secret_access_key = os.environ.get("STORAGE_AWS_SECRET_ACCESS_KEY")
s3_file_bucket = os.environ.get("S3_FILE_BUCKET_NAME")
asset_path = os.environ.get("ASSET_PATH")
poppler_path = os.environ.get("POPPLER_PATH")
gg_api = os.environ.get("GOOGLE_API")
langchain_api = os.environ.get("LANGCHAIN_API")

if platform.system() == "Windows":
    # Windows also needs poppler_exe
    path_to_poppler_exe = Path(poppler_path)

# Path of the Input pdf
PDF_file = Path(asset_path)

# Store all the pages of the PDF in a variable
image_file_list = []


# Đọc ảnh từ file PDF
def readImg(i, inputPath):
    PDF_file = Path(inputPath)
    with TemporaryDirectory() as tempdir:
        if platform.system() == "Windows":
            pdf_pages = convert_from_path(
                PDF_file, 80, poppler_path=path_to_poppler_exe
            )
        else:
            pdf_pages = convert_from_path(PDF_file, 80)

    image = pdf_pages[i]
    opencvImage = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
    # cv2.imshow("Image", opencvImage)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # Lưu ảnh trong ổ cứng như file tạm để có thể apply OCR
    filename = "{}.png".format(os.getpid())
    cv2.imwrite(filename, opencvImage)  # ghi ảnh vào filename

    # Load ảnh và apply nhận dạng bằng Tesseract OCR
    textFromFile = pytesseract.image_to_string(
        Image.open(filename), lang="vie"
    )  # có nhiều ngôn ngữ thì trong lang các ngôn ngữ cách nhau bằng dấu  +
    # """ Cần chú ý các chế độ nhận diện được điều chỉnh bằng config """

    # Thực hiện chuyển đổi xong thì xóa ảnh tạm
    os.remove(filename)

    return textFromFile
