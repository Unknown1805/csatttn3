# Báo cáo kiểm thử phục hồi dữ liệu Restic trên VM sạch độc lập (P4)

- Người thực hiện: Nguyễn Vũ Tuấn Phong (@nvtp0511)
- Reviewer / Nghiệm thu: Nhữ Duy Anh Minh (@Unknown1805)
- Căn cứ đầu vào: Tiếp nối kết quả P3 (Issue #18 / PR #25)
- Issue theo dõi: #27

---

## 1. Môi trường thực tế và Bằng chứng phân biệt VM độc lập

Để đảm bảo tính độc lập tuyệt đối theo chuẩn Disaster Recovery (DR) và loại trừ hoàn toàn khả năng sử dụng lại cấu hình, cache hay clone trạng thái đang chạy của VM P3, các thông số định danh phần cứng ảo, hệ điều hành và nguồn cài đặt của 2 VM được ghi nhận và đối chiếu:

### 1.1. Bảng đối chiếu định danh và môi trường 2 máy ảo

| Thuộc tính định danh | VM P3 (Nguồn sao lưu) | VM Phục hồi (VM sạch) | Đánh giá độc lập & Nguồn gốc |
| :--- | :--- | :--- | :--- |
| **Hostname** | `nvtp05112` | `recovery-node` | Khác biệt 100% |
| **Tài khoản người dùng** | `nvtp05112` (UID: 1000) | `kali` (UID: 1000) | Tách biệt hoàn toàn |
| **Machine ID (`/etc/machine-id`)** | `915d7c13989443589b2a5965a79c0576` | `f8b08150ef8d4e1b926e29982e3fe680` | Hai hệ thống OS độc lập hoàn toàn |
| **Địa chỉ MAC (`eth0`)** | `00:0c:29:88:24:54` | `00:0c:29:0c:4d:ec` | Hai card mạng ảo riêng biệt |
| **Nguồn ảnh nền (Base Image)** | `kali-linux-2025.4-installer-amd64.iso` | `kali-linux-2025.4-installer-amd64.iso` | Nguồn ISO gốc chuẩn từ hãng, cài mới hoàn toàn |
| **Phiên bản Restic** | `restic 0.19.1` | `restic 0.19.1 (compiled with go1.26.4 on linux/amd64)` | Đồng nhất phiên bản nhị phân |
| **Hệ điều hành & Kernel** | Kali Rolling 2025.4 (Kernel 6.16.8+kali-amd64) | Kali Rolling 2025.4 (Kernel 6.16.8+kali-amd64) | Bản phân phối chuẩn tương thích |
| **Thư mục làm việc** | `~/lab-restic-p3/` | `~/lab-p4-restore/` | Cấu trúc không gian làm việc mới tinh |

### 1.2. Bằng chứng VM phục hồi là bản cài đặt mới (Clean State)
- **Thời điểm khởi tạo hệ thống tệp:** Phân vùng gốc `/dev/sda1` được tạo vào sáng ngày diễn tập (`Sun Nov 1 06:11:24 2026`):
  ```text
  Filesystem created:       Sun Nov  1 06:11:24 2026
  ```
- **Nhật ký bộ cài đặt OS (`/var/log/installer`):** Toàn bộ file log cài đặt (`syslog`, `partman`, `status`) được ghi nhận đồng bộ lúc `06:39 UTC` ngày 01/11/2026.
- **Lịch sử Shell:** File `~/.bash_history` hoàn toàn không tồn tại trước khi bắt đầu quy trình (`No such file or directory`).
- **Thư mục Home:** Trống trơn, chỉ chứa các thư mục mặc định của hệ thống (`Desktop`, `Documents`, `Downloads`...) và các dotfile hệ thống.

---

## 2. Kiểm tra tiến trình ngầm và Đóng gói chuyển giao trên VM P3

### 2.1. Kiểm tra an toàn tiến trình
Trước khi thực hiện trích xuất dữ liệu kho, VM P3 được rà soát để đảm bảo không có tiến trình Restic nào đang can thiệp hoặc ghi ngầm vào repository:
```bash
pgrep -fl restic || echo "Khong co tien trinh restic dang chay"
```
*Đầu ra thực tế:*
```text
Khong co tien trinh restic dang chay
```

### 2.2. Đóng gói bản sao kho P4
Toàn bộ kho lưu trữ P3 (`repo`), manifest ban đầu (`manifest_p3.sha256`), metadata của snapshot và file hướng dẫn phục hồi được gom vào một gói nén duy nhất:
```bash
cd ~/lab-restic-p4-export
tar -czvf p4_package.tar.gz repo_p4_copy manifest_p3.sha256 snapshot_metadata.json README.txt
```

### 2.3. Quản lý an toàn thông tin và Tính toán mã băm SHA-256
- **Nguyên tắc an toàn mật khẩu:** Tuyệt đối không đưa mật khẩu kho vào gói nén hay lưu trữ trong Git. Mật khẩu được quản trị độc lập và chỉ truyền qua biến môi trường phiên terminal tại thời điểm thực thi.
- **Mã băm SHA-256 chính thức của gói lưu chuyển:**
  ```text
  41db50e0bffb4347b26b197d8dbc685d82ac98de5a6af8952564eb97834be9c8  p4_package.tar.gz
  ```
  File mã băm `p4_package.tar.gz.sha256` được lưu tách rời bên ngoài gói nén.

---

## 3. Tiếp nhận và Kiểm định gói nén trên VM Sạch

Gói dữ liệu và file băm được chuyển giao sang thư mục `~/lab-p4-restore` trên VM `recovery-node`.

### 3.1. Đối chiếu mã băm gói trước khi giải nén
Lệnh thực thi trên VM sạch:
```bash
cd ~/lab-p4-restore
sha256sum -c p4_package.tar.gz.sha256
```
Đầu ra terminal xác nhận:
```text
p4_package.tar.gz: OK
```
*Kết luận:* Gói dữ liệu toàn vẹn 100%, không bị lỗi bit hay sai lệch trong quá trình truyền dẫn giữa 2 máy ảo.

### 3.2. Nạp khóa bảo mật an toàn ngoài Git

Giải nén gói dữ liệu và nạp mật khẩu kho thông qua cơ chế nhập kín (không lưu vết vào lịch sử shell hay tài liệu):

```bash
tar -xzvf p4_package.tar.gz

# Nạp mật khẩu kín qua prompt tương tác của shell (không hiện ký tự và không lưu vào history)
read -s -p "Nhập mật khẩu Restic: " RESTIC_PASSWORD
export RESTIC_PASSWORD
echo ""
```
> *Ghi chú bảo mật:* Giá trị mật khẩu thực tế không được lưu trữ dưới dạng bản rõ (plaintext) trong bất kỳ file tài liệu, script hay commit nào trên kho mã nguồn.

---

## 4. Kiểm định toàn vẹn kho lưu trữ trên VM sạch (`restic check`)

Trước khi tiến hành phục hồi, toàn bộ khối dữ liệu mã hóa của bản sao kho được kiểm tra tính toàn vẹn:

```bash
restic -r ./repo_p4_copy check --read-data
```

> **Đầu ra thực tế từ terminal:**
> ```text
> using temporary cache in /tmp/restic-check-cache-2704140144
> create exclusive lock for repository
> repository e09f489d opened (version 2, compression level auto)
> created new cache in /tmp/restic-check-cache-2704140144
> load indexes
> 100.00%  1 / 1 index files loaded
> check all packs
> check snapshots, trees and blobs
> 100.00%  1 / 1 snapshots
> read all data
> 100.00%  2 / 2 packs
> no errors were found
> ```

- **Exit code:** `0`
- **Kết quả:** Repository `e09f489d` mở thành công, đọc trọn vẹn 2/2 pack data, không phát hiện bất kỳ khối dữ liệu hay index nào bị lỗi (`no errors were found`).

---

## 5. Đối chiếu Snapshot ID và Thực thi khôi phục dữ liệu

### 5.1. Đối chiếu định danh Snapshot
Kiểm tra danh mục snapshot trong kho bản sao:
```bash
restic -r ./repo_p4_copy snapshots
```
> **Đầu ra thực tế:**
> ```text
> repository e09f489d opened (version 2, compression level auto)
> created new cache in /home/kali/.cache/restic
> ID        Time                 Host        Tags        Paths                                       Size
> -----------------------------------------------------------------------------------------------------------
> 3ad2e70f  2026-10-30 06:36:32  nvtp05112               /home/nvtp05112/lab-restic-p3/data_source  1.040 KiB
> -----------------------------------------------------------------------------------------------------------
> Timestamps shown in local time
> 1 snapshots
> ```

Snapshot được chọn để khôi phục khớp chính xác với snapshot được tạo tại P3:
- **Full Snapshot ID:** `3ad2e70fed735583ec674b13b56482d39aecc77f2a994d1b5c038adc2e4e60e8`
- **Short ID:** `3ad2e70f`

### 5.2. Đường dẫn thực tế sau phục hồi
- Thư mục đích chỉ định ban đầu: `./restored_target`
- Thư mục chứa dữ liệu thực tế sau phục hồi: `./restored_target/data_source`
- Tóm tắt tiến trình Restic: Phục hồi thành công 16 files/dirs (tổng dung lượng 1.040 KiB).

---

## 6. Xác minh tính toàn vẹn 2 lớp sau phục hồi

### 6.1. Lớp 1: Đối chiếu mã băm SHA-256 với Manifest gốc
Thực thi kiểm tra tính toàn vẹn 15 file mẫu dựa trên manifest gốc `manifest_p3.sha256`:
```bash
cd ./restored_target/data_source
sha256sum -c ~/lab-p4-restore/manifest_p3.sha256
```

> **Đầu ra đối chiếu mã băm thực tế:**
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
*Kết quả:* **15/15 file đạt trạng thái OK**, khớp 100% với dữ liệu trước khi sao lưu.

### 6.2. Lớp 2: Kiểm tra số lượng và rà soát file ẩn/file rác
Thực thi kiểm tra số lượng và liệt kê chi tiết mọi file (kể cả file ẩn):
```bash
ls -1 | wc -l
ls -la
```

> **Đầu ra terminal:**
> ```text
> 15
> ```
> ```text
> total 68
> drwxrwxr-x 2 kali kali 4096 Oct 30 06:34 .
> drwxrwxr-x 3 kali kali 4096 Nov  2 12:15 ..
> -rw-rw-r-- 1 kali kali   71 Oct 30 06:34 file_01.txt
> -rw-rw-r-- 1 kali kali   71 Oct 30 06:34 file_02.txt
> -rw-rw-r-- 1 kali kali   71 Oct 30 06:34 file_03.txt
> -rw-rw-r-- 1 kali kali   71 Oct 30 06:34 file_04.txt
> -rw-rw-r-- 1 kali kali   71 Oct 30 06:34 file_05.txt
> -rw-rw-r-- 1 kali kali   71 Oct 30 06:34 file_06.txt
> -rw-rw-r-- 1 kali kali   71 Oct 30 06:34 file_07.txt
> -rw-rw-r-- 1 kali kali   71 Oct 30 06:34 file_08.txt
> -rw-rw-r-- 1 kali kali   71 Oct 30 06:34 file_09.txt
> -rw-rw-r-- 1 kali kali   71 Oct 30 06:34 file_10.txt
> -rw-rw-r-- 1 kali kali   71 Oct 30 06:34 file_11.txt
> -rw-rw-r-- 1 kali kali   71 Oct 30 06:34 file_12.txt
> -rw-rw-r-- 1 kali kali   71 Oct 30 06:34 file_13.txt
> -rw-rw-r-- 1 kali kali   71 Oct 30 06:34 file_14.txt
> -rw-rw-r-- 1 kali kali   71 Oct 30 06:34 file_15.txt
> ```
*Kết luận:* Thư mục phục hồi chỉ chứa đúng 15 file dữ liệu, không có bất kỳ file rác, file tạm hay file ẩn lạ nào xuất hiện.

---

## 7. Đo lường thời gian thực tế bằng đồng hồ đơn điệu

### 7.1. Mã nguồn script đo lường và kiểm soát lỗi (`run_measure_p4.py`)

Script Python được xây dựng nhằm đảm bảo tính tái lập (reproducibility), sử dụng đồng hồ đơn điệu `time.perf_counter()`, kiểm tra nghiêm ngặt tiền điều kiện thư mục rỗng, bắt lỗi mã trả về (`returncode`) và kiểm định số lượng tệp phục hồi:

```python
import subprocess
import time
from datetime import datetime, timezone
import os
import shutil

SNAP_ID = "3ad2e70fed735583ec674b13b56482d39aecc77f2a994d1b5c038adc2e4e60e8"
REPO = "./repo_p4_copy"
TARGET = "./restored_target"
MANIFEST = os.path.abspath("./manifest_p3.sha256")

# 1. TIỀN ĐIỀU KIỆN: Dọn sạch và xác nhận thư mục đích trước khi đo
if os.path.exists(TARGET):
    shutil.rmtree(TARGET)
os.makedirs(TARGET, exist_ok=True)
if len(os.listdir(TARGET)) != 0:
    raise RuntimeError(f"LỖI: Thư mục đích {TARGET} không rỗng trước khi đo!")

print(f"=== BẮT ĐẦU QUY TRÌNH P4 (UTC): {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')} ===")
t_all_start = time.perf_counter()

# 2. ĐO VÀ THỰC THI RESTORE (CÓ CHECK RETURNCODE)
t_restore_start = time.perf_counter()
res_restore = subprocess.run(
    ["restic", "-r", REPO, "restore", SNAP_ID, "--target", TARGET],
    capture_output=True, text=True
)
t_restore_end = time.perf_counter()

if res_restore.returncode != 0:
    raise RuntimeError(f"LỖI: Tiến trình Restic restore thất bại (exit code {res_restore.returncode})!\n{res_restore.stderr}")

restore_duration = t_restore_end - t_restore_start

# 3. ĐỊNH VỊ THƯ MỤC CHỨA FILE VÀ CHECK LỖI
find_res = subprocess.run(
    ["find", TARGET, "-type", "f", "-name", "file_01.txt"],
    capture_output=True, text=True
)
if not find_res.stdout.strip():
    raise RuntimeError("LỖI: Không tìm thấy dữ liệu sau khi khôi phục!")

restored_dir = os.path.dirname(find_res.stdout.strip())

# 4. ĐO CÔNG ĐOẠN XÁC MINH SHA-256 (CÓ CHECK RETURNCODE)
res_hash = subprocess.run(
    ["sha256sum", "-c", MANIFEST],
    cwd=restored_dir, capture_output=True, text=True
)
if res_hash.returncode != 0:
    raise RuntimeError(f"LỖI: Xác minh SHA-256 thất bại!\n{res_hash.stdout}\n{res_hash.stderr}")

# 5. KIỂM ĐỊNH SỐ LƯỢNG FILE VÀ FILE ẨN
files_in_dir = [f for f in os.listdir(restored_dir) if os.path.isfile(os.path.join(restored_dir, f))]
file_count = len(files_in_dir)
if file_count != 15:
    raise AssertionError(f"LỖI: Số lượng file phục hồi là {file_count}, không khớp kỳ vọng 15 file!")

res_ls = subprocess.run(
    ["ls", "-la"],
    cwd=restored_dir, capture_output=True, text=True
)

t_all_end = time.perf_counter()
total_duration = t_all_end - t_all_start

print(f"=== HOÀN TẤT QUY TRÌNH P4 (UTC): {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')} ===")
print("--------------------------------------------------")
print(f"Thư mục phục hồi thực tế: {restored_dir}")
print(f"Thời lượng restore: {restore_duration:.4f}s")
print(f"Tổng thời lượng restore + xác minh: {total_duration:.4f}s")
print("--------------------------------------------------")
print("Log stdout của lệnh restore:\n", res_restore.stdout.strip())
print("\nLog kiểm tra SHA-256:\n", res_hash.stdout.strip())
print(f"\nSố lượng file xác nhận: {file_count}/15 (Khớp tuyệt đối)")
print("\nDanh sách chi tiết file (ls -la):\n", res_ls.stdout.strip())
```

### 7.2. Kết quả đo đạc thực tế

**Trích xuất log thực thi từ script (`p4_execution.log`):**

```text
=== BẮT ĐẦU QUY TRÌNH P4 (UTC): 2026-11-02 17:15:55 UTC ===
=== HOÀN TẤT QUY TRÌNH P4 (UTC): 2026-11-02 17:15:55 UTC ===
--------------------------------------------------
Thư mục phục hồi thực tế: ./restored_target/data_source
Thời lượng restore: 0.7472s
Tổng thời lượng restore + xác minh: 0.7591s
--------------------------------------------------
Log stdout của lệnh restore:
 restoring snapshot 3ad2e70f of [/home/nvtp05112/lab-restic-p3/data_source] at 2026-10-30 06:36:32.711446492 -0400 EDT by nvtp05112@nvtp05112 to ./restored_target
Summary: Restored 16 files/dirs (1.040 KiB) in 0:00

Log kiểm tra SHA-256:
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

Số lượng file xác nhận: 15/15 (Khớp tuyệt đối)

Danh sách chi tiết file (ls -la):
 total 68
drwxrwxr-x 2 kali kali 4096 Oct 30 06:34 .
drwxrwxr-x 3 kali kali 4096 Nov  2 12:15 ..
-rw-rw-r-- 1 kali kali   71 Oct 30 06:34 file_01.txt
-rw-rw-r-- 1 kali kali   71 Oct 30 06:34 file_02.txt
-rw-rw-r-- 1 kali kali   71 Oct 30 06:34 file_03.txt
-rw-rw-r-- 1 kali kali   71 Oct 30 06:34 file_04.txt
-rw-rw-r-- 1 kali kali   71 Oct 30 06:34 file_05.txt
-rw-rw-r-- 1 kali kali   71 Oct 30 06:34 file_06.txt
-rw-rw-r-- 1 kali kali   71 Oct 30 06:34 file_07.txt
-rw-rw-r-- 1 kali kali   71 Oct 30 06:34 file_08.txt
-rw-rw-r-- 1 kali kali   71 Oct 30 06:34 file_09.txt
-rw-rw-r-- 1 kali kali   71 Oct 30 06:34 file_10.txt
-rw-rw-r-- 1 kali kali   71 Oct 30 06:34 file_11.txt
-rw-rw-r-- 1 kali kali   71 Oct 30 06:34 file_12.txt
-rw-rw-r-- 1 kali kali   71 Oct 30 06:34 file_13.txt
-rw-rw-r-- 1 kali kali   71 Oct 30 06:34 file_14.txt
-rw-rw-r-- 1 kali kali   71 Oct 30 06:34 file_15.txt
```

**Bảng tổng hợp chỉ số đo lường hiệu năng:**

| Hạng mục đo lường | Thời điểm / Thời lượng | Đơn vị tính | Phương pháp xác thực |
| :--- | :--- | :--- | :--- |
| **Thời điểm bắt đầu** | `2026-11-02 17:15:55 UTC` | ISO-8601 UTC | `datetime.now(timezone.utc)` |
| **Thời điểm kết thúc** | `2026-11-02 17:15:55 UTC` | ISO-8601 UTC | `datetime.now(timezone.utc)` |
| **Lệnh Restore Restic** | `0.7472` | Giây (s) | `time.perf_counter()` bóc tách riêng (exit code 0) |
| **Toàn trình (Restore + Verify)** | `0.7591` | Giây (s) | `time.perf_counter()` toàn bộ quy trình (assert 15/15) |
| **Số lượng tệp phục hồi** | `15 / 15` | Tệp tin | Khớp tuyệt đối `manifest_p3.sha256` |

---

## 8. Giới hạn kỹ thuật và Kết luận nghiệm thu

1. **Giới hạn kỹ thuật:**
   - Thử nghiệm P4 chứng minh tính độc lập và khả năng phục hồi dữ liệu từ bản sao kho Restic trên một máy ảo sạch hoàn toàn khi có đủ khóa bảo mật.
   - Kết quả này **chưa chứng minh** việc khôi phục toàn bộ các dịch vụ hệ thống phức hợp trong lab chính và **chưa chứng minh** việc loại bỏ triệt để mã độc sau một sự cố an ninh thực tế. Nhóm thực hiện không tự ý suy diễn các chỉ số đo lường thực nghiệm thành chỉ số RTO/RPO cho sự cố diện rộng.
2. **Tính toàn vẹn dữ liệu gốc:** Toàn bộ kho lưu trữ P3 (`~/lab-restic-p3/repo`), 15 file dữ liệu gốc và các log cũ trên VM `nvtp05112` được bảo lưu nguyên vẹn 100%.
3. **Trạng thái nghiệm thu:** **ĐẠT TẤT CẢ CÁC TIÊU CHÍ NGHIỆM THU ISSUE #27**.