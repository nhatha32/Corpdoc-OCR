def checkFullInfo(ocrVal, type):
    if ocrVal is not None:
        if type == "book":
            if "isbn" in ocrVal or ("title" in ocrVal and "author" in ocrVal):
                return True
        else:
            if "tieu_de" in ocrVal:
                return True
    return False
