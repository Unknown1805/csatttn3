# B2 — Timeline kiểm thử backup và khôi phục bằng Restic

## 1. Thông tin chung

- **Người thực hiện:** Trần Bảo Minh (@winolf)
- **Issue:** #15
- **Reviewer:** Nhữ Duy Anh Minh (@Unknown1805)
- **Nguồn thực nghiệm:** Nguyễn Vũ Tuấn Phong (@nvtp0511)
- **Phạm vi:** Phân tích timeline kiểm thử backup và restore dữ liệu giả bằng Restic.
- **Ngày thực nghiệm:** 28/10/2026
- **Trạng thái:** Đã đọc và đối chiếu log bàn giao; chờ review và xác nhận các thông tin còn thiếu.

### Môi trường thực nghiệm

Theo báo cáo P2 tại PR #9:

| Thành phần | Thông tin |
|---|---|
| Hệ điều hành VM | Kali GNU/Linux 2025.4 |
| Phần mềm ảo hóa | VMware Workstation 17.6.4 |
| Restic | 0.19.1 |
| Repository backend | Local |
| Repository path | `~/lab-restic/repo_backup` |
| Source path | `~/lab-restic/data_source` |
| Restore path | `~/lab-restic/data_restored` |

Đây là phép thử backup/restore dữ liệu giả, không phải chứng cứ về một cuộc tấn công ransomware thực tế.

## 2. Thông tin gói chứng cứ

### 2.1. Tiếp nhận gói dữ liệu

- **Tên gói:** `p2b_restic_tuanphong.tar.gz`
- **Người bàn giao:** Nguyễn Vũ Tuấn Phong
- **Nguồn:** Issue #13.
- **Thời điểm nhận UTC chính xác:** Chưa ghi nhận tại thời điểm tiếp nhận.
- **Run ID:** Chưa được cung cấp.

### 2.2. Kiểm tra SHA-256

SHA-256 do Phong cung cấp:

`74a4a535fd75e6e4ecec6bab18302e6d853a39acf50e3b91d15b2fd808da717a`

Lệnh kiểm tra trên máy nhận:

```bash
sha256sum p2b_restic_tuanphong.tar.gz
```

**Kết quả: PASS.**

SHA-256 của gói tải về trùng khớp với mã do Phong cung cấp.

Kết quả này xác nhận tính nhất quán với giá trị hash tham chiếu, không tự chứng minh tính đầy đủ hoặc độ chính xác của toàn bộ nội dung bên trong.

### 2.3. Kiểm tra cấu trúc gói

Lệnh sử dụng:

```bash
tar -tzf p2b_restic_tuanphong.tar.gz
```

Các thành phần quan sát được:

| Thành phần | Nội dung | Số lượng |
|---|---|---|
| `source/` | Dữ liệu nguồn | 15 file |
| `restored/` | Dữ liệu khôi phục | 15 file |
| `manifest/` | `manifest_goc.txt` | 1 file |
| `logs/` | Các log kiểm thử Restic | 4 file |
| `README.txt` | Thông tin gói bàn giao | 1 file |

### 2.4. Danh sách log

| File | Nội dung |
|---|---|
| `01_backup.log` | Lệnh backup và kết quả |
| `02_check.log` | Kiểm tra repository |
| `03_restore.log` | Lệnh restore và kết quả |
| `04_verify_hash.log` | Kiểm tra SHA-256 |

Đã mở và đọc được README cùng toàn bộ bốn file log.

Các đường dẫn `logs/...` bên dưới được tính tương đối từ thư mục `p2b_export/` trong gói.

### 2.5. Định danh thực nghiệm

- **Snapshot ID:** `b4efe585`, được ghi trong log backup và restore.
- **Repository ID:** Log và README hiển thị `b4efe585`; chưa xác minh độc lập định danh đầy đủ.
- **Run ID:** Chưa được cung cấp.

Repository ID và Snapshot ID là hai loại định danh khác nhau. Việc cả hai cùng hiển thị tiền tố `b4efe585` cần được Phong xác nhận.

## 3. Quy tắc thời gian

Các log sử dụng timestamp dạng:

