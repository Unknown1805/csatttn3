# Biên bản nghiệm thu nền lab — giai đoạn 1–2

Liên quan: Issue #6 — nền lab Docker trong máy ảo.

Ngày tổng hợp: 30/10/2026, múi giờ Việt Nam (UTC+7).

## 1. Kết luận và phạm vi

Đã hoàn tất thiết lập nền lab giai đoạn 1–2: workstation Docker và hệ thống sao lưu, kiểm tra kho, khôi phục bằng Restic bên trong VM Ubuntu.

Biên bản tổng hợp đầu ra thực tế do người triển khai cung cấp trong phiên hướng dẫn. Phần cấu hình container đang chạy đã được đối chiếu bằng Docker inspect; các worker chạy một lần và tự xóa sau khi hoàn tất.

## 2. Bản nguồn và môi trường

| Thành phần | Thông tin đã ghi nhận |
| --- | --- |
| VM chính | `CSATTT-QEMU`, QEMU/KVM qua libvirt |
| Hệ điều hành trong VM | Ubuntu 24.04.5 LTS |
| Kernel trong VM | `6.8.0-147-generic` |
| Tài nguyên VM | 6 vCPU, khoảng 8 GiB RAM |
| Ổ hệ điều hành | `vda` 50 GiB; logical volume gốc khoảng 48 GiB |
| Commit nguồn triển khai | `980721d086d354da9d01b020d3b9f99fae00be09` |
| Thư mục bản triển khai | `/home/csattt3/csattt-lab/deploy/980721d086d3-djDNGj` |
| Image workstation | `csatttn3/workstation:stage1` |
| Image client backup/restore | `restic/restic:0.19.1` |
| Image backup-server | `restic/rest-server:0.14.0` |

Nguồn chuyển vào VM có `source.tar`, `COMMIT.txt`, `SHA256SUMS`; đã kiểm tra hai mục trong manifest đều trả về `OK` và commit đúng bản triển khai.

## 3. Kết quả kiểm tra

| Hạng mục | Kết quả thực tế | Đánh giá |
| --- | --- | --- |
| Workstation | Đã kiểm tra đúng 15 file mẫu và HTTP phục vụ đúng nội dung 15/15 file | Đạt |
| Thu và phân tích RAM thử nghiệm | Đã thu RAM dạng ELF; Volatility nhận banner kernel và liệt kê đúng tiến trình Python kiểm chứng PID 2946 | Đạt phép thử nền |
| Quyền container workstation và backup-server | UID/GID `1000:1000`, root filesystem chỉ đọc, `Privileged=false`, bỏ `ALL` capabilities, `no-new-privileges:true` | Đạt |
| Cổng công bố của hai container | `PortBindings={}` | Đạt |
| Mạng workstation | Chỉ nối `csatttn3_incident_net`, `Internal=true` | Đạt |
| Mạng backup-server | Chỉ nối `csatttn3_backup_net`, `Internal=true` | Đạt |
| Mount workstation | Chỉ có dữ liệu mẫu tại `/lab/data`, cho phép ghi; không gắn repository hoặc secret backup | Đạt |
| Mount backup-server | Repository tại `/data` cho phép ghi; file xác thực tại `/run/secrets/rest_htpasswd` chỉ đọc | Đạt |
| Xác thực REST | Không credential: HTTP 401; sai mật khẩu: HTTP 401; đúng mật khẩu trước init: HTTP 404 | Đạt |
| Sao lưu | Đã lưu 15 file, tổng dữ liệu nguồn 600 B, có full snapshot ID | Đạt |
| Kiểm tra kho | `check --read-data` kiểm tra 1 snapshot, đọc 2/2 packs; `no errors were found` | Đạt |
| Khôi phục | Đủ đúng 15 tên file thường, tổng 600 B, 15/15 SHA-256 khớp manifest trước backup | Đạt |
| Bảo toàn nguồn | Kiểm tra lại dữ liệu nguồn sau restore: 15/15 SHA-256 khớp | Đạt |
| Bảo vệ bản backup trước mô phỏng | Backup-server đã dừng; ổ backup đã unmount và tháo khỏi cấu hình VM đang chạy cùng cấu hình khởi động sau | Đạt |

Restic in `Restored 16 files/dirs (600 B)` vì tổng này gồm 15 file và thư mục `source`. Phép kiểm tra riêng xác nhận đúng 15 file dữ liệu.

Trong phép thử kết nối ra ngoài đã thực hiện, VM kết nối được `1.1.1.1:443`; workstation trả về `errno=101`, `Network is unreachable`. Kết quả này ghi nhận cho đúng đích TCP đã thử.

### Kiểm tra bổ sung về ranh giới VM ngày 30/10/2026

- Đã đọc trực tiếp `dumpxml`, `domiflist --inactive`, `net-dumpxml default` và `domif-getlink` trên Kali: VM vẫn nối mạng `default`, mạng này có `forward mode='nat'`, link hiện tại là `up`.
- XML đang chạy không có thiết bị chia sẻ filesystem từ host hoặc ổ vật lý host được gắn trực tiếp; ổ hệ thống là file qcow2 và nguồn chuyển vào VM là ISO chỉ đọc.
- VM vẫn có kênh SPICE và thiết bị USB redirection. Chưa cấu hình khóa clipboard/file transfer rõ ràng cho chế độ diễn tập; chưa kiểm tra đầy đủ các kênh này khi diễn tập.
- Kết luận hoàn tất giai đoạn 1–2 áp dụng cho cài đặt và chức năng workstation/backup/restore. Việc ngắt mạng ngoài của VM, khóa kênh chia sẻ và kiểm chứng chế độ diễn tập được theo dõi trong Issue #19: https://github.com/Unknown1805/csatttn3/issues/19.

Cấu hình này chưa phải căn cứ để tuyên bố an toàn khi chạy virus thật. Kịch bản dự án vẫn là mô phỏng có phạm vi giới hạn trên dữ liệu mẫu.

## 4. Snapshot và thời gian khôi phục

Full snapshot ID:

```text
4e9113aa6cb9e395797abe8c2f1c410c4437d928ff4bbf5a5122b2496ac6d5d1
```

| Mốc đo | Giá trị |
| --- | --- |
| Thời gian snapshot theo Restic, UTC | `2026-10-29T18:19:03.090596853Z` |
| Bắt đầu bước restore, UTC | `2026-10-29T18:34:27.324774+00:00` |
| Kết thúc bước restore, UTC | `2026-10-29T18:34:30.974153+00:00` |
| Thời gian bước restore, đồng hồ monotonic | 3.649 giây |
| File được khôi phục | 15 |
| Tổng dữ liệu file được khôi phục | 600 B |
| Hash khôi phục được xác minh | 15/15 |
| Hash nguồn được xác minh lại | 15/15 |

Phạm vi đo 3.649 giây gồm chạy helper, kiểm tra đầu vào và khởi chạy container để restore. Đây là phép thử khôi phục nền trong cùng VM; RTO/RPO của kịch bản sự cố và khôi phục ứng dụng trong môi trường sạch sẽ được đo ở giai đoạn thực nghiệm sự cố.

## 5. Trạng thái ổ backup

- UUID filesystem backup: `72fd2516-3134-4ff1-abcd-50369a6db1b9`, ext4.
- Mountpoint đã dùng: `/mnt/csattt-backup`.
- Repository trên VM khi ổ còn gắn: `/mnt/csattt-backup/repository/csattt`.
- File đĩa backup trên Kali: `/run/media/ndam/New Volume/CSATTT-Lab/csattt-backup.qcow2`.
- Trước tháo: đã có log `BACKUP UNMOUNTED: OK`.
- Sau tháo: `domblklist` cho cả VM đang chạy và cấu hình lần khởi động sau đều không còn `vdb`; ổ hệ điều hành `vda` còn nguyên.
- Kiểm tra trong Ubuntu: `lsblk` không còn `vdb`, `findmnt -M /mnt/csattt-backup` không trả về mount, `BackupServerRunning=false`.

Ổ backup được tách khỏi VM. File qcow2 vẫn nằm trên máy thật; chưa có bằng chứng về bản sao độc lập ngoài máy hoặc chính sách sao lưu 3-2-1.

## 6. Vị trí log và metadata

Thư mục lượt kiểm thử trong Ubuntu VM:

```text
/home/csattt3/csattt-lab/deploy/980721d086d3-djDNGj/backup-20261029T181858Z-nJ7edi
```

Các file đã được tạo trong quy trình: `init.log`, `backup-start.txt`, `backup.log`, `backup-end.txt`, `source.sha256`, `snapshots.json`, `snapshot-id.txt`, `check.log`, `restore.log`, `restore-hashes.log`, `source-after-restore-hashes.log`, `restore-result.json`, `runtime-check.log`, `backup-stop.log`, `backup-unmounted.txt`.

Ở thư mục bản triển khai còn có `COMMIT.txt`, `SHA256SUMS`, `backup-images.json`, `auth-probe.json`. File `auth-probe.json` chỉ chứa mã HTTP của các phép thử.

Biên bản này không chứa giá trị mật khẩu. Giữ secret và dữ liệu thô của lab ngoài Git; chỉ đưa bản mô tả, kết quả đã rà soát và các chứng cứ phù hợp vào báo cáo.

## 7. Công việc tiếp theo

1. Đưa biên bản nghiệm thu vào tài liệu của Issue #6, cập nhật tài liệu kiến trúc/runbook theo QEMU/KVM và các kết quả đã chạy.
2. Chuẩn bị kịch bản mô phỏng an toàn trên dữ liệu mẫu, chỉ đổi tên file và tạo thông báo mô phỏng.
3. Thực hiện lượt sự cố có thu RAM, ảnh đĩa, log và PCAP theo kế hoạch; quản lý hash và chuỗi bàn giao chứng cứ.
4. Phân tích timeline, khôi phục trong môi trường sạch, kiểm tra ứng dụng và đo RTO/RPO theo phạm vi đã định.

Mốc hoàn tất hiện tại là nền lab giai đoạn 1–2. Các thử nghiệm sự cố, phân tích và sản phẩm báo cáo cuối kỳ thuộc các giai đoạn tiếp theo.
