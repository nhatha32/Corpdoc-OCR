###################### LIBRARY ###################################

import regex as re

##################################################################
##################################################################

#######################   FUNCTION   #############################

from src.chuanHoa import chuan_hoa_dau_cau_tieng_viet

##################################################################
##################################################################

def postAdminDoc(raw_text):
    ocrValInPage = {}

    ######## GET title #################################
    lowerRawText = raw_text.lower()
    noAccentText = no_accent_vietnamese(lowerRawText).lower()
    # print (lowerRawText)
    regType = re.search(
        "(ban ghi nho|ban thoa thuan|chi thi|bao cao|cong dien|bien ban|chuong trinh|cong thu|don|cong van|de an|du an|giay gioi thieu|giay moi|giay nghi phep|giay uy quyen|hop dong|giay de nghi|cong bo|huong dan|dieu le|giay phep|ke hoach|nghi quyet|phieu bao|thoa uoc|giay xac nhan|phieu chuyen|phieu gui|phuong an|quy che|quy dinh|quyet dinh|thong bao|giay bien nhan|giay cam ket|thu|noi quy|ban cam ket|chung chi|phieu lay y kien|to trinh|to khai|v/v|v4y|v/w|v4v).*\n?",
        noAccentText,
    )

    reg = re.search("(căn cứ|kính|tại)", lowerRawText)

    if regType and reg:
        ocrValInPage["tieu_de"] = raw_text[regType.span()[0] : reg.span()[0]]
        ocrValInPage["tieu_de"] = ocrValInPage["tieu_de"].replace("\n", " ")

    print(ocrValInPage)

    return ocrValInPage
