# Giám sát thay đổi file bằng Wazuh — giai đoạn 4

Trạng thái: đã chuẩn bị cấu hình; chưa nghiệm thu runtime, dashboard hoặc cảnh báo.
VM đã nhận RAM 12 GiB, đĩa 70 GiB; root LVM 68 GiB. Sau khi tải ba image Wazuh,
đầu ra ngày 31/10/2026 cho thấy `/` hiển thị 67G và còn trống 47G.

## Luồng hoạt động

1. Workstation tiếp tục phục vụ 15 file giả từ thư mục `sample_data`.
2. Manager nhìn cùng thư mục qua bind mount **chỉ đọc** tại `/lab/data`.
   FIM theo dõi thêm, sửa, xóa; đổi tên thường tạo hai sự kiện xóa/thêm.
3. Manager tạo `alerts.json`; Filebeat trong image Manager gửi cảnh báo tới Indexer qua HTTPS.
4. Indexer lưu và tìm kiếm cảnh báo. Dashboard truy vấn Indexer và API Manager.
5. Người dùng xem dashboard bằng Firefox **trong Ubuntu VM** tại
   `https://127.0.0.1:8443`. Đây là loopback của Ubuntu, không phải Kali.

Đây là ba container Wazuh, không cần thêm ba máy ảo. FIM là giám sát thay đổi;
cảnh báo không tự chứng minh ransomware và cấu hình này không tự diệt tiến trình.
Active response đang tắt. Không chạy mẫu thật để nghiệm thu phần này.

## Phạm vi và quyền

- Overlay `lab/compose.monitoring.yaml` dùng cùng project `csatttn3` nhưng mạng
  `monitoring_net` riêng, `internal: true`. Workstation chỉ ở `incident_net`.
- Chỉ Dashboard công bố `127.0.0.1:8443`; Manager/API/Indexer không công bố cổng.
- Không gắn Docker socket, ổ backup hoặc thư mục Windows vào Wazuh.
- Image được cố định cả phiên bản 4.14.9 và digest đã tải trên VM.
- Manager giữ cơ chế S6 chạy init bằng root của hãng, không dùng privileged hoặc
  host PID. Indexer và Dashboard chạy user mặc định của image (UID 1000), bỏ capabilities.
- Các file cấu hình/chứng chỉ và hai thư mục FIM gắn chỉ đọc. Dữ liệu hoạt động
  của Wazuh nằm trong volume riêng. Không xóa volume để xử lý lỗi khởi động.
- Ba mật khẩu độc lập, ngẫu nhiên; Indexer chỉ khai báo admin và kibanaserver.
  Init Manager thay mật khẩu wazuh-wui và vô hiệu hóa mật khẩu mặc định của wazuh.
- Filebeat và Dashboard kiểm tra CA/tên Indexer. Dashboard có SAN localhost và
  127.0.0.1. CA private key không gắn vào container.
- API Manager dùng cơ chế HTTPS của image hãng; chưa nghiệm thu xác minh danh tính
  API từ Dashboard. Không gộp trạng thái này với gate TLS 1.3 của Restic.
- Mật khẩu truyền bằng environment theo image hãng: người có quyền Docker/root
  trong VM có thể đọc. `monitoring.env`, certificate key và login luôn ở ngoài Git.
- Các volume cùng nằm trong VM. Root VM bị chiếm có thể tác động cả giám sát;
  đây chưa phải nguồn log độc lập chống sửa.
- Giới hạn RAM: Manager 2 GiB, Indexer 4 GiB (heap 1 GiB), Dashboard 2 GiB.
  Log stdout quay vòng 3 x 10 MiB/container. Dữ liệu Indexer và log nội bộ Wazuh
  chưa có chính sách tự xóa: kiểm tra dung lượng trước/sau mỗi buổi, dừng thử nghiệm
  nếu guest hoặc ổ D host còn dưới 15 GiB; xuất chứng cứ rồi mới bàn việc dọn dẹp.

## 1. Kiểm tra mã nguồn trên Kali

Chạy trong checkout dự án, nhánh `feature/giam-sat-phat-hien`:

```bash
docker compose --env-file lab/.env.monitoring.example \
  -f lab/compose.yaml -f lab/compose.monitoring.yaml config --quiet
python3 -m unittest discover -s tests -p 'test_monitoring.py' -v
git diff --check
```

Các kiểm tra này không khởi chạy container. Commit nguồn trước khi tạo ISO;
chuyển bản nguồn xác định và SHA-256 vào VM theo quy trình đang dùng của lab.

## 2. Chuẩn bị trong Ubuntu VM

Đứng trong thư mục `source` của bản triển khai mới. Không sửa bản HTTPS lịch sử.
Không gắn lại đĩa backup cho bước này.

```bash
hostname
sysctl vm.max_map_count
date -u --iso-8601=seconds
sudo -v
python3 scripts/create_monitoring_runtime.py \
  "$HOME/csattt-lab/secrets/wazuh-stage4"
```

Giữ `vm.max_map_count` hiện tại nếu từ 262144 trở lên. Script tái sử dụng htpasswd
trong image Restic server đã có để tạo bcrypt, rồi dùng OpenSSL có sẵn tạo CA/chứng chỉ.
Nó chạy hai container tạo hash ngắn hạn với `--network none`, không chạy dịch vụ Wazuh,
không sửa 15 file nguồn. Thư mục riêng 0700, file 0600, từ chối ghi đè.
Nếu dừng giữa chừng, giữ nguyên thư mục và kiểm tra lỗi; không xóa secret rồi tạo lại tùy tiện.

## 3. Khởi chạy có kiểm soát

Sau khi bước 2 thành công và không có bộ Wazuh cũ đang chạy:

```bash
task_monitor_env="$HOME/csattt-lab/secrets/wazuh-stage4/monitoring.env"

sudo docker --host unix:///var/run/docker.sock compose \
  --env-file "$task_monitor_env" \
  -f lab/compose.yaml -f lab/compose.monitoring.yaml config --quiet

sudo docker --host unix:///var/run/docker.sock compose \
  --env-file "$task_monitor_env" \
  -f lab/compose.yaml -f lab/compose.monitoring.yaml \
  up -d --no-deps --no-build --pull never \
  wazuh.indexer wazuh.manager wazuh.dashboard

sudo docker --host unix:///var/run/docker.sock compose \
  --env-file "$task_monitor_env" \
  -f lab/compose.yaml -f lab/compose.monitoring.yaml ps -a
```

Không dùng `--remove-orphans`, `down -v` hoặc prune. Backup-server đã dừng có thể
được báo orphan vì overlay này không khai báo backup; không cần xóa nó.
`Up` chưa chứng minh sẵn sàng. Khi chưa vào được dashboard, lấy log ba dịch vụ
và kiểm tra quyền file trước khi sửa. Che thông tin nhạy cảm trước khi chia sẻ log.

## 4. Kiểm tra HTTPS Dashboard và đăng nhập

Kiểm tra TLS trước khi mở trình duyệt:

```bash
curl --noproxy '*' --max-time 15 \
  --cacert "$HOME/csattt-lab/secrets/wazuh-stage4/tls/root-ca.pem" \
  -sS -o /dev/null -w 'HTTPS status=%{http_code}\n' \
  https://127.0.0.1:8443/
```

Phải không có lỗi chứng chỉ và HTTP thường là 200 hoặc 302. Không dùng `-k`.
Import file CA public vào Firefox của VM nếu trình duyệt chưa tin CA; đối chiếu
fingerprint bằng `openssl x509 -in .../tls/root-ca.pem -noout -fingerprint -sha256`.
Chỉ xem `dashboard-login.txt` tại VM để đăng nhập admin; không gửi file/nội dung lên GitHub.

## 5. Nghiệm thu FIM — chỉ sau khi Dashboard đã hoạt động

- Chờ lượt quét ban đầu hoàn tất; xác nhận Manager theo dõi `/lab/data` và `/lab/fim-probe`.
- Dùng file giả riêng trong `~/csattt-lab/runtime/fim-probe`, mỗi thao tác một lượt:
  thêm, sửa nội dung, đổi tên, xóa. Ghi UTC trước thao tác và khi thấy cảnh báo.
- Tìm rule FIM 554 (thêm), 550 (thay đổi), 553 (xóa); đổi tên có thể là 553 + 554.
- Đối chiếu `alerts.json` trong Manager với Dashboard: agent local 000,
  đường dẫn `/lab/fim-probe/...`, rule, hash và thời gian thực tế.
- Giữ nguyên 15 file nguồn, không thêm file thử vào `sample_data`.
- Lưu log/ảnh kết quả và SHA-256 ở ngoài Git. Chỉ tóm tắt kết quả đã kiểm chứng lên báo cáo.
- `ps`, HTTPS hoặc một cảnh báo chưa đủ để kết luận toàn bộ hệ thống hoàn thành.

Sau buổi thử, dừng đúng ba dịch vụ bằng cùng Compose với lệnh `stop` và tên
`wazuh.dashboard wazuh.manager wazuh.indexer`; volume được giữ lại.

## Tham khảo

- https://github.com/wazuh/wazuh-docker/tree/v4.14.9/single-node
- https://documentation.wazuh.com/current/deployment-options/docker/wazuh-container.html
- https://documentation.wazuh.com/current/deployment-options/docker/changing-default-password.html
- https://documentation.wazuh.com/current/user-manual/capabilities/file-integrity/basic-settings.html
