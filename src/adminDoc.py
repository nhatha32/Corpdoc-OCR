###################### LIBRARY ###################################

import regex as re

##################################################################
##################################################################

#######################   FUNCTION   #############################

from chuanHoa import chuan_hoa_dau_cau_tieng_viet

##################################################################
##################################################################

def postAdminDoc(raw_text):
    ocrValInPage = {}

    ######## GET title #################################
    regType = re.search(
        "(NGHỊ QUYẾT|NGHI QUYẾT|QUYẾT ĐỊNH|CHỈ THỊ|QUY CHẾ|QUY ĐỊNH|THÔNG CÁO|THONG CÁO|THÔNG BÁO|THONG BÁO|KẾ HOẠCH|HƯỚNG DẪN|HUỚNG DẪN|HƯÓNG DẪN|CHƯƠNG TRÌNH|PHƯƠNG ÁN|ĐỀ ÁN|DỰ ÁN|BÁO CÁO|BIÊN BẢN|TỜ TRÌNH|HỢP ĐỒNG|CÔNG VĂN|CÔNG ĐIỆN|BẢN GHI NHỚ|BẢN THỎA THUẬN|GIẤY ỦY QUYỀN|GIẤY MỜI|GIẤY GIỚI THIỆU|GIẤY NGHỈ PHÉP|PHIẾU GỬI|PHIẾU CHUYỂN|PHIẾU BÁO|THƯ CÔNG|THU CÔNG).*\n?",
        raw_text,
    )

    reg = re.search("\n(Căn cứ|Kính gửi|Tại)", raw_text)

    if regType and reg:
        ocrValInPage["tieu_de"] = raw_text[regType.span()[0] : reg.span()[0]]
        ocrValInPage["tieu_de"] = ocrValInPage["tieu_de"].replace("\n", " ")

    return ocrValInPage
