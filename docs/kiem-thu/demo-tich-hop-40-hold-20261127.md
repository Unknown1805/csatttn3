# Biên bản #40 — lượt HOLD từ Ready đến Recovery

- **Lượt nghiệm thu:** `sim33-20261127T063350Z-ae714596`, ngày 27/11/2026 (UTC).
- **Kết luận:** luồng kỹ thuật đạt trong một lượt, từ Ready đến Recovery; ảnh Dashboard Wazuh xác nhận **7 sự kiện FIM đúng lượt** và đã lưu trong kho LUKS. [Issue #40](https://github.com/Unknown1805/csatttn3/issues/40) còn chờ bàn giao qua PR. Không dùng kết quả từ [lượt không đạt trước đó](demo-tich-hop-40-20261127.md) để bù cho lượt này.
- **Phạm vi:** 15 tệp giả, tổng 600 B; simulator chỉ đổi tên trên bản sao, không đổi nội dung. Thao tác theo [runbook demo](../runbook-demo.md), áp dụng `--apply --hold-after-three`.
- **Nguồn triển khai:** bundle từ commit nền `281835d785d227ebd4649859a84ac7b990e5720a`, với bản sửa HOLD chưa commit được đóng gói riêng. SHA-256 của `src/simulator/simulator.py` trong bundle: `f8fd66e58e5bf5dd4e6763651897b0b0fa0cf0efd7316eda22f14e855d496a6e`. Manifest ISO được kiểm tra trước khi chạy.

## Kết quả theo từng mốc

| Hạng mục | Kết quả của đúng lượt |
|---|---|
| Ready | Checkpoint khớp manifest **12/12**. `CSATTT-READY40-HOLD` và `CSATTT-RECOVERY40-HOLD` dùng overlay riêng; không có NIC ngoài, chia sẻ thư mục hoặc clipboard. Ready không gắn backup. Workstation và simulator cùng dùng bản sao của project `csatttn3-d1-e1428941502f`. SHA-256 và HTTP **15/15**, Wazuh FIM Inventory **15/15**, không tệp thừa; dry-run không đổi tệp gốc hoặc bản sao. |
| Phục hồi thử | Bản sao backup khớp SHA-256. Phục hồi thử đúng snapshot vào `recovery-final-40-Ox9GXp`: SHA-256 và HTTP **15/15**, manifest **27/27**. VM Recovery đã tắt trước Apply. Kết quả này không thay cho phục hồi chính thức. |
| Apply và Pause | Apply đúng một lần. Chỉ container simulator được Pause; kiểm kê xác nhận **3 tệp** đổi tên (`file_01.txt`–`file_03.txt`). HTTP **3×404 + 12×200**. Wazuh Manager ghi **7/7** sự kiện đúng lượt: 3 tên cũ, 3 tên `.simlocked`, 1 tệp ghi chú. Wazuh ghi nhận sự kiện, không thực hiện Pause. |
| Wazuh Dashboard | Trên bản sao cô lập `CSATTT-DASHBOARD40-HOLD`, mục **File Integrity Monitoring → Events** lọc theo thư mục `/lab/fim-probe/sim33-20261127T044507Z-iaqdfdj1/` của bộ dữ liệu Ready. Ảnh hiển thị **7 hits** (added/deleted) vào khoảng `06:33:50–06:33:52 UTC` ngày 27/11, khớp **7/7** sự kiện trong JSON của Manager cho lượt HOLD. Chỉ bật Wazuh trên bản sao để xem lại sự kiện đã lưu; không bật Ready gốc, chạy lại simulator hay tạo lại cảnh báo. |
| RAM, log và PCAP | RAM ELF core được thu khi simulator còn Paused; manifest **2/2**. Volatility `2.28.2` xác nhận PID guest `5708` và dòng lệnh `python /app/simulator.py --apply --hold-after-three`. Log JSON, FIM, kết quả HTTP và bản kiểm kê lúc Pause cùng nằm trong kho LUKS. `tshark` xác nhận nhãn lượt, `/file_01.txt` → `404` và `/file_04.txt` → `200`. Đây là **HTTP đối chứng sau khống chế**, không phải C2 hay lưu lượng simulator tạo. |
| Dừng và ảnh đĩa | Simulator thoát mã `137`; quy trình không gửi lệnh Unpause riêng. Kiểm kê lúc Pause, sau khi thoát và đọc QCOW2 sau shutdown cho **3 → 3 → 3**; SHA-256 nội dung **15/15** và tệp ghi chú khớp. Ready tắt mềm qua ACPI. Cả hai VM tắt lúc sao chép; `qemu-img check` đạt, SHA-256 nguồn trước/sau và bản sao trùng nhau. Bản sao QCOW2 vẫn phụ thuộc checkpoint gốc. |
| Phục hồi chính thức | Ready vẫn tắt. Recovery dùng đĩa `R40_BACKUP_COPY` chỉ đọc; kho Restic mount `ro,noload`. Restic `0.19.1` chạy offline, dùng đúng snapshot vào đích mới `recovery-final-40-8G40Tu`. SHA-256 **15/15**, HTTP `200` và hash nội dung **15/15**, manifest **27/27**. Firefox trong Recovery mở đúng `http://127.0.0.1:18040/file_01.txt`. |

## Timeline UTC

| Mốc | UTC |
|---|---|
| Snapshot `f54b7415a7237e538dc9733ad0f17ce09a305832592e10c86005b90dce56ab70` | `2026-10-30T03:45:55.285507536Z` |
| Simulator Apply | `2026-11-27T06:33:50.733570Z` |
| Xác nhận simulator Paused | `2026-11-27T06:33:52.910150Z` |
| Bắt đầu restore chính thức | `2026-11-27T06:53:36.534213094Z` |
| Kết thúc restore | `2026-11-27T06:53:37.578928937Z` |
| Xác nhận HTTP và hash nội dung 15/15 | `2026-11-27T06:53:37.767231186Z` |

- **Thời lượng riêng của lệnh restore:** `1,044 giây` theo đầu ra script, không phải RTO.
- **Từ Apply đến xác nhận HTTP 15/15:** `19 phút 47,034 giây`, gồm thời gian giữ hiện trường, thu chứng cứ và chờ thao tác. Lấy Apply làm mốc tham chiếu; không coi đây là RTO sản xuất hoặc thời lượng chỉ riêng công đoạn phục hồi.
- **Tuổi snapshot tại Apply:** khoảng `28 ngày 2 giờ 47 phút 55 giây`. Dữ liệu giả khớp 15/15 với manifest nền; không suy ra RPO bằng 0.

## Chỉ mục chứng cứ ngoài Git

| Mục | Nơi lưu và cách đối chiếu |
|---|---|
| RAM | `run40-hold-e2e/evidence.luks` → `ram40h-20261127T063743Z-R9YZgM`; đối chiếu `SHA256SUMS` của `ram.elf` và `capture.txt`. |
| Wazuh, log simulator và PCAP | Cùng kho LUKS → `evidence40h-20261127T064846Z-6f9i594d`; JSON/FIM, PCAP đối chứng và bảng `http-frames.tsv` có `SHA256SUMS`. |
| Ảnh Wazuh Dashboard | Cùng kho LUKS → `dashboard40-hold.jtS5Kl/wazuh-fim-events` (PNG). SHA-256 `84de0c2e9c1222557ccf68dc850a987280225656855d7f212167826768bb0d4e`; `sha256sum --strict -c SHA256SUMS` báo `OK` khi lưu. |
| Ảnh đĩa | Cùng kho LUKS → `disk40h-20261127T065216Z-1mqssb`; đối chiếu `SHA256SUMS`, `provenance.txt` và `offline-inventory.json`. |
| Kết quả phục hồi chính thức | `recovery-final-40-8G40Tu` trên VM Recovery; manifest **27/27**, log, metadata snapshot và mốc UTC. Kết quả Firefox được đối chiếu riêng trong buổi nghiệm thu. |

Không đưa RAM, PCAP, QCOW2, log thô, dữ liệu phục hồi hoặc thông tin xác thực vào Git. Kho LUKS đã khóa sau thu chứng cứ. Giữ Ready tắt và không khởi động ảnh đĩa chứng cứ.

**Còn trước khi đóng #40:** bàn giao qua PR vào `develop` và xác nhận CI sau merge. Không cần chụp lại ảnh, chạy lại mô phỏng hay truy vấn Dashboard. EICAR, SOC nhiều máy và quay demo nằm ngoài biên bản này.
