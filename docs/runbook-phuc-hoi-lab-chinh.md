# Runbook Phục hồi Dữ liệu và Dịch vụ HTTP Lab Chính sau Sự cố (P5)

- **Người soạn thảo:** Nguyễn Vũ Tuấn Phong (@nvtp0511)
- **Người review / Xác nhận đầu vào:** Nhữ Duy Anh Minh (@Unknown1805)
- **Issue theo dõi:** `#36` *(cập nhật mã Issue thực tế sau khi được tạo)*
- **Trạng thái thực thi:** `CHƯA THỰC HIỆN` (Giai đoạn chuẩn bị tài liệu & mẫu đo)
- **Tài liệu tham chiếu:** `docs/runbook-https-backup.md`, `scripts/backup_lab.py`

---

## 1. Mục tiêu và Phạm vi áp dụng

Runbook này quy định quy trình chuẩn để khôi phục dữ liệu của **lab chính** từ kho sao lưu Restic sang một **máy ảo sạch độc lập (Clean Recovery VM)** sau kịch bản sự cố, xác minh toàn vẹn dữ liệu và khôi phục hoạt động dịch vụ HTTP.

### 1.1. Phân biệt dữ liệu Lab chính và dữ liệu thử nghiệm P4

| Tiêu chí | Dữ liệu thử nghiệm P4 (Đã hoàn tất) | Dữ liệu Lab chính (P5 - Áp dụng Runbook này) |
| :--- | :--- | :--- |
| **Mục đích** | Diễn tập luồng kỹ thuật trên kho mẫu | Phục hồi dữ liệu vận hành của lab chính sau sự cố |
| **Quy mô tệp nguồn** | 15 tệp mẫu (71 B/tệp, tổng 1.040 KiB) | **15 tệp dữ liệu chính, tổng dung lượng 600 B** |
| **Manifest đối chiếu** | `manifest_p3.sha256` (Chỉ dùng cho P4) | **Manifest chính thức của lab chính** do @Unknown1805 xác nhận |
| **Snapshot ID** | `3ad2e70f...` (Không dùng cho lab chính) | **Full Snapshot ID (64 ký tự hex)** từ bản kho hợp lệ của lab chính |

> **Quy tắc bắt buộc:** Tuyệt đối không sử dụng lại manifest/snapshot của P4 và **nghiêm cấm** sử dụng từ khóa `latest` khi chạy lệnh `restic restore`.

---

## 2. Danh mục bàn giao ngoài Git (Out-of-Band Deliverables)

Toàn bộ bí mật, chứng chỉ, ảnh đĩa và container image không được lưu trong kho mã nguồn Git mà phải được bàn giao trực tiếp qua kênh an toàn độc lập trước khi kích hoạt ứng cứu:

| Nhóm thành phần | Tên tệp / Đối tượng bàn giao | Quy cách lưu trữ & Phân quyền trên VM sạch | Mục đích sử dụng |
| :--- | :--- | :--- | :--- |
| **Mã nguồn & cấu hình** | Bundle sạch (`source.tar`, `SHA256SUMS`) và manifest dữ liệu nền do người nghiệm thu xác nhận | Kiểm tra SHA-256, giải nén vào thư mục mới | Đối chiếu và phục vụ dữ liệu từ VM Recovery |
| **Kho sao lưu** | Bản sao QCOW2 cùng SHA-256 đã xác nhận | Đính kèm ở chế độ chỉ đọc vào VM Recovery; xác minh serial và UUID ext4 trước khi mount | Nguồn Restic offline, không gắn vào VM sự cố |
| **Tệp mật khẩu kho** | `<LAB_SECRET_DIR>/repository-password` | Thư mục `0700`, tệp `0600` thuộc UID `1000`; không in giá trị | Restic đọc qua `--password-file` |
| **Chứng chỉ và xác thực HTTPS (chỉ cho luồng tùy chọn)** | `<LAB_TLS_DIR>/{ca.crt,server.crt,server.key}`; `<LAB_SECRET_DIR>/{rest-http-password,rest.htpasswd}` | Bàn giao ngoài Git, không chép `ca.key` vào runtime | Dùng với [runbook HTTPS](runbook-https-backup.md) trên bản sao làm việc được phép ghi |
| **Container image** | `restic/restic:0.19.1`; image Workstation nếu dùng Compose; `restic/rest-server:0.14.0` chỉ cho HTTPS | Nạp sẵn, không pull trong VM cô lập | Không cần bật Internet hoặc backup-server để phục hồi offline |
| **Căn cứ đối chiếu** | Full Snapshot ID (64 ký tự hex) và tệp manifest gốc `<DUONG_DAN_MANIFEST_LAB_CHINH>` | Lưu ngoài thư mục đích phục hồi; được @Unknown1805 xác nhận trước lượt chạy | Đối chiếu danh sách 15 tệp và mã băm SHA-256 |

