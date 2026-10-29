# Biên bản bàn giao dữ liệu và log kiểm thử Restic (P2b)

- Người thực hiện bàn giao: Nguyễn Vũ Tuấn Phong (@nvtp0511)
- Người nhận:
  - Nguyễn Gia Khánh (Phụ trách đối chiếu SHA-256 & Chain of Custody)
  - Trần Bảo Minh (Phụ trách trích xuất log & Timeline)
- Reviewer: Nhữ Duy Anh Minh (@Unknown1805)
- Ngày lập biên bản: 29/10/2026
- Căn cứ đầu vào: Kết quả kiểm thử P2 đã nghiệm thu và merge tại PR #9 (Issue #8)

---

## 1. Môi trường thực nghiệm và định danh kỹ thuật

- Môi trường kiểm thử: Kali GNU/Linux Rolling 2025.4 (Kernel x86_64) trên VMware Workstation Pro 17.6.4 build-24832109.
- Phiên bản công cụ: `restic 0.19.1 compiled with go1.26.4 on linux/amd64`.
- Phân biệt định danh kho và bản sao lưu:
  - **Repository ID:** `e2cb2e79` (Định danh kho lưu trữ cục bộ tại `~/lab-restic/repo_backup`, sinh ra từ lệnh `init`).
  - **Snapshot ID:** `b4efe585` (Mã định danh bản sao lưu chụp dữ liệu tại thời điểm `Wed Oct 28 08:49:30 AM UTC 2026`).

> **Trích đoạn kiểm chứng phân biệt hai ID từ lệnh `restic snapshots`:**
> ```text
> $ restic -r ./repo_backup snapshots
> repository e2cb2e79 opened (version 2, compression level auto)
> ID        Time                 Host        Tags        Paths                                   Size
> --------------------------------------------------------------------------------------------------------
> b4efe585  2026-10-28 04:49:42  nvtp05112               /home/nvtp05112/lab-restic/data_source  1.040 KiB
> --------------------------------------------------------------------------------------------------------
> Timestamps shown in local time
> 1 snapshots
> ```

---

## 2. Thông tin gói bàn giao (Lưu trữ ngoài Git)

- Tên file gói nén: `p2b_restic_tuanphong.tar.gz`
- SHA-256 của gói bàn giao: `74a4a535fd75e6e4ecec6bab18302e6d853a39acf50e3b91d15b2fd808da717a`
- Kênh bàn giao: Kênh trao đổi nội bộ nhóm trên Messenger.
- Thời điểm gửi bàn giao (UTC+7): `2026-10-28 16:46:23 UTC+7`
- Trạng thái xác nhận:
  - Nguyễn Gia Khánh: Đã tải gói, xác nhận khớp SHA-256 gói và mở kiểm tra được cấu trúc 15 file nguồn / 15 file restore.
  - Trần Bảo Minh: Đã tải gói, xác nhận khớp SHA-256 gói và trích xuất thành công 4 file log.

---

## 3. Cấu trúc và thành phần dữ liệu trong gói

Gói bàn giao được phân tách thành 4 phân vùng độc lập, không chứa thông tin xác thực hay mật khẩu:

| Tên thư mục | Số lượng file | Mô tả mục đích sử dụng | Người thụ hưởng |
| --- | --- | --- | --- |
| `source/` | 15 file (`file_01.txt` - `file_15.txt`) | Dữ liệu giả gốc trước khi đưa vào backup Restic | Nguyễn Gia Khánh |
| `restored/` | 15 file (`file_01.txt` - `file_15.txt`) | Dữ liệu được trích xuất hoàn chỉnh từ snapshot `b4efe585` | Nguyễn Gia Khánh |
| `manifest/` | 1 file (`manifest_goc.txt`) | Danh mục mã băm SHA-256 tham chiếu chuẩn của 15 file nguồn | Nguyễn Gia Khánh |
| `logs/` | 4 file log (`.log`) | Nhật ký câu lệnh thực thi, mốc thời gian UTC và kết quả xác thực | Trần Bảo Minh |

