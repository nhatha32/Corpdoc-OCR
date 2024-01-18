from PIL import Image
import pytesseract
import argparse
import cv2
import os
# import re
import regex as re

""" Ảnh nên được xử lý trước như khử nhiễu, chuyển về đen trắng... sẽ cho kết quả tốt hơn đới với Tesseract """
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, help="path to the input image")
ap.add_argument("-p", "--preprocess", type=str, default="thresh", help="kind of image pre-processing")
args = vars(ap.parse_args())

# Đọc ảnh và convert về grayscale
image = cv2.imread(args["image"])
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
 
# Kiểm tra xem có chuyển về ảnh đen trắng 
if args["preprocess"] == "thresh":
	_, gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)		# trả về 2 tham số threshold và image
 
# Có blur không
elif args["preprocess"] == "blur":
	gray = cv2.medianBlur(gray, 3)	# tham số thứ hai là kernel size, giảm salt và pepper noise

# Lưu ảnh trong ổ cứng như file tạm để có thể apply OCR
filename = "{}.png".format(os.getpid())		# os.getpid() method in Python is used to get the process ID of the current process, trả về 1 số nguyên
cv2.imwrite(filename, gray)		# ghi ảnh gray vào filename

# Load ảnh và apply nhận dạng bằng Tesseract OCR
text = pytesseract.image_to_string(Image.open(filename), lang='vie')	# có nhiều ngôn ngữ thì trong lang các ngôn ngữ cách nhau bằng dấu  +
""" Cần chú ý các chế độ nhận diện được điều chỉnh bằng config """

# Thực hiện chuyển đổi xong thì xóa ảnh tạm
os.remove(filename)

# In dòng chữ nhận dạng được
print(text)

# Hiển thị ảnh ban đầu, ảnh đã được pre-processing
# cv2.imshow("Image", image)
# cv2.imshow("Output", gray)
# cv2.waitKey(0)

# Phân tích text

# Chuẩn hóa bảng mã tiếng việt

uniChars = "àáảãạâầấẩẫậăằắẳẵặèéẻẽẹêềếểễệđìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵÀÁẢÃẠÂẦẤẨẪẬĂẰẮẲẴẶÈÉẺẼẸÊỀẾỂỄỆĐÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴÂĂĐÔƠƯ"
unsignChars = "aaaaaaaaaaaaaaaaaeeeeeeeeeeediiiiiooooooooooooooooouuuuuuuuuuuyyyyyAAAAAAAAAAAAAAAAAEEEEEEEEEEEDIIIOOOOOOOOOOOOOOOOOOOUUUUUUUUUUUYYYYYAADOOU"

def loaddicchar():
    dic = {}
    char1252 = 'à|á|ả|ã|ạ|ầ|ấ|ẩ|ẫ|ậ|ằ|ắ|ẳ|ẵ|ặ|è|é|ẻ|ẽ|ẹ|ề|ế|ể|ễ|ệ|ì|í|ỉ|ĩ|ị|ò|ó|ỏ|õ|ọ|ồ|ố|ổ|ỗ|ộ|ờ|ớ|ở|ỡ|ợ|ù|ú|ủ|ũ|ụ|ừ|ứ|ử|ữ|ự|ỳ|ý|ỷ|ỹ|ỵ|À|Á|Ả|Ã|Ạ|Ầ|Ấ|Ẩ|Ẫ|Ậ|Ằ|Ắ|Ẳ|Ẵ|Ặ|È|É|Ẻ|Ẽ|Ẹ|Ề|Ế|Ể|Ễ|Ệ|Ì|Í|Ỉ|Ĩ|Ị|Ò|Ó|Ỏ|Õ|Ọ|Ồ|Ố|Ổ|Ỗ|Ộ|Ờ|Ớ|Ở|Ỡ|Ợ|Ù|Ú|Ủ|Ũ|Ụ|Ừ|Ứ|Ử|Ữ|Ự|Ỳ|Ý|Ỷ|Ỹ|Ỵ'.split(
        '|')
    charutf8 = "à|á|ả|ã|ạ|ầ|ấ|ẩ|ẫ|ậ|ằ|ắ|ẳ|ẵ|ặ|è|é|ẻ|ẽ|ẹ|ề|ế|ể|ễ|ệ|ì|í|ỉ|ĩ|ị|ò|ó|ỏ|õ|ọ|ồ|ố|ổ|ỗ|ộ|ờ|ớ|ở|ỡ|ợ|ù|ú|ủ|ũ|ụ|ừ|ứ|ử|ữ|ự|ỳ|ý|ỷ|ỹ|ỵ|À|Á|Ả|Ã|Ạ|Ầ|Ấ|Ẩ|Ẫ|Ậ|Ằ|Ắ|Ẳ|Ẵ|Ặ|È|É|Ẻ|Ẽ|Ẹ|Ề|Ế|Ể|Ễ|Ệ|Ì|Í|Ỉ|Ĩ|Ị|Ò|Ó|Ỏ|Õ|Ọ|Ồ|Ố|Ổ|Ỗ|Ộ|Ờ|Ớ|Ở|Ỡ|Ợ|Ù|Ú|Ủ|Ũ|Ụ|Ừ|Ứ|Ử|Ữ|Ự|Ỳ|Ý|Ỷ|Ỹ|Ỵ".split(
        '|')
    for i in range(len(char1252)):
        dic[char1252[i]] = charutf8[i]
    return dic

