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
    inputPath = asset_path + id + ".pdf"
    # Access S3
    s3 = boto3.client(
        "s3",
        aws_access_key_id=s3_access_key_id,
        aws_secret_access_key=s3_secret_access_key,
        region_name=s3_region,
    )
    s3.download_file(s3_file_bucket, id + ".pdf", inputPath)

    # Path of the Input pdf
    PDF_file = Path(inputPath)

    #################################################
    ##### CHECKTYPE #################################

    reader = PdfReader(PDF_file)
    textFromOCR = ""
    textPDF = ""
    ocrVal = {"body": ""}
    typeDoc = ""

    textPDF = reader.pages[0].extract_text()
    if len(textPDF) > 10:
        ocrVal["body"] = textPDF
        checkType = chuan_hoa_dau_cau_tieng_viet(textPDF)
        if re.search("cộng hòa xã hội chủ nghĩa việt nam", checkType):
            typeDoc = "admin-doc"
        else:
            typeDoc = "book"
    else:
        ocrVal["body"] = readImg(0, inputPath)
        checkType = chuan_hoa_dau_cau_tieng_viet(ocrVal["body"])
        checkAdminDoc = re.search(
            "cộng hòa xã hội chủ nghĩa việt nam|cọng hòa xã hội chủ nghĩa việt nam",
            checkType,
        )
        if checkAdminDoc:
            typeDoc = "admin-doc"
        else:
            typeDoc = "book"

    if typeDoc == "book":
        if reader.pages[1].extract_text():
            for i, page in enumerate(reader.pages):
                textBook = page.extract_text()
                if len(textBook) > 700:
                    valInPage = postBook(textBook)
                    if valInPage is not None:
                        ocrVal.update(valInPage)
                        break
                    if i == 2:
                        ocrVal["body"] = textBook
        else:
            ocrVal["body"] = readImg(2, inputPath)
    else:
        textExtract = reader.pages[0].extract_text()
        if len(textExtract) > 10:
            textAdmin = textExtract
        else:
            textAdmin = readImg(0, inputPath)
        if textAdmin:
            valInPage = postAdminDoc(textAdmin)
            if valInPage is not None:
                ocrVal.update(valInPage)
                ocrVal["body"] = textAdmin

    # Phân tích text

    # print(text)

    langchainInput = ""

    if typeDoc == "book":
        if "isbn" in ocrVal:
            response = requests.get(gg_api + "q=isbn:" + ocrVal["isbn"])
            resData = response.json()
            if resData["totalItems"] > 0:
                item = resData["items"][0]["volumeInfo"]
                if "description" in item:
                    langchainInput = item["description"]
                else:
                    langchainInput = ocrVal["body"]
        if "title" in ocrVal and "author" in ocrVal:
            response = requests.get(
                gg_api + "q=intitle:" + ocrVal["title"] + "&inauthor:" + ocrVal["author"]
            )
            resData = response.json()
            if resData["totalItems"] > 0:
                item = resData["items"][0]["volumeInfo"]
                if item["title"].upper() == ocrVal["title"].upper():
                    if "description" in item:
                        langchainInput = item["description"]
                    else:
                        langchainInput = ocrVal["body"]
            else:
                langchainInput = ocrVal["body"]
    else:
        if "tieu_de" in ocrVal:
            langchainInput = ocrVal["tieu_de"]

    response = requests.get(langchain_api + "type=" + typeDoc + "&title=" + langchainInput)

    os.remove(PDF_file)

    return {"dataLang": response.json(), "dataOcr": ocrVal}
