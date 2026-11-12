# Lượt chạy lại D2 — kết quả chức năng và giới hạn

Người vận hành: Nhữ Duy Anh Minh. Các mốc dưới đây theo UTC ngày 05/11/2026; hoàn thiện biên bản trên Kali ngày 06/11/2026. Nguồn Git: `54c0e4f352b941ef2a6267a6eefe7b6cd3218949`, nhánh công việc `feature/demo-chay-lai`.

## Kết luận

D2 đã đi từ bản chuẩn bị mới tới sự cố mô phỏng, Wazuh/FIM, thu RAM/log/PCAP/chuỗi đĩa và kết quả phục hồi cuối cùng. Ảnh terminal do người vận hành cung cấp ghi `D2 FINAL RECOVERY: OK / HASHES 15/15 / HTTP 15/15`, dữ liệu 15 file/600 B; dữ liệu gốc và D1 giữ nguyên. Đây là xác nhận chức năng lần chạy thứ hai; chưa nghiệm thu một launcher chung hoặc một lượt trình diễn ngắn liên tục có bấm giờ.

Người vận hành đã chạy `sha256sum -c SHA256SUMS` ngay trong thư mục kết quả recovery D2: cả 28 mục hiển thị `OK`, gồm result.json, hash dữ liệu và log HTTP. Firefox trong Ubuntu recovery mở được file_01 đúng hai dòng dữ liệu giả tại URL trên. Hai ảnh màn hình xác nhận checkpoint này; không coi ảnh là bản sao raw chứng cứ hoặc khẳng định đã tái tính các file recovery độc lập trên Kali.

## Định danh

| Mục | D2 |
|---|---|
| VM sự cố | CSATTT-REPLAY-D2; UUID b6a61016-e313-4360-a0f1-2a1ab7b1ed26 |
| Project sự cố | csatttn3-d1-15459d7d5ddb; tiền tố d1 được helper dùng lại, đây là lượt D2 |
| Bundle | /home/csattt3/csattt-lab/deploy/d1-54c0e4f352b9-kdtieqod |
| Active data | /home/csattt3/csattt-lab/runtime/fim-probe/sim33-20261105T150902Z-ca6vi2ie |
| Incident | d1-incident-20261105T155015Z-waytgw2f dưới bundle |
| Runtime evidence | d1-evidence-20261105T163139Z-3m4jftoy dưới bundle |
| VM phục hồi | CSATTT-RECOVERY-D1; UUID 2b3b6749-45d6-4518-a953-66d2bdc62fcc |
| Kết quả phục hồi | /home/csattt3/csattt-lab/runtime/recovery-d2-20261105T204926Z-z85thxwk |
| HTTP phục hồi | http://172.24.0.2:8080/file_01.txt trong Ubuntu recovery; IP thuộc lượt này |

Recovery dùng lại VM dựa trên checkpoint trước sự cố, khôi phục vào đích/project mới và giữ kết quả D1. Bundle nguồn f46ff32 có sẵn trong VM recovery dùng để chạy Workstation; chứng cứ D2 được ghim riêng với project/commit D2. Đây không phải hệ điều hành cài mới. Kho sao lưu copy mount chỉ đọc và Restic chạy network=none; đường phục hồi offline không đi qua HTTPS backup-server.

## Kết quả đối chiếu

- Ready: HTTP 15/15, baseline FIM đủ 15 tên; dry-run không đổi dữ liệu.
- Incident/runtime: file_01..03 đổi tên; HTTP tên cũ 3×404, 12×200; 7 sự kiện FIM mới trong 22 bản ghi. Pause do bộ điều phối, không phải Wazuh tự diệt ransomware.
- RAM: PID 12959, COMM python, ARGS `python /app/simulator.py --apply`; Volatility PsList/PsAux offline đối chiếu thành công.
- PCAP: HTTP kiểm tra sau containment có nhãn D2, quan sát 404 và 200; không gọi là lưu lượng C2 hoặc lưu lượng tấn công ban đầu.
- Đĩa: sao chép riêng base và overlay khi cả ba VM tắt. Nguồn trước/sau/bản sao khớp; manifest 18 mục đạt. Đọc hai bản sao bằng pyqcow với set_parent trỏ rõ copied base, qua GPT/LVM/ext4 ở chế độ chỉ đọc; không boot/rebase/mount ảnh chứng cứ.
- Manifest guest được đọc từ ảnh: 21 mục incident và 22 mục runtime đạt; toàn bộ 15 nội dung gốc/active khớp mẫu và hash.
- Phục hồi: hash 15/15 và HTTP 15/15; script giữ dữ liệu gốc/D1 nguyên vẹn. Người vận hành xác nhận manifest 28/28 và xem file_01 trên Firefox; ảnh kết quả và hai ảnh checkpoint được lưu ngoài Git.

### Điểm khác giữa runtime và đĩa lạnh

Runtime đã thu xác nhận **3 file đổi tên** và kết thúc lúc 16:31:49.787757 UTC. Log Docker trên ảnh đĩa ghi thêm `file_04.txt` đổi tên lúc **16:33:53.816422 UTC**, sau đó `stopped`, signal 15, lúc **16:33:54.816687 UTC**. Vì vậy **đĩa lạnh có 4 file `.simlocked`**, còn 15 nội dung đều giữ nguyên.

Không sửa chứng cứ để ép khớp con số ba. Pause là tạm đóng băng, không phải kết thúc tiến trình. Lượt trình diễn sau cần thao tác kết thúc tác nhân đã kiểm chứng trước khi shutdown; không dùng shutdown/TERM để mặc định giữ nguyên trạng thái container đang Pause.

## Thời gian phục hồi

| Số đo | Giá trị | Phạm vi |
|---|---|---|
| Script recovery | 12.202 giây | Không gồm boot VM; không phải toàn bộ RTO |
| HTTP 15/15 hoàn tất | 2026-11-05T20:49:38.067233+00:00 | Từ ảnh terminal |
| HTTP 404 quan sát đầu tiên | 2026-11-05T15:50:17.929873+00:00 | Từ log runtime được đọc độc lập |
| Khoảng gián đoạn quan sát | 17960.137 giây | Gồm thu chứng cứ và chờ người vận hành; không phải benchmark |
| Tuổi snapshot tại sự cố | 561862.644 giây | Không phải RPO sản xuất được đo |

Ảnh không hiển thị thời gian riêng của bước Restic restore, nên không suy đoán giá trị này. Snapshot được chọn có ID đầy đủ `f54b7415a7237e538dc9733ad0f17ce09a305832592e10c86005b90dce56ab70`; bộ file thử không đổi nội dung giữa snapshot và sự cố.

## Bảo quản và bước chốt

Raw đang dùng nằm trên D, dưới `/run/media/ndam/New Volume/CSATTT-Lab/evidence-d2`:

- RAM: `ram-d2-20261105T155327Z-2XaTJM`, SHA-256 `c937b70d0913440d93667a10ca068b65027e035a6f9e1b7688ebe29b352595ce`.
- Chuỗi đĩa: `disk-d2-20261105T191232Z-dq21y8_e`; base SHA-256 `6ddf9b267d019fba40b755befcf44d90dec7536de639be239a5940b1a819484c`; overlay SHA-256 `9db5d3e1661e2acf0c76cf4e6de44aeba593cb34d3eac1dda174a3bb90467117`.
- RAM đã chuyển khỏi C có receipt tại `evidence-d2/ram-relocation-20261105T190808Z.json`. Metadata thu ban đầu giữ nguyên đường dẫn lịch sử.
- Bản cũ D1/A3 đã chuyển sang My Passport, archive `CSATTT-Archive/old-lab-20261105T180330Z-8iehaes0`; đối chiếu ARCHIVE.json để tìm vị trí mới. Các đường dẫn D1 trong biên bản cũ là đường dẫn lúc thu.

Không xóa/di chuyển checkpoint chung `checkpoint-d1-20261105T060137Z-eorcagzm/disk.qcow2`: các overlay recovery và replay còn phụ thuộc. Không xóa marker apply để chạy lại lượt cũ. Raw/screenshot/secret giữ ngoài Git.

Chuỗi chức năng demo tối thiểu D2 đã hoàn thành, gồm manifest và Firefox. Còn cần để biểu diễn gọn: gói quy trình/lệnh; kiểm thử tạo lại một lượt mới. Bước kết thúc tác nhân đã được xác nhận trong phép thử riêng ngày 12/11 (3 → 3 → 3, SHA-256 15/15). [Quy trình dừng và kiểm tra sau shutdown](../runbook-demo.md#7-dừng-simulator-và-kiểm-tra-sau-shutdown). SOC nhiều máy/Tailscale và phần mẫu thật không thuộc demo tối thiểu.
