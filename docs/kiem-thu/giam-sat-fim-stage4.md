# Biên bản kiểm thử giám sát file bằng Wazuh — giai đoạn 4

Ngày thực hiện: 02/11/2026. Người vận hành: Nhữ Duy Anh Minh (@Unknown1805).

Trạng thái: **ĐẠT phạm vi kiểm thử FIM cơ bản với năm ca vô hại**:
tạo, sửa, đổi tên, đối chứng chỉ đọc và xóa file thử.
Biên bản tổng hợp đầu ra và ảnh người vận hành đã gửi; không thay thế việc kiểm tra gói chứng cứ gốc.

## 1. Môi trường và nguồn triển khai

- VM CSATTT-QEMU, QEMU/KVM trên Kali; Ubuntu 24.04.5 LTS, kernel 6.8.0-147-generic.
- Cấu hình VM đã tăng lên 6 vCPU, RAM 12 GiB, vda 70 GiB, root LV khoảng 68 GiB.
- Ba image Wazuh 4.14.9 đã cố định digest trong Compose: Manager, Indexer và Dashboard.
- Commit đã chuyển vào VM: `78806db2b2107c53ba5ca88e980ab0858f0a0977`.
- Nguồn đang dùng trong VM: `/home/csattt3/csattt-lab/deploy/wazuh-78806db2b210-hMfsfE/source`.
- Mạng `csatttn3_monitoring_net` internal; Manager đọc `/lab/data` và `/lab/fim-probe` qua bind mount chỉ đọc.
- File thử trên Ubuntu nằm trong `/home/csattt3/csattt-lab/runtime/fim-probe`, tách khỏi 15 file nền.
- Không dùng mẫu độc hại; active response đang tắt.

Các thay đổi bỏ yêu cầu publish cổng và cập nhật tài liệu sau lượt thử là thay đổi
nguồn tiếp theo; chưa được coi là đã áp dụng vào VM chỉ vì đã có trong Git.

## 2. Truy cập và khởi động

- Đã thấy HostConfig yêu cầu `127.0.0.1:8443 → 5601` nhưng ActualPorts là null;
  truy cập loopback bị từ chối khi Dashboard chỉ nối mạng internal.
- Đã kiểm tra trực tiếp IP container bằng curl `--connect-to`, giữ xác minh CA/tên chứng chỉ.
- Sau khởi động lại, Dashboard ghi ECONNREFUSED tới Indexer lúc 13:49:36 UTC;
  Indexer chuyển GREEN lúc 13:49:40 UTC và Dashboard phục vụ HTTPS lúc 13:49:42 UTC.
- Curl sau đó trả 302 với CA của lab, không dùng `-k`.
- Người vận hành đã ánh xạ `172.20.0.4 wazuh.dashboard` trong `/etc/hosts` của Ubuntu,
  nhập CA public vào Firefox và xác nhận đăng nhập admin tại `https://wazuh.dashboard:5601`.
- Không thêm mạng có đường ra ngoài cho các container để mở Dashboard.
- API Manager dùng cấu hình HTTPS của image; chưa nghiệm thu riêng việc Dashboard xác minh danh tính API.

## 3. Kết quả FIM từ log Manager

Tất cả cảnh báo dưới đây có agent `000` (`wazuh.manager`) và mode `realtime`.
Thời gian là timestamp UTC của cảnh báo, không phải thời gian thao tác hoặc độ trễ phát hiện.

| Ca thử | Thời gian cảnh báo UTC | Rule / sự kiện | ID bản ghi | Kết quả đã quan sát |
|---|---|---|---|---|
| Tạo `fim-demo-01.txt` | 14:09:11.956 | 554 / added | `1793628551.241` | File 34 B; log và ảnh Dashboard cùng ID |
| Sửa nội dung | 14:15:27.804 | 550 / modified | `1793628927.888` | 34 → 58 B; hash cũ khớp bản ghi tạo |
| Đổi tên: xuất hiện `fim-demo-01-renamed.txt` | 14:19:45.946 | 554 / added | `1793629185.2085` | 58 B, giữ hash và inode |
| Đổi tên: mất `fim-demo-01.txt` | 14:19:45.946 | 553 / deleted | `1793629185.2741` | Cùng hash và inode với tên mới |
| Xóa `fim-demo-01-renamed.txt` | 14:32:18.845 | 553 / deleted | `1793629938.3387` | Đúng tên mới; hash trùng trước xóa |

SHA-256 file sau tạo:

```text
1826fe88230300482de23a4e3a0d438df9156678544edcc0ba484c80b5bc5260
```

SHA-256 sau sửa, cũng là hash giữ nguyên qua đổi tên và ghi trong cảnh báo xóa:

```text
8ae77ffac8d3cb84e45fbf5ba59168a5c6a2ee19f2ac55068963e61a80032fd0
```

