###################### LIBRARY ###################################

import os
import platform
import regex as re
import boto3
from pathlib import Path
from PyPDF2 import PdfReader
import requests
import pika
import json

##################################################################
##################################################################


#######################   FUNCTION   #############################

from chuanHoa import chuan_hoa_dau_cau_tieng_viet
from adminDoc import postAdminDoc
from book import postBook
from checkInfo import checkFullInfo
from readImg import readImg
from rabbitMQ import producer_channel

##################################################################
##################################################################

#######################   VARIABLE   #############################

from envLoader import (
    s3_region,
    s3_access_key_id,
    s3_secret_access_key,
    s3_file_bucket,
    asset_path,
    poppler_path,
    gg_api,
    amqp_langchain_queue,
)

##################################################################
##################################################################

if platform.system() == "Windows":
    # Windows also needs poppler_exe
    path_to_poppler_exe = Path(poppler_path)

# Path of the Input pdf
PDF_file = Path(asset_path)

# Store all the pages of the PDF in a variable
image_file_list = []


def OCRProcessor(companyId, fileId):
    inputPath = asset_path + fileId + ".pdf"
    # Access S3
    s3 = boto3.client(
        "s3",
        aws_access_key_id=s3_access_key_id,
        aws_secret_access_key=s3_secret_access_key,
        region_name=s3_region,
    )
    s3.download_file(s3_file_bucket, fileId + ".pdf", inputPath)

    # Path of the Input pdf
    PDF_file = Path(inputPath)

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
        test["body"] = readImg(0, inputPath)
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
            test["body"] = readImg(2, inputPath)
    else:
        temp = reader.pages[0].extract_text()
        if len(temp) > 10:
            textAdmin = temp
        else:
            textAdmin = readImg(0, inputPath)
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

    os.remove(PDF_file)

    data_string = json.dumps(
        {
            "data": {
                "fileId": fileId,
                "companyId": companyId,
                "type": typeDoc,
                "title": s,
                "ocr": test,
            }
        }
    )
    
    # Send message to Langchain queue
    producer_channel.queue_declare(queue=amqp_langchain_queue, durable=True)
    producer_channel.basic_qos(prefetch_count=10)
    producer_channel.basic_publish(
        exchange="",
        routing_key=amqp_langchain_queue,
        body=data_string,
        properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent),
    )