---

## 4. Trích đoạn log thực tế và mốc thời gian kiểm thử

### 4.1. Nhật ký sao lưu (Backup)
- Thư mục thực thi: `~/lab-restic`
- Mốc bắt đầu (UTC): `Wed Oct 28 08:49:30 AM UTC 2026`
- Mốc kết thúc (UTC): `Wed Oct 28 08:49:53 AM UTC 2026`
- Trích đoạn log thực tế:
  ```text
  $ restic -r ./repo_backup backup ./data_source
  repository e2cb2e79 opened (version 2, compression level auto)
  created new cache in /home/nvtp05112/.cache/restic
  processed 15 files, 735 B in 0:00
  snapshot b4efe585 saved
  ```

### 4.2. Nhật ký kiểm tra tính toàn vẹn kho (Check Repository)
- Thư mục thực thi: `~/lab-restic`
- Mốc thời gian (UTC): Chưa xác định chính xác theo giây (thực hiện ngay sau bước sao lưu, khoảng 08:50 UTC)
- Trích đoạn log thực tế:
  ```text
  $ restic -r ./repo_backup check --read-data
  repository e2cb2e79 opened (version 2, compression level auto)
  [0:00] 100.00%  3 / 3 index files loaded
  check for trees, pack files, and indexes
  [0:00] 100.00%  1 / 1 snapshots
  read all data
  [0:01] 100.00%  16 / 16 packs
  no errors were found
  ```

### 4.3. Nhật ký khôi phục dữ liệu (Restore)
- Thư mục thực thi: `~/lab-restic`
- Mốc thời gian (UTC): Chưa xác định chính xác theo giây (thực hiện khoảng 08:50 UTC)
- Trích đoạn log thực tế:
  ```text
  $ restic -r ./repo_backup restore b4efe585 --target ./data_restored
  repository e2cb2e79 opened (version 2, compression level auto)
  restoring <Snapshot 04:49:42 2026-10-28 [./data_source] at b4efe585 by nvtp05112 of> to ./data_restored
  summary: Restored 15 files
  ```

### 4.4. Nhật ký đối chiếu mã băm (Verify Hash)
- Thư mục thực thi: `~/lab-restic/data_restored/data_source`
- Mốc thời gian (UTC): Chưa xác định chính xác theo giây (thực hiện khoảng 08:51 UTC)
- Trích đoạn log thực tế xác nhận 15/15 file:
  ```text
  $ sha256sum -c ~/lab-restic/manifest/manifest_goc.txt
  file_01.txt: OK
  file_02.txt: OK
  file_03.txt: OK
  file_04.txt: OK
  file_05.txt: OK
  file_06.txt: OK
  file_07.txt: OK
  file_08.txt: OK
  file_09.txt: OK
  file_10.txt: OK
  file_11.txt: OK
  file_12.txt: OK
  file_13.txt: OK
  file_14.txt: OK
  file_15.txt: OK
  ```

---

## 5. Hướng dẫn đối chiếu và trích xuất cho thành viên

- **Dành cho Nguyễn Gia Khánh:** Đứng tại thư mục `restored/` và chạy lệnh `sha256sum -c ../manifest/manifest_goc.txt` để tự kiểm chứng tính toàn vẹn 100% độc lập.
- **Dành cho Trần Bảo Minh:** Có thể trích dẫn trực tiếp tên file log trong thư mục `logs/` và dòng tương ứng vào bảng Timeline của nhóm. Các mốc check, restore và verify do không chạy kèm lệnh `date -u` nên được ghi nhận là "chưa xác định chính xác theo giây".

---

## 6. Kết luận bảo mật

Gói bàn giao hoàn toàn sạch:
- Toàn bộ dữ liệu kiểm thử, log chi tiết và file nén đều nằm ngoài Git.
- Repository Restic gốc, cache và mật khẩu kho không được đính kèm trong gói bàn giao.
- Chỉ đưa biên bản bàn giao và bảng tổng kết lên repository Git theo đúng quy định an toàn thông tin.