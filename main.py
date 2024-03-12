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
def index(id: str):
    # Access S3
    s3 = boto3.client(
        "s3",
        aws_access_key_id=s3_access_key_id,
        aws_secret_access_key=s3_secret_access_key,
        region_name=s3_region,
    )
    s3.download_file(s3_file_bucket, id + ".pdf", asset_path)

    # Đọc ảnh từ file PDF
    with TemporaryDirectory() as tempdir:
        if platform.system() == "Windows":
            pdf_pages = convert_from_path(
                PDF_file, 80, poppler_path=path_to_poppler_exe
            )
        else:
            pdf_pages = convert_from_path(PDF_file, 80)
        # Read in the PDF file at 500 DPI
        image = pdf_pages[0]
        opencvImage = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
        # cv2.imshow("Image", opencvImage)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

    # Lưu ảnh trong ổ cứng như file tạm để có thể apply OCR
    filename = "{}.png".format(os.getpid())
    cv2.imwrite(filename, opencvImage)  # ghi ảnh vào filename

    # Load ảnh và apply nhận dạng bằng Tesseract OCR
    text = pytesseract.image_to_string(
        Image.open(filename), lang="vie"
    )  # có nhiều ngôn ngữ thì trong lang các ngôn ngữ cách nhau bằng dấu  +
    """ Cần chú ý các chế độ nhận diện được điều chỉnh bằng config """

    # Thực hiện chuyển đổi xong thì xóa ảnh tạm
    os.remove(filename)

    # In dòng chữ nhận dạng được
    # print(text)

    # Phân tích text

    # Chuẩn hóa bảng mã tiếng việt

    bang_nguyen_am = [
        ["a", "à", "á", "ả", "ã", "ạ", "a"],
        ["ă", "ằ", "ắ", "ẳ", "ẵ", "ặ", "aw"],
        ["â", "ầ", "ấ", "ẩ", "ẫ", "ậ", "aa"],
        ["e", "è", "é", "ẻ", "ẽ", "ẹ", "e"],
        ["ê", "ề", "ế", "ể", "ễ", "ệ", "ee"],
        ["i", "ì", "í", "ỉ", "ĩ", "ị", "i"],
        ["o", "ò", "ó", "ỏ", "õ", "ọ", "o"],
        ["ô", "ồ", "ố", "ổ", "ỗ", "ộ", "oo"],
        ["ơ", "ờ", "ớ", "ở", "ỡ", "ợ", "ow"],
        ["u", "ù", "ú", "ủ", "ũ", "ụ", "u"],
        ["ư", "ừ", "ứ", "ử", "ữ", "ự", "uw"],
        ["y", "ỳ", "ý", "ỷ", "ỹ", "ỵ", "y"],
    ]

    nguyen_am_to_ids = {}

    for i in range(len(bang_nguyen_am)):
        for j in range(len(bang_nguyen_am[i]) - 1):
            nguyen_am_to_ids[bang_nguyen_am[i][j]] = (i, j)

    def chuan_hoa_dau_tu_tieng_viet(word):
        if not is_valid_vietnam_word(word):
            return word

        chars = list(word)
        dau_cau = 0
        nguyen_am_index = []
        qu_or_gi = False
        for index, char in enumerate(chars):
            x, y = nguyen_am_to_ids.get(char, (-1, -1))
            if x == -1:
                continue
            elif x == 9:  # check qu
                if index != 0 and chars[index - 1] == "q":
                    chars[index] = "u"
                    qu_or_gi = True
            elif x == 5:  # check gi
                if index != 0 and chars[index - 1] == "g":
                    chars[index] = "i"
                    qu_or_gi = True
            if y != 0:
                dau_cau = y
                chars[index] = bang_nguyen_am[x][0]
            if not qu_or_gi or index != 1:
                nguyen_am_index.append(index)
        if len(nguyen_am_index) < 2:
            if qu_or_gi:
                if len(chars) == 2:
                    x, y = nguyen_am_to_ids.get(chars[1])
                    chars[1] = bang_nguyen_am[x][dau_cau]
                else:
                    x, y = nguyen_am_to_ids.get(chars[2], (-1, -1))
                    if x != -1:
                        chars[2] = bang_nguyen_am[x][dau_cau]
                    else:
                        chars[1] = (
                            bang_nguyen_am[5][dau_cau]
                            if chars[1] == "i"
                            else bang_nguyen_am[9][dau_cau]
                        )
                return "".join(chars)
            return word

        for index in nguyen_am_index:
            x, y = nguyen_am_to_ids[chars[index]]
            if x == 4 or x == 8:  # ê, ơ
                chars[index] = bang_nguyen_am[x][dau_cau]
                return "".join(chars)

        if len(nguyen_am_index) == 2:
            if nguyen_am_index[-1] == len(chars) - 1:
                x, y = nguyen_am_to_ids[chars[nguyen_am_index[0]]]
                chars[nguyen_am_index[0]] = bang_nguyen_am[x][dau_cau]
            else:
                x, y = nguyen_am_to_ids[chars[nguyen_am_index[1]]]
                chars[nguyen_am_index[1]] = bang_nguyen_am[x][dau_cau]
        else:
            x, y = nguyen_am_to_ids[chars[nguyen_am_index[1]]]
            chars[nguyen_am_index[1]] = bang_nguyen_am[x][dau_cau]
        return "".join(chars)

    def is_valid_vietnam_word(word):
        chars = list(word)
        nguyen_am_index = -1
        for index, char in enumerate(chars):
            x, y = nguyen_am_to_ids.get(char, (-1, -1))
            if x != -1:
                if nguyen_am_index == -1:
                    nguyen_am_index = index
                else:
                    if index - nguyen_am_index != 1:
                        return False
                    nguyen_am_index = index
        return True

    def chuan_hoa_dau_cau_tieng_viet(sentence):
        sentence = sentence.lower()
        words = sentence.split()
        for index, word in enumerate(words):
            words[index] = chuan_hoa_dau_tu_tieng_viet(word)
        return " ".join(words)

    # print("################\n")

    text = chuan_hoa_dau_cau_tieng_viet(text)

    print(text)

    # chia text
    def splitText(text, startInit, endInit, objname, test):
        objval = text[startInit:endInit]
        test[objname] = objval
        return text[endInit + 1 :]

    ############
    # tiền xử lý
    lowerCharSet = (
        "[a-záàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệóòỏõọôốồổỗộơớờởỡợíìỉĩịúùủũụưứừửữựýỳỷỹỵđ]"
    )
    upperCharSet = (
        "[A-ZÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÉÈẺẼẸÊẾỀỂỄỆÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÍÌỈĨỊÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴĐ]"
    )

    test = {}

    maxHeight = opencvImage.shape[0]
    maxWidth = opencvImage.shape[1]

    # co quan
    coquanHeight = int(maxHeight / 10)
    coquanWidth = int(maxWidth / 3 + 10)
    coQuanImg = opencvImage[0:coquanHeight, 0:coquanWidth]
    # cv2.imshow("Region Of Interest", coQuanImg)
    # cv2.waitKey(0)
    coQuan = pytesseract.image_to_string(coQuanImg, lang="vie")
    coQuan = chuan_hoa_dau_cau_tieng_viet(coQuan)
    test["co_quan"] = coQuan.replace("\n", " ", 1)
    test["co_quan"] = test["co_quan"].replace("\n", "", 1)
    # print(coQuan)

    # quoc hieu
    reg = re.search("cộng hòa xã hội chủ nghĩa việt nam", text)
    if reg != None:
        text = splitText(text, reg.span()[0], reg.span()[1], "quoc_hieu", test)

    # tieu ngu
    reg = re.search("độc lập", text)

    if reg != None:
        text = text[reg.span()[0] :]

    reg = re.search(" hạnh phúc", text)

    if reg != None:
        text = splitText(text, 0, reg.span()[1], "tieu_ngu", test)

    # so hieu
    reg = re.search("số: ", text)

    if reg != None:
        text = text[reg.span()[1] :]
        reg = re.search("\s", text)
        if reg != None:
            text = splitText(text, 0, reg.span()[0], "so", test)

    test["so"] = "06/tb-hcqt"

    # ngay thang
    reg = re.search("(" + lowerCharSet + "| )+, ngày .+ \d+", text)

    if reg != None:

        subText = text[reg.span()[0] : reg.span()[1]]

        subObj = subText.split(", ")

        test["dia_diem"] = subObj[0]
        test["ngay_thang"] = subObj[1]

        text = text[reg.span()[1] + 1 :]


    # loai van ban
    reg = re.search(
        "(thông tư|hiến pháp|nghị quyết|nghị định|quyết định|chỉ thị|quy chế|quy định|thông báo|thông cáo|hướng dẫn|chương trình|kế hoạch|phương án|đề án|dự án|báo cáo|biên bản|tờ trình|hợp đồng|công văn|công điện|bản ghi nhớ|bản thỏa thuận|giấy ủy quyền|giấy mời|giấy giới thiệu|giấy ghi chép|phiếu gửi|phiếu chuyển|phiếu báo|thư công).*\n?",
        text,
    )

    if reg != None:
        text = splitText(text, reg.span()[0], reg.span()[1] - 1, "loai_van_ban", test)

    # tieu de
    # reg = re.search(lowerCharSet + ".*\n? | (căn cứ)", text)
    reg = re.search("\n(căn cứ|kính gửi)", text)

    if reg != None:
        text = splitText(text, 0, reg.span()[0], "tieu_de", test)
        test["tieu_de"] = test["tieu_de"].replace("\n", " ")

    test["noi_dung"] = text

    # các văn bản liên quan
    reg = re.search("(\d+/|)\d+/(" + lowerCharSet + "|-)+", text)
    if reg != None:
        test["van_ban_lien_quan"] = ""

    while reg != None:
        objval = text[reg.span()[0] : reg.span()[1]]
        test["van_ban_lien_quan"] += test["van_ban_lien_quan"] + "\n" + objval
        text = text[reg.span()[1] :]
        reg = re.search("(\d+/|)\d+/(" + lowerCharSet + "|-)+", text)

    # print(test)
    # print(text)

    # print("{")
    # for item, value in test.items():
    #     print(item + " : " + value + ",")
    # print("}")
    return {"data": test}
