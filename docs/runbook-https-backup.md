# HTTPS cho backup Restic

Trạng thái: đã chuẩn bị cấu hình và bài kiểm tra. Chỉ ghi nhận triển khai thành công sau khi các lệnh thực tế trong Ubuntu VM trả kết quả đạt. Không thay thế nghiệm thu cô lập sự cố, phục hồi VM sạch hoặc RTO/RPO.

## 1. Luồng và chứng chỉ

    backup-worker / restore-worker
      -> xác minh CA, thời hạn và tên backup-server
      -> TLS 1.3 tới backup-server:8000
      -> HTTP Basic bên trong đường TLS
      -> cùng repository /data/csattt đã có

- RESTIC_REPOSITORY là `rest:https://backup-server:8000/csattt/`.
- Hai worker chỉ nhận chứng chỉ CA công khai qua RESTIC_CACERT. Không nhận khóa server hoặc khóa CA.
- Server chỉ nhận server.crt và server.key; SAN phải có DNS:backup-server.
- CA riêng của lab cấp chứng chỉ server. Khóa CA nằm trong thư mục riêng, không mount vào container.
- Các file TLS thật nằm ngoài Git; thư mục 0700, file 0600, UID/GID 1000. Không cài CA này vào kho tin cậy toàn hệ thống.
- Mạng backup_net vẫn internal; không publish cổng; giữ UID 1000, rootfs chỉ đọc và bỏ capabilities.
- Kho, mật khẩu và snapshot cũ được giữ nguyên. Không chạy init trong lượt nâng cấp HTTPS.

## 2. Chuẩn bị và chuyển nguồn

Review và commit nguồn trên nhánh feature/https-backup. Xuất đúng commit bằng git archive và ISO chỉ đọc có COMMIT.txt, source.tar, SHA256SUMS như các giai đoạn trước. Giải nén vào bundle mới; không sửa bundle 980721d086d3-djDNGj đã chạy HTTP.

Trong bundle mới, sao chép backup.env cũ ra ngoài thư mục source. Chỉ bổ sung LAB_TLS_DIR và chọn LAB_RESTORE_DIR mới chưa tồn tại. Giữ nguyên UUID, repository, thư mục bí mật và nguồn dữ liệu.

Giá trị mẫu của VM chính:

    LAB_TLS_DIR=/home/csattt3/csattt-lab/secrets/restic-tls-stage3
    LAB_RESTORE_DIR=/home/csattt3/csattt-lab/runtime/restore-stage3-https

Các image restic/restic:0.19.1 và restic/rest-server:0.14.0 đã dùng ở lượt trước; không đổi phiên bản trong lượt này.

## 3. Tạo chứng chỉ trong Ubuntu VM

Chạy bằng csattt3, không sudo, từ source mới:

    python3 scripts/create_backup_tls.py \
      "$HOME/csattt-lab/secrets/restic-tls-stage3" \
      --ca-directory "$HOME/csattt-lab/secrets/restic-tls-ca-stage3"

Script tạo RSA 3072-bit, CA có hiệu lực 1095 ngày và chứng chỉ server 365 ngày. Nó từ chối thư mục đã tồn tại; không ghi đè chứng chỉ hoặc mật khẩu. Nếu có lỗi giữa chừng, giữ thư mục và đầu ra để kiểm tra; không xóa/tạo lại khóa tùy ý.

Đầu ra cần có server.crt: OK, SAN DNS:backup-server, thời hạn và fingerprint SHA-256. Đây là kiểm tra chứng chỉ tĩnh, chưa chứng minh server/worker chạy HTTPS.

## 4. Gắn lại đĩa backup đúng lúc

Chỉ trong giai đoạn chuẩn bị sạch, người vận hành trên Kali xác minh VM hiện không có vdb và gắn lại đúng file csattt-backup.qcow2 bằng libvirt. Không tạo đĩa mới, không mkfs và không init lại repository.

Trong Ubuntu, xác minh UUID 72fd2516-3134-4ff1-abcd-50369a6db1b9 rồi mount vào /mnt/csattt-backup. Helper kiểm tra UUID, ext4, RW, quyền repository, bí mật, cặp khóa/chứng chỉ và tên server:

    python3 scripts/backup_lab.py --env-file ../backup.env preflight

Nếu UUID hoặc chứng chỉ không đạt, dừng kiểm tra; không nới quyền bằng chmod 777 hoặc bỏ kiểm tra TLS.

## 5. Khởi động HTTPS và nghiệm thu

    python3 scripts/backup_lab.py --env-file ../backup.env start
    python3 scripts/backup_lab.py --env-file ../backup.env status
    python3 scripts/probe_backup_https.py --env-file ../backup.env

Probe thực hiện request tới IP container nhưng xác minh tên backup-server. Chứng chỉ không cấp cho IP, do đó dùng https://IP trực tiếp với kiểm tra tên sẽ bị từ chối như thiết kế.

Kết quả yêu cầu:

- Chứng chỉ đúng, CA đúng và tên đúng: TLSv1.3, GET /csattt/config trả 200 vì kho đã tồn tại.
- Không xác thực và mật khẩu sai: 401.
- Không tin CA hoặc tên sai: lỗi xác minh chứng chỉ.
- TLS 1.2: từ chối vì server yêu cầu TLS 1.3.
- HTTP thường không gửi credential: 400 yêu cầu HTTPS hoặc đóng kết nối. Không yêu cầu bắt buộc connection refused.
- Server chỉ có backup_net nội bộ và không publish cổng.

Chạy gate đầy đủ; LAB_RESTORE_DIR phải là đường dẫn mới chưa tồn tại, script tự tạo:

    python3 scripts/verify_backup_https.py --env-file ../backup.env

Gate kiểm tra đúng 15 file giả / 600 B, chạy hai phép thử CA/tên sai bằng chính Restic worker, đọc được snapshot gốc, backup một snapshot có tag mới, check --read-data, rồi restore snapshot gốc qua HTTPS vào thư mục mới. Nó đối chiếu 15/15 SHA-256 dữ liệu khôi phục và 15/15 nguồn còn nguyên.

Snapshot gốc bắt buộc giữ được:

    4e9113aa6cb9e395797abe8c2f1c410c4437d928ff4bbf5a5122b2496ac6d5d1

Các lượt kiểm tra âm dùng entrypoint Restic trực tiếp để cố tình thử điều kiện sai; helper và worker vận hành bình thường vẫn chặn override URL/CA/insecure-tls. Đây là rào chắn chống thao tác nhầm, không ngăn được người có quyền quản trị Docker cố ý bỏ qua.

Kết quả nằm ở thư mục https-UTC-* cạnh backup.env: transport.json, log kiểm tra âm, snapshot trước/sau, log backup/check/restore, manifest và result.json. Không đưa bộ log/chứng cứ thô hoặc bí mật lên Git. Chỉ tổng hợp thông số cần thiết và liên kết commit vào báo cáo.

Nếu gate dừng giữa chừng, giữ log và thư mục đích; muốn chạy lại phải chọn LAB_RESTORE_DIR mới, không xóa dữ liệu để ép kiểm tra chạy tiếp.

## 6. Kết thúc

    python3 scripts/backup_lab.py --env-file ../backup.env stop

Xác nhận không còn backup-worker/restore-worker đang chạy; unmount thành công trong guest rồi mới tháo đĩa vdb trên host, cả live và config, như lượt trước. Không dùng force/lazy unmount hoặc detach đĩa đang được ghi.

Chỉ cập nhật README/biên bản thành “HTTPS đã nghiệm thu” sau khi có đầu ra runtime đạt. Giữ rõ thời gian restore chỉ là thời gian bước kiểm tra, không phải RTO của sự cố. SOC nhiều người/Tailscale là phần mở rộng để sau nếu còn thời gian.

## 7. Kiểm tra nguồn và tài liệu chính thức

Kiểm tra nguồn không khởi động dịch vụ:

    docker compose --env-file lab/.env.backup.example -f lab/compose.yaml -f lab/compose.backup.yaml config --quiet
    python3 -m unittest discover -s tests -p 'test_backup_tls.py' -v

- [rest-server 0.14.0: TLS và xác thực](https://github.com/restic/rest-server/blob/v0.14.0/README.md)
- [Restic: biến môi trường và RESTIC_CACERT](https://restic.readthedocs.io/en/stable/075_scripting.html)
- [OpenSSL 3.0: tạo chứng chỉ](https://docs.openssl.org/3.0/man1/openssl-req/)
