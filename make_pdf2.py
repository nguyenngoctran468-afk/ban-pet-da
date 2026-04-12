import urllib.request
import os
from fpdf import FPDF

# Download fonts
font_reg = "Roboto-Regular.ttf"
font_bold = "Roboto-Bold.ttf"
try:
    urllib.request.urlretrieve("https://raw.githubusercontent.com/googlefonts/roboto/main/src/hinted/Roboto-Regular.ttf", font_reg)
    urllib.request.urlretrieve("https://raw.githubusercontent.com/googlefonts/roboto/main/src/hinted/Roboto-Bold.ttf", font_bold)
except Exception as e:
    print("Download error:", e)

content = """
CẨM NANG GIAO TIẾP VỚI PET ĐÁ
(Dành riêng cho những kẻ sắp trầm cảm chốn công sở)

---
LỜI NÓI ĐẦU / DISCLAIMER

Bạn đang cầm trong tay cuốn cẩm nang này vì hai lý do: 
Một là bạn vừa tốn tiền mua một cục đá vô tri. Hai là bạn đang quá stress 
với mớ deadline ngập đầu và cần một đứa chịu ngồi yên nghe bạn chửi thề 
mà không méch lẻo với phòng HR.

Chúc mừng, bạn tìm đúng "đối tượng" rồi đó!
Cuộc đời đi làm 8 tiếng vốn đã mệt mỏi, dọn shit cho sếp dọn ruồi cho 
đồng nghiệp đã đủ hết thanh xuân. Nên về nhà hay ngồi văn phòng, bạn 
xứng đáng có một đứa "thú cưng" không ỉa bậy, đòi ăn hay rụng lông. 

Hãy đọc các trang tiếp theo để biết cách "vận nội công" giao tiếp 
với Pet Đá, biến nó thành tấm bình phong hoàn hảo giữa bạn và công ty toxic.

---
BÀI 1: BÀI TẬP "NHÌN ĐÁ TỊNH TÂM"

Lúc 3h chiều sếp báo: "Em ơi sửa lại cả slide này cho chị nhé". 
Thay vì đập phím, bạn hãy:
1. Quay mặt sang phải (hoặc trái), nơi cục đá đang ngồi.
2. Nhìn thẳng vào những vết lõm lồi lỳ lợm của nó.
3. Hít một hơi thật sâu. 
4. Tự nhủ: "Nó là đá mà nó còn đéo thèm nói gì. Sếp nói có tí thì nhằm nhò gì." 

Chỉ với 5 phút nhìn đá, nhịp tim bạn sẽ giảm từ 120 xuống 80. Tin tui đi.

---
BÀI 2: DÙNG ĐÁ LÀM BÌNH PHONG "SET BOUNDARY"

Bạn bè thường dặn phải biết "say No" chốn công sở để không bị đè đầu.
Phải khéo léo để không mất lòng ai.
Giải pháp đây: Hãy dùng Pet Đá làm "người phát ngôn"!

- Đồng nghiệp nhờ vả lúc 5h30 chiều: Nhấc nhẹ cục đá lên. "Nhỏ đá nay bị ốm, 
tụi nó bắt tao về xoa đầu nó rồi mày ơi. Nay không OT được nha".
- Sếp giao task ngang hông: Cầm cục đá lên vuốt ve. "Ánh mắt của cụ đá em 
nuôi bảo hôm nay không hợp rớt mạng... ý lộn, thêm việc sếp ạ".
Kẻ khùng sẽ không bao giờ bị giao thêm bài tập.

---
BÀI 3: KẾT NỐI QUA NHỮNG LỜI THÌ THẦM

Người ta hay bảo có gì tiêu cực đừng giữ trong lòng, phải xả ra mới tốt.
Thế là từ nay bạn có Pet Đá.
Cứ lúc nào hậm hực: bốc nó lên ngang tầm mắt, lấy tay chọc chọc vào nó:
- "Mẹ cha cái thứ... sao nay hãm vậy ta."
- "Bán cái mạng đi làm mấy triệu bạc, má nó tức!"
Đá không phán xét. Đá không tag bạn trên Facebook. Đá giữ bí mật tuyệt đối. 
Hãy chửi thẳng vào mặt đá. Cảm xúc xấu sẽ bị phong ấn vào cục cưng này.

---
LỜI KẾT: HÃY NHƯ ĐÁ!

Cuộc đời dâu bể, dù có chìm xuống nước, đá vẫn là đá. Nó kệ thây sự đời. 
Thấy mệt quá thì rúc vào góc nằm im. 
Bạn cũng vậy! Thấy mệt quá thì kệ đời, nghỉ ngơi. Đi làm vì đam mê hốt bạc 
chứ không phải bán ráng để bệnh viện thu hết. Hãy sống bền bỉ và lì lợm như một viên đá!

"Vô tri mà trường tồn!" - Founder Bé Đá Vô Tri.
"""

class PDF(FPDF):
    def footer(self):
        self.set_y(-15)
        if os.path.exists('Roboto-Regular.ttf'):
            self.set_font('Roboto', '', 8)
        else:
            self.set_font('helvetica', '', 8)
        self.cell(0, 10, f'Trang {self.page_no()}', align='C')

pdf = PDF()

# Add unicode font
if os.path.exists('Roboto-Regular.ttf'):
    pdf.add_font('Roboto', '', 'Roboto-Regular.ttf')
    pdf.add_font('Roboto', 'B', 'Roboto-Bold.ttf')
    pdf.set_font('Roboto', '', 11)
else:
    pdf.set_font('helvetica', '', 11)

pdf.add_page()

try:
    pdf.set_font("Roboto", "B", 16)
    pdf.cell(200, 10, text="CẨM NANG GIAO TIẾP VỚI PET ĐÁ", new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.set_font("Roboto", "", 12)
    pdf.cell(200, 10, text="(Dành riêng cho những kẻ sắp trầm cảm chốn công sở)", new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(10)

    lines = content.split('\n')
    pdf.set_font("Roboto", "", 12)
    for line in lines[3:]:
        if line.startswith("BÀI") or line.startswith("LỜI") or line.startswith("CẨM"):
            pdf.set_font("Roboto", "B", 14)
            pdf.multi_cell(0, 10, text=line)
            pdf.set_font("Roboto", "", 12)
        else:
            pdf.multi_cell(0, 8, text=line)

    pdf.output("Cam_Nang_Pet_Da.pdf")
    print("SUCCESS")
except Exception as e:
    print("Error generating:", e)

