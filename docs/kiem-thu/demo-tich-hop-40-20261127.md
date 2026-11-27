# Biên bản #40 — mốc dừng không đạt, Recovery đạt

Lượt `sim33-20261127T030738Z-b1d1b744` (27/11/2026 UTC), theo [runbook demo](../runbook-demo.md). Chỉ dùng bản sao 15 tệp giả. **Lượt tích hợp chưa đạt [#40](https://github.com/Unknown1805/csatttn3/issues/40):** tại mốc Pause có 3 tệp đổi tên, nhưng sau khi container thoát và sau khi tắt VM đều có 4. Phục hồi sau sự cố đạt trên VM riêng; kết quả này không thay thế mốc dừng.

## Kết quả cùng lượt

| Bước | Kết quả và nguồn xác nhận |
|---|---|
| Ready | Checkpoint khớp manifest **12/12**. `CSATTT-READY-40` dùng overlay riêng, không NIC ngoài hoặc đĩa backup. Bản sao có SHA-256 và HTTP **15/15**; Wazuh FIM Inventory **15/15**. Dry-run không đổi tệp. |
| Mô phỏng và Pause | Apply đúng một lần. Pause **chỉ container simulator** lúc `03:07:41.001840 UTC`; xác nhận 3 lần đổi tên. Workstation trả **3×404, 12×200**; Wazuh Manager ghi đúng **7/7** sự kiện FIM: 3 tên cũ, 3 tên `.simlocked` và 1 tệp ghi chú. Wazuh ghi nhận, không thực hiện Pause. |
| RAM và PCAP | Manifest dump ELF khớp **2/2**. Volatility `2.28.2` xác nhận PID guest `7119` và dòng lệnh simulator. `tshark` đọc lại PCAP đúng nhãn lượt, `/file_01.txt` → `404`, `/file_04.txt` → `200`. Đây là **HTTP đối chứng sau Pause**, không phải C2 hoặc lưu lượng simulator tạo. |
| Dừng — không đạt | Docker báo exit `137`, `FinishedAt=2026-11-27T03:40:06.088750336Z`; có sự kiện `kill` và `die` trong cùng giây. Kiểm kê sau thoát thấy `file_04.txt.simlocked` ngoài ba tên đã ghi nhận lúc Pause. SHA-256 nội dung **15/15** vẫn khớp. Log simulator sau thoát khớp log lúc Pause và chỉ có **3** bản ghi đổi tên. Chưa xác định được thời điểm hoặc nguyên nhân của lần đổi tên thứ tư. |
| Ảnh đĩa | Ready tắt mềm qua ACPI; cả hai VM tắt khi sao chép. `qemu-img check` đạt; SHA-256 overlay nguồn trước/sau và bản sao nguyên byte trùng nhau. Đọc bản sao chỉ đọc xác nhận **4 tên `.simlocked`, 11 tên gốc, 1 ghi chú**; hash **16/16** khớp kiểm kê trước tắt. Bản sao vẫn phụ thuộc checkpoint gốc. |
| Recovery sau sự cố — đạt | Ready vẫn tắt. `CSATTT-RECOVERY-40` dùng bản sao backup đúng SHA-256, đĩa và kho mount chỉ đọc; Restic `0.19.1` chạy offline. Snapshot `f54b7415a7237e538dc9733ad0f17ce09a305832592e10c86005b90dce56ab70` được phục hồi vào đích mới `recovery-final-40-9vXZnk`, khác đích thử. SHA-256 **15/15**, HTTP `200` và hash nội dung **15/15**, manifest **27/27**. Firefox mở đúng `http://127.0.0.1:18040/file_01.txt` trong VM Recovery. |

Thời gian lệnh restore: **1,701 giây**. Các mốc UTC của restore và HTTP được ghi riêng trong thư mục kết quả trên VM Recovery; biên bản chưa kết luận RTO/RPO. HTTP phục hồi được xác nhận trên loopback của VM, không phải truy cập từ máy khác.

## Chỉ mục chứng cứ ngoài Git

| Mục | Thư mục và đối chiếu |
|---|---|
| RAM | `ram40-20261127T031202Z-tCTXQb`: `ram.elf`, `capture.txt` và `SHA256SUMS`. |
| HTTP đối chứng | `pcap40-20261127T033111Z-q4hz1a3h`: PCAP khớp `SHA256SUMS`; kết quả đọc lại ở `http-frames.tsv`. |
| Log lúc Pause | `logs40-20261127T033539Z-ubgj3utd`: JSON simulator, JSON Wazuh FIM và metadata, SHA-256 **3/3**. |
| Sai lệch sau khi thoát | `deviation40-20261127T035223Z-bhixwya0`: log sau thoát, sự kiện Docker, kiểm kê tệp và metadata; SHA-256 **4/4**. |
| Ảnh đĩa không đạt mốc dừng | `disk40-deviation-20261127T035934Z-PwQByw`: overlay, thông tin chuỗi đĩa, bản đối chiếu offline và manifest. |
| Kết quả Recovery | `recovery-final-40-9vXZnk` trên VM Recovery: dữ liệu đã phục hồi, log, mốc UTC và manifest. Không dùng kết quả phục hồi thử để thay thế. |

Năm gói chứng cứ đầu nằm trong kho LUKS2. Không đính kèm log thô, RAM, PCAP, QCOW2, dữ liệu phục hồi hoặc thông tin xác thực vào Git.

## Điều kiện trước khi quay demo

- Giữ nguyên lượt này và không sửa tên tệp để làm kết quả khớp log. Rà lại quy trình dừng trên bản thử riêng; đối chiếu danh sách tên và SHA-256 ở cả ba mốc, không dựa vào mã `137` hoặc log simulator đơn lẻ.
- Nghiệm thu một lượt mới liền mạch Ready → mô phỏng → khống chế → thu chứng cứ → Recovery, đạt **3 → 3 → 3** và Recovery **15/15** trong chính lượt đó. Không ghép với D2, D4, D5B hay STOP-TEST để đóng #40.
- Chưa nghiệm thu EICAR hoặc SOC nhiều máy trong biên bản này. Chưa quay demo.
