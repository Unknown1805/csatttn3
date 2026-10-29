# Biên bản bàn giao dữ liệu và log kiểm thử Restic (P2b)

- Người thực hiện bàn giao: Nguyễn Vũ Tuấn Phong (@nvtp0511)
- Người nhận:
  - Nguyễn Gia Khánh (Phụ trách đối chiếu SHA-256 & Chain of Custody)
  - Nguyễn Bảo Minh (Phụ trách trích xuất log & Timeline)
- Reviewer: Nhữ Duy Anh Minh (@Unknown1805)
- Ngày lập biên bản: 29/10/2026
- Căn cứ đầu vào: Kết quả kiểm thử P2 đã nghiệm thu và merge tại PR #9 (Issue #8)

---

## 1. Môi trường thực nghiệm và định danh kỹ thuật

- Môi trường kiểm thử: Kali GNU/Linux Rolling 2025.4 (Kernel x86_64) trên VMware Workstation Pro 17.6.4 build-24832109.
- Phiên bản công cụ: `restic 0.19.1 compiled with go1.26.4 on linux/amd64`.
- Phân biệt định danh kho và bản sao lưu:
  - **Repository ID:** `b4efe585` (Định danh kho lưu trữ cục bộ tại `~/lab-restic/repo_backup`).
  - **Snapshot ID:** `b4efe585` (Mã định danh bản sao lưu chụp dữ liệu tại thời điểm `2026-10-28 08:49:30 AM UTC`).

---

## 2. Thông tin gói bàn giao (Lưu trữ ngoài Git)

- Tên file gói nén: `p2b_restic_tuanphong.tar.gz`
- SHA-256 của gói bàn giao: `74a4a535fd75e6e4ecec6bab18302e6d853a39acf50e3b91d15b2fd808da717a`
- Kênh bàn giao: Kênh trao đổi nội bộ nhóm trên Messenger.
- Thời điểm gửi bàn giao (UTC+7): `2026-10-28 16:46:23 UTC+7`
- Trạng thái xác nhận: Đã gửi file thành công; đang chờ Khánh và Bảo Minh xác nhận đọc được dữ liệu.

---

## 3. Cấu trúc và thành phần dữ liệu trong gói

Gói bàn giao được phân tách thành 4 phân vùng độc lập, không chứa thông tin xác thực hay mật khẩu:

| Tên thư mục | Số lượng file | Mô tả mục đích sử dụng | Người thụ hưởng |
| --- | --- | --- | --- |
| `source/` | 15 file (`file_01.txt` - `file_15.txt`) | Dữ liệu giả gốc trước khi đưa vào backup Restic | Nguyễn Gia Khánh |
| `restored/` | 15 file (`file_01.txt` - `file_15.txt`) | Dữ liệu được trích xuất hoàn chỉnh từ snapshot `b4efe585` | Nguyễn Gia Khánh |
| `manifest/` | 1 file (`manifest_goc.txt`) | Danh mục mã băm SHA-256 tham chiếu chuẩn của 15 file nguồn | Nguyễn Gia Khánh |
| `logs/` | 4 file log (`.log`) | Nhật ký câu lệnh thực thi, mốc thời gian UTC và kết quả xác thực | Nguyễn Bảo Minh |

### Chi tiết các file nhật ký (logs):
1. `01_backup.log`: Lệnh `restic backup`, log mở kho, snapshot ID tạo ra và mốc thời gian UTC bắt đầu/kết thúc.
2. `02_check.log`: Lệnh `restic check --read-data` và log quét 16/16 packs toàn vẹn (`no errors were found`).
3. `03_restore.log`: Lệnh `restic restore b4efe585` và bản tóm tắt khôi phục 15 file.
4. `04_verify_hash.log`: Lệnh đối chiếu tự động `sha256sum -c` xác nhận 15/15 file đạt kết quả `OK`.

---

## 4. Hướng dẫn đối chiếu và trích xuất cho thành viên

- **Dành cho Nguyễn Gia Khánh:** Có thể đứng tại thư mục `restored/` và chạy lệnh `sha256sum -c ../manifest/manifest_goc.txt` để tự kiểm chứng tính toàn vẹn 100% độc lập.
- **Dành cho Nguyễn Bảo Minh:** Toàn bộ các mốc thời gian sự kiện trong `logs/` đều sử dụng chuẩn UTC, có thể trích dẫn trực tiếp tên file log và dòng tương ứng vào bảng Timeline của nhóm.

---

## 5. Kết luận bảo mật

Gói bàn giao hoàn toàn sạch:
- Toàn bộ dữ liệu kiểm thử, log chi tiết và file nén đều nằm ngoài Git.
- Repository Restic gốc, cache và mật khẩu kho không được đính kèm trong gói bàn giao.
- Chỉ đưa biên bản bàn giao và bảng tổng kết lên repository Git theo đúng quy định an toàn thông tin.