`YYYY-MM-DD HH:MM:SS UTC`

Báo cáo chuẩn hóa sang ISO 8601 với hậu tố `Z`:

`YYYY-MM-DDTHH:MM:SSZ`

Ví dụ:

`2026-10-28 08:49:30 UTC`

Được biểu diễn thành:

`2026-10-28T08:49:30Z`

**Nguyên tắc:**

- Giữ nguyên múi giờ UTC được ghi trong log.
- Không tự bổ sung timestamp cho sự kiện chưa có thời gian.
- Phân biệt thời điểm ghi nhận lệnh và thời điểm hoàn thành thao tác.
- Không sử dụng thời gian commit hoặc PR GitHub làm thời gian thực nghiệm.
- Không tự suy ra timestamp tuyệt đối từ các chỉ số tiến trình tương đối của Restic.
- Chưa xác minh độc lập độ chính xác của đồng hồ trên VM nguồn.

Riêng `04_verify_hash.log`, timestamp `08:51:00 UTC` được ghi tại dòng thông tin thư mục làm việc (`CWD`), không trực tiếp xác nhận thời điểm bắt đầu thực thi lệnh kiểm tra SHA-256.

### Bảng múi giờ theo từng nguồn 
| File log | Timestamp gốc | Giới hạn |
|---|---|---|
| `01_backup.log` | UTC, dòng 1 và 6 | Có mốc bắt đầu/kết thúc |
| `02_check.log` | UTC, dòng 1 | Thiếu timestamp kết thúc |
| `03_restore.log` | UTC, dòng 1 | Dòng 3 chứa thời gian snapshot, không phải giờ hoàn tất restore |
| `04_verify_hash.log` | UTC, dòng 1 | Timestamp gắn với CWD, không trực tiếp ghi giờ chạy lệnh |

## 4. Timeline kiểm thử

| Thời gian UTC | Sự kiện | Nguồn chứng cứ | Quan sát từ log | Suy luận / giới hạn |
|---|---|---|---|---|
| `2026-10-28T08:49:30Z` | Ghi nhận lệnh backup | `01_backup.log:1` | Lệnh `restic -r ./repo_backup backup ./data_source` | Mốc bắt đầu theo log |
| `2026-10-28T08:49:53Z` | Backup hoàn thành | `01_backup.log:4-6` | Xử lý 15 file, lưu snapshot `b4efe585` và báo thành công | Hai mốc ghi nhận cách nhau 23 giây |
| `2026-10-28T08:50:10Z` | Ghi nhận lệnh kiểm tra repository | `02_check.log:1` | Chạy `check --read-data` | Chưa có timestamp kết thúc |
| Không xác định | Kết quả repository check | `02_check.log:3-8` | Kiểm tra 1/1 snapshot, đọc 16/16 packs, không phát hiện lỗi | Không xác định thời điểm hoàn tất |
| `2026-10-28T08:50:35Z` | Ghi nhận lệnh restore | `03_restore.log:1` | Restore snapshot `b4efe585` | Mốc bắt đầu theo log |
| Không xác định | Kết quả restore | `03_restore.log:3-4` | Log báo đã restore 15 file | Chưa xác định thời điểm hoàn thành |
| `2026-10-28T08:51:00Z` | Ghi nhận thư mục làm việc trước bước kiểm tra SHA-256 | `04_verify_hash.log:1-2` | Log ghi CWD và lệnh `sha256sum -c` | Không xác định chính xác thời điểm bắt đầu thực thi lệnh |
| Không xác định | Kết quả kiểm tra SHA-256 | `04_verify_hash.log:3-17` | 15 file đều có kết quả `OK` | Chưa có timestamp hoàn tất |

**Lưu ý:** Các kết quả không có timestamp được giữ theo thứ tự ghi nhận trong từng log. Không tự gán thời điểm hoàn thành.

### Phân biệt 15 file và 16 packs

Trong `02_check.log`, Restic ghi:

```text
[0:00] 100.00%  1 / 1 snapshots
read all data
[0:01] 100.00%  16 / 16 packs
no errors were found
```

Các con số có ý nghĩa khác nhau:

