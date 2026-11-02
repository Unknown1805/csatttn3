# Simulator đổi tên dữ liệu giả — Issue #33

Trạng thái: mã và cấu hình được chuẩn bị để kiểm tra. Chưa triển khai hoặc nghiệm thu simulator trong VM. Không dùng tài liệu này để kết luận đã thực hiện lượt sự cố.

## 1. Luồng và giới hạn

Simulator là container chạy một lần, dùng lại image Python `csatttn3/workstation:stage1` đang có. Nó chỉ nối `incident_net` internal, không publish cổng, không có Docker socket, secret hoặc backup. UID/GID 1000, root filesystem chỉ đọc, cap-drop ALL, no-new-privileges, giới hạn CPU/RAM/PID. Profile `incident` tách nó khỏi các lần up thông thường.

Mặc định là **dry-run**. CLI chỉ có `--apply`, không có lựa chọn quét đường dẫn tùy ý. Bên trong container đường dữ liệu cố định `/lab/data`; người vận hành chọn đúng bind mount đã duyệt.

Chỉ chấp nhận đúng 15 tên `file_01.txt` đến `file_15.txt`, nội dung 40 B/file khớp dữ liệu giả của Workstation. Directory/file symlink, hardlink, thư mục con, file thiếu/thừa, nội dung sai hoặc tên đích tồn tại đều bị từ chối trong preflight. Đọc có giới hạn kích thước và không theo symlink. Giữ directory descriptor và khóa flock trong lượt chạy.

Apply tạo `SIMULATION_NOTE.txt` với nhãn SAFE SIMULATION, rồi đổi từng tên thành `.simlocked`, cách nhau khoảng một giây. Nội dung không được mã hóa hoặc xóa. Đổi tên dùng `renameat2(RENAME_NOREPLACE)` của Linux để từ chối ghi đè cả khi tên đích xuất hiện sau kiểm tra. Phạm vi hệ điều hành là Linux/glibc và filesystem hỗ trợ cờ này; VM hiện dùng ext4.

Log JSON ra stdout có run ID, PID, UTC, kế hoạch và từng thao tác. SIGINT/SIGTERM yêu cầu dừng ở ranh giới bước; lượt đang dở được giữ nguyên, không tự rollback hoặc chạy lại. SIGKILL/mất điện không bảo đảm có bản ghi kết thúc. Khóa flock chỉ điều phối tiến trình hợp tác; môi trường thử phải có duy nhất simulator ghi tập dữ liệu. Đây không phải cơ chế bảo vệ trước root guest độc hại.

## 2. Kiểm tra nguồn trên Kali

Trong checkout, nhánh của Issue #33:

```bash
python3 -m unittest discover -s tests -p 'test_simulator.py' -v
docker compose --env-file lab/.env.simulator.example --profile incident \
  -f lab/compose.yaml -f lab/compose.incident.yaml config --quiet
git diff --check
```

Unit test chỉ tạo dữ liệu tạm; Compose config không khởi động container. Không lấy `.env.simulator.example` làm cấu hình triển khai thật: đường dẫn test trong ví dụ chưa được tạo.

Commit nguồn đã kiểm tra, xuất đúng commit và SHA-256 vào ISO như quy trình nền. Đưa vào bundle nguồn mới trong Ubuntu. VM tiếp tục không có NIC ngoài; không bật mạng để tải image. Không chạy các lệnh Docker ở mục sau trên Kali.

## 3. Chuẩn bị bản sao thử trong Ubuntu

Điều kiện: A2 đạt, backup vẫn tháo, Workstation và Wazuh đang chạy, Docker có sẵn image stage1; `sample_data` vẫn nguyên 15 file. Đứng trong thư mục `source` của bundle mới.

```bash
python3 scripts/prepare_simulator_test.py
```

Helper dùng kiểm tra Ubuntu VM/UID/GID hiện có, xác minh dữ liệu nguồn, tạo một thư mục `sim33-UTC-random` mới bên dưới `~/csattt-lab/runtime/fim-probe` và ghi 15 file giả. Workstation vẫn dùng `sample_data`; simulator thử chỉ dùng thư mục mới. Wazuh nhìn thư mục thử qua `/lab/fim-probe/...` chỉ đọc.

Helper tạo `../simulator-test.env` và `../simulator-test.json` ở ngoài checkout, từ chối ghi đè. Metadata có tên container apply dự kiến. Nếu lặp lại một lượt đã chạy, giữ nguyên trạng thái cũ và dùng bundle triển khai mới; không xóa thư mục cũ để vượt qua preflight.

Tạo file trong vùng FIM có thể sinh cảnh báo baseline; ghi rõ đây là thao tác chuẩn bị. Trước apply, xác nhận Wazuh đã thấy các file thử tại đường dẫn mới để phân biệt cảnh báo chuẩn bị với hành vi simulator.

## 4. Dry-run trước, chưa apply

Trong cùng thư mục `source` của Ubuntu:

```bash
set -o pipefail
task_compose() {
  sudo docker --host unix:///var/run/docker.sock compose \
    --env-file ../simulator-test.env --profile incident \
    -f lab/compose.yaml -f lab/compose.incident.yaml "$@"
}
task_compose config --quiet
task_compose run --rm --no-deps --pull never -T simulator \
  2>&1 | tee ../simulator-dry-run.log
```

Cần exit code 0, sự kiện `preflight_ok` rồi `dry_run_complete`, `changed_files=0`, đúng 15 kế hoạch đổi tên và chưa có note. Kiểm tra lại cả dữ liệu nguồn và bản sao thử. Dừng tại checkpoint này để người vận hành review trước apply. Không nhầm `--dry-run` của Docker Compose với dry-run mặc định bên trong chương trình simulator.

## 5. Apply trên bản sao thử sau khi dry-run đạt

Chưa được dùng đường dẫn `sample_data` cho giai đoạn này. Đối chiếu `LAB_SIM_DATA_DIR` trong env phải là thư mục thử dưới `fim-probe`. Không đưa mật khẩu hoặc toàn bộ môi trường Wazuh vào env này.

```bash
task_name="$(python3 -c 'import json; print(json.load(open("../simulator-test.json"))["container_name"])')"
task_compose run --no-deps --pull never -T --name "$task_name" simulator --apply \
  2>&1 | tee ../simulator-apply.log
```

Apply giữ container sau khi thoát để thu log/inspect chọn lọc; không xóa nó trước khi bảo quản chứng cứ. Không dùng cùng tên container cho lượt khác.

Đối chiếu:

- Có sự kiện `complete` với `renamed_files=15`, chỉ 15 tên `.simlocked` và note trong thư mục thử.
- Từng file sau đổi tên giữ đúng byte/hash nội dung gốc. Thư mục `sample_data` và HTTP Workstation vẫn 15/15 đúng vì chưa dùng dữ liệu chính cho mô phỏng.
- Wazuh có cảnh báo liên quan đúng `/lab/fim-probe/<tên-lượt-thử>/...`; đối chiếu tên, loại sự kiện và UTC với log simulator. Đổi tên có thể hiển thị thành added/deleted; không tự coi là đã phát hiện một họ ransomware hoặc đã diệt mã độc. Không giả định cứng tổng số cảnh báo khi chưa đọc log thực tế.
- Giữ log, metadata, exit code và hash ngoài Git. Không chạy helper A2 trên tập đã đổi tên rồi tự reset để làm phép kiểm tra xanh.

## 6. Dừng và kết thúc

Ctrl+C trong phiên run hoặc `docker stop --timeout 10 TEN_CONTAINER` yêu cầu simulator dừng; chương trình giữ trạng thái đang dở. Trên Kali, `virsh suspend CSATTT-QEMU` dừng toàn VM theo [runbook cô lập](runbook-co-lap.md); không dùng script tự Resume của lượt diễn tập A2 để tiếp tục một VM đang nghi vấn.

Không tự đổi tên ngược hoặc xóa note để tính là recovery. Giữ bản sao thử đã chạy cho đối chiếu; chưa áp dụng vào dữ liệu chính trước khi nghiệm thu các giới hạn và quan sát FIM. Lượt sự cố chính cần kế hoạch riêng về RAM/ảnh đĩa/log/PCAP, backup phù hợp, mốc mất khả dụng/phát hiện/phục hồi và môi trường sạch.

## Tài liệu cơ chế

- [Linux rename/renameat2 và RENAME_NOREPLACE](https://man7.org/linux/man-pages/man2/rename.2.html).
- [Python 3.13: thao tác đường dẫn và directory descriptor](https://docs.python.org/3.13/library/os.html).
- [Docker Compose run](https://docs.docker.com/reference/cli/docker/compose/run/).
