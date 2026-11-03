# Biên bản kiểm thử simulator S1 — Issue #33

Ngày ghi nhận: 03/11/2026. Người thao tác: Nhữ Duy Anh Minh.

## 1. Phạm vi và kết luận

Đã chạy dry-run và apply simulator đổi tên trên một bản sao riêng gồm 15 file giả, tổng 600 B, trong Ubuntu VM CSATTT-QEMU. Apply đổi 15 tên `.txt` thành `.txt.simlocked` và tạo `SIMULATION_NOTE.txt`. Kiểm tra nội dung/hash của 15 file sau đổi tên đạt; 15 file gốc trong `sample_data` vẫn nguyên vẹn. Wazuh ghi nhận các đường dẫn dự kiến và Dashboard hiển thị các cặp added/deleted của lượt thử.

Chỉ nghiệm thu simulator trên bản sao và đường quan sát FIM. Không mã hóa, không chạy mẫu ransomware thật, không làm gián đoạn dữ liệu chính của Workstation. Chưa có bộ chứng cứ hoặc kết quả recovery/RTO/RPO cho lượt sự cố chính.

## 2. Nguồn và môi trường

- Commit nguồn simulator: `513cd78f007220d843e9bee247d2049eeae848b0`.
- VM: CSATTT-QEMU, Ubuntu 24.04.5; image có sẵn `csatttn3/workstation:stage1`, không tải image trong lượt thử.
- Bản sao thử trong guest: `/home/csattt3/csattt-lab/runtime/fim-probe/sim33-20261102T192034Z-8wjzcpp9`.
- Đường Wazuh quan sát: `/lab/fim-probe/sim33-20261102T192034Z-8wjzcpp9/`.
- Operator ISO: `CSATTT_APPLY`; SHA-256 `901bf90d2a71c239f137dafe54e263f735a294d2844f84d58729695c19f466d3`.
- Bộ điều phối được chuẩn bị ngoài Git tại `outputs/sim33-fim-history-fix-dcbsizjm` trong workspace CSATTT trên Kali; không coi mã điều phối là một phần của commit nguồn nêu trên. Trước khi chạy đã kiểm tra hash các file nguồn quan trọng và artifact.

## 3. Kết quả quan sát

| Kiểm tra | Kết quả |
|---|---|
| Dry-run | Container thoát 0; log `dry_run_complete`, `changed_files=0`; nguồn và bản sao đều 15/15 không đổi |
| Baseline FIM trước apply | Đủ 15 tên file khác nhau; tìm thấy 15 bản ghi phù hợp trong `/var/ossec/logs/alerts/2026/Nov/ossec-alerts-02.json.gz` |
| Nguồn/cô lập trước apply | Runner báo precheck đạt; kiểm tra UUID VM, không NIC ngoài/default route, phép thử TCP không có đường đi và đĩa backup vắng mặt |
| Giới hạn container trước start | Runner kiểm tra UID/GID 1000, rootfs RO, không privileged/host PID/publish cổng, drop ALL capabilities, no-new-privileges, CPU 0.5 / RAM 128 MiB / PID 32 |
| Mount/mạng simulator | Chỉ chương trình RO và bản sao thử RW; chỉ mạng incident internal; không mount socket, backup hoặc secret |
| Apply | Container thoát 0, không OOM; log kết thúc `complete`, đủ 15 thao tác đổi tên theo thứ tự |
| Sau apply | Đúng 15 file `.simlocked` và note; nội dung/hash 15/15 giữ nguyên, note ghi rõ mô phỏng và đúng run ID |
| Dữ liệu gốc | `sample_data` khớp nội dung mẫu 15/15; không được dùng làm mount ghi của lượt simulator |
| Dịch vụ/cô lập sau apply | Runner kiểm tra bốn dịch vụ nền vẫn running, không OOM; phép thử mạng được kiểm tra lại |
| FIM sau apply | Tập tên cũ có sự kiện deleted; tập tên mới và note có added; kiểm tra theo tên/đường dẫn, không theo tổng số dòng |
| Dashboard | Ảnh người vận hành cung cấp hiển thị added/deleted đúng prefix lượt thử; các hàng thấy trong ảnh thuộc 03:36:33–03:36:47 UTC ngày 03/11 |