---

## 3. Nguyên tắc Cô lập và Điều kiện Dừng Khẩn cấp (Stop Conditions)

### 3.1. Nguyên tắc cô lập sự cố
1. **Không thao tác trên VM sự cố:** Toàn bộ quy trình khôi phục phải thực hiện trên **VM sạch mới khởi tạo** (Ubuntu VM chuẩn, UID/GID `1000`, mạng nội bộ `backup_net` cô lập, không publish cổng ra ngoài).
2. **Không mount kho backup vào VM sự cố:** Nghiêm cấm gắn đĩa `csattt-backup.qcow2` hoặc mount bản sao kho Restic vào máy ảo đang nghi nhiễm/gặp sự cố để tránh nguy cơ mã độc phá hủy hoặc mã hóa chéo bản sao lưu.
3. **Bảo toàn hiện trường và chứng cứ:** Giữ nguyên trạng VM sự cố, bản kho nguồn, các thư mục log và thư mục phục hồi dở dang. **Cấm tuyệt đối** các lệnh phá hủy hoặc làm thay đổi cấu trúc kho:
   - Không chạy `rm -rf` lên dữ liệu phục hồi hoặc thư mục chứng cứ.
   - Không chạy `restic init`, `restic prune`, `restic unlock` tùy tiện.
   - Không chạy `mkfs`, `chmod 777`, `umount -f` hoặc `umount -l`.

### 3.2. Điều kiện dừng quy trình ngay lập tức (Fail-Fast)
Người vận hành phải dừng quy trình ngay lập tức và báo cáo lại nếu phát hiện bất kỳ điều kiện nào dưới đây:
- **Sai định danh hoặc cô lập:** Sai UUID VM, serial đĩa hoặc UUID ext4; có NIC ngoài/default route; hoặc đĩa/kho không chỉ đọc trong luồng offline.
- **Sai kho / snapshot:** Không mở được kho hoặc không tìm thấy đúng ID snapshot đủ 64 ký tự. Nếu chọn luồng HTTPS, thêm kiểm tra CA, SAN `DNS:backup-server` và TLS 1.3 theo runbook HTTPS.
- **Thiếu tệp xác thực hoặc sai quyền:** Dừng nếu không đọc được `repository-password` hợp lệ; chỉ yêu cầu bộ xác thực HTTP/TLS trong luồng HTTPS. Không in hoặc tạo lại mật khẩu.
- **Lỗi toàn vẹn dữ liệu (Hash Mismatch):** Sai lệch mã băm SHA-256 của gói chuyển giao, lệnh `restic check --read-data` báo lỗi, dữ liệu sau restore không đủ 15 tệp hoặc lệch mã băm so với manifest gốc.
- **Đích phục hồi không hợp lệ:** Thư mục đích `<LAB_RESTORE_DIR>` đã tồn tại dữ liệu trước đó hoặc là symlink.

---

## 4. Quy trình Thực thi Phục hồi trên Môi trường Sạch

### Bước 1: Ghi nhận mốc bắt đầu ứng cứu và kiểm tra bàn giao
1. Khởi tạo thư mục lưu nhật ký phiên ứng cứu ngoài thư mục đích phục hồi (ví dụ: `<RUN_LOG_DIR>/recovery-UTC-<YYYYMMDDTHHMMSSZ>`).
2. Ghi nhận mốc thời gian bắt đầu ứng cứu chuẩn UTC (`date -u +"%Y-%m-%dT%H:%M:%SZ"`) và mốc đồng hồ đơn điệu.
3. Kiểm tra mã băm SHA-256 của gói mã nguồn và gói/ảnh đĩa kho sao lưu trước khi giải nén hoặc gắn đĩa:
   ```bash
   sha256sum -c <TEN_GOI_CHUYEN_GIAO>.sha256
   ```
   *Yêu cầu:* Tất cả các dòng trả về trạng thái `OK`.

