# Demo tích hợp D1 — một người vận hành, giữ màn hình SOC

Người chuẩn bị, thao tác và review: Nhữ Duy Anh Minh. **Lượt D1 đầu tiên ngày 05/11/2026 đã đạt chuỗi chức năng tích hợp.** SOC là Wazuh trong VM; phối hợp nhiều máy/Tailscale để sau nếu còn thời gian. [Biên bản D1](kiem-thu/demo-tich-hop-d1.md) lưu kết quả và giới hạn; D2 cũng đã phục hồi hash/HTTP 15/15; người vận hành xác nhận manifest 28/28 và Firefox. [Biên bản D2](kiem-thu/demo-chay-lai-d2.md) ghi riêng việc còn chờ và khác biệt sau shutdown.

## 1. Luồng đã thực hiện

1. Workstation D1 phục vụ 15 URL file giả: HTTP 200, đúng nội dung; FIM ghi nhận baseline 15 tên.
2. Simulator đổi tên đúng bản sao mà Workstation D1 đang phục vụ. Sau ba lần đổi tên, bộ điều phối Pause simulator; ba URL tên cũ trả 404, 12 URL còn lại trả 200.
3. Quan sát Wazuh: ba tên cũ mất, ba tên `.simlocked` xuất hiện và một note mô phỏng được tạo. Dashboard của đúng thư mục D1 có 22 hit gồm 15 baseline và 7 sự kiện mới.
4. Thu RAM khi simulator còn Paused, giữ VM hoạt động để thu log và PCAP HTTP kiểm tra sau cô lập có nhãn. Sau đó kết thúc simulator, shutdown VM và chụp QCOW2 khi VM tắt.
5. Đọc/phân tích bản sao chứng cứ; xác nhận tiến trình RAM, ba file đổi tên, 15 nội dung nguyên vẹn, FIM và HTTP 404/200.
6. Trên recovery VM riêng, đọc bản sao repository chỉ đọc, restore đúng snapshot vào đích mới và phục vụ chính dữ liệu phục hồi qua HTTP: hash 15/15, HTTP 15/15. Người vận hành đã kiểm tra manifest và xem file_01 trên Firefox.

Đây là diễn tập ảnh hưởng khả dụng bằng đổi tên, không mã hóa hoặc chạy ransomware thật. FIM quan sát thay đổi file. Việc Pause được điều phối sau ba lần đổi tên, chưa phải Wazuh tự phân loại/ngăn chặn ransomware.

## 2. Thành phần và dữ liệu

| Thành phần | D1 sử dụng |
|---|---|
| `runtime/sample_data` | 15 file gốc được giữ nguyên |
| Bản sao dưới `runtime/fim-probe/sim33-...` | Workstation D1 và simulator cùng gắn tại `/lab/data` |
| Project `csatttn3` | Workstation nền và ba dịch vụ Wazuh hiện có |
| Project `csatttn3-d1-8062e27c4236` | Workstation/simulator của lượt sự cố; mạng internal, không publish cổng |
| Wazuh Manager | Quan sát bản sao qua bind chỉ đọc `/lab/fim-probe` |
| `CSATTT-QEMU` | VM sự cố; không NIC ngoài/chia sẻ dữ liệu, backup gốc tháo rời |
| `CSATTT-RECOVERY-D1` | Overlay từ checkpoint trước sự cố và bản sao đĩa backup riêng; 2 vCPU, 3 GiB RAM |
| Restore worker | `network=none`, repository và mật khẩu bind chỉ đọc; chỉ đích `/restore` được ghi |
| Project `csatttn3-rfinal-cc6f134b55ce` | Workstation phục vụ thư mục thực sự được Restic phục hồi trên mạng internal |

Project Compose riêng tách tên/vòng đời dịch vụ, vẫn chung kernel Ubuntu. VM recovery dựa trên checkpoint đã kiểm tra trước sự cố, không phải hệ điều hành cài mới. Backup HTTPS được nghiệm thu nền; recovery D1 là đọc repository offline, không khởi động đường HTTPS backup.

## 3. Chuẩn bị và điều kiện trước mỗi lượt

- Trên Kali, kiểm tra nhánh và dung lượng thật của ổ chứa QCOW2. RAM dump khoảng 12 GiB, bản sao QCOW2 khoảng 15,4 GiB vật lý; giữ ít nhất 15 GiB dự phòng và tính cả tăng trưởng overlay. Không suy ra dung lượng ổ D từ `df` bên trong Ubuntu.
- Kiểm tra A2 ở live/config và trong guest: không NIC ngoài/default route; không chia sẻ thư mục/clipboard/truyền file/USB; backup vắng mặt; dịch vụ cần dùng hoạt động.
- Chỉ dùng image đã có. Xuất commit đầy đủ và SHA-256 vào ISO chỉ đọc; không chia sẻ checkout thật với VM sự cố.
- Chốt snapshot phục hồi bằng ID đầy đủ, kiểm tra kho/bản sao và diễn tập restore trước apply. Xác định nơi lưu chứng cứ, mốc đo và cách dừng.
- Mỗi lượt tạo bundle, bản sao dữ liệu, project và thư mục restore mới. Không ghi đè kết quả cũ hoặc xóa marker một lần để ép chạy lại.

Kiểm thử khi thay đổi mã nguồn:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
git diff --check
```

Trong nguồn đã xuất vào Ubuntu, `python3 scripts/prepare_demo.py` kiểm tra VM/dữ liệu/dịch vụ, tái sử dụng helper S1 và tạo `copy.env`, `copy.json`, `demo.env`, `demo.json`, `source.sha256` ở ngoài thư mục nguồn. `LAB_DATA_DIR` và `LAB_SIM_DATA_DIR` trỏ cùng bản sao mới. Helper này chỉ chuẩn bị dữ liệu; không gọi Docker start/apply.

`demo.json` có `prepared_only` phản ánh checkpoint chuẩn bị; kết quả apply và recovery được ghi trong biên bản/manifest riêng, không sửa metadata chuẩn bị để thay cho bằng chứng thực thi.

## 4. Các gate vận hành đã dùng

| Gate | Điều kiện đạt |
|---|---|
| Ready | Runtime image/mount/quyền/giới hạn/network đúng; HTTP 15/15; FIM đủ 15 tên; dry-run không đổi dữ liệu |
| Checkpoint và recovery thử | Checkpoint khi VM tắt khớp hash; recovery dùng overlay và backup copy riêng; restore thử vào đích mới đạt hash/HTTP 15/15 |
| Incident | Apply đúng một lần, Workstation/simulator cùng bản sao; Pause sau ba lần đổi tên; ba HTTP 404 và bảy sự kiện FIM đúng lượt |
| RAM | Thu khi simulator còn sống/Paused; Volatility đối chiếu PID và dòng lệnh; có manifest |
| Log và PCAP | Lưu JSON/FIM/log; PCAP có nhãn post-containment HTTP control, xác nhận 404 và 200 |
| Disk | Kết thúc simulator, shutdown; giữ cả hai VM tắt khi copy; nguồn trước/sau/bản sao cùng SHA-256, QCOW2 check đạt |
| Recovery | VM chính tắt; kiểm tra UUID/serial và cô lập recovery; repo mount chỉ đọc; snapshot đúng; đích mới; hash/HTTP 15/15 |

Luôn dùng **PID của đúng lượt đang chạy**, đã đối chiếu container và guest; PID 27840 chỉ thuộc lượt D1 ngày 05/11. Không dùng lại PID lịch sử cho lượt mới. Thu RAM trước khi kết thúc tiến trình; log/PCAP thu xong trước shutdown. Root URL hoặc trạng thái healthy không thay cho kiểm tra đủ các URL file.

Các gate ISO đã dùng được lưu ở workspace vận hành trên Kali, ngoài Git: `demo-d1-iso`, `demo-d1-ready`, `demo-d1-resume`, `demo-d1-incident`, `demo-d1-ram`, `demo-d1-evidence`, `demo-d1-disk`, `demo-d1-recovery-final` (hậu tố từng artifact ghi trong biên bản). Đây là các artifact cho lượt cụ thể, chưa phải một launcher tái lập mọi lượt từ checkout. Một số artifact có phụ thuộc module/đường dẫn của artifact trước; giữ nguyên bộ workspace và checkpoint hiện tại.

## 5. Kết quả recovery và thời gian

Lượt đã nghiệm thu có `result.json` tại:

```text
/home/csattt3/csattt-lab/runtime/recovery-final-20261105T131346Z-jwrfr735
```

Từ chính thư mục đó có thể đọc biên bản và kiểm tra manifest:

```bash
cat result.json
sha256sum -c SHA256SUMS
```

Mở URL `recovered_http_url` trong Firefox của Ubuntu recovery. IP container được ghi theo lượt, không dùng IP cũ để kết luận dịch vụ lượt mới. Dòng `Not Secure` của Workstation HTTP phù hợp dịch vụ dữ liệu giả trên mạng internal; đây không phải kênh HTTPS của kho backup.

- Bước Restic restore: **1.163 giây**.
- Script kiểm tra kho, restore, hash và HTTP: **12.179 giây**, không gồm khởi động VM.
- Khoảng từ HTTP 404 quan sát đầu tiên đến đủ HTTP 15/15: **10537.530 giây**, gồm thời gian thu chứng cứ/chờ thao tác, không phải benchmark phục hồi lặp lại.
- Tuổi snapshot tại mốc 404: **541945.401 giây**. Đây là tuổi bản sao, chưa phải RPO sản xuất được đo. Bộ 15 file giả không mất nội dung đã đối chiếu; không suy ra RPO = 0 cho dữ liệu khác.

## 6. Chuẩn bị lượt trình bày lại

Giữ VM chính tắt, không boot ảnh đĩa chứng cứ; giữ recovery và dữ liệu phục hồi để quan sát. Recovery overlay phụ thuộc checkpoint trước sự cố: không di chuyển/xóa/sửa checkpoint hoặc commit overlay vào base.

D2 đã lặp chuỗi chức năng trên bản chuẩn bị mới, đạt recovery và được người vận hành xác nhận manifest 28/28 cùng trang Firefox. Còn phải đóng gói thao tác ngắn cho một lượt mới, giữ data/project/đích restore riêng và thử liên tục từ Ready đến Recovery. Giữ màn hình SOC, đo thời gian theo cùng mốc, ghi đầy đủ hash và thử cách reset mà không ghi đè chứng cứ. Chỉ sau khi lượt này đạt mới xác nhận khả năng chạy lại demo từ đầu.

Tham chiếu: [cô lập A2](runbook-co-lap.md), [simulator S1](runbook-simulator.md), [HTTPS backup](runbook-https-backup.md), [biên bản D1](kiem-thu/demo-tich-hop-d1.md). Phần SOC nhiều máy/Tailscale giữ cho giai đoạn sau.

## 7. Dừng simulator và kiểm tra sau shutdown

Trong D2, log runtime thu lúc simulator Pause ghi 3 lần đổi tên; đĩa sau shutdown có lần đổi tên thứ tư trước khi tiến trình nhận SIGTERM và thoát. Dữ liệu nội dung vẫn 15/15 nguyên vẹn. Không khẳng định shutdown mặc định bảo toàn trạng thái Pause hoặc sửa chứng cứ để bỏ lần đổi tên thứ tư. Xem mốc cụ thể trong [biên bản D2](kiem-thu/demo-chay-lai-d2.md).

Phép thử ngày 12/11/2026 trong VM riêng `CSATTT-STOP-TEST` dùng Docker Engine 29.1.3 và 15 file giả. Sau Pause, người vận hành giữ VM chạy để ghi trạng thái, log và SHA-256. Bộ thử gửi SIGKILL tới đúng container đang Pause và xác nhận container thoát với mã 137. Số file đổi tên giữ nguyên ở cả ba mốc sau Pause, sau khi container thoát và sau shutdown (**3 → 3 → 3**). Đọc ổ ảo ở chế độ chỉ đọc xác nhận log Docker, manifest 7/7 và SHA-256 nội dung 15/15.

Với một lượt mới, hoàn tất thu RAM, log và PCAP trước khi dừng. Trong Ubuntu, lấy ID đầy đủ của simulator từ biên bản đúng lượt. Kiểm tra ID thuộc project của lượt, service là simulator và trạng thái là Paused. Ghi danh sách tên cùng SHA-256 của bản sao thử trước khi chạy hai lệnh sau với `ID_SIM` là ID đã xác nhận.

```bash
sudo docker --host unix:///var/run/docker.sock kill --signal=KILL "$ID_SIM"
sudo docker --host unix:///var/run/docker.sock inspect "$ID_SIM" --format 'Status={{.State.Status}} Running={{.State.Running}} Paused={{.State.Paused}} ExitCode={{.State.ExitCode}}'
```

Chỉ shutdown khi thấy `Status=exited Running=false Paused=false ExitCode=137` và đối chiếu lại tên, SHA-256 cùng log đều khớp trước khi dừng. Sau shutdown, giữ VM tắt và đối chiếu ảnh đĩa với kết quả runtime của đúng lượt.

Phép thử xác nhận bước dừng riêng. Launcher, thao tác tạo lượt mới và diễn tập live từ Ready đến Recovery với bước dừng này vẫn cần nghiệm thu.