Inode trong các bản ghi là `1615019`. Không diễn giải hai cảnh báo đổi tên thành
hai thao tác xóa/tạo nội dung độc lập; đây là cách FIM biểu diễn thao tác đã thực hiện.

## 4. Đối chứng chỉ đọc

- File đối chứng: `fim-demo-01-renamed.txt`, 58 B, hash sau sửa ở trên.
- Đầu ra người vận hành đã gửi: `CONTENT UNCHANGED: OK` và hash không đổi.
- Log trích cho file chỉ có bản ghi added cũ lúc 14:19:45.946 UTC.
- Người vận hành đã gửi `start.utc`: `2026-11-02T14:25:27+00:00` và
  `end.utc`: `2026-11-02T14:26:27+00:00`; chênh lệch hai mốc UTC đúng 60 giây.
- Kết luận trong cửa sổ trên: nội dung không đổi và log đã trích không có sự kiện mới
  cho file đối chứng. Không suy ra việc chỉ đọc sẽ không bao giờ tạo cảnh báo ở cấu hình khác.
- Thư mục lưu: `/home/csattt3/csattt-lab/setup/fim-readonly-z0aEyA`.

## 5. Bảo quản chứng cứ và đối chiếu Dashboard

- File xuất: `/home/csattt3/csattt-lab/setup/fim-acceptance-dmFTlR/fim-events.jsonl`.
- Danh mục hash: cùng thư mục, file `SHA256SUMS`.
- Người vận hành đã gửi kết quả `fim-events.jsonl: OK` và giá trị SHA-256 dưới đây;
  chưa có phép kiểm tra độc lập trên bản chuyển giao:

```text
523b8eecceb136bb5a64c251b25b4691369f4fa09692737d1c8c5c17384251c2  fim-events.jsonl
```

- Kiểm tra lại thư mục `sample_data` đã trả `BASELINE 15/15: OK`: đúng danh sách
  15 file thường, không symlink/file thừa và từng file khớp byte nội dung gốc.
- Ảnh Dashboard ban đầu chỉ có hai bản ghi thêm file khi bật chip
  `rule.level: 0 to 6`. Rule 554 có level 5, còn rule 550/553 trong log có level 7.
- Sau khi người vận hành đổi phạm vi thành `rule.level: 1 to 10` và Refresh,
  ảnh Dashboard hiển thị `5 hits`: hai added, một modified và hai deleted.
  Timestamp, đường dẫn và loại sự kiện khớp cả năm bản ghi log trong mục 3.
- Ảnh do người vận hành gửi đã được giữ nguyên byte, lưu ngoài repository tại
  `/home/ndam/Documents/ChatGPT/CSATTT/outputs/wazuh-acceptance-20261102-nte_6ldu/evidence`.
  Đây là nơi bảo quản ảnh trên Kali, khác nơi lưu log gốc trong Ubuntu.

| Ảnh | SHA-256 |
|---|---|
| `dashboard-create-details.png` | `b3b127cada4282e6d37677a0fce2b3c4e35e773b7b21c972c659df6a468ce179` |
| `dashboard-fim-5-events.png` | `4df3ae7b516baf907fe1039be42a7e5b0c0e2134b5fca74137d1bfcf85374477` |

- Không đưa log thô, repo backup, mật khẩu hoặc private key vào Git.

Danh mục nghiệm thu:

- [x] Đọc hai mốc UTC đối chứng, chênh lệch đúng 60 giây.
- [x] Kiểm tra lại đúng 15 file nền, không file thừa và đúng nội dung gốc.
- [x] Trên Dashboard đối chiếu đủ năm bản ghi theo timestamp, đường dẫn và loại sự kiện;
  rule ID đối chiếu từ log Manager. Bộ lọc mức độ sau cùng là level 1–10.
- [x] Bổ sung giá trị hash file xuất đã nhận từ người vận hành.
- [x] Lưu ảnh đối chiếu đủ bản ghi, hash ảnh và nơi bảo quản vào biên bản.

## 6. Giới hạn kết luận

Kết quả xác nhận năm ca kiểm thử trong phạm vi trên đạt: Manager phát hiện các
thao tác tạo/sửa/đổi tên/xóa đã thử và năm cảnh báo tương ứng được hiển thị trên Dashboard;
đối chứng chỉ đọc không đổi hash hoặc sinh sự kiện mới trong 60 giây quan sát.
Luồng Manager → Indexer → Dashboard đã được đối chiếu bằng log và ảnh kết quả.

Không dùng chênh lệch thời gian giữa các ca làm độ trễ phát hiện.
Chưa đo độ trễ theo từng thao tác, chưa đo RTO/RPO, chưa thử simulator hoặc mẫu thật,
chưa chứng minh loại bỏ mã độc hoặc cô lập hoàn chỉnh cho phiên sự cố.
Log cùng nằm trong VM nên chưa phải nguồn chứng cứ độc lập chống sửa bởi root VM.
