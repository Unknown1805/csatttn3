# Biên bản thu và đọc chứng cứ nền A3

- Ngày nghiệm thu: 04/11/2026. Các mốc bên dưới dùng UTC.
- Người vận hành: Nhữ Duy Anh Minh (@Unknown1805).
- Nguồn lab: develop tại be6d81cd088b6856d097d287b2d3c73cbc1c9323; VM CSATTT-QEMU.
- Phạm vi: kiểm chứng đường thu RAM, PCAP và ảnh đĩa; đọc lại chứng cứ của phép thử vô hại và S1 đã lưu.
- Chưa thực hiện lượt sự cố chính, tiêu diệt mã độc hoặc phục hồi HTTP/RTO/RPO của lab tích hợp.

## 1. Môi trường và điều kiện trước thu

Kali là máy thật. Ubuntu 24.04.5 LTS, kernel 6.8.0-147-generic chạy trong QEMU/KVM; VM có 6 vCPU, 12 GiB RAM, đĩa hệ thống vda 70 GiB. UUID VM: bd0eab21-9089-4489-a703-b7771e210d5e.

Đã chạy lại kiểm tra A2 sau reboot: không NIC phần cứng trong guest, không default route; đĩa backup vắng mặt; 15 file gốc đúng mẫu. Bốn dịch vụ Workstation/Wazuh đang chạy; HTTP 15/15 và Dashboard HTTPS 302 đạt. Những kiểm tra này không phải bảo đảm tuyệt đối về khả năng chống VM escape.

## 2. RAM — tiến trình kiểm chứng đã biết

- Gói RAM: ram-a3-20261104T060312Z-QCucAl.
- Định dạng: ELF 64-bit core x86-64; kích thước 12.893.492.595 byte.
- Bắt đầu dump: 2026-11-04T06:03:12Z; kết thúc: 2026-11-04T06:04:19Z.
- Thời lượng bước dump: 67 giây; không phải RTO.
- Công cụ thu: virsh dump CSATTT-QEMU --memory-only --format elf --verbose.
- Volatility 3 phiên bản 2.28.2, linux.pslist.PsList, chạy offline với ISF phù hợp kernel.
- Đã nhận đúng PID 6309, COMM csattt-a3, UID/GID 1000. Gói chuẩn bị được đọc từ ảnh đĩa cũng ghi đúng PID và tên này.
- Thời hạn probe theo guest: 2026-11-04T06:32:07.275727Z. Lượt dump thành công nằm trước hạn.
- Manifest gói RAM khớp 7/7 file; pslist trả mã 0, có 303 PID riêng biệt.

SHA-256 ram.elf:

    15e1be55486da7bfaa39e5745b0a15729dcd017f3aec92c74afc03dacd2f86e6

ISF được lấy từ bản đã cache của bộ sưu tập Abyss-W4tcher/volatility3-symbols, không phải symbol do nhóm tự tạo. File Ubuntu_6.8.0-147-generic_6.8.0-147.147_amd64.json.xz có SHA-256:

    3b12e65300e15676117ce6c1f10909f4babaff37cf4f7e3718abf1fdedd94c9a

Lượt cũ ngày 03/11/2026 bắt đầu sau khi probe PID 8510 đã hết hạn. Ảnh cũ được giữ riêng, không dùng để kết luận đã nhận đúng probe của A3.

## 3. PCAP — HTTP control có nhãn

- Gói guest: pcap-a3-20261104T062313Z-u1u8h1gf.
- Thời gian: 2026-11-04T06:23:13.497057Z đến 2026-11-04T06:23:23.629216Z.
- Interface: br-868936e565e4; bộ lọc: host 172.18.0.2 and tcp port 8080.
- Bắt bằng tcpdump trong 10 giây, gửi một GET /file_01.txt từ Ubuntu tới Workstation.
- User-Agent: CSATTT-A3-HARMLESS-PCAP-CONTROL/pcap-a3-20261104T062313Z-u1u8h1gf.
- Trả HTTP/1.0 200 OK, Content-Length 40 và đúng nội dung dữ liệu giả.
- Mã 124 là timeout kết thúc cửa sổ bắt theo thiết kế; PCAP sau đó được mở lại và xác minh nội dung.
- Gói PCAP đọc từ ảnh đĩa khớp manifest 10/10 file. Đã mở PCAP độc lập bằng tcpdump trên Kali, kiểm tra lại nhãn yêu cầu, HTTP 200 và nội dung trả về. Khi tổng hợp timeline dùng TZ=UTC; không trộn giờ hiển thị địa phương với mốc UTC.

SHA-256 http-control.pcap:

    b7b5098d078ffaf36732b6c0595f900c3a9c72bf6f12f0433595454929a4ceda

Đây là lưu lượng kiểm chứng đường thu, không phải lưu lượng simulator, C2 hoặc mã độc.

## 4. Ảnh đĩa — bản sao QCOW2 sau shutdown

Sau khi RAM và PCAP đã lưu, người vận hành shutdown Ubuntu bình thường; libvirt xác nhận shut off. Không dùng forced destroy.

- Gói: disk-a3-20261104T070230Z-u5zy3648.
- Bắt đầu: 2026-11-04T07:02:30.128926Z; kết thúc: 2026-11-04T07:07:02.730654Z.
- Đĩa ảo logic: 70 GiB; file QCOW2: 53.698.756.608 byte. Bản sao chiếm thực tế 16.406.929.408 byte nhờ vùng sparse.
- Dùng GNU cp với --sparse=always, --reflink=never, --update=none-fail; đích là thư mục mới, không ghi đè ảnh cũ.
- SHA-256 nguồn trước = nguồn sau = bản sao. qemu-img check không sửa chữa báo check-errors = 0.
- Manifest gói đĩa khớp 10/10 file. Sau đọc/phân tích, hash ảnh đĩa và metadata nguồn vẫn không đổi.
- Đây là bản sao giữ nguyên từng byte của container QCOW2, không phải raw disk image hoặc snapshot RAM/đĩa đồng thời. Log ghi khi shutdown là một phần trạng thái ảnh này.

SHA-256 disk.qcow2:

    e03e4134246f9eafe211402e6b33ce59ba5b253c834be559dbf7c502d3ed3b00

## 5. Đọc và đối chiếu dữ liệu trong ảnh

Không khởi động hoặc mount ảnh chứng cứ. Dùng các thư viện có sẵn: pyqcow 20240308 đọc QCOW2 ở mode r; pyvslvm 20240504 đọc LVM qua file-like view chỉ đọc; pytsk3 đọc filesystem. Không kích hoạt VG của guest trong LVM máy thật.

Đã xác định GPT với PV bắt đầu sector 4.198.400, sector 512 byte; VG ubuntu-vg, LV ubuntu-lv khoảng 68 GiB; filesystem ext4, block 4.096 byte. Hostname đọc được là csattt3.

Chỉ trích xuất các đường dẫn lab đã chọn: gói chuẩn bị RAM, gói PCAP, kết quả apply S1, sample_data và bản sao thử S1. Tổng 70 file, 194.232 byte; ghi kèm đường dẫn guest, inode, kích thước, mtime/ctime và hash của từng file. Không trích xuất thư mục secrets.

| Kiểm tra | Kết quả |
|---|---|
| Manifest chuẩn bị RAM lấy từ đĩa | 12/12 khớp |
| Manifest gói PCAP lấy từ đĩa | 10/10 khớp |
| Manifest kết quả S1 lấy từ đĩa | 14/14 khớp |
| sample_data | Đúng 15 file, tổng 600 B, byte/hash đúng mẫu |
| Bản sao thử S1 | 15 file .simlocked + SIMULATION_NOTE.txt |
| Nội dung sau đổi tên | 15/15 khớp dữ liệu gốc và renamed-sha256.json đã lưu |
| FIM của S1 | Đủ 31 cặp đường dẫn/sự kiện: mất 15 tên cũ, thêm 15 tên mới và 1 note |

31 cặp FIM trên được đối chiếu trong fim-after.json đã thu ở lượt S1 và bảo toàn qua manifest; không phải 31 cảnh báo mới sinh ra do đọc ảnh đĩa. Dữ liệu chỉ được đổi tên, không được mã hóa.

## 6. Nơi giữ chứng cứ và giới hạn

Ảnh RAM và QCOW2 nằm ngoài Git trong CSATTT-Lab trên ổ D; giữ nguyên gói, manifest và bản nguồn. Script thu, báo cáo Volatility, chỉ mục trích xuất và kết quả kiểm tra được lưu ở vùng outputs/acquisition-a3-* và outputs/a3-*-20261104-* của workspace người vận hành. Các bản phân tích dẫn xuất có manifest riêng; ảnh chứng cứ không được boot để phân tích.

A3 xác nhận công cụ thu và khả năng đọc/đối chiếu chứng cứ nền. Chưa thay thế lượt sự cố chính có thời điểm mất dịch vụ, phát hiện, xử lý, thu chứng cứ và phục hồi sạch. Chưa kết luận phát hiện họ ransomware, tự động diệt mã độc hoặc RTO/RPO của lab tích hợp.