### Bước 2: Gắn lưu trữ sao lưu và kiểm tra tiền điều kiện (`preflight`)
1. Trên hypervisor (Kali), xác nhận VM sạch chưa gắn `vdb` và gắn đúng tệp `<DUONG_DAN_QCOW2_HOAC_BAN_SAO_KHO>`.
2. Bên trong Ubuntu VM sạch (user UID `1000`), xác minh UUID phân vùng và mount vào `<MOUNT_POINT>` (ví dụ `/mnt/csattt-backup`):
   ```bash
   lsblk -f
   sudo mount -o rw UUID=<EXPECTED_BACKUP_UUID> <MOUNT_POINT>
   ```
3. Kiểm tra cấu hình tệp `<DUONG_DAN_BACKUP_ENV>` đảm bảo:
   - `LAB_TLS_DIR` trỏ đúng thư mục chứa bộ TLS hợp lệ (`0700`/`0600`).
   - `LAB_RESTORE_DIR` là đường dẫn **mới hoàn toàn** (chưa có dữ liệu). Tạo thư mục rỗng thuộc UID `1000`:
     ```bash
     mkdir -p "<LAB_RESTORE_DIR>"
     chmod 0700 "<LAB_RESTORE_DIR>"
     ```
4. Chạy kiểm tra tiền điều kiện bằng helper chính thức:
   ```bash
   python3 scripts/backup_lab.py --env-file <DUONG_DAN_BACKUP_ENV> preflight
   ```
   *Yêu cầu:* Trả về `PREFLIGHT: OK` và exit code `0`.

### Bước 3: Khởi động `backup-server` (HTTPS) và kiểm tra toàn vẹn kho
1. Khởi động dịch vụ `backup-server` qua TLS 1.3:
   ```bash
   python3 scripts/backup_lab.py --env-file <DUONG_DAN_BACKUP_ENV> start
   python3 scripts/backup_lab.py --env-file <DUONG_DAN_BACKUP_ENV> status
   ```
2. Kiểm tra toàn bộ cấu trúc và dữ liệu mã hóa của kho thông qua `backup-worker`:
   ```bash
   python3 scripts/backup_lab.py --env-file <DUONG_DAN_BACKUP_ENV> client check --read-data
   ```
3. Liệt kê snapshot và đối chiếu chính xác từng ký tự của **Full Snapshot ID (64 ký tự hex)** với thông tin do @Unknown1805 xác nhận:
   ```bash
   python3 scripts/backup_lab.py --env-file <DUONG_DAN_BACKUP_ENV> client snapshots
   ```

### Bước 4: Thực thi khôi phục vào thư mục đích mới (`restic restore`)
Ghi nhận riêng mốc thời gian bắt đầu và kết thúc của lệnh khôi phục (sử dụng đồng hồ đơn điệu `time.perf_counter()` hoặc `CLOCK_MONOTONIC`) để bóc tách thời lượng thực thi lệnh `restore`:

```bash
python3 scripts/backup_lab.py --env-file <DUONG_DAN_BACKUP_ENV> restore <FULL_64_CHAR_SNAPSHOT_ID>
```

> **Lưu ý:** Helper `backup_lab.py` sẽ tự động kiểm tra thư mục đích `/restore` (tương ứng `<LAB_RESTORE_DIR>`) phải rỗng, không phải symlink và không chồng lấn với dữ liệu nguồn hoặc kho backup trước khi chạy `restore-worker`.

### Bước 5: Xác minh dữ liệu sau khôi phục (15/15 tệp và SHA-256)
Di chuyển tới thư mục dữ liệu đã khôi phục bên trong `<LAB_RESTORE_DIR>` và thực hiện kiểm tra 2 lớp:

1. **Kiểm tra số lượng và tên tệp (kể cả tệp ẩn):**
   ```bash
   ls -la "<DUONG_DAN_DU_LIEU_SAU_RESTORE>"
   find "<DUONG_DAN_DU_LIEU_SAU_RESTORE>" -maxdepth 1 -type f | wc -l
   ```
   *Yêu cầu:* Đúng **15 tệp**, tổng dung lượng **600 B**, không thiếu tên tệp nào và không phát sinh tệp rác/tệp ẩn lạ.

2. **Đối chiếu mã băm SHA-256 với manifest của lab chính:**
   ```bash
   (cd "<DUONG_DAN_DU_LIEU_SAU_RESTORE>" && sha256sum -c "<DUONG_DAN_MANIFEST_LAB_CHINH>")
   ```
   *Yêu cầu:* Đạt **15/15 tệp `OK`** (exit code `0`).

