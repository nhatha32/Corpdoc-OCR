###################### LIBRARY ###################################

import regex as re

##################################################################
##################################################################

lowerCharSet = (
    "[a-záàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệóòỏõọôốồổỗộơớờởỡợíìỉĩịúùủũụưứừửữựýỳỷỹỵđ]"
)
upperCharSet = (
    "[A-ZÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÉÈẺẼẸÊẾỀỂỄỆÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÍÌỈĨỊÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴĐ]"
)


def splitText(text, startInit, endInit, objname, ocrValInPage):
    objval = text[startInit:endInit]
    ocrValInPage[objname] = objval
    return text[endInit + 1 :]


def postBook(raw_text):
    ocrValInPage = {}
    ocrValInPage["body"] = raw_text[0:700]
    reg = re.search("isbn|ISBN|Isbn", raw_text)
    if reg != None:
        x = raw_text.split("\n")
        for j in x:
            reg = re.search("isbn|ISBN|Isbn", j)
            if reg != None:
                ocrValInPage["isbn"] = j[reg.span()[1] :]

    reg = re.search("NHÀ XUẤT BẢN", raw_text)
    if "nxb" not in ocrValInPage and reg != None:
        x = raw_text.split("\n")
        for j in x:
            reg = re.search("NHÀ XUẤT BẢN", j)
            if reg != None:
                ocrValInPage["nxb"] = j

    reg = re.search("NXB", raw_text)
    if "nxb" not in ocrValInPage and reg != None:
        x = raw_text.split("\n")
        for j in x:
            reg = re.search("NXB", j)
            if reg != None:
                ocrValInPage["nxb"] = j

    reg = re.search("trách nhiệm xuất bản", raw_text)

    if reg != None:

        x = raw_text.split("\n")
        for j in x:
            if "title" not in ocrValInPage and j == j.upper():
                ocrValInPage["title"] = j
                continue
            if "author" not in ocrValInPage and j == j.upper():
                ocrValInPage["author"] = j
                continue
            reg = re.search("NHÀ XUẤT BẢN", j)
            if "nxb" not in ocrValInPage and reg != None:
                ocrValInPage["nxb"] = j
                continue
            reg = re.search("NXB", j)
            if "nxb" not in ocrValInPage and reg != None:
                ocrValInPage["nxb"] = j
                continue
            reg = re.search("Người dịch", j)
            if reg != None:
                ocrValInPage["nguoi_dich"] = j[reg.span()[1] + 1 :]
                continue
            reg = re.search("Email", j)
            if reg != None:
                ocrValInPage["email"] = j[reg.span()[1] + 1 :]
                continue
            reg = re.search("isbn", j)
            if reg != None:
                ocrValInPage["isbn"] = j[reg.span()[1] :]
                continue

    return ocrValInPage