- **15 file nguồn:** Số file văn bản trong dữ liệu kiểm thử.
- **15 file restored:** Số file dữ liệu trong thư mục khôi phục.
- **1 snapshot:** Số snapshot được kiểm tra.
- **16 packs:** Số pack lưu trữ nội bộ được Restic kiểm tra.

**16 packs không có nghĩa là 16 file dữ liệu nguồn hoặc 16 file khôi phục.**

## 5. Đối chiếu với báo cáo P2

Nguồn tham chiếu: `docs/kiem-thu/backup-restore-p2.md`, PR #9.

| Hạng mục | Báo cáo P2 | Log bàn giao | Đánh giá |
|---|---|---|---|
| Backup bắt đầu | 08:49:30 UTC | `01_backup.log:1` | Trùng Khớp |
| Backup kết thúc | 08:49:53 UTC | `01_backup.log:6` | Trùng Khớp |
| Snapshot ID | `b4efe585` | `01_backup.log:5` | Trùng Khớp |
| Repository check | Không phát hiện lỗi | `02_check.log:8` | Trùng Khớp |
| Restore | Khôi phục thành công | `03_restore.log:4` | Trùng Khớp |
| SHA-256 | 15/15 file | `04_verify_hash.log:3-17` | Trùng Khớp |

### 5.1. Kết quả đối chiếu

Hai timestamp backup trong báo cáo P2 phù hợp với log bàn giao.

Snapshot ID được sử dụng nhất quán giữa báo cáo backup và lệnh restore.

Repository check không phát hiện lỗi theo log.

Log restore ghi nhận đã khôi phục 15 file.

Log kiểm tra SHA-256 ghi nhận 15 kết quả `OK`, tương ứng `file_01.txt` đến `file_15.txt`.

### 5.2. Giới hạn kiểm chứng

Việc đối chiếu hiện tại dựa trên báo cáo P2 và các log do cùng người thực hiện phép thử bàn giao.

Chưa thực hiện kiểm chứng độc lập về thời gian hệ thống hoặc Repository ID.

Chưa tự tính và đối chiếu SHA-256 cho từng cặp file nguồn và file khôi phục. Đây là nội dung kiểm tra độc lập thuộc nhiệm vụ của Khánh.

### 5.3. Trích đoạn log tiêu biểu

| Nguồn | Dòng và nội dung log |
|---|---|
| `01_backup.log` | **Dòng 1:** `[2026-10-28 08:49:30 UTC] CMD: restic -r ./repo_backup backup ./data_source` <br> **Dòng 5:** `snapshot b4efe585 saved` <br> **Dòng 6:** `[2026-10-28 08:49:53 UTC] Backup completed successfully.` |
| `02_check.log` | **Dòng 7:** `[0:01] 100.00%  16 / 16 packs` <br> **Dòng 8:** `no errors were found` |
| `03_restore.log` | **Dòng 4:** `summary: Restored 15 files` |
| `04_verify_hash.log` | **Dòng 3:** `file_01.txt: OK` <br> **Dòng 17:** `file_15.txt: OK` |

**Ghi chú:** Đây là các dòng tiêu biểu được trích từ bốn file log trong gói P2b, không phải toàn bộ nội dung log. Con số 16/16 trong `02_check.log` là số packs được kiểm tra, không phải số file dữ liệu.

## 6. Phân tích thời lượng

### 6.1. Backup

Nguồn: `01_backup.log`

- Bắt đầu: `2026-10-28T08:49:30Z`
- Kết thúc: `2026-10-28T08:49:53Z`
- Chênh lệch: **23 giây**.

Đây là khoảng thời gian giữa hai timestamp được ghi trong log, không phải phép đo độc lập thời lượng xử lý nội bộ của Restic.

### 6.2. Repository check

Nguồn: `02_check.log`

- Mốc ghi nhận lệnh: `2026-10-28T08:50:10Z`
- Kết thúc: Không xác định.
- Kết quả: `no errors were found`.

Chưa đủ dữ liệu để xác định thời lượng đầy đủ.

### 6.3. Restore

Nguồn: `03_restore.log`

