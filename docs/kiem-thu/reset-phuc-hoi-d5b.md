# Biên bản D5B — reset lab và phục hồi dữ liệu

Lượt kiểm thử ngày **26/11/2026 (UTC)** cho [Issue #46](https://github.com/Unknown1805/csatttn3/issues/46). Đã xác nhận boot từ checkpoint trong VM reset mới và phục hồi dữ liệu trong một VM khác. Người vận hành đã đối chiếu manifest của bộ kết quả phục hồi; chưa bàn giao qua PR.

## Đầu vào và cấu hình

| Hạng mục | Kết quả đối chiếu |
|---|---|
| Checkpoint trước sự cố | `checkpoint-d1-20261105T060137Z-eorcagzm`: SHA-256 **12/12**; `disk.qcow2` không có backing file. Hai VM D5B dùng overlay khác nhau, cùng trỏ về checkpoint này. |
| Bản sao kho Restic | `recovery-d5-20261126T171626Z-QeKlkm/backup-copy.qcow2` khớp SHA-256. VM reset không gắn kho; VM phục hồi nhận đĩa `RO=1`, UUID `72fd2516-3134-4ff1-abcd-50369a6db1b9`, lúc đầu chưa mount. |
| Snapshot Restic | `f54b7415a7237e538dc9733ad0f17ce09a305832592e10c86005b90dce56ab70`, đã đọc được từ bản sao kho. |
| Cấu hình VM | `CSATTT-RESET-D5B` và `CSATTT-RECOVERY-D5B`: nạp trực tiếp kernel/initramfs `6.8.0-147-generic`, đĩa hệ thống SATA, CPU `host-passthrough`; không NIC, thư mục chia sẻ, clipboard hay truyền file SPICE. VM phục hồi bật ACPI và gắn đĩa backup qua VirtIO chỉ đọc. |

## Kết quả kiểm thử

| Bước | Kết quả | Nguồn xác nhận |
|---|---|---|
| Reset | VM mới boot từ overlay của checkpoint tới màn hình đăng nhập Ubuntu. | XML libvirt và ảnh màn hình đăng nhập. |
| Baseline | SHA-256 trên đĩa **15/15**; HTTP trả `200` và SHA-256 nội dung tải về khớp **15/15**. Cả hai so với bảng hash của 15 file nền trước sự cố. | Đầu ra kiểm tra trong Workstation trên VM reset. |
| Wazuh FIM | Manager ghi rule `554` (file mới) cho `d5b-fim-20261126T181451Z-3496.txt` lúc `18:14:51.532 UTC`. File thử vô hại nằm trong `fim-probe`, ngoài bộ 15 file nền. | Kết quả lọc đúng đường dẫn trong `alerts.json`; chưa đối chiếu trên Dashboard. |
| Phục hồi | VM reset đã tắt trước khi bật VM phục hồi. Restic `0.19.1` chạy với `--network none`, đọc kho mount `ro,noload` và ghi vào đích mới. Đủ đúng 15 file, SHA-256 khớp **15/15**. | Kiểm tra đĩa trong guest và kết quả `RESTORE_SHA256=15/15 OK`. |
| HTTP sau phục hồi | Lúc `18:30:23` theo đồng hồ VM, HTTP localhost phục vụ chính thư mục vừa restore: `200` và SHA-256 nội dung khớp **15/15**. Firefox trong VM mở `file_01.txt` lúc `18:31:51`. Yêu cầu `favicon.ico` trả `404` không thuộc bộ kiểm tra. | Kết quả `HTTP_BODY_SHA256=15/15 OK` và ảnh Firefox/console. |

Lượt phục hồi kiểm tra trước trên Kali cũng đạt SHA-256 và HTTP **15/15**. Kết quả trong bảng là lượt trong VM riêng, không dùng kết quả Kali để thay thế.

## Trở ngại và giới hạn

- D5 ban đầu kẹt ở `initramfs`. D5B nhận ổ hệ thống sau khi chuyển sang SATA; `host-passthrough` khắc phục lỗi `glibc` thiếu `x86-64-v2` trong Manager. Trong VM phục hồi, VirtIO nhận diện được đĩa backup sau khi bật ACPI. Biên bản xác nhận cấu hình đã chạy, không kết luận đường boot GRUB cũ đã được sửa.
- Chỉ xác nhận FIM ở Manager và HTTP trên `127.0.0.1` trong VM phục hồi. Chưa nghiệm thu Dashboard, truy cập từ máy khác, hoặc RTO/RPO. Không quay demo ở lượt này.
- Không ghép D5B với [D4](demo-live-d4.md), [D2](demo-chay-lai-d2.md) hoặc STOP-TEST thành một lần chạy liên tục. [Issue #40](https://github.com/Unknown1805/csatttn3/issues/40) vẫn cần một lượt Ready → Recovery theo [runbook demo](../runbook-demo.md).

## Chứng cứ và bàn giao

- VM reset: `CSATTT-Lab/reset-d5b-20261126T175526Z-SzsBBX/`. VM phục hồi: `CSATTT-Lab/recovery-d5b-20261126T181642Z-qIAd1a/`.
- Trong VM phục hồi, người vận hành chạy `sha256sum --strict -c` với `restore-d5b-GRdjvy/SHA256SUMS-restore-d5b.1Ufvjx`: **17/17 OK**, gồm 15 file đã phục hồi, `restore.log` và `verify-result.txt`. Kết quả này xác nhận toàn vẹn bộ tệp kể từ lúc lập manifest, không thay thế phép so với dữ liệu nền và không bao gồm ảnh màn hình, chứng cứ reset hay log FIM.
- Giữ manifest, ảnh, log thô, ảnh đĩa và thông tin xác thực ngoài Git. Chưa xác nhận commit nguồn của bundle trong guest hoặc thời gian chạy riêng của script restore; không suy ra các số liệu đó từ thời điểm HTTP.
- Bàn giao qua nhánh `feature/46-reset-va-phuc-hoi`, PR vào `develop`; dùng [runbook backup](../runbook-backup.md) và runbook demo thay vì viết lại hướng dẫn.
