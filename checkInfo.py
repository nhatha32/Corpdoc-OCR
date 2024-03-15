def checkFullInfo(test, type):
    if test is not None:
        if type == "book":
            if "isbn" in test or ("title" in test and "author" in test):
                return True
        else:
            if "tieu_de" in test and "so" in test and "loai_van_ban" in test:
                return True
    return False