dicchar = loaddicchar()

def covert_unicode(txt):
    return re.sub(
        r'à|á|ả|ã|ạ|ầ|ấ|ẩ|ẫ|ậ|ằ|ắ|ẳ|ẵ|ặ|è|é|ẻ|ẽ|ẹ|ề|ế|ể|ễ|ệ|ì|í|ỉ|ĩ|ị|ò|ó|ỏ|õ|ọ|ồ|ố|ổ|ỗ|ộ|ờ|ớ|ở|ỡ|ợ|ù|ú|ủ|ũ|ụ|ừ|ứ|ử|ữ|ự|ỳ|ý|ỷ|ỹ|ỵ|À|Á|Ả|Ã|Ạ|Ầ|Ấ|Ẩ|Ẫ|Ậ|Ằ|Ắ|Ẳ|Ẵ|Ặ|È|É|Ẻ|Ẽ|Ẹ|Ề|Ế|Ể|Ễ|Ệ|Ì|Í|Ỉ|Ĩ|Ị|Ò|Ó|Ỏ|Õ|Ọ|Ồ|Ố|Ổ|Ỗ|Ộ|Ờ|Ớ|Ở|Ỡ|Ợ|Ù|Ú|Ủ|Ũ|Ụ|Ừ|Ứ|Ử|Ữ|Ự|Ỳ|Ý|Ỷ|Ỹ|Ỵ',
        lambda x: dicchar[x.group()], txt)

# Chuẩn hóa kiểu gõ tiếng Việt
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
            if index != 0 and chars[index - 1] == 'q':
                chars[index] = 'u'
                qu_or_gi = True
        elif x == 5:  # check gi
            if index != 0 and chars[index - 1] == 'g':
                chars[index] = 'i'
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
                    chars[1] = bang_nguyen_am[5][dau_cau] if chars[1] == 'i' else bang_nguyen_am[9][dau_cau]
            return ''.join(chars)
        return word

    for index in nguyen_am_index:
        x, y = nguyen_am_to_ids[chars[index]]
        if x == 4 or x == 8:  # ê, ơ
            chars[index] = bang_nguyen_am[x][dau_cau]
            # for index2 in nguyen_am_index:
            #     if index2 != index:
            #         x, y = nguyen_am_to_ids[chars[index]]
            #         chars[index2] = bang_nguyen_am[x][0]
            return ''.join(chars)

    if len(nguyen_am_index) == 2:
        if nguyen_am_index[-1] == len(chars) - 1:
            x, y = nguyen_am_to_ids[chars[nguyen_am_index[0]]]
            chars[nguyen_am_index[0]] = bang_nguyen_am[x][dau_cau]
            # x, y = nguyen_am_to_ids[chars[nguyen_am_index[1]]]
            # chars[nguyen_am_index[1]] = bang_nguyen_am[x][0]
        else:
            # x, y = nguyen_am_to_ids[chars[nguyen_am_index[0]]]
            # chars[nguyen_am_index[0]] = bang_nguyen_am[x][0]
            x, y = nguyen_am_to_ids[chars[nguyen_am_index[1]]]
            chars[nguyen_am_index[1]] = bang_nguyen_am[x][dau_cau]
    else:
        # x, y = nguyen_am_to_ids[chars[nguyen_am_index[0]]]
        # chars[nguyen_am_index[0]] = bang_nguyen_am[x][0]
        x, y = nguyen_am_to_ids[chars[nguyen_am_index[1]]]
        chars[nguyen_am_index[1]] = bang_nguyen_am[x][dau_cau]
        # x, y = nguyen_am_to_ids[chars[nguyen_am_index[2]]]
        # chars[nguyen_am_index[2]] = bang_nguyen_am[x][0]
    return ''.join(chars)


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
    """
        Chuyển câu tiếng việt về chuẩn gõ dấu kiểu cũ.
        :param sentence:
        :return:
        """
    sentence = sentence.lower()
    words = sentence.split()
    for index, word in enumerate(words):
        cw = re.sub(r'(^p{P}*)([p{L}.]*p{L}+)(p{P}*$)', r'1/2/3', word)
        # print(cw)
        # if len(cw) == 3:
        #     cw[1] = chuan_hoa_dau_tu_tieng_viet(cw[1])
        words[index] = ''.join(cw)
    return ' '.join(words)

def chuanHoaDauCauTheoTungLine(text):
	sentences = text.splitlines(True)
	# print(sentences)
	sentences = list(filter(lambda a: a != '\n', sentences))
	for index, sentence in enumerate(sentences):
		# print(re.sub(r'(^p{P}*)([p{L}.]*p{L}+)(p{P}*$)', r'1/2/3', sentence).split('/'))
		# print(sentence)
		sentences[index] = chuan_hoa_dau_cau_tieng_viet(sentence)
	return '\n'.join(sentences)

print('################\n')

text = covert_unicode(text)
text = chuanHoaDauCauTheoTungLine(text)

# print (text)

# chia text
def splitText(text, startInit, endInit, objname, test):
	objval = text[startInit:endInit]
	test[objname] = objval
	return text[endInit+1:]

############
# tiền xử lý 
lowerCharSet = "[a-záàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệóòỏõọôốồổỗộơớờởỡợíìỉĩịúùủũụưứừửữựýỳỷỹỵđ]"
upperCharSet = "[A-ZÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÉÈẺẼẸÊẾỀỂỄỆÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÍÌỈĨỊÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴĐ]"

test = {}

maxHeight = gray.shape[0]
maxWidth = gray.shape[1]
width = int(maxWidth/2-10)
coQuanImg = gray[0:90, 0:width]
cv2.imshow('Region Of Interest', coQuanImg)
cv2.waitKey(0)

coQuan = pytesseract.image_to_string(coQuanImg, lang='vie')
coQuan = covert_unicode(coQuan)
coQuan = chuanHoaDauCauTheoTungLine(coQuan)
test['co_quan'] = coQuan.replace('\n', ' ',1)
test['co_quan'] = test['co_quan'].replace('\n', '',1)
# print(coQuan)

# cơ quan
# reg = re.search(" cộng hòa xã hội chủ nghĩa việt nam", text)

# if(reg != None):
# 	text = splitText(text, 0, reg.span()[0], "co_quan", test)

# quoc hieu
reg = re.search("cộng hòa xã hội chủ nghĩa việt nam", text)

if(reg != None):
	text = splitText(text, reg.span()[0], reg.span()[1], "quoc_hieu", test)

# tieu ngu
reg = re.search("độc lập", text)

if (reg != None):
	text = text[reg.span()[0]:]

reg = re.search(" hạnh phúc", text)

if(reg != None):
	text = splitText(text, 0, reg.span()[1], "tieu_ngu", test)

# so hieu
reg = re.search("số: ", text)

if (reg != None):
	text = text[reg.span()[1]:]
	reg = re.search("\s", text)
	if(reg != None):
		text = splitText(text, 0, reg.span()[0], "so", test)

test['so'] = '06/tb-hcqt'

# ngay thang
reg = re.search("(" + lowerCharSet + "| )+, ngày .+ \d+", text)

if (reg != None):
	
	subText = text[reg.span()[0]:reg.span()[1]]
	
	subObj = subText.split(", ")

	test["dia_diem"] = subObj[0]
	test["ngay_thang"] = subObj[1]
	
	text = text[reg.span()[1]+1:]

# loai van ban
reg = re.search("(thông tư|hiến pháp|nghị quyết|nghị định|quyết định|chỉ thị|quy chế|quy định|thông báo|thông cáo|hướng dẫn|chương trình|kế hoạch|phương án|đề án|dự án|báo cáo|biên bản|tờ trình|hợp đồng|công văn|công điện|bản ghi nhớ|bản thỏa thuận|giấy ủy quyền|giấy mời|giấy giới thiệu|giấy ghi chép|phiếu gửi|phiếu chuyển|phiếu báo|thư công).*\n?", text)

if(reg != None):
	text = splitText(text, reg.span()[0], reg.span()[1]-1, "loai_van_ban", test)

# tieu de
# reg = re.search(lowerCharSet + ".*\n? | (căn cứ)", text)
reg = re.search("\n(căn cứ|kính gửi)", text)

if(reg != None):
	text = splitText(text, 0, reg.span()[0], "tieu_de", test)
	test['tieu_de'] = test['tieu_de'].replace('\n', ' ')

test["noi_dung"] = text

# các văn bản liên quan
reg = re.search("(\d+/|)\d+/(" + lowerCharSet + "|-)+", text)
if(reg != None):
	test['van_ban_lien_quan']= ''

while(reg != None):
	objval = text[reg.span()[0]: reg.span()[1]]
	test['van_ban_lien_quan'] += test['van_ban_lien_quan'] + '\n' + objval
	text = text[reg.span()[1]:]
	reg = re.search("(\d+/|)\d+/(" + lowerCharSet + "|-)+", text)

# print(test)
# print(text)

print('{')
for item, value in test.items():
	print(item + ' : ' + value + ',')
print('}')

