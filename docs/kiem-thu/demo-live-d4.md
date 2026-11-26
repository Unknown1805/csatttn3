# Biên bản D4 — tác động HTTP, FIM và phân tích RAM

Lượt diễn tập ngày 13/11/2026, thuộc [Issue #40](https://github.com/Unknown1805/csatttn3/issues/40). Các mốc trong biên bản dùng UTC. D4 dùng 15 file giả; mô phỏng chỉ đổi tên và tạo thông báo, không mã hóa dữ liệu.

## Định danh

| Mục | Giá trị |
|---|---|
| VM sự cố | `CSATTT-REPLAY-D4` |
| Project Docker | `csatttn3-d1-f5f244c41a46` — tiền tố `d1` do công cụ dùng lại; đây là lượt D4 |
| Commit nguồn trong `result.json` | `f8d23ea2878330f245660fccb18fb8d24b3162ae` |
| Trạng thái lưu khi kết thúc bước sự cố | `d1_incident_contained_ready_for_ram` |

## Kết quả thực nghiệm

| Mốc hoặc phép kiểm tra | Kết quả | Nguồn |
|---|---|---|
| Bắt đầu mô phỏng | `02:42:58.819258` | `result.json`, trường `apply_started_utc` |
| Tạm dừng | Xác nhận lúc `02:43:01.225384` sau 3 lần đổi tên: `file_01.txt`, `file_02.txt`, `file_03.txt` | `result.json` và log simulator |
| HTTP sau khi tạm dừng | Ba URL tên cũ trả `404`; 12 URL còn lại trả `200` | `result.json` |
| Wazuh FIM | Đủ 7 đường dẫn dự kiến: 3 tên cũ bị xóa, 3 tên mới được thêm và 1 thông báo mô phỏng được thêm | `result.json`, trường `fim_expected_paths_verified` |
| Toàn vẹn dữ liệu | Nội dung 15/15 file mô phỏng không đổi; bộ dữ liệu gốc kiểm tra đạt 15/15 | `result.json` |
| Toàn vẹn bộ RAM | 9/9 mục, gồm `ram.elf`, khớp `SHA256SUMS` | Kết quả `sha256sum -c SHA256SUMS` trên Kali |
| Nhận diện tiến trình từ RAM | `PsList`: PID guest `12819`, PPID `12782`, tên `python`, tạo lúc `02:42:58.546849`. `PsAux`: `python /app/simulator.py --apply` | Volatility 3 `2.28.2`, chạy offline với symbol Ubuntu `6.8.0-147-generic` |

Tiến trình tìm thấy trong bản RAM khớp PID guest ghi trong `result.json`. Wazuh ghi nhận thay đổi đường dẫn; bộ điều phối lab thực hiện Pause. Kết quả không chứng minh Wazuh tự nhận diện hoặc tự dừng ransomware.

## Nguồn và bảo quản chứng cứ

- Đầu ra sự cố được đối chiếu từ ảnh Terminal của người vận hành: `d1-incident-*/result.json` và log container D4. `paused_after: true` là trạng thái tại thời điểm lưu kết quả, không phải trạng thái hiện tại sau reboot.
- Bộ RAM lưu ngoài Git ở `CSATTT-Lab/evidence-d4/ram-d4-20261113T032655Z-LIR6xg/`, gồm `ram.elf`, `SHA256SUMS` và metadata thu thập. Mốc 9/9 áp dụng cho manifest của bộ RAM, không phải toàn bộ hồ sơ D4.
- Repo chỉ lưu biên bản tóm tắt; RAM dump, ảnh đĩa, log thô và thông tin xác thực không được đưa vào Git.

## Giới hạn nghiệm thu

| Lượt | Điều có thể trình bày từ chứng cứ đã có |
|---|---|
| **D4** | Tác động HTTP, FIM, tạm dừng và nhận diện tiến trình trong RAM. Chưa có xác nhận riêng cho bước kết thúc tác nhân có kiểm soát, ảnh đĩa sau kết thúc, PCAP hoặc phục hồi của D4. |
| **STOP-TEST** | [Lượt kiểm thử riêng](../runbook-demo.md#7-dừng-simulator-và-kiểm-tra-sau-shutdown) xác nhận mã thoát 137, số file đổi tên giữ 3 → 3 → 3 và nội dung 15/15 khớp hash. Không gán mã thoát này cho D4. |
| **D2** | [Lượt phục hồi riêng](demo-chay-lai-d2.md): SHA-256 và HTTP đều đạt 15/15. Thời gian 12.202 giây chỉ là thời gian script phục hồi, không phải RTO toàn quy trình. |

Các lượt trên không phải một lần chạy liên tục và không dùng để kết luận RTO/RPO của D4. Quy trình reset và khả năng tái lập để trình diễn thuộc phần chưa nghiệm thu của Issue #40.
