import regex as re

lowerCharSet = (
    "[a-záàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệóòỏõọôốồổỗộơớờởỡợíìỉĩịúùủũụưứừửữựýỳỷỹỵđ]"
)
upperCharSet = (
    "[A-ZÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÉÈẺẼẸÊẾỀỂỄỆÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÍÌỈĨỊÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴĐ]"
)

def splitText(text, startInit, endInit, objname, test):
    objval = text[startInit:endInit]
    test[objname] = objval
    return text[endInit + 1 :]

def postAdminDoc(text):
    test={}
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

    return test