###################### LIBRARY ###################################

import regex as re

##################################################################
##################################################################

#######################   FUNCTION   #############################

from src.chuanHoa import chuan_hoa_dau_cau_tieng_viet
from src.chuanHoa import no_accent_vietnamese

##################################################################
##################################################################

def postAdminDoc(raw_text):
    ocrValInPage = {}

    ######## GET title #################################
    lowerRawText = raw_text.lower()
    noAccentText = no_accent_vietnamese(lowerRawText).lower()
    # print (noAccentText)
    regType = re.search(
        "cong hoa xa hoi chu nghia viet nam|hoa xa hoi chu nghia viet nam",
        noAccentText,
    )
    titleRawContent = raw_text[regType.span()[0]:]

    titleRawNoAccent = no_accent_vietnamese(titleRawContent).lower()
    titleRawLower = titleRawContent.lower()

    regType = re.search(
        "(nghi dinh|quy dinh|quyet dinh|chi thi|bao cao|cong dien|bien ban|giay gioi thieu|giay moi|giay nghi phep|giay uy quyen|phieu chuyen|phieu gui|phuong an|quy che|thong bao|giay bien nhan|giay cam ket|hop dong|cong van|ban ghi nho|ban thoa thuan|cong bo|de an|du an|chuong trinh|cong thu|giay de nghi|huong dan|dieu le|giay phep|ke hoach|nghi quyet|phieu bao|giay xac nhan|noi quy|ban cam ket|phieu lay y kien|to trinh|to khai|chung chi|thoa uoc|don|thu|giay dang ky|giay chung nhan|thong cao|v/v|v4y|v/w|v4v).*\n?",
        titleRawNoAccent,
    )

    # print(regType)

    reg = re.search("(căn cứ|kính|tại|trước)", titleRawLower)

    if regType and reg:
        ocrValInPage["tieu_de"] = titleRawContent[regType.span()[0] : reg.span()[0]]
        ocrValInPage["tieu_de"] = ocrValInPage["tieu_de"].replace("\n", " ")

    # print(ocrValInPage)

    return ocrValInPage
