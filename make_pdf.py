import os
from fpdf import FPDF
import textwrap

content = """
CẨM NANG GIAO TIẾP VỚI PET ĐÁ
(Dành riêng cho những kẻ sắp trầm cảm chốn công sở)

---
LỜI NÓI ĐẦU / DISCLAIMER

Bạn đang cầm trong tay cuốn cẩm nang này vì hai lý do: 
Một là bạn vừa tốn tiền mua một cục đá vô tri. Hai là bạn đang quá stress với mớ deadline ngập đầu và cần một đứa chịu ngồi yên nghe bạn chửi thề mà không méch lẻo với phòng HR.

Chúc mừng, bạn tìm đúng "đối tượng" rồi đó!
Cuộc đời đi làm 8 tiếng vốn đã mệt mỏi, dọn shit cho sếp dọn ruồi cho đồng nghiệp đã đủ hết thanh xuân. Nên về nhà hay ngồi văn phòng, bạn xứng đáng có một đứa "thú cưng" không ỉa bậy, không cắn dây điện, đòi ăn hay rụng lông. 

Hãy mở trang tiếp theo để biết cách "vận nội công" giao tiếp với Pet Đá, biến nó thành tấm bình phong hoàn hảo giữa bạn và công ty toxic.

---
BÀI 1: BÀI TẬP "NHÌN ĐÁ TỊNH TÂM"

Lúc 3h chiều sếp báo: "Em ơi sửa lại cả slide này cho chị nhé, ý tưởng chán quá". 
Thay vì đập phím, bạn hãy:
1. Quay mặt sang phải (hoặc trái), nơi cục đá đang ngồi.
2. Nhìn thẳng vào những vết lõm lồi lỳ lợm của nó.
3. Hít một hơi thật sâu. 
4. Tự nhủ: "Nó là đá mà nó còn đéo thèm nói gì. Sếp nói có tí thì nhằm nhò mẹ gì." 

Chỉ với 5 phút nhìn đá, nhịp tim bạn sẽ giảm từ 120 beats/phút xuống còn 80. Tin tui đi. Nó vô tri nhưng sự vô tri đó lại mang sức mạnh chữa lành cực mạnh.

---
BÀI 2: DÙNG ĐÁ LÀM BÌNH PHONG "SET BOUNDARY"

Bạn bè thường dặn phải biết "say No" chốn công sở để không bị đè đầu cưỡi cổ đúng không? Nhưng mở mồm ra từ chối thì sợ mất lòng, sợ sếp ghét.
Giải pháp đây: Hãy dùng Pet Đá làm "người phát ngôn"!

- Đồng nghiệp nhờ vả lúc 5h30 chiều: Nhấc giong ục ịch cục đá đặt ngay giữa bàn phím. "Nhỏ đá nay bị ốm, tụi nó bắt tao về xoa đầu nó rồi mày ơi. Nay không OT được nha".
- Sếp giao task ngang hông: Cầm cục đá lên vuốt ve. "Ánh mắt của cụ đá em nuôi bảo hôm nay không hợp rớt mạng... ý lộn, thêm việc sếp ạ".
Mọi người sẽ nghĩ bạn hơi khùng. Đúng rồi! Kẻ khùng sẽ không bao giờ bị giao thêm bài tập. 

---
BÀI 3: KẾT NỐI QUA NHỮNG LỜI THÌ THẦM CHỬI THỀ

Người ta hay bảo có gì tiêu cực đừng giữ trong lòng, phải xả ra mới tốt. Nhưng nói với đồng nghiệp thì thành cái chợ, nói với người yêu thì tội ngta phải nghe đống rác của bạn.
Thế là từ nay bạn có Pet Đá.
Cứ lúc nào hậm hực: bốc nó lên ngang tầm mắt, lấy tay chọc chọc vào nó:
- "Mẹ cha cái thứ... sao nay hãm vậy ta."
- "Bán cái mạng đi làm 8 triệu bạc, má nó tức!"
Đá không phán xét. Đá không tag bạn trên Facebook. Đá giữ bí mật tuyệt đối. 
Hãy chửi thề thẳng vào mặt đá bao nhiêu tuỳ ý. Cảm xúc xấu sẽ bị phong ấn vào cục cưng này. Đừng lo, nó thuộc hệ mộc thạch, phong ấn bao năm nó vẫn y thinh một màu xám lầm lỳ. Đỉnh cow!

---
LỜI KẾT: HÃY NHƯ ĐÁ!

Cuộc đời dâu bể, dù có chìm xuống nước, đá vẫn là đá. Nó kệ thây sự đời. Thấy mệt quá thì rúc vào góc nằm im. 
Bạn cũng vậy! Thấy mệt quá thì kệ đời, nghỉ ngơi. Đi làm vì đam mê hốt bạc chứ không phải bán mạng để bệnh viện thu hết. Hãy sống bền bỉ và lì lợm như một viên đá!

"Vô tri mà trường tồn!" - Founder Bé Đá Vô Tri.
"""

class PDF(FPDF):
    def header(self):
        pass
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', '', 8)
        self.cell(0, 10, f'Trang {self.page_no()}', 0, 0, 'C')

try:
    pdf = PDF()
    
    # Try using system Arial
    font_path = "/Library/Fonts/Arial.ttf"
    font_bold_path = "/Library/Fonts/Arial Bold.ttf"
    
    if os.path.exists(font_path):
        pdf.add_font('Arial', '', font_path, uni=True)
        pdf.add_font('Arial', 'B', font_bold_path, uni=True)
    else:
        # Fallback to default, though utf-8 might complain
        pass

    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="CẨM NANG GIAO TIẾP VỚI PET ĐÁ", ln=True, align='C')
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, txt="(Dành riêng cho những kẻ sắp trầm cảm chốn công sở)", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", "", 11)
    lines = content.split('\n')
    for line in lines[3:]:
        if line.startswith("BÀI") or line.startswith("LỜI") or line.startswith("CẨM"):
            pdf.set_font("Arial", "B", 14)
            pdf.multi_cell(0, 10, text=line)
            pdf.set_font("Arial", "", 11)
        else:
            pdf.multi_cell(0, 8, text=line)

    pdf.output("Cam_nang_Pet_Da.pdf")
    print("PDF created successfully!")
except Exception as e:
    print(f"Error: {e}")
