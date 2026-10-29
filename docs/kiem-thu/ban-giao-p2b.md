# Biên bản bàn giao dữ liệu và log kiểm thử Restic (P2b)

* Người thực hiện bàn giao: Nguyễn Vũ Tuấn Phong (@nvtp0511)

* Người nhận:

  * Nguyễn Gia Khánh (Phụ trách đối chiếu SHA-256 & Chain of Custody)

  * Trần Bảo Minh (Phụ trách trích xuất log & Timeline)

* Reviewer: Nhữ Duy Anh Minh (@Unknown1805)

* Ngày lập biên bản: 29/10/2026

* Căn cứ đầu vào: Kết quả kiểm thử P2 đã nghiệm thu và merge tại PR #9 (Issue #8)

* Issue theo dõi bàn giao: #13

## 1. Môi trường thực nghiệm và định danh kỹ thuật

* Môi trường kiểm thử: Kali GNU/Linux Rolling 2025.4 (Kernel x86_64) trên VMware Workstation Pro 17.6.4 build-24832109.

* Thiết lập thời gian hệ thống VM: Do máy ảo Kali cài đặt mặc định chưa cấu hình lại múi giờ nội địa, hệ thống đang nhận múi giờ EDT (`UTC-4`).

* Phiên bản công cụ: `restic 0.19.1 compiled with go1.26.4 on linux/amd64`.

* Phân biệt định danh kho và bản sao lưu:

  * **Repository ID:** `e2cb2e79` (Định danh kho lưu trữ cục bộ tại `~/lab-restic/repo_backup`, sinh ra từ lệnh `init`).

  * **Snapshot ID:** `b4efe585` (Mã băm đầy đủ: `b4efe5857f83b5e9e4ae87e2b97d3632443d721a67a96e7eb37818e58dac8291`).

> **Trích đoạn kiểm chứng phân biệt hai ID từ lệnh `restic snapshots`:**
>
> ```text
> $ restic -r ./repo_backup snapshots
> repository e2cb2e79 opened (version 2, compression level auto)
> ID        Time                 Host        Tags        Paths                                   Size
> --------------------------------------------------------------------------------------------------------
> b4efe585  2026-10-28 04:49:42  nvtp05112               /home/nvtp05112/lab-restic/data_source  1.040 KiB
> --------------------------------------------------------------------------------------------------------
> Timestamps shown in local time
> 1 snapshots
>
> ```

## 2. Thông tin gói bàn giao (Lưu trữ ngoài Git)

* Tên file gói nén: `p2b_restic_tuanphong.tar.gz`

* SHA-256 của gói bàn giao: `74a4a535fd75e6e4ecec6bab18302e6d853a39acf50e3b91d15b2fd808da717a`

* Kênh bàn giao: Kênh trao đổi nội bộ nhóm trên Messenger.

* Thời điểm gửi bàn giao (UTC+7): `2026-10-28 16:46:23 UTC+7`

