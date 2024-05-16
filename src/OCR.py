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
from datetime import datetime

##################################################################
##################################################################


#######################   FUNCTION   #############################

from src.chuanHoa import chuan_hoa_dau_cau_tieng_viet
from src.chuanHoa import no_accent_vietnamese
from src.adminDoc import postAdminDoc
from src.book import postBook
from src.readImg import readImg
from src.rabbitMQ import params

##################################################################
##################################################################

#######################   VARIABLE   #############################

from src.envLoader import (
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

def OCRProcessor(companyId, userId, fileId):
    try:
        # Log request
        logRequest(companyId, userId, fileId)
        
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
        textFromOCR = ""
        textPDF = ""
        ocrVal = {"body": ""}
        typeDoc = ""

        if len(reader.pages) < 4:
            typeDoc = "admin-doc"
        else:
            textPDF = reader.pages[0].extract_text()
            if len(textPDF) > 10:
                ocrVal["body"] = textPDF
                # checkType = chuan_hoa_dau_cau_tieng_viet(ocrVal["body"])
                checkType = no_accent_vietnamese(ocrVal["body"]).lower()
                # print(checkType1)
                checkAdminDoc = re.search(
                    "cong hoa xa hoi chu nghia viet nam|xa hoi chu nghia viet nam",
                    checkType,
                )
                if checkAdminDoc:
                    typeDoc = "admin-doc"
                else:
                    typeDoc = "book"
            else:
                ocrVal["body"] = readImg(0, inputPath)
                # checkType = chuan_hoa_dau_cau_tieng_viet(ocrVal["body"])
                checkType = no_accent_vietnamese(ocrVal["body"]).lower()
                # print(checkType1)
                checkAdminDoc = re.search(
                    # "cộng hòa xã hội chủ nghĩa việt nam|cọng hòa xã hội chủ nghĩa việt nam|cọng hòa xã họi chủ nghĩa việt nam|cộng hòa xã họi chủ nghĩa việt nam",
                    "cong hoa xa hoi chu nghia viet nam|xa hoi chu nghia viet nam",
                    checkType,
                )
                if checkAdminDoc:
                    typeDoc = "admin-doc"
                else:
                    typeDoc = "book"

        if typeDoc == "book":
            if reader.pages[len(list(reader.pages)) // 2].extract_text() or reader.pages[(len(list(reader.pages)) // 2) - 1].extract_text():
                finalBody = ""
                for i, page in enumerate(reader.pages):
                    if i<2:
                        continue
                    textBook = page.extract_text()
                    if len(finalBody.split()) < 1000:
                        valInPage = postBook(textBook)
                        if valInPage is not None:
                            ocrVal.update(valInPage)
                        finalBody += textBook
                ocrVal["body"] = finalBody
            else:
                if reader.pages[len(list(reader.pages)) // 2].extract_text():
                    ocrVal["body"] = readImg(len(list(reader.pages)) // 2, inputPath)
                else:
                    ocrVal["body"] = readImg((len(list(reader.pages)) // 2) - 1, inputPath)
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

        # Text Analysis
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
                    gg_api
                    + "q=intitle:"
                    + ocrVal["title"]
                    + "&inauthor:"
                    + ocrVal["author"]
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

        os.remove(PDF_file)

        if langchainInput == '':
            langchainInput = ocrVal["body"]

        data_string = json.dumps(
            {
                "data": {
                    "companyId": companyId,
                    "userId": userId,
                    "fileId": fileId,
                    "type": typeDoc,
                    "title": langchainInput,
                    "ocr": ocrVal,
                    "status": True,
                }
            }
        )
        print("success")
        print(data_string)

        # Send message to Langchain queue
        producer_conn = pika.BlockingConnection(params)
        producer_channel = producer_conn.channel()
        producer_channel.queue_declare(queue=amqp_langchain_queue, durable=True)
        producer_channel.basic_qos(prefetch_count=10)
        producer_channel.basic_publish(
            exchange="",
            routing_key=amqp_langchain_queue,
            body=data_string,
            properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent),
        )
        producer_conn.close()

    except:
        print("error")
        reader = PdfReader(PDF_file)
        textPDF = ""
        ocrVal = {"body": ""}
        typeDoc = "book"
        status = False
        try:
            if reader.pages[len(list(reader.pages)) // 2].extract_text() or reader.pages[(len(list(reader.pages)) // 2) - 1].extract_text():
                finalBody = ""
                for i, page in enumerate(reader.pages):
                    if i<2:
                        continue
                    textBook = page.extract_text()
                    if len(finalBody.split()) < 1000:
                        valInPage = postBook(textBook)
                        if valInPage is not None:
                            ocrVal.update(valInPage)
                        finalBody += textBook
                ocrVal["body"] = finalBody
            else:
                if reader.pages[len(list(reader.pages)) // 2].extract_text():
                    ocrVal["body"] = readImg(len(list(reader.pages)) // 2, inputPath)
                else:
                    ocrVal["body"] = readImg((len(list(reader.pages)) // 2) - 1, inputPath)
            langchainInput = ocrVal["body"]
            status = True
        except:
            typeDoc = ""
        print(data_string)

        data_string = json.dumps(
            {
                "data": {
                    "companyId": companyId,
                    "userId": userId,
                    "fileId": fileId,
                    "type": typeDoc,
                    "title": langchainInput,
                    "ocr": ocrVal,
                    "status": status,
                }
            }
        )

        # Send message to Langchain queue
        producer_conn = pika.BlockingConnection(params)
        producer_channel = producer_conn.channel()
        producer_channel.queue_declare(queue=amqp_langchain_queue, durable=True)
        producer_channel.basic_qos(prefetch_count=10)
        producer_channel.basic_publish(
            exchange="",
            routing_key=amqp_langchain_queue,
            body=data_string,
            properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent),
        )
        producer_conn.close()

def logRequest(companyId, userId, fileId):
    current_time = datetime.now()
    current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
    print(current_time_str + " - " + companyId + " - " + userId + " - " + fileId)
