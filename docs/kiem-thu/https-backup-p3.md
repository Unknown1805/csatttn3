# Nghiệm thu backup/restore qua HTTPS — giai đoạn 3

Ngày: 30/10/2026. Môi trường: Ubuntu trong VM CSATTT-QEMU, QEMU/KVM và Docker.

## 1. Kết luận và nguồn chứng cứ

Đạt hạng mục chức năng backup/restore qua HTTPS/TLS 1.3 trên repository hiện có. Kết luận dựa trên đầu ra thực tế do Nhữ Duy Anh Minh cung cấp, kết thúc bằng `HTTPS GATE: OK`.

Thư mục chứng cứ trong Ubuntu VM:

```text
/home/csattt3/csattt-lab/deploy/https-82e1ede917ea-qDTc8t/bounded-fix-yf__xhl7/https-20261030T034532Z-6l6wka7a
```

Giữ toàn bộ thư mục này ngoài Git, gồm transport.json, restic-negative-tests.json, log phép thử âm, snapshot trước/sau, backup.log, check.log, restore-original-snapshot.log, source.sha256 và result.json. Báo cáo chỉ tổng hợp metadata đã rà soát.

## 2. Bản nguồn đã thực thi

Commit nguồn nền: `82e1ede917ea0e2be20b5a58872f67e95e3eebc0`, cộng hai bản sửa: đọc config Restic như byte mã hóa và giới hạn thời gian/dọn container của phép thử CA hoặc tên sai. Không quy kết quả này cho riêng commit nền chưa sửa.

SHA-256 của hai script sau sửa:

```text
91985ce6f32bf05f1c18eafc9a7c459afc9687290be287ed2a678ecc92c81801  scripts/probe_backup_https.py
c25c71471dd71ef27f35551871aa777beefe3618ad0a655d1fa79953760ebf10  scripts/verify_backup_https.py
```

Lưu COMMIT.txt và source-override.json tại bundle, cùng source-override.json trong `bounded-fix-yf__xhl7`, để truy vết các lần sửa. Commit hoàn thiện trên Git phải bao gồm hai bản sửa và các test hồi quy.

## 3. Kết quả

| Phép kiểm tra | Kết quả |
| --- | --- |
| Preflight | Đúng UUID, ext4, RW, quyền secrets và chứng chỉ TLS |
| Transport probe trong gate | Đạt TLS 1.3, kiểm tra CA/tên, xác thực, từ chối TLS 1.2 và HTTP thường theo yêu cầu bài kiểm tra |
| Restic dùng CA sai | Từ chối chứng chỉ; tiến trình chẩn đoán kết thúc có giới hạn |
| Restic dùng tên sai | Từ chối chứng chỉ; tiến trình chẩn đoán kết thúc có giới hạn |
| Đọc snapshot gốc | Thành công qua HTTPS |
| Backup mới | 15 file, 600 B; snapshot mới được lưu |
| Kiểm tra kho | 2 snapshot, đọc 2/2 packs; không phát hiện lỗi |
| Restore snapshot gốc | 15 file / 600 B; 15/15 SHA-256 khớp |
| Bảo toàn nguồn | 15/15 SHA-256 nguồn vẫn khớp |

Snapshot mới qua HTTPS:

```text
f54b7415a7237e538dc9733ad0f17ce09a305832592e10c86005b90dce56ab70
```

Snapshot gốc được khôi phục qua HTTPS:

```text
4e9113aa6cb9e395797abe8c2f1c410c4437d928ff4bbf5a5122b2496ac6d5d1
```

Bước restore bắt đầu `2026-10-30T03:46:02.315871+00:00`, kết thúc `2026-10-30T03:46:04.992547+00:00`, mất **2.677 giây** theo đồng hồ monotonic của script. Đây là thời gian bước restore nền; chưa phải RTO/RPO của sự cố hoặc khôi phục VM sạch.

## 4. Giới hạn và bước tiếp theo

- Gate này kiểm tra dữ liệu nguồn trên filesystem và các worker backup/restore; không xác nhận HTTP workstation đang hoạt động sau reboot. Lần kiểm tra trước đó workstation đã dừng, cần khởi động lại và kiểm tra HTTP 15/15 riêng.
- Khi gate đạt, backup-server và đĩa backup vẫn đang phục vụ lượt kiểm thử; chưa có xác nhận đã tháo lại đĩa sau lượt HTTPS. Dừng server, xác minh không còn worker chạy, unmount thành công trong guest, sau đó mới tháo vdb khỏi live/config trên host.
- Chưa nghiệm thu giám sát/phát hiện, cô lập cho phiên sự cố, simulator, chuỗi chứng cứ của sự cố, phục hồi VM sạch hoặc RTO/RPO.
- Giữ SOC nhiều người và Tailscale là phần mở rộng sau khi hoàn tất luồng diễn tập chính.
