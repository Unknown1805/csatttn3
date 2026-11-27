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
1. **Không thao tác trên VM sự cố:** Khôi phục trên VM Recovery riêng, UID/GID 1000, không NIC ngoài/default route và không chia sẻ với VM sự cố. Restic offline dùng `--network none`; chỉ luồng HTTPS tùy chọn mới dùng `backup_net` nội bộ, không publish cổng ra ngoài.
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

### Bước 2: Gắn bản sao kho chỉ đọc và xác minh định danh

Trên hypervisor, giữ VM sự cố tắt; chỉ gắn bản sao đã đối chiếu SHA-256 vào VM Recovery với cờ chỉ đọc và serial đã được bàn giao. Xác nhận Recovery không có NIC ngoài, chia sẻ thư mục hoặc clipboard. Bên trong Ubuntu, đặt `BACKUP_UUID`, `BACKUP_SERIAL`, `SNAPSHOT`, `PASSWORD_FILE` và `RUN_ROOT` theo bàn giao; `RUN_ROOT` là thư mục ghi được của UID 1000, nằm ngoài kho và nguồn.

~~~bash
set -euo pipefail
umask 077
device=$(readlink -e "/dev/disk/by-uuid/${BACKUP_UUID:?}")
test -b "$device"
test "$(lsblk -dnro RO,SERIAL,UUID,FSTYPE "$device")" = "1 ${BACKUP_SERIAL:?} $BACKUP_UUID ext4"
test -z "$(findmnt -rn -S "$device")"
[[ ${SNAPSHOT:?} =~ ^[0-9a-f]{64}$ ]]
test -f "${PASSWORD_FILE:?}" && test ! -L "$PASSWORD_FILE" && test -r "$PASSWORD_FILE"
OUT=$(mktemp -d "${RUN_ROOT:?}/recovery-XXXXXX")
MOUNT_POINT="$OUT/repo-mount"
RESTORE_DIR="$OUT/restored"
mkdir -- "$MOUNT_POINT" "$RESTORE_DIR"
trap 'if mountpoint -q "$MOUNT_POINT"; then sudo umount "$MOUNT_POINT"; fi' EXIT
sudo mount -t ext4 -o ro,noload,nodev,nosuid,noexec "$device" "$MOUNT_POINT"
test "$(findmnt -nro MAJ:MIN -M "$MOUNT_POINT")" = "$(lsblk -dnro MAJ:MIN "$device")"
findmnt -nro OPTIONS -M "$MOUNT_POINT" | grep -Eq '(^|,)ro(,|$)'
test -f "$MOUNT_POINT/repository/csattt/config"
~~~

### Bước 3: Kiểm tra kho và snapshot bằng Restic offline

~~~bash
restic_offline() {
  sudo docker --host unix:///var/run/docker.sock run --rm --pull=never \
    --network none --user 1000:1000 --read-only --cap-drop ALL \
    --security-opt no-new-privileges:true \
    --mount "type=bind,src=$MOUNT_POINT/repository/csattt,dst=/repo,readonly" \
    --mount "type=bind,src=$PASSWORD_FILE,dst=/password,readonly" \
    --mount "type=bind,src=$RESTORE_DIR,dst=/restore" \
    restic/restic:0.19.1 --no-lock --no-cache -r /repo --password-file /password "$@"
}
restic_offline check --read-data
restic_offline cat snapshot "$SNAPSHOT" > "$OUT/snapshot.json"
~~~

### Bước 4: Phục hồi vào đích mới

~~~bash
date -u +'%Y-%m-%dT%H:%M:%S.%NZ' > "$OUT/restore-start.utc"
TIMEFORMAT='RESTORE_COMMAND_SECONDS=%R'
{ time restic_offline restore "$SNAPSHOT" --target /restore --include '/source/file_*.txt' --verify > "$OUT/restore.log" 2>&1; } 2> "$OUT/restore-time.txt"
date -u +'%Y-%m-%dT%H:%M:%S.%NZ' > "$OUT/restore-end.utc"
sudo umount "$MOUNT_POINT"
~~~

Chạy các khối bước 2–4 trong cùng một Bash để giữ biến và hàm. Giữ lại dữ liệu đang dở nếu gặp lỗi. Bước tiếp theo chỉ đọc các tệp vừa phục hồi ở `$RESTORE_DIR/source`. Thời lượng riêng của lệnh không phải RTO.

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

Đặt `RESTORED_DIR` thành đường dẫn tuyệt đối của thư mục vừa qua bước đối chiếu 15/15. Chạy HTTP từ chính thư mục đó, không chép sang thư mục dữ liệu nền. Ví dụ cho diễn tập offline, chạy trên terminal khác trong VM Recovery:

~~~bash
python3 -m http.server 18040 --bind 127.0.0.1 --directory "${RESTORED_DIR:?}"
~~~

Nếu dùng Workstation thay cho HTTP loopback trên, cấu hình `LAB_DATA_DIR=$RESTORED_DIR` trong tệp env dành riêng cho Workstation, kiểm tra bind mount thực tế trỏ đúng thư mục, rồi chạy `docker compose up -d --no-deps workstation` với tệp env đó. Không tái dùng env trỏ vào `sample_data`.

Đối chiếu đủ 15 URL với manifest nền: mỗi URL phải trả đúng HTTP `200` và SHA-256 phần thân phản hồi phải khớp. Dừng khi thiếu URL, sai mã HTTP hoặc lệch SHA-256; chỉ sau khi đủ 15/15 mới ghi mốc UTC `HTTP_15/15`.

### Bước 7: Bảo toàn kết quả và bàn giao

Luồng offline không bật `backup-server`. Xác minh kho đã unmount, lưu manifest, log và mốc UTC; giữ HTTP trên VM Recovery cho bước nghiệm thu. Không đặt log thô hoặc tệp xác thực trong Git.

**Tùy chọn HTTPS:** nếu thực sự cần diễn tập kênh HTTPS, chỉ chạy [runbook HTTPS](runbook-https-backup.md) trên **bản sao làm việc riêng được phép ghi**; không remount bản sao chứng cứ sang `rw`. Tắt `backup-server` theo runbook sau khi hoàn tất. Ghi rõ luồng nào đã chạy.

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