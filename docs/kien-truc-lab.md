# Kiến trúc lab — Pháp chứng số và ứng cứu sự cố ransomware

Liên quan: Issue #6.
Trạng thái: Đã triển khai nền lab bằng QEMU/KVM và Docker; đã kiểm thử backup/restore. Phần giám sát phát hiện và chế độ cô lập cho phiên sự cố chưa được nghiệm thu.

## 1. Mục tiêu

Xây dựng môi trường mô phỏng sự cố ransomware để thực hành phát hiện, cô lập, thu chứng cứ, phân tích diễn biến và khôi phục dữ liệu từ bản sao lưu.

Tài liệu này mô tả nền Docker và luồng demo có kiểm soát. Simulator dự kiến chỉ tác động danh sách file giả đã duyệt bằng cách đổi tên, tạo thông báo hoặc kiểm thử mã hóa; hiện chưa triển khai simulator. Giữ manifest và bản sao lưu sạch trước thử nghiệm. Không phát triển tự lây lan, đánh cắp dữ liệu hoặc tác động dữ liệu cá nhân.

Linux.Encoder.1 là case nghiên cứu mẫu thật dự kiến trên máy phụ, cần thiết kế lab và runbook riêng trước thực nghiệm. Chưa xác minh file mẫu hoặc SHA-256 và chưa thực thi mẫu thật. Nhánh nghiên cứu này phải kiểm chứng cô lập, giám sát, nút dừng và khả năng phục hồi; không mang mẫu thật hoặc VM đã nhiễm sang máy chính để chạy demo. Phạm vi chung được ghi trong README.

## 2. Mô hình tổng thể

    Máy thật: Kali Linux
    ├── VS Code và repository trên ổ Windows dùng chung
    └── Máy ảo Linux dành riêng cho lab
        ├── Docker: mạng incident_net
        │   ├── workstation
        │   └── simulator
        ├── Docker: mạng backup_net
        │   ├── backup-worker hoặc restore-worker
        │   └── backup-server
        └── Công cụ tin cậy thu log, PCAP, RAM và ảnh đĩa

Các thành phần chạy theo từng giai đoạn; không khởi động tất cả cùng lúc.

| Thành phần | Nhiệm vụ | Mạng |
|---|---|---|
| workstation | Tạo, sử dụng dữ liệu giả và cung cấp phép kiểm tra khả dụng | incident_net |
| simulator (chưa triển khai) | Thực hiện kịch bản mô phỏng đã duyệt trên dữ liệu giả | incident_net |
| backup-worker | Đọc dữ liệu nguồn để sao lưu bằng Restic | backup_net |
| backup-server | Cung cấp REST backend và lưu repository sao lưu | backup_net |
| restore-worker | Khôi phục bản sao lưu vào volume mới trong môi trường sạch | backup_net |

Công cụ thu chứng cứ chạy dưới quyền người vận hành trong VM. Simulator không được nhận các quyền thu chứng cứ này.

## 3. Ranh giới cô lập

### Máy thật và máy ảo

- Mã nguồn tiếp tục được sửa bằng VS Code tại repository trên ổ Windows dùng chung.
- Đưa bản source đã review vào VM bằng bản xuất có commit ID và SHA-256; có thể dùng ISO chỉ đọc rồi tháo sau khi chép.
- Khi diễn tập: tắt shared folders, shared clipboard và drag-and-drop; ngắt card mạng ảo nối VM ra ngoài.
- Chỉ sử dụng NAT tạm thời trong giai đoạn chuẩn bị công cụ và image; kiểm tra lại trạng thái trước phiên sự cố.

### Các container

- incident_net và backup_net đều cấu hình internal.
- workstation và simulator chỉ tham gia incident_net.
- Không có container làm cầu nối giữa hai mạng.
- Không publish cổng ra máy thật; không dùng host networking, host PID, privileged hoặc Docker socket.
- Simulator chạy bằng tài khoản không root, bỏ capability không cần thiết, dùng root filesystem chỉ đọc và có giới hạn tài nguyên.
- Simulator chỉ được ghi volume dữ liệu giả; không nhận volume hoặc thông tin xác thực sao lưu/chứng cứ.

Mạng internal hạn chế kết nối ra ngoài nhưng vẫn có thể giao tiếp với gateway và dịch vụ phù hợp của Docker host. Trong thiết kế này, Docker host là VM Linux; phải kiểm tra cả dịch vụ trên VM. [Docker internal networking](https://docs.docker.com/reference/cli/docker/network/create/#network-internal-mode---internal)

## 4. Dữ liệu và quyền truy cập

| Vùng dữ liệu | Nơi lưu dự kiến | Quyền truy cập |
|---|---|---|
| sample_data | Filesystem trên đĩa dữ liệu lab của VM | workstation và simulator đọc/ghi; backup-worker chỉ đọc |
| backup_repo | Filesystem trên đĩa ảo sao lưu riêng, có thể tháo khỏi VM | Chỉ backup-server được mount repository |
| restored_data | Volume mới trong môi trường sạch | restore-worker ghi; ứng dụng sạch kiểm tra sử dụng |
| evidence | Vùng chứng cứ riêng | Người vận hành thu và bảo quản; simulator không được mount |

Named volume mặc định nằm trên Docker host, không tự nằm trên đĩa ảo tháo rời. Khi triển khai phải xác định ánh xạ volume với filesystem, UUID và mountpoint thực tế. [Docker volumes](https://docs.docker.com/engine/storage/volumes/)

Trước khi chạy backup-server phải xác nhận đúng đĩa sao lưu đã được mount. Nếu đĩa vắng mặt, quy trình phải dừng để tránh ghi nhầm repository xuống đĩa hệ thống.

## 5. Trình tự diễn tập

1. Chuẩn bị VM, công cụ, image và cấu hình; ghi lại phiên bản.
2. Tạo dữ liệu giả, danh mục file, SHA-256 và các mốc thời gian UTC.
3. Tạm dừng tiến trình ghi dữ liệu; thực hiện backup và thử restore một bộ nhỏ.
4. Dừng thành phần sao lưu, giải phóng mount, unmount thành công rồi tháo đĩa sao lưu khỏi VM. Nếu không tháo nóng an toàn được, tắt VM để tháo trước phiên sự cố.
5. Kiểm tra cô lập; bắt đầu ghi log và thu PCAP.
6. Chạy mô phỏng; ghi thời điểm mất khả dụng, phát hiện và xử lí.
7. Thu RAM trước khi dừng tiến trình hoặc tắt VM; sau đó bảo toàn log, PCAP và ảnh đĩa.
8. Giữ nguyên bản chứng cứ; chuẩn bị VM sạch từ bản gốc đã kiểm tra.
9. Chỉ gắn lại bản sao lưu vào môi trường sạch; restore vào volume mới.
10. Đối chiếu dữ liệu, kiểm tra sử dụng và tính RTO/RPO từ các mốc thực đo.

Không ghi đè dữ liệu của phiên sự cố trong quá trình restore. Đổi tên file trở lại hoặc reset VM không được tính là khôi phục từ backup.

## 6. Phạm vi chứng cứ

- RAM: RAM của toàn VM, sau đó xác định các tiến trình liên quan đến lab.
- Ảnh đĩa: phải chứa filesystem thực sự lưu sample_data và dấu vết cần phân tích.
- Log: nhật ký hệ thống, container và các thao tác của người vận hành.
- PCAP: thu trên interface/bridge tương ứng với incident_net.
- Mỗi chứng cứ có mã, nguồn, người thu, thời gian UTC, công cụ và SHA-256; phân tích trên bản sao.

Volatility dùng để phân tích RAM. Với Linux, symbol table phải khớp chính xác kernel banner của ảnh RAM; cần thử khả năng thu và phân tích sớm. [Volatility symbol tables](https://volatility3.readthedocs.io/en/stable/symbol-tables.html)

Nếu simulator không phát sinh lưu lượng mạng, PCAP ít hoặc không có lưu lượng ứng dụng là kết quả hợp lệ. Lưu lượng HTTP vô hại dùng để kiểm tra đường thu phải được ghi nhãn riêng.

## 7. Các kiểm tra phải thực hiện khi triển khai

- [ ] VM đã ngắt kết nối ra ngoài và tắt các tính năng chia sẻ với máy thật.
- [ ] Container chỉ tham gia đúng mạng; không có cổng publish hoặc quyền ngoài thiết kế.
- [ ] Simulator không truy cập được repository sao lưu và vùng chứng cứ.
- [ ] Đĩa sao lưu đã thực sự được tháo trước phiên sự cố.
- [ ] Thu được RAM và phân tích được một tiến trình thử nghiệm đã biết.
- [ ] Đọc được ảnh đĩa chứa dữ liệu mẫu.
- [ ] Backup và restore bộ dữ liệu nhỏ thành công, đối chiếu được danh mục và SHA-256.
- [ ] Mỗi kết quả có bằng chứng kiểm tra và thời điểm thực hiện.

Kiểm tra cú pháp Compose thành công chỉ xác nhận cấu hình được công cụ chấp nhận; chưa chứng minh hệ thống chạy đúng hoặc cô lập đúng.

## 8. Trạng thái triển khai và các mục còn phải kiểm chứng

- VM chính sử dụng QEMU/KVM qua libvirt, tên CSATTT-QEMU.
- Ubuntu 24.04.5 LTS; 6 vCPU, khoảng 8 GiB RAM.
- Đĩa hệ điều hành vda dung lượng 50 GiB; root LV khoảng 48 GiB.
- Đã thử thu RAM và phân tích được tiến trình kiểm chứng bằng Volatility.
- Đã backup 15 file, tổng 600 B; kiểm tra kho thành công; restore khớp 15/15 SHA-256.
- Backup-server đã dừng; đĩa backup đã tháo khỏi cấu hình VM đang chạy và lần khởi động sau.
- Còn phải triển khai giám sát phát hiện, kiểm chứng cô lập và thực hiện lượt sự cố.

Trước lượt sự cố, phải nghiệm thu phần giám sát, cô lập, thu ảnh đĩa và khôi phục trong môi trường sạch.
