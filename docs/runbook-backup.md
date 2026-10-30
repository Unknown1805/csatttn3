# Runbook backup và restore — giai đoạn 2

Liên quan Issue #6. Đã triển khai và kiểm thử backup/restore cơ bản trong VM Ubuntu bằng QEMU/KVM. Ở cuối lượt HTTP giai đoạn 2, backup-server đã dừng và ổ backup đã tháo khỏi VM; đĩa đã được gắn lại khi kiểm thử HTTPS giai đoạn 3. Chưa nghiệm thu chế độ cô lập và khôi phục trong môi trường sạch cho phiên sự cố.

> HTTPS đã nghiệm thu ngày 30/10/2026; xem [biên bản](kiem-thu/https-backup-p3.md) và [runbook HTTPS](runbook-https-backup.md). Các kết quả HTTP bên dưới là lịch sử giai đoạn 2; không chạy lại init hoặc tạo lại secret khi nâng cấp.

## Mô hình và quyền

- Workstation tiếp tục ở incident_net; phần cấu hình và dữ liệu của stage 1 được giữ nguyên.
- Backup-server, backup-worker và restore-worker chỉ nối backup_net nội bộ.
- Chỉ server gắn thư mục repository trên đĩa backup. Worker sao lưu chỉ đọc /source; worker phục hồi chỉ ghi /restore.
- Các dịch vụ chạy UID/GID 1000, root filesystem chỉ đọc, bỏ capabilities và không công bố cổng.
- Client dùng restic/restic:0.19.1; server dùng restic/rest-server:0.14.0. Kênh REST HTTP có xác thực nằm trong mạng backup riêng của VM.
- Giới hạn của lượt HTTP lịch sử: credential HTTP Basic chưa được bảo vệ bởi TLS. Lượt HTTPS giai đoạn 3 đã bổ sung TLS 1.3 và được kiểm chứng riêng; không sử dụng cấu hình HTTP lịch sử để vận hành lượt hiện tại.
- Kho bên trong container là /data/csattt, tương ứng /mnt/csattt-backup/repository/csattt trên VM.
- Hai mật khẩu riêng: khóa repository và mật khẩu HTTP. Server chỉ nhận bản bcrypt htpasswd. Các file thật nằm ngoài Git, owner 1000, file 0600, thư mục 0700.
- Wrapper nạp mật khẩu HTTP từ secret khi worker chạy; URL và cấu hình Compose không chứa giá trị mật khẩu.
- Không có depends_on tự bật server. Lệnh worker dùng --no-deps. Chạy qua backup_lab.py để kiểm tra mount trước mỗi lần start/worker; quyền quản trị Docker vẫn có thể cố ý bỏ qua helper.

## Các file cần review

- lab/compose.backup.yaml: phần bổ sung vào Compose gốc, gồm ba dịch vụ và mạng backup.
- lab/.env.backup.example: ví dụ đường dẫn của Ubuntu VM chính; chỉ chứa đường dẫn và UUID.
- scripts/restic-worker.sh: nạp secret HTTP rồi gọi Restic.
- scripts/create_backup_secrets.py: tạo bộ mật khẩu mới và bcrypt record, giữ nguyên bộ cũ nếu đường dẫn đã tồn tại.
- scripts/backup_lab.py: kiểm tra VM, mount được Compose sử dụng, UUID, ext4, RW và quyền; điều khiển đúng dịch vụ.
- docs/runbook-backup.md: quy trình này.

## Trạng thái nền đã có

VM thực tế dùng QEMU/KVM, Ubuntu 24.04.5, kernel 6.8.0-147-generic, 6 vCPU, khoảng 8 GiB RAM. Root LV đã mở rộng tới 48 GiB. Đã thử dump RAM ELF và dùng Volatility nhận đúng tiến trình Python PID 2946.

Stage 1 đã kiểm tra HTTP 15/15, hash 15/15, UID/GID 1000, rootfs chỉ đọc, không privileged, cap_drop ALL, no-new-privileges và một incident_net Internal=true. VM kết nối được tới 1.1.1.1:443; workstation không kết nối được, errno 101 Network is unreachable. Kết quả này là phép thử một đích TCP; chưa thay cho kiểm tra mọi đường tới VM host.

Đĩa backup vdb đã được kiểm tra: ext4, UUID 72fd2516-3134-4ff1-abcd-50369a6db1b9, RW, thư mục repository owner csattt3 và mode 0750.

Kết quả kiểm thử nền: backup 15 file, tổng 600 B; kiểm tra kho không phát hiện lỗi; restore khớp 15/15 SHA-256 và dữ liệu nguồn giữ nguyên. Thời gian bước restore là 3.649 giây, chưa phải RTO của sự cố.

## 1. Chuẩn bị nguồn

Review, commit nguồn trên nhánh #6 và chuyển đúng commit vào VM theo quy trình ISO có COMMIT.txt, source.tar và SHA256SUMS đã dùng ở stage 1. Giải nén bằng user thường vào thư mục mới. Các lệnh dưới chạy tại thư mục source của bản xuất mới.

## 2. Cấu hình và image trong Ubuntu VM

Sao chép ví dụ thành file thật bên ngoài source, ở bundle mới:

    cp lab/.env.backup.example ../backup.env

Đọc lại đường dẫn và UUID trong file thật. Mẫu đang dành cho tài khoản csattt3 của VM chính. Nếu dùng VM khác phải điền đúng username, mount và UUID của VM đó.

Khi VM còn mạng chuẩn bị, tải image:

    sudo docker --host unix:///var/run/docker.sock compose --env-file ../backup.env -f lab/compose.yaml -f lab/compose.backup.yaml pull backup-server backup-worker restore-worker

Lưu metadata image để biết chính xác bản đã dùng:

    sudo docker --host unix:///var/run/docker.sock image inspect restic/restic:0.19.1 restic/rest-server:0.14.0 > ../backup-images.json

## 3. Tạo secret và kiểm tra

Lệnh tạo secret chỉ chạy trong Ubuntu VM UID/GID 1000. Nó dùng htpasswd của image server đã tải, với network none và mật khẩu qua stdin. Giá trị mật khẩu không được in. Đường dẫn đã tồn tại sẽ bị từ chối; không tự đổi khóa của kho đang có.

    python3 scripts/create_backup_secrets.py "$HOME/csattt-lab/secrets/restic-stage2"

Chạy preflight; phải thấy PREFLIGHT: OK trước khi tiếp tục:

    python3 scripts/backup_lab.py --env-file ../backup.env preflight

Preflight dùng đúng mount source từ Compose đã render, không tạo/chown/mount thư mục hoặc sửa đĩa. Mỗi lệnh start/client/restore đều kiểm tra lại. File secret và nội dung file môi trường thật không được đưa lên GitHub.

## 4. Khởi động server và tạo kho

    python3 scripts/backup_lab.py --env-file ../backup.env start
    python3 scripts/backup_lab.py --env-file ../backup.env status

Trạng thái running mới chứng minh tiến trình đã chạy. Sau đó phải thử API/xác thực và lệnh Restic thực tế. Nếu có lỗi kết nối, giữ nguyên đầu ra để điều tra; không coi đó là lỗi dữ liệu hoặc tự init lại đường dẫn khác.

Với kho mới, init một lần:

    python3 scripts/backup_lab.py --env-file ../backup.env client init

## 5. Sao lưu và kiểm tra kho

Giữ dữ liệu mẫu ở trạng thái không có tiến trình ghi. Từ thư mục source của bundle:

    task_bundle="$(cd .. && pwd)"
    (
      cd "$HOME/csattt-lab/runtime/sample_data"
      sha256sum file_*.txt > "$task_bundle/stage2-source.sha256"
    )

Ghi UTC trước/sau và dùng mã lượt chạy mới:

    task_runid="baseline-$(date -u +%Y%m%dT%H%M%SZ)"
    date -u --iso-8601=seconds
    python3 scripts/backup_lab.py --env-file ../backup.env client backup /source --tag "$task_runid"
    date -u --iso-8601=seconds
    python3 scripts/backup_lab.py --env-file ../backup.env client snapshots --json > ../stage2-snapshots.json
    python3 scripts/backup_lab.py --env-file ../backup.env client check --read-data

Ghi full snapshot ID và kiểm tra đúng tag, 15 file, tổng byte nguồn và metadata của cùng lượt. Thông báo preflight nằm ở stderr để file JSON của snapshots giữ đúng định dạng. Khi tự thêm pipeline lưu log phải bật pipefail hoặc giữ mã thoát thật của chương trình.

## 6. Thử restore

LAB_RESTORE_DIR trong file môi trường phải trỏ tới thư mục mới, rỗng, thuộc UID 1000 và không chồng dữ liệu nguồn/repository. Với mẫu của VM chính:

    mkdir "$HOME/csattt-lab/runtime/restore-stage2"

Sau đó gọi helper với full snapshot ID gồm 64 ký tự hex đã đọc từ JSON. Tham số bên dưới là chỗ cần thay trước khi chạy:

    python3 scripts/backup_lab.py --env-file ../backup.env restore FULL_SNAPSHOT_ID

Backup dùng đường dẫn /source nên kết quả nằm dưới thư mục source bên trong đích restore. Đối chiếu từ đúng thư mục:

    (
      cd "$HOME/csattt-lab/runtime/restore-stage2/source"
      sha256sum -c "$task_bundle/stage2-source.sha256"
    )

Phải đủ đúng 15 đường dẫn và 15 hash khớp. Đây là kiểm thử phục hồi nền; chưa phải RTO/RPO của sự cố chính hoặc kiểm thử ứng dụng sạch trong VM phục hồi.

## 7. Kết thúc và các kiểm tra runtime còn phải làm

Dừng server trước khi unmount/tháo ổ backup trong giai đoạn sự cố:

    python3 scripts/backup_lab.py --env-file ../backup.env stop

Helper stop không đòi preflight mount thành công, để vẫn dừng được server khi mount đang có lỗi. Sau stop còn phải xác nhận các worker đã thoát, unmount thành công và đĩa đã được tháo đúng quy trình.

Chỉ nghiệm thu stage 2 khi đã có:
- Đầu ra start, init, backup, check và restore thật.
- Kết nối REST thiếu/sai credential bị từ chối; credential đúng dùng được.
- Snapshot, số lượng, byte và thời gian nhất quán; hash restore đủ 15/15.
- Inspect runtime chứng minh từng dịch vụ chỉ có đúng mạng, mount và secret của mình.
- Lưu log/image metadata an toàn ngoài Git; bản source có commit ID.
