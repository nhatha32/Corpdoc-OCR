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
    print (lowerRawText)
    regType = re.search(
        "(bản ghi nhớ|bản thỏa thuận|chỉ thị|báo cáo|công điện|biên bản|chương trình|công thư|đơn|công văn|đề án|dự án|giấy giới thiệu|giấy mời|giấy nghỉ phép|giấy ủy quyền|hợp đồng|giấy đề nghị|công bố|hướng dẫn|điều lệ|giấy phép|kế hoạch|nghị quyết|phiếu báo|thỏa ước|giấy xác nhận|phiếu chuyển|phiếu gửi|phương án|quy chế|quy định|quyết định|thông báo|giấy biên nhận|giấy cam kết|thư|nội quy|bản cam kết|chứng chỉ|phiếu lấy ý kiến|tờ trình|tờ khai|v/v|v4y|v/w|v4v).*\n?",
        lowerRawText,
    )

    reg = re.search("(căn cứ|kính|tại)", lowerRawText)

    if regType and reg:
        ocrValInPage["tieu_de"] = raw_text[regType.span()[0] : reg.span()[0]]
        ocrValInPage["tieu_de"] = ocrValInPage["tieu_de"].replace("\n", " ")

    print(ocrValInPage)

    return ocrValInPage
