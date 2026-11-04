# Demo tích hợp D1 — một người vận hành, giữ màn hình SOC

Người chuẩn bị, thao tác và review: Nhữ Duy Anh Minh. Trạng thái: đang chuẩn bị; chưa chạy hoặc nghiệm thu demo tích hợp. SOC là Wazuh hiện có trong VM; phối hợp nhiều máy/Tailscale để sau nếu còn thời gian.

## 1. Luồng sẽ trình bày

1. Một Workstation D1 phục vụ 15 URL file giả: HTTP 200, đúng nội dung.
2. Simulator đã nghiệm thu đổi tên đúng bản sao dữ liệu Workstation D1 đang đọc. Các URL tên cũ lần lượt trả 404; Wazuh quan sát tên cũ mất và tên mới xuất hiện.
3. Người vận hành nhận cảnh báo, khống chế, bảo quản RAM/log/PCAP/ảnh đĩa theo kế hoạch acquisition của lượt chạy.
4. Phục hồi snapshot đã chọn trên môi trường sạch; xác minh 15 tên, 15 SHA-256 và HTTP 15/15; ghi thời điểm phục hồi dịch vụ.

Đây là diễn tập ảnh hưởng khả dụng bằng đổi tên, không phải mã hóa hoặc chạy ransomware thật. FIM quan sát thay đổi file; hiện chưa tự phân loại hay ngăn chặn ransomware.

## 2. Phần được giữ và phần tạo mới

| Thành phần | D1 sử dụng |
|---|---|
| `runtime/sample_data` | Giữ nguyên 15 file gốc; không gắn vào container D1 |
| Bản sao dưới `runtime/fim-probe/sim33-...` | Tạo mới cho từng bundle; Workstation D1 và simulator cùng gắn tại `/lab/data` |
| Project `csatttn3` | Giữ nguyên Workstation nền, Wazuh và log/chứng cứ S1 |
| Project `csatttn3-d1-...` | Project riêng cho Workstation D1 và simulator; mạng incident mới vẫn internal, không publish cổng |
| Wazuh Manager | Nhìn bản sao qua bind chỉ đọc `/lab/fim-probe`; không cần đổi cấu hình hoặc agent mới |
| Đĩa backup | Vẫn tháo khỏi VM sự cố; phục hồi dùng bản sao kho trên môi trường sạch |

Project mới chỉ tách tên container/network và vòng đời dịch vụ; vẫn dùng chung kernel Ubuntu. Nó không thay thế cô lập VM.

## 3. Checkpoint chuẩn bị hiện tại

Trên Kali kiểm tra nhánh sạch và dung lượng thật của ổ chứa qcow2. Một RAM dump hiện khoảng 12 GiB; ảnh đĩa lạnh A3 chiếm khoảng 15,3 GiB vật lý. Cần dự trù cả tăng trưởng VM, môi trường phục hồi và ít nhất 15 GiB dự phòng. Chỗ trống trong Ubuntu không thay thế chỗ trống trên ổ D.

