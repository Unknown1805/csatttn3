# Báo cáo diễn tập phát hiện dữ liệu thay đổi và khôi phục bằng Restic (P3)

- Người thực hiện: Nguyễn Vũ Tuấn Phong (@nvtp0511)
- Reviewer: Nhữ Duy Anh Minh (@Unknown1805)
- Mã lượt chạy (Run ID): `P3-RESTIC-20261030103414`
- Căn cứ đầu vào: Tiếp nối kết quả P2 (PR #9 / Issue #8) và biên bản bàn giao P2b (PR #16 / Issue #13)
- Issue theo dõi: #18

---

## 1. Môi trường thực tế và định danh kỹ thuật

- Môi trường kiểm thử: Kali GNU/Linux Rolling 2025.4 (Kernel x86_64) trên VMware Workstation Pro 17.6.4 build-24832109.
- Múi giờ hệ thống VM: Môi trường tiếp tục duy trì cấu hình múi giờ mặc định EDT (`UTC-4`) nhằm bảo đảm tính nhất quán thực nghiệm xuyên suốt từ P2. Toàn bộ mốc thời gian ghi nhận và đo lường sự kiện đều được trích xuất theo chuẩn quốc tế UTC (`date -u`).
- Phiên bản công cụ: `restic 0.19.1 compiled with go1.26.4 on linux/amd64`.
- Phân vùng thử nghiệm: `~/lab-restic-p3/` (Khu vực độc lập ngoài Git, bảo lưu toàn bộ dữ liệu, kho và log của P2).
- Thông tin định danh:
  - **Repository ID:** `e09f489deb` (Định danh kho cục bộ tạo mới tại `~/lab-restic-p3/repo`).
  - **Snapshot ID:** `3ad2e70f` (Mã băm SHA-256 đầy đủ: `3ad2e70fed735583ec674b13b56482d39aecc77f2a994d1b5c038adc2e4e60e8`).
  - **Thư mục chạy lệnh backup:** `~/lab-restic-p3`

---

## 2. Dữ liệu gốc và Manifest trước sao lưu

- Số lượng dữ liệu giả: 15 file mẫu (`file_01.txt` đến `file_15.txt`) được sao chép sang `~/lab-restic-p3/data_source`.
- Vị trí lưu Manifest: `~/lab-restic-p3/manifest/manifest_p3.sha256` (Lưu độc lập bên ngoài thư mục dữ liệu nguồn).
- Quy chuẩn lập Manifest: Thực thi trực tiếp bên trong thư mục dữ liệu nguồn để mã băm chỉ gắn với tên file tương đối, lưu file manifest ra thư mục độc lập bên ngoài:

```bash
cd ~/lab-restic-p3/data_source
sha256sum file_*.txt > ~/lab-restic-p3/manifest/manifest_p3.sha256
```

> **Danh mục mã băm SHA-256 tham chiếu ban đầu:**
> ```text
> 5cc99c59c212e43bafc1fb9556e282655058497169ebeb676b8c8f29c96167f1  file_01.txt
> 40b54fd0d8712f1cc0383c2f297656d0b37ace02b1cb03e100424bde2eeecc61  file_02.txt
> 36fcc25df3166df8a318930fa8279431e9c7ea2973267057f03af6ddb64e1356  file_03.txt
> 6d66d7ebe59ccb22f69c219f7a25dc18d6931f58b421cb1650b597df820c13d6  file_04.txt
> a06a82276444497de96620a3e87d56cd8f6d1a84b04a8251ae1695140d90d8a1  file_05.txt
> b1099c5445bc7c5dc664596c878fc52e94608449208b893e9babc180208b9d43  file_06.txt
> 4415645587270ed337171b925eaec170180a0f0be8fff66d9cb812c6f1802d30  file_07.txt
> 6a51b707f51218c2544bc89184fbae9b985c250ba4ccdffc015b60441d049c87  file_08.txt
> 17eae89a8491228a86eae84bc67afec58253b777df76d9d3f44f6f3fdd02240b  file_09.txt
> 3d62432080ba79d99ce88066fd2623457294e9383362e0a099c4c46fce397e3d  file_10.txt
> 96579a075797dcf67034f29d9685241580e1bd96a7509fa88f78acc45305fffa  file_11.txt
> ba7adb9cb33acb1096a6fc103add3b83da4a5a366bc880b0589f916d462c4926  file_12.txt
> 48513b0ceec268a440be5e863cb87afc21be9a08c87449021bfd3a709e4b6d89  file_13.txt
> f1e65a3f4724ec880f756a6d75764dce20815091fada666867c8d9368eea58dc  file_14.txt
> 2c56b54153b3b97284d203c899f42c7dbb3c4c6f5b5207d9e481dd1d237a42e2  file_15.txt
> ```

---

## 3. Nhật ký sao lưu và trích xuất JSON Metadata
### 3.1. Lệnh thực thi và mốc thời gian Backup

- Thư mục chạy lệnh: `~/lab-restic-p3`
- File log ghi nhận: `~/lab-restic-p3/logs/01_backup.log`
- Mốc bắt đầu chạy lệnh (UTC): `2026-10-30 10:36:14 UTC`
- Mốc hoàn thành ghi nhận (UTC): `2026-10-30 10:36:40 UTC`

```bash
echo "--- BACKUP START (UTC): $(date -u +"%Y-%m-%d %H:%M:%S UTC") ---" | tee ~/lab-restic-p3/logs/01_backup.log
restic -r ./repo backup ./data_source | tee -a ~/lab-restic-p3/logs/01_backup.log
echo "--- BACKUP END (UTC): $(date -u +"%Y-%m-%d %H:%M:%S UTC") ---" | tee -a ~/lab-restic-p3/logs/01_backup.log
```

### 3.2. Trích đoạn JSON Metadata của snapshot P3 (`3ad2e70f`)
Trích xuất từ lệnh `restic -r ~/lab-restic-p3/repo --json snapshots 3ad2e70f`:

```json
[
  {
    "time": "2026-10-30T06:36:32.711446492-04:00",
    "tree": "a5a1a9056028bb00d573676f54c11ae02a20d65f4684577f5a6853f388620098",
    "paths": [
      "/home/nvtp05112/lab-restic-p3/data_source"
    ],
    "hostname": "nvtp05112",
    "username": "nvtp05112",
    "uid": 1000,
    "gid": 1000,
    "program_version": "restic 0.19.1",
    "summary": {
      "backup_start": "2026-10-30T06:36:32.711446492-04:00",
      "backup_end": "2026-10-30T06:36:33.436445184-04:00",
      "files_new": 15,
      "files_changed": 0,
      "files_unmodified": 0,
      "dirs_new": 1,
      "dirs_changed": 0,
      "dirs_unmodified": 0,
      "data_blobs": 15,
      "tree_blobs": 2,
      "data_added": 7149,
      "data_added_packed": 3652,
      "total_files_processed": 15,
      "total_bytes_processed": 1065
    },
    "id": "3ad2e70fed735583ec674b13b56482d39aecc77f2a994d1b5c038adc2e4e60e8",
    "short_id": "3ad2e70f"
  }
]
```

### 3.3. Đối chiếu tính nhất quán số liệu
- **Khớp nối thời gian:** Metadata ghi nhận `backup_start: 2026-10-30T06:36:32.711446492-04:00`. Quy đổi từ múi giờ EDT (`UTC-4`) sang UTC tương ứng là `10:36:32 UTC`. Mốc này nằm chuẩn xác trong khoảng thời gian chạy lệnh terminal (`10:36:14 UTC` đến `10:36:40 UTC`).
- **Khớp nối dữ liệu:** 
  - `total_files_processed`: 15 file mới hoàn toàn (`files_new: 15`).
  - `total_bytes_processed`: 1065 bytes. Trường này phản ánh thuần túy tổng kích thước thực tế của 15 file dữ liệu nguồn được xử lý (không bao gồm metadata hay cấu trúc cây thư mục).
  - Đối chiếu kiểm tra thực tế bằng lệnh `wc -c file_*.txt` trong thư mục nguồn:
    ```text
    71 file_01.txt
    71 file_02.txt
    71 file_03.txt
    71 file_04.txt
    71 file_05.txt
    71 file_06.txt
    71 file_07.txt
    71 file_08.txt
    71 file_09.txt
    71 file_10.txt
    71 file_11.txt
    71 file_12.txt
    71 file_13.txt
    71 file_14.txt
    71 file_15.txt
    1065 total
    ```
    Tổng kích thước đo được là 1065 bytes, khớp hoàn toàn 1:1 với giá trị `total_bytes_processed: 1065` trong JSON metadata.

---

## 4. Diễn tập phát hiện thay đổi dữ liệu (Tampering Detection)

### 4.1. Kịch bản can thiệp chủ ý trên bản sao P3
Sau khi hoàn tất backup, dữ liệu được sao chép sang vùng kiểm thử giả lập `~/lab-restic-p3/tampered` và can thiệp bằng các lệnh:

1. file_01.txt: Thêm chuỗi ký tự giả mạo làm sai lệch mã băm SHA-256
```bash
echo "MALICIOUS TAMPERED CONTENT" >> ~/lab-restic-p3/tampered/file_01.txt
```
2. file_02.txt: Xóa hoàn toàn file khỏi hệ thống
```bash
rm ~/lab-restic-p3/tampered/file_02.txt
```
3. 13 file còn lại (file_03.txt đến file_15.txt): Giữ nguyên vẹn

### 4.2. Bảng kết quả đối chiếu với Manifest gốc
- Mốc thời gian thực hiện kiểm tra (UTC): `2026-10-30 10:39:43 UTC`
- Thư mục thực thi: `~/lab-restic-p3/tampered`
- Lệnh thực thi:
  ```bash
  cd ~/lab-restic-p3/tampered
  sha256sum -c ~/lab-restic-p3/manifest/manifest_p3.sha256
  ```

| Tên file | Trạng thái thực tế | Kết quả kiểm tra SHA-256 | Đánh giá nghiệm thu |
| --- | --- | --- | --- |
| `file_01.txt` | Bị sửa nội dung | FAILED (Không khớp mã băm) | Phát hiện đúng 100% |
| `file_02.txt` | Bị xóa khỏi thư mục | FAILED open or read (Không tìm thấy file) | Phát hiện đúng 100% |
| `file_03.txt` - `file_15.txt` | Giữ nguyên gốc | OK (13/13 file khớp mã băm) | Đạt chuẩn toàn vẹn |

> **Trích đoạn log phát hiện thay đổi:**
> ```text
> file_01.txt: FAILED
> sha256sum: file_02.txt: No such file or directory
> file_02.txt: FAILED open or read
> file_03.txt: OK
> file_04.txt: OK
> file_05.txt: OK
> file_06.txt: OK
> file_07.txt: OK
> file_08.txt: OK
> file_09.txt: OK
> file_10.txt: OK
> file_11.txt: OK
> file_12.txt: OK
> file_13.txt: OK
> file_14.txt: OK
> file_15.txt: OK
> sha256sum: WARNING: 1 listed file could not be read
> sha256sum: WARNING: 1 computed checksum did NOT match
> ```

---

## 5. Kết quả khôi phục dữ liệu (Restore) và xác minh

### 5.1. Ánh xạ đường dẫn sau restore
- Thư mục đích rỗng chỉ định khi chạy lệnh: `~/lab-restic-p3/restored`
- Cơ chế ánh xạ của Restic: Restic bảo toàn cấu trúc đường dẫn tương đối đã backup từ root của snapshot. Do snapshot lưu `~/lab-restic-p3/data_source`, cây thư mục phục hồi thực tế nằm tại: `~/lab-restic-p3/restored/data_source/`

### 5.2. Đối chiếu toàn vẹn sau phục hồi
- Thư mục kiểm tra: `~/lab-restic-p3/restored/data_source`

**a) Kiểm tra số lượng và danh sách file (chứng minh không thiếu / không thừa):**
- Lệnh thực thi:
  ```bash
  cd ~/lab-restic-p3/restored/data_source
  ls -1 | wc -l
  ls -1
  ```
- Kết quả đầu ra:
  ```text
  15
  ```
  Danh sách hiển thị trả về đúng 15 file từ `file_01.txt` đến `file_15.txt`, không tồn tại bất kỳ file rác hoặc file thừa ngoài danh mục.

**b) Đối chiếu mã băm tính toàn vẹn:**
- Lệnh thực thi:
  ```bash
  cd ~/lab-restic-p3/restored/data_source
  sha256sum -c ~/lab-restic-p3/manifest/manifest_p3.sha256
  ```
- Kết quả: Đủ 15/15 file đạt trạng thái `OK`, toàn vẹn 100% so với trước khi bị can thiệp.

> **Trích đoạn log đối chiếu 15 file sau phục hồi:**
> ```text
> file_01.txt: OK
> file_02.txt: OK
> file_03.txt: OK
> file_04.txt: OK
> file_05.txt: OK
> file_06.txt: OK
> file_07.txt: OK
> file_08.txt: OK
> file_09.txt: OK
> file_10.txt: OK
> file_11.txt: OK
> file_12.txt: OK
> file_13.txt: OK
> file_14.txt: OK
> file_15.txt: OK
> ```


---

## 6. Đo lường thời gian thực tế

### 6.1. Phương pháp đo và cách thức thực thi
- **Cách thức chạy:** Tiến trình đo thời gian được tự động hóa bằng đoạn mã shell script thực thi trực tiếp trên terminal của máy ảo Kali Linux.
- **Thư mục chạy lệnh ban đầu:** `~/lab-restic-p3`
- **Cơ chế đo:** Sử dụng mốc thời gian epoch nanosecond (`date +%s%N`) tại các điểm chặn (checkpoints) trước và sau lệnh restore, lệnh verify, sau đó tính toán thời lượng bằng lệnh `bc` và ghi nhận mốc giờ chuẩn UTC (`date -u`):

```bash
cd ~/lab-restic-p3

# Mốc bắt đầu toàn trình
START_ALL=$(date +%s%N)
START_UTC=$(date -u +"%Y-%m-%d %H:%M:%S UTC")

# 1. Đo riêng tiến trình Restore từ snapshot
RESTORE_START=$(date +%s%N)
restic -r ./repo restore 3ad2e70f --target ./restored
RESTORE_END=$(date +%s%N)

# 2. Chuyển thư mục và đo công đoạn xác minh tính toàn vẹn (Verify)
cd ~/lab-restic-p3/restored/data_source
sha256sum -c ~/lab-restic-p3/manifest/manifest_p3.sha256

# Mốc kết thúc toàn trình
END_ALL=$(date +%s%N)
END_UTC=$(date -u +"%Y-%m-%d %H:%M:%S UTC")

# Tính toán thời lượng (đơn vị: giây)
RESTORE_DURATION=$(echo "scale=3; ($RESTORE_END - $RESTORE_START) / 1000000000" | bc)
TOTAL_DURATION=$(echo "scale=3; ($END_ALL - $START_ALL) / 1000000000" | bc)

echo "=========================================="
echo "Mốc bắt đầu (UTC): $START_UTC"
echo "Mốc kết thúc (UTC): $END_UTC"
echo "Thời lượng chạy lệnh restore: ${RESTORE_DURATION}s"
echo "Tổng thời lượng từ restore đến xác minh: ${TOTAL_DURATION}s"
echo "=========================================="
```

### 6.2. Dữ liệu và trích đoạn log đo lường thực tế
- Mốc bắt đầu quy trình khôi phục (UTC): `2026-10-30 10:46:05 UTC`
- Mốc kết thúc xác minh toàn vẹn (UTC): `2026-10-30 10:47:29 UTC`
- **Thời lượng chạy lệnh restore:** `52.075 giây`
- **Tổng thời lượng từ bắt đầu restore đến hoàn tất xác minh:** `83.426 giây`

> **Trích đoạn đầu ra log thực tế từ terminal:**
> ```text
> restoring snapshot 3ad2e70f of [/home/nvtp05112/lab-restic-p3/data_source] at 2026-10-30 06:36:32.711446492 -0400 EDT by nvtp05112@nvtp05112 to /home/nvtp05112/lab-restic-p3/restored
> ==========================================
> Mốc bắt đầu (UTC): 2026-10-30 10:46:05 UTC
> Mốc kết thúc (UTC): 2026-10-30 10:47:29 UTC
> Thời lượng chạy lệnh restore: 52.075s
> Tổng thời lượng từ restore đến xác minh: 83.426s
> ==========================================
> ```

> **Lưu ý kỹ thuật về chỉ số phục hồi:** 
> Kết quả đo lường trên là thời lượng diễn tập quy trình kỹ thuật độc lập trong môi trường máy ảo cục bộ. Phép thử này chưa bao gồm độ trễ mạng, lưu lượng thực tế và các yếu tố kiểm soát phân tán của bài lab tích hợp, do đó nhóm không tự ý suy diễn hoặc kết luận chỉ số RPO/RTO = 0.

---

## 7. Kết luận an toàn và trạng thái nghiệm thu

1. **Tuân thủ an toàn thông tin:** Dữ liệu mẫu, gói log thô, repository Restic (`~/lab-restic-p3/repo`) và biến mật khẩu được lưu trữ hoàn toàn ngoài Git.
2. **Độ chính xác kỹ thuật:**
   - Phát hiện chuẩn xác 100% hai hành vi can thiệp (1 file sai mã băm, 1 file bị xóa, 13 file giữ nguyên).
   - Khôi phục nguyên vẹn 15/15 file từ snapshot `3ad2e70f` khớp hoàn toàn với manifest gốc.
3. **Trạng thái:** **ĐẠT TẤT CẢ TIÊU CHÍ NGHIỆM THU DIỄN TẬP P3**.