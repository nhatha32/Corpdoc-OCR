###################### LIBRARY ######################################

import os
import platform
from fastapi import FastAPI
import regex as re
import boto3
from dotenv import load_dotenv
from pathlib import Path
from PyPDF2 import PdfReader
import requests

##################################################################
##################################################################


#######################   FUNCTION   #############################

from src.chuanHoa import chuan_hoa_dau_cau_tieng_viet
from src.adminDoc import postAdminDoc
from src.book import postBook
from src.checkInfo import checkFullInfo
from src.readImg import readImg

##################################################################
##################################################################

app = FastAPI()

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


@app.get("/")
def index(id: str):
    # Access S3
    s3 = boto3.client(
        "s3",
        aws_access_key_id=s3_access_key_id,
        aws_secret_access_key=s3_secret_access_key,
        region_name=s3_region,
    )
    s3.download_file(s3_file_bucket, id + ".pdf", asset_path + id + ".pdf")

    # Path of the Input pdf
    PDF_file = Path(asset_path + id + ".pdf")

    #################################################
    ##### CHECKTYPE #################################

    reader = PdfReader(PDF_file)
    checkText = False
    textFromOCR = ""
    textPDF = ""
    test = {"body": ""}
    typeDoc = ""

    textPDF = reader.pages[0].extract_text()
    if len(textPDF) > 10:
        test["body"] = textPDF
        temp = chuan_hoa_dau_cau_tieng_viet(textPDF)
        if re.search("cộng hòa xã hội chủ nghĩa việt nam", temp):
            typeDoc = "admin-doc"
        else:
            typeDoc = "book"
    else:
        test["body"] = readImg(0, id)
        temp = chuan_hoa_dau_cau_tieng_viet(test["body"])
        temp1 = re.search(
            "cộng hòa xã hội chủ nghĩa việt nam|cọng hòa xã hội chủ nghĩa việt nam",
            temp,
        )
        if temp1:
            typeDoc = "admin-doc"
        else:
            typeDoc = "book"

    if typeDoc == "book":
        if reader.pages[1].extract_text():
            for i, page in enumerate(reader.pages):
                textBook = page.extract_text()
                if len(textBook) > 700:
                    temp = postBook(textBook)
                    if temp is not None:
                        test.update(temp)
                        break
                    if i == 2:
                        test["body"] = textBook
        else:
            test["body"] = readImg(2, id)
    else:
        temp = reader.pages[0].extract_text()
        if len(temp) > 10:
            textAdmin = temp
        else:
            textAdmin = readImg(0, id)
        if textAdmin:
            temp = postAdminDoc(textAdmin)
            if temp is not None:
                test.update(temp)
                test["body"] = textAdmin

    # Phân tích text

    # print(text)

    s = ""

    if typeDoc == "book":
        if "isbn" in test:
            response = requests.get(gg_api + "q=isbn:" + test["isbn"])
            resData = response.json()
            if resData["totalItems"] > 0:
                item = resData["items"][0]["volumeInfo"]
                if "description" in item:
                    s = item["description"]
                else:
                    s = test["body"]
        if "title" in test and "author" in test:
            response = requests.get(
                gg_api + "q=intitle:" + test["title"] + "&inauthor:" + test["author"]
            )
            resData = response.json()
            if resData["totalItems"] > 0:
                item = resData["items"][0]["volumeInfo"]
                if item["title"].upper() == test["title"].upper():
                    if "description" in item:
                        s = item["description"]
                    else:
                        s = test["body"]
            else:
                s = test["body"]
    else:
        if "tieu_de" in test:
            s = test["tieu_de"]

    response = requests.get(langchain_api + "type=" + typeDoc + "&title=" + s)

    os.remove(PDF_file)

    return {"dataLang": response.json(), "dataOcr": test}
