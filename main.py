from fastapi import FastAPI
from PIL import Image
import pytesseract
import cv2
import os
import regex as re
import numpy as np
import boto3
from dotenv import load_dotenv
import platform
from tempfile import TemporaryDirectory
from pathlib import Path
from pdf2image import convert_from_path
from PyPDF2 import PdfReader
from chuanHoa import chuan_hoa_dau_cau_tieng_viet
from adminDoc import postAdminDoc
from book import postBook
from checkInfo import checkFullInfo
import requests

app = FastAPI()

# Load variables from .env file
load_dotenv()
s3_region = os.environ.get("STORAGE_AWS_REGION")
s3_access_key_id = os.environ.get("STORAGE_AWS_ACCESS_KEY_ID")
s3_secret_access_key = os.environ.get("STORAGE_AWS_SECRET_ACCESS_KEY")
s3_file_bucket = os.environ.get("S3_FILE_BUCKET_NAME")
asset_path = os.environ.get("ASSET_PATH")
poppler_path = os.environ.get("POPPLER_PATH")

if platform.system() == "Windows":
    # Windows also needs poppler_exe
    path_to_poppler_exe = Path(poppler_path)

# Path of the Input pdf
PDF_file = Path(asset_path)

# Store all the pages of the PDF in a variable
image_file_list = []


@app.get("/")
def index(id: str, type: str):
    # Access S3
    s3 = boto3.client(
        "s3",
        aws_access_key_id=s3_access_key_id,
        aws_secret_access_key=s3_secret_access_key,
        region_name=s3_region,
    )
    s3.download_file(s3_file_bucket, id + ".pdf", asset_path)

    reader = PdfReader(PDF_file)
    checkText = False
    textFromOCR = ""
    textPDF = ""
    test = {}

    for i, page in enumerate(reader.pages):
        raw_text = page.extract_text()
        if raw_text:
            checkText = True
            break

    if checkText == False:
        # Đọc ảnh từ file PDF
        with TemporaryDirectory() as tempdir:
            if platform.system() == "Windows":
                pdf_pages = convert_from_path(
                    PDF_file, 80, poppler_path=path_to_poppler_exe
                )
            else:
                pdf_pages = convert_from_path(PDF_file, 80)

        # Read in the PDF file at 500 DPI
        for i, page in enumerate(reader.pages):
            image = pdf_pages[i]
            opencvImage = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
            # cv2.imshow("Image", opencvImage)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()

            # Lưu ảnh trong ổ cứng như file tạm để có thể apply OCR
            filename = "{}.png".format(os.getpid())
            cv2.imwrite(filename, opencvImage)  # ghi ảnh vào filename

            # Load ảnh và apply nhận dạng bằng Tesseract OCR
            textFromOCR = pytesseract.image_to_string(
                Image.open(filename), lang="vie"
            )  # có nhiều ngôn ngữ thì trong lang các ngôn ngữ cách nhau bằng dấu  +
            # """ Cần chú ý các chế độ nhận diện được điều chỉnh bằng config """

            # Thực hiện chuyển đổi xong thì xóa ảnh tạm
            os.remove(filename)

            # In dòng chữ nhận dạng được
            if type == "book":
                temp = postBook(textFromOCR)
            else: 
                temp = postAdminDoc(textFromOCR)
            if temp is not None and test is not None:
                test = test.update(temp)
            elif test is None:
                test = temp
            if checkFullInfo(test, type):
                break

    else:
        for i, page in enumerate(reader.pages):
            textPDF = page.extract_text()
            if textPDF:
                if type == "book":
                    temp = postBook(textPDF)
                else: 
                    temp = postAdminDoc(textPDF)
                if temp is not None and test is not None:
                    test = test.update(temp)
                elif test is None:
                    test = temp
                if checkFullInfo(test, type):
                    break


    # Phân tích text

    # text = chuan_hoa_dau_cau_tieng_viet(textFromOCR)

    # print(text)

    # # print(test)
    # print(text)

    s=""
    print(s)
    
    if type == "book":
        if test is not None and "isbn" in test:
            response = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:" + test["isbn"])
            resData = response.json()
            if resData["totalItems"] > 0:
                item = resData["items"][0]["volumeInfo"]
                if "description" in item:
                    s = item["description"]
                if "subtitle" in item:
                    s = item["subtitle"]
                else:
                    s = item["title"]
        if test is not None and "title" in test and "author" in test:
            response = requests.get("https://www.googleapis.com/books/v1/volumes?q=intitle:" + test["title"] + "&inauthor:" + test["author"])
            resData = response.json()
            if resData["totalItems"] > 0:
                item = resData["items"][0]["volumeInfo"]
                print(item)

                if item["title"].upper() == test["title"].upper() and item["authors"]:
                    if "description" in item:
                        s = item["description"]
        elif test is not None and "body" in test:
            s = test["body"]
    else:
        if "tieu_de" in test:
            s = test["tieu_de"]

    response = requests.get("https://langchain-server-6xga72vola-as.a.run.app/?type="+ type +"&title="+s)
    
    return {"dataLang": response.json(), "dataOcr": test}