- Mốc ghi nhận lệnh: `2026-10-28T08:50:35Z`
- Kết thúc: Không xác định.
- Kết quả: `Restored 15 files`.

Chưa đủ dữ liệu để xác định thời lượng restore.

### 6.4. Kiểm tra SHA-256

Nguồn: `04_verify_hash.log`

- Mốc ghi nhận thư mục làm việc: `2026-10-28T08:51:00Z`
- Thời điểm bắt đầu thực thi lệnh: Không xác định chính xác.
- Thời điểm kết thúc: Không xác định.
- Kết quả trong log: 15/15 file báo `OK`.

Không sử dụng timestamp của dòng `CWD` để khẳng định thời điểm bắt đầu thực thi lệnh kiểm tra SHA-256.

### 6.5. RTO/RPO

Chưa đủ dữ liệu để xác định RTO và RPO thực đo.

Phép thử hiện tại không cung cấp đầy đủ mốc mất khả dụng, thời điểm hệ thống được xác nhận phục hồi và thời điểm dữ liệu cần phục hồi tại lúc xảy ra sự cố.

Không coi thời lượng backup hoặc restore là RTO/RPO.

## 7. Các vấn đề cần xác nhận

1. Run ID chính thức của bộ dữ liệu P2b.
2. Repository ID thực tế, xác minh độc lập với Snapshot ID.
3. Timestamp kết thúc kiểm tra repository (nếu có).
4. Timestamp kết thúc restore (nếu có).
5. Timestamp bắt đầu/kết thúc thực tế của bước kiểm tra SHA-256 (nếu có).
6. Phương pháp ghi timestamp và độ tin cậy của đồng hồ VM nguồn.

Các thông tin chưa có được giữ ở trạng thái chưa xác định, không tự suy đoán hoặc bổ sung vào log cũ.

## 8. Kết luận

Đã tiếp nhận gói chứng cứ P2b từ Phong và xác nhận SHA-256 của gói trùng với giá trị được cung cấp.

Đã kiểm tra cấu trúc gói và đọc được bốn file log Restic.

Từ log, xác định được các mốc:

- `08:49:30 UTC`: Ghi nhận lệnh backup.
- `08:49:53 UTC`: Backup hoàn thành.
- `08:50:10 UTC`: Ghi nhận lệnh kiểm tra repository.
- `08:50:35 UTC`: Ghi nhận lệnh restore.
- `08:51:00 UTC`: Ghi nhận thư mục làm việc trước bước kiểm tra SHA-256.

Khoảng thời gian giữa hai mốc backup là **23 giây**.

Các kết quả trong log phù hợp với thông tin chính của báo cáo P2:

- Backup được báo cáo thành công.
- Repository check không phát hiện lỗi.
- Restore được báo cáo hoàn thành với 15 file.
- Kiểm tra SHA-256 trong log báo 15/15 file `OK`.

Log kiểm tra repository ghi nhận 16/16 packs được đọc. Đây là số đơn vị lưu trữ nội bộ của Restic, không phải số lượng file dữ liệu nguồn.

Do thiếu một số timestamp kết thúc, chưa đủ căn cứ để xác định thời lượng của toàn bộ các bước hoặc tính RTO/RPO.

Kết quả chỉ phản ánh phép thử backup/restore bằng Restic trên dữ liệu giả. Không sử dụng kết quả để khẳng định đã xảy ra hoặc đã xử lý thành công một cuộc tấn công ransomware.

## 9. Liên kết minh chứng

- Issue B2: #15
- Issue bàn giao P2b: #13
- PR bàn giao P2b: #16
- Báo cáo P2: PR #9
- Tài liệu P2: `docs/kiem-thu/backup-restore-p2.md`
- Gói dữ liệu: `p2b_restic_tuanphong.tar.gz`, lưu ngoài Git.
- SHA-256 gói: `74a4a535fd75e6e4ecec6bab18302e6d853a39acf50e3b91d15b2fd808da717a`

Các file dữ liệu và log gốc được giữ ngoài repository GitHub. Báo cáo chỉ lưu thông tin tổng hợp và các tham chiếu chứng cứ cần thiết.