* Trạng thái xác nhận bàn giao (Đã nghiệm thu tại Issue #13):

  * **Nguyễn Gia Khánh:** Đã xác nhận tại Issue #13: Tải gói thành công, mã băm SHA-256 của gói khớp chính xác, giải nén và kiểm tra đọc tốt 15 file nguồn (`source/`), 15 file khôi phục (`restored/`) và `manifest_goc.txt`. [Comment xác nhận của Khánh tại Issue #13](https://github.com/Unknown1805/csatttn3/issues/13#issuecomment-6500699957)

  * **Trần Bảo Minh:** Đã xác nhận tại Issue #13: Tải gói thành công, mã băm SHA-256 của gói khớp chính xác, giải nén và trích xuất nguyên vẹn 4 file nhật ký (`logs/`) phục vụ dựng Timeline. [Comment xác nhận của Bảo Minh tại Issue #13](https://github.com/Unknown1805/csatttn3/issues/13#issuecomment-6500830065)

## 3. Cấu trúc và thành phần dữ liệu trong gói

Gói bàn giao được phân tách thành 4 phân vùng độc lập, không chứa thông tin xác thực hay mật khẩu:

| Tên thư mục | Số lượng file | Mô tả mục đích sử dụng | Người nhận |
| ----- | ----- | ----- | ----- |
| `source/` | 15 file (`file_01.txt` - `file_15.txt`) | Dữ liệu giả gốc trước khi đưa vào backup Restic | Nguyễn Gia Khánh |
| `restored/` | 15 file (`file_01.txt` - `file_15.txt`) | Dữ liệu được trích xuất hoàn chỉnh từ snapshot `b4efe585` | Nguyễn Gia Khánh |
| `manifest/` | 1 file (`manifest_goc.txt`) | Danh mục mã băm SHA-256 tham chiếu chuẩn của 15 file nguồn | Nguyễn Gia Khánh |
| `logs/` | 4 file log (`.log`) | Nhật ký câu lệnh thực thi, mốc thời gian UTC và kết quả xác thực | Trần Bảo Minh |

## 4. Trích đoạn metadata và giải trình kỹ thuật

Trích xuất JSON metadata thực tế từ lệnh `restic -r ./repo_backup --json snapshots b4efe585`:

```json
[
  {
    "time": "2026-10-28T04:49:42.767898488-04:00",
    "tree": "abe77f202f465928e13427dc1f1f1ec2e02ec43c513927f0013da53c96fe517b",
    "paths": ["/home/nvtp05112/lab-restic/data_source"],
    "hostname": "nvtp05112",
    "username": "nvtp05112",
    "uid": 1000,
    "gid": 1000,
    "program_version": "restic 0.19.1",
    "summary": {
      "backup_start": "2026-10-28T04:49:42.767898488-04:00",
      "backup_end": "2026-10-28T04:49:48.747991337-04:00",
      "files_new": 15,
      "files_changed": 0,
      "files_unmodified": 0,
      "dirs_new": 1,
      "dirs_changed": 0,
      "dirs_unmodified": 0,
      "data_blobs": 15,
      "tree_blobs": 2,
      "data_added": 7152,
      "data_added_packed": 3581,
      "total_files_processed": 15,
      "total_bytes_processed": 1065
    },
    "id": "b4efe5857f83b5e9e4ae87e2b97d3632443d721a67a96e7eb37818e58dac8291",
    "short_id": "b4efe585"
  }
]

```

### 4.1. Giải trình mốc thời gian (Timestamp & Timezone)

* **Nguyên nhân chênh lệch hiển thị:** Máy ảo Kali Linux tại thời điểm thử nghiệm đặt múi giờ mặc định là EDT (`UTC-4`). Do đó, lệnh `restic snapshots` khi xuất dạng bảng tự động hiển thị theo giờ địa phương của máy ảo là `04:49:42`.

* **Quy đổi chuẩn UTC:** Trong metadata JSON, mốc thời gian ghi nhận kèm offset rõ ràng:
  `04:49:42.767898488-04:00` tương đương chuẩn với `08:49:42.767898488 UTC`.

* **Phân tách hai mốc sự kiện:**

  * *Mốc bắt đầu thực thi lệnh ngoài terminal:* `08:49:30 UTC` (thời điểm gõ lệnh chạy tiến trình backup).

  * *Mốc Restic chính thức ghi nhận snapshot (`backup_start` trong metadata):* `08:49:42 UTC`. Hai mốc này cách nhau 12 giây khởi tạo cache và quét chỉ mục, hoàn toàn logic và nhất quán.

### 4.2. Giải trình kích thước dữ liệu (Data Size)

* Cả hai đầu ra đều thuộc chính xác cùng một snapshot `b4efe585`.

* **Giá trị 1.040 KiB:** Lấy từ trường `total_bytes_processed: 1065` byte trong metadata snapshot. Giá trị này bao gồm toàn bộ 15 file nội dung cộng với metadata của các node thư mục và cấu trúc cây Restic (phép tính: 1065 chia cho 1024 làm tròn xấp xỉ bằng 1.040 KiB).

* **Giá trị 735 B:** Là tổng kích thước nội dung dữ liệu thô (payload) của đúng 15 file văn bản mẫu (phép tính: 15 file nhân với 49 byte/file bằng 735 byte), phản ánh dung lượng file vật lý trước khi đóng gói cây thư mục.

## 5. Trích đoạn log thực tế và mốc thời gian kiểm thử

### 5.1. Nhật ký sao lưu (Backup)

* Thư mục thực thi: `~/lab-restic`

* Mốc bắt đầu (UTC): `Wed Oct 28 08:49:30 AM UTC 2026`

* Mốc kết thúc (UTC): `Wed Oct 28 08:49:53 AM UTC 2026`

* Trích đoạn log thực tế:

  ```text
  $ restic -r ./repo_backup backup ./data_source
  repository e2cb2e79 opened (version 2, compression level auto)
  created new cache in /home/nvtp05112/.cache/restic
  processed 15 files, 735 B in 0:00
  snapshot b4efe585 saved

  ```

### 5.2. Nhật ký kiểm tra tính toàn vẹn kho (Check Repository)

* Thư mục thực thi: `~/lab-restic`

* Mốc thời gian (UTC): Chưa xác định chính xác theo giây (thực hiện ngay sau bước sao lưu, khoảng 08:50 UTC)

* Trích đoạn log thực tế:

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

### 5.3. Nhật ký khôi phục dữ liệu (Restore)

* Thư mục thực thi: `~/lab-restic`

* Mốc thời gian (UTC): Chưa xác định chính xác theo giây (thực hiện khoảng 08:50 UTC)

* Trích đoạn log thực tế:

  ```text
  $ restic -r ./repo_backup restore b4efe585 --target ./data_restored
  repository e2cb2e79 opened (version 2, compression level auto)
  restoring <Snapshot 04:49:42 2026-10-28 [./data_source] at b4efe585 by nvtp05112 of> to ./data_restored
  summary: Restored 15 files

  ```

### 5.4. Nhật ký đối chiếu mã băm (Verify Hash)

* Thư mục thực thi: `~/lab-restic/data_restored/data_source`

* Mốc thời gian (UTC): Chưa xác định chính xác theo giây (thực hiện khoảng 08:51 UTC)

* Trích đoạn log thực tế xác nhận 15/15 file:

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

## 6. Hướng dẫn đối chiếu và trích xuất cho thành viên

* **Dành cho Nguyễn Gia Khánh:** Đứng tại thư mục `restored/` và chạy lệnh `sha256sum -c ../manifest/manifest_goc.txt` để tự kiểm chứng tính toàn vẹn 100% độc lập.

* **Dành cho Trần Bảo Minh:** Có thể trích dẫn trực tiếp tên file log trong thư mục `logs/` và dòng tương ứng vào bảng Timeline của nhóm. Các mốc check, restore và verify do không chạy kèm lệnh `date -u` nên được ghi nhận là "chưa xác định chính xác theo giây".

## 7. Kết luận bảo mật

Gói bàn giao hoàn toàn sạch:

* Toàn bộ dữ liệu kiểm thử, log chi tiết và file nén đều nằm ngoài Git.

* Repository Restic gốc, cache và mật khẩu kho không được đính kèm trong gói bàn giao.

* Chỉ đưa biên bản bàn giao và bảng tổng kết lên repository Git theo đúng quy định an toàn thông tin.