### Bước 6: Nạp dữ liệu sạch và Khởi động dịch vụ HTTP
Chỉ thực hiện bước này sau khi Bước 5 đạt **15/15 OK**:

1. Nạp 15 tệp đã xác minh từ `<DUONG_DAN_DU_LIEU_SAU_RESTORE>` vào thư mục dữ liệu sạch của dịch vụ HTTP (`<WORKSTATION_HTTP_DATA_DIR>`, thư mục rỗng mới tạo trên VM sạch).
2. Khởi động dịch vụ HTTP (`workstation`) trong môi trường sạch:
   ```bash
   sudo docker --host unix:///var/run/docker.sock compose \
     --env-file <DUONG_DAN_BACKUP_ENV> \
     -f lab/compose.yaml \
     -f lab/compose.backup.yaml \
     up -d --no-deps workstation
   ```
3. Kiểm tra phục hồi HTTP đủ **15/15 tệp** (trả về HTTP `200 OK` và mã băm nội dung tải qua HTTP khớp 15/15 với manifest):
   ```bash
   # Kiểm tra phản hồi HTTP status 200 và đối chiếu SHA-256 từng tệp qua giao thức HTTP
   while read -r expected_hash filename; do
     actual_hash=$(curl -fsS "http://<WORKSTATION_HTTP_HOST>:<HTTP_PORT>/${filename}" | sha256sum | awk '{print $1}')
     if [ "$actual_hash" != "$expected_hash" ]; then
       echo "FAIL: ${filename} (HTTP hash mismatch)"
       exit 1
     fi
     echo "HTTP 200 & HASH OK: ${filename}"
   done < "<DUONG_DAN_MANIFEST_LAB_CHINH>"
   ```
4. Ghi nhận mốc thời gian hoàn tất phục hồi HTTP 15/15 (UTC và đồng hồ đơn điệu).

### Bước 7: Dừng dịch vụ backup an toàn sau khi hoàn tất phục hồi
Sau khi dữ liệu đã được nạp sang `workstation` và HTTP hoạt động ổn định:
```bash
python3 scripts/backup_lab.py --env-file <DUONG_DAN_BACKUP_ENV> stop
python3 scripts/backup_lab.py --env-file <DUONG_DAN_BACKUP_ENV> status
```
Xác nhận không còn container `backup-worker` / `restore-worker` đang chạy trước khi tháo đĩa sao lưu (nếu cần).

---

## 5. Quy tắc Tính toán Mốc Thời gian, RTO và RPO

Toàn bộ kết quả thực thi thực tế của lượt ứng cứu sẽ được ghi vào mẫu tại `docs/kiem-thu/mau-ghi-so-lieu-phuc-hoi-lab-chinh.md` tuân theo các quy định sau:

1. **Chuẩn thời gian:**
   - Mọi mốc thời điểm sự kiện sử dụng chuẩn **UTC (`YYYY-MM-DDTHH:MM:SSZ`)**.
   - Mọi khoảng thời lượng thực thi sử dụng **đồng hồ đơn điệu (`CLOCK_MONOTONIC` / Python `time.perf_counter()`)** tính bằng giây (`s`), tránh sai số do đồng bộ NTP.
2. **Tách riêng thời gian lệnh `restic restore`:**
   - Thời gian chạy riêng lệnh `restic restore` phải được đo và ghi thành một chỉ số độc lập, tách biệt với thời gian chuẩn bị VM, kiểm tra `check --read-data`, xác minh hash và khởi động HTTP.
3. **Quy tắc tính RTO (Recovery Time Objective):**
   - Chỉ được tính toán khi có **mốc thời điểm xảy ra sự cố ($T_{\text{incident}}$)** đã được quy ước chính thức trong kịch bản diễn tập:
     $$\text{RTO thực tế} = T_{\text{HTTP\_15/15}} - T_{\text{incident}}$$
   - Không đánh đồng thời gian chạy lệnh `restic restore` là RTO của toàn bộ sự cố.
4. **Quy tắc đánh giá RPO (Recovery Point Objective):**
   - RPO được xác định dựa trên khoảng cách giữa **thời điểm tạo snapshot ($T_{\text{snapshot}}$)** và **thời điểm xảy ra sự cố ($T_{\text{incident}}$)**, kết hợp đối chiếu **phiên bản dữ liệu trước sự cố**.
   - **Nghiêm cấm** tự động ghi `RPO = 0` chỉ vì dữ liệu phục hồi khớp mã băm SHA-256 với manifest của snapshot đó.