Tên file trong ảnh Dashboard bị rút gọn; ảnh xác nhận luồng hiển thị. Kết luận đủ 15 tên lấy từ kiểm tra log có cấu trúc của runner, không suy ra chỉ từ số hàng trong ảnh. Note được runner xác nhận trong log; hai ảnh Dashboard sau apply không cho thấy riêng hàng note.

## 4. Chứng cứ được giữ trong guest

Thư mục kết quả runner báo:

```text
/home/csattt3/csattt-lab/deploy/sim33-auto-OVYiwh/apply-test-20261103T033632Z-4veo9c93
```

- `result.json`: commit, container ID, thư mục thử, số file/hash và `fim_expected_events_seen`.
- `simulator.log`, `create.log`, `start.log`: thao tác và kết quả chương trình.
- `container-before.json`, `container-after.json`: inspect chọn lọc, không xuất toàn bộ biến môi trường.
- `network-before.json`, `network-after.json`: phép kiểm tra mạng trong guest.
- `fim-before.json`, `fim-after.json`, các file `fim-*-sources.json`: bản ghi chọn lọc đúng prefix và nguồn log.
- `renamed-sha256.json`, `override.json`, `SHA256SUMS`.

Runner đã tạo manifest trước khi in RESULTS. Sau lượt thử, người vận hành chạy riêng `sha256sum -c SHA256SUMS` trong thư mục kết quả; ảnh terminal xác nhận cả 14/14 file đều OK. Đây là kiểm tra khớp manifest tại thời điểm kiểm tra, không thay thế bản sao chứng cứ độc lập hoặc nhật ký bàn giao. Chưa xác nhận xuất bộ chứng cứ khỏi guest. Không đưa chứng cứ thô hoặc secret vào Git; giữ container thoát và bản sao thử sau apply.

## 5. Các lần dừng và cách xử lý

Wrapper dry-run ban đầu báo STOP dù container thoát 0 và có log hoàn tất. Kiểm tra riêng sau đó xác nhận cả dữ liệu gốc và bản sao vẫn nguyên 15/15. Chưa xác định chính xác nguyên nhân exit code của wrapper; không coi là chương trình đã đổi file hoặc tự chạy apply lại để sửa kết quả.

Apply lần đầu dừng trước khi tạo/start container vì bộ đọc chỉ xét `alerts.json` hiện tại, chưa thấy đủ tên baseline. Bộ đọc mới xét thêm JSON/JSON.gz lưu trữ liên quan, giải mã JSON rồi so đường dẫn và loại bản ghi lặp theo ID. Điều kiện đủ 15 tên khác nhau vẫn giữ nguyên. Lượt thành công tìm được baseline tại log nén ngày 02/11, rồi mới tạo/start container apply.

## 6. Giới hạn và bước kế tiếp

- FIM ghi nhận tên file xuất hiện/biến mất; không xác định tác nhân ghi file từ riêng các bản ghi này, không tự phân loại họ ransomware hoặc diệt mã độc. Tương quan với log simulator là nguồn biết trước trong lượt có kiểm soát.
- Kiểm tra runtime/mount trong S1 không chứng minh chống mọi cách thoát container/VM hoặc mọi đường truy cập tới host. Không thay thế nghiệm thu cô lập trước lượt sự cố sau.
- Khoảng thời gian của các hàng cảnh báo không phải số đo độ trễ phát hiện, MTTD hoặc RTO.
- Lượt này chưa thu RAM/ảnh đĩa/PCAP của sự cố, chưa chạy trên dữ liệu chính, chưa phục hồi từ backup trong VM sạch và chưa đo RTO/RPO.
- Sau khi bảo quản chứng cứ S1, chuẩn bị kế hoạch lượt sự cố tích hợp và phục hồi sạch; không đổi tên ngược để tính là restore.

Tham chiếu: [runbook simulator](../runbook-simulator.md), [kiến trúc](../kien-truc-lab.md), [nghiệm thu A2](co-lap-vm-a2.md).