Kiểm thử nguồn trước khi commit:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
git diff --check
```

Xuất đúng commit và manifest vào ISO chỉ đọc như các lượt trước; không mở mạng/clipboard hoặc chia sẻ checkout với guest. Đưa nguồn vào bundle triển khai mới trong `~/csattt-lab/deploy`; `COMMIT.txt` nằm cạnh thư mục `source`.

Trong Ubuntu, sau khi A2 đã kiểm tra lại và ba dịch vụ Wazuh có sẵn đang chạy:

```bash
python3 scripts/prepare_demo.py
```

Helper kiểm tra Ubuntu VM/UUID, không có NIC phần cứng/default route, backup vắng mặt, guest còn ít nhất 15 GiB và trạng thái project Wazuh. Helper không thay đổi cấu hình libvirt; kiểm tra live/config, clipboard, USB và shared folder vẫn thực hiện từ Kali theo A2.

Helper tái sử dụng bộ kiểm tra/copy S1, giữ nguyên dữ liệu nguồn và tạo:

- `../copy.env`, `../copy.json`: nguồn và bản sao do helper S1 tạo.
- `../demo.env`: cả `LAB_DATA_DIR` và `LAB_SIM_DATA_DIR` trỏ cùng bản sao mới.
- `../demo.json`: project riêng, commit, đường dẫn FIM, UTC và SHA-256; trạng thái `prepared_only`.
- `../source.sha256`: manifest 15 file giả, dùng lại để đối chiếu phục hồi.

Các file trên nằm ngoài thư mục nguồn, mode 0600. Nếu đầu ra đã tồn tại hoặc dữ liệu không đúng mẫu, dừng và giữ nguyên để kiểm tra; không xóa/ghi đè để chạy lại. Helper không gọi start/create/up, không chạy dry-run hoặc apply.

Đầu ra mong đợi: `D1 PREP: OK`, tên project `csatttn3-d1-...`, thư mục active khác sample_data và đường dẫn FIM tương ứng. Dừng tại checkpoint này, lưu kết quả rồi mới chuẩn bị khởi động Workstation D1.

## 4. Các checkpoint tiếp theo, chưa thực hiện

1. Dùng `docker compose --project-name <project trong demo.json>` với `demo.env` và hai file Compose đã có. Đối chiếu config chỉ gồm Workstation/simulator, cùng mount bản sao; mạng internal, quyền và giới hạn giống S1. Chỉ dùng image có sẵn, không build/pull.
2. Tạo nhưng chưa start container để kiểm tra image/mount/quyền/network thực tế. Start Workstation D1, kiểm tra riêng đủ 15 URL và hash. Kiểm tra FIM đã ghi nhận đủ 15 tên baseline trong đúng thư mục, đọc cả log hiện tại/lưu trữ khi cần.
3. Dry-run simulator và đối chiếu cả nguồn/bản sao vẫn nguyên 15/15. Giữ container và log. Chưa apply khi một gate chưa đạt.
4. Chốt snapshot đầy đủ, manifest, môi trường phục hồi, mốc đo và cách dừng; chuẩn bị capture trước apply. Simulator hiện chạy khoảng 15 giây rồi tự thoát: muốn thu tiến trình đang sống hoặc dừng giữa lượt phải sắp xếp trước. Không gọi kết quả RAM probe A3 là RAM của simulator.
5. Apply đúng một lần, đo HTTP tên cũ bị lỗi và sự kiện FIM cùng lượt; ghi trạng thái khi khống chế. Root URL vẫn có thể trả 200 và container vẫn healthy dù 15 URL file bị 404.
6. Thu/phân tích chứng cứ của lượt này, giữ trạng thái đã đổi tên. Không đổi tên ngược để gọi là phục hồi. PCAP chỉ có HTTP đối chứng phải ghi rõ, không gọi là lưu lượng C2 của simulator.
7. Phục hồi trong môi trường sạch từ bản sao kho độc lập. Đích mới rỗng, đúng snapshot, 15 tên/hash và HTTP 15/15. Thời gian lệnh restore ghi riêng; thời gian phục hồi dịch vụ đo từ mốc ảnh hưởng đã thống nhất. RPO cần phiên bản/thời điểm dữ liệu và snapshot, không suy ra 0 chỉ từ hash khớp.

Chưa nghiệm thu checkpoint nào trên đây bằng chỉ kết quả unit test/Compose config. Mỗi lượt có UTC, commit/image, kết quả, SHA-256 và đường dẫn chứng cứ riêng; dữ liệu thô/secret ngoài Git.

Nguồn cơ chế project riêng: [Docker Compose project name và độ ưu tiên của `-p`](https://docs.docker.com/compose/how-tos/project-name/). Tham chiếu vận hành: [cô lập A2](runbook-co-lap.md), [simulator S1](runbook-simulator.md), [HTTPS backup](runbook-https-backup.md).
