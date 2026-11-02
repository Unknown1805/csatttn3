# Nghiệm thu cô lập nền và diễn tập Pause/Resume VM — A2

Ngày tổng hợp: **03/11/2026, giờ Việt Nam (UTC+7)**. Người vận hành: Nhữ Duy Anh Minh (@Unknown1805). Liên quan Issue #19.

**Kết luận: đạt các phép thử cô lập nền và Pause/Resume được liệt kê trong biên bản.**
Đây là lượt thử vô hại, chưa thực thi simulator hoặc malware thật. Kết quả không chứng minh khả năng chống mọi đường thoát VM.

## 1. Môi trường và nguồn kiểm tra

- VM `CSATTT-QEMU`, UUID `bd0eab21-9089-4489-a703-b7771e210d5e`, QEMU/KVM trên Kali.
- Ubuntu 24.04.5; 6 vCPU, RAM 12 GiB, vda 70 GiB, root LVM khoảng 68 GiB.
- Checkout nền trước cập nhật tài liệu: `86969cf07d79fc791bc379f2490a7e8b6fb00f6c`.
- Nguồn Wazuh đã chuyển vào guest vẫn là `78806db2b2107c53ba5ca88e980ab0858f0a0977`; việc merge Git không tự thay đổi source trong VM.
- Gói kiểm tra A2 được chuyển bằng ISO chỉ đọc nhãn `CSATTT_A2`. Đây là công cụ chuẩn bị ngoài checkout, được định danh bằng hash dưới đây.
- Gói trên Kali: `/home/ndam/Documents/ChatGPT/CSATTT/outputs/co-lap-vm-a2-20261102-jkgyxdnz`.

| Thành phần | SHA-256 |
|---|---|
| `isolation-a2.iso` | `c802bdb6680ba7289ffb7b88324c50362f31f1a95fdd044bb87b4132d6afc6fe` |
| `start_and_check.py` trong ISO | `71c551446e7f9e170955a4131061d70b6e47825d605cb566f995bc168490ecb2` |
| `pause-drill.sh` trên Kali | `6ede3fa1682e270191dedb298e4972f1bc976a55b97fd70d06422be2c7972dc4` |

Trước khi chạy, công cụ guest đạt 9 unit test, kiểm tra cú pháp Python 3.12 và đối chiếu hash sau giải nén ISO. Script Pause đã kiểm tra cú pháp và từ chối chạy không có Terminal tương tác. Những kiểm tra chuẩn bị này được tách khỏi kết quả runtime ở các mục sau.

## 2. Bản khôi phục trước thay đổi

- VM được tắt đúng cách trước khi sao lưu.
- Nơi lưu bản dự phòng: `/run/media/ndam/My Passport/CSATTT-baseline-wazuh-20261102T161556Z-BmW3kr`.
- Đĩa làm việc vẫn ở `/run/media/ndam/New Volume/CSATTT-Lab/csattt-qemu.qcow2` trên ổ D.
- Bản sao `disk.qcow2` có kích thước file `16350183424` byte; dung lượng đĩa ảo vẫn là 70 GiB.
- Log `qemu-img check` ghi không phát hiện lỗi; log `qemu-img compare` ghi `Images are identical.`
- SHA-256 bản sao: `a3ccd3377716f6e72416c2b19267ece84a0b92e0b309833af26199b8df80d356`.
- XML cấu hình trước thay đổi: `27a37428543aaa7e6b861819d98846deb50b0e19ecff588f3d5b5d9ed38b597a`.

Đã đối chiếu lại hash XML và các file metadata/log nhỏ với manifest. Không đọc lại toàn bộ hash đĩa HDD trong lần tổng hợp này. Bản sao chưa được boot thử để nghiệm thu phục hồi đầy đủ; không dùng nó thay cho bộ chứng cứ của lượt sự cố sau này.

## 3. Thay đổi cấu hình và kiểm chứng từ Kali

File trước/sau được lưu trong gói A2, đều qua kiểm tra schema libvirt. Người vận hành áp dụng cấu hình khi VM tắt. Sau khi boot, đã đọc lại cả XML live và persistent:

| Hạng mục | Kết quả |
|---|---|
| Card mạng ngoài | Không còn phần tử `interface` trong cả live/config |
| Clipboard SPICE | `copypaste='no'` |
| Truyền file SPICE | `filetransfer enable='no'` |
| USB redirection | Đã bỏ hai `redirdev`; số còn lại bằng 0 |
| USB passthrough và shared filesystem | `hostdev=0`, `filesystem=0` |
| Đĩa guest | Chỉ có đĩa hệ thống vda và CD chứa ISO kiểm tra; không có vdb |
| Thao tác người dùng | Xác nhận không còn dán từ Kali sang Ubuntu |

Chuột, bàn phím và hiển thị qua SPICE vẫn được giữ để vận hành. Kênh guest agent vẫn có trong cấu hình. Chưa thử riêng chiều clipboard Ubuntu → Kali hoặc cắm USB vật lý; kết luận về các kênh này dựa vào cấu hình live/config và quan sát nêu trên.

## 4. Kiểm tra trong Ubuntu trước Pause

Thư mục kết quả: `/home/csattt3/csattt-lab/setup/isolation-a2-20261102T171344Z-z34ugu96`.

- `PAYLOAD HASH: OK`; script kiểm tra đúng hostname, UID và UUID VM.
- Không có NIC phần cứng trong guest, không có default route IPv4/IPv6.
- TCP tới `1.1.1.1:443`, IP Kali `192.168.1.4:443` và gateway libvirt cũ `192.168.122.1:443` đều trả `ENETUNREACH` (errno 101).
- Đối chứng từ Kali lúc `2026-11-02T17:05:46.758198+00:00`: kết nối TCP tới `1.1.1.1:443` thành công. Hai IP nội bộ là địa chỉ tại thời điểm thử, không dùng làm hằng số cho máy khác.
- Không thấy UUID ổ backup trong guest, mountpoint backup không được mount, không có dịch vụ backup đang chạy trong project.
- Đủ đúng 15 file thường, không symlink/file thừa; nội dung khớp từng byte, tổng 600 B.
- Chỉ khởi động bốn container có sẵn: Workstation, Wazuh Indexer, Manager và Dashboard.
- Kiểm tra mạng internal, namespace/quyền cơ bản, bind mount trong vùng lab và không có cổng host thực sự được công bố.
- Workstation HTTP 15/15 đạt. Dashboard khởi động qua các mã `000 → 503 → 302`; curl xác minh CA và tên `wazuh.dashboard`.
- Kết thúc: `NETWORK AND SERVICES: OK`.

Đầu ra Docker được chọn lọc, không xuất `Config.Env` chứa mật khẩu. Gói JSON/log guest chưa được chuyển sang Kali để kiểm tra hash độc lập; kết quả runtime guest ở đây dựa trên ảnh và đầu ra người vận hành cung cấp.

## 5. Diễn tập Pause/Resume từ Kali

Nhật ký gốc: `/home/ndam/Documents/ChatGPT/CSATTT/outputs/a2-pause-DML1vg`.

| Mốc UTC ngày 02/11/2026 | Trạng thái/kết quả |
|---|---|
| 17:23:54 | Trước thao tác: `running (booted)` |
| 17:23:54 | Sau suspend: `paused (user)` |
| 17:24:31 | Người vận hành yêu cầu tiếp tục |
| 17:24:31 | Sau resume: `running (unpaused)` |

Chênh lệch hai mốc UTC có độ phân giải giây trong trạng thái paused là **37 giây**. Đây là nhật ký diễn tập, không phải thời gian phát hiện hoặc RTO/RPO. Theo giờ Việt Nam, các mốc này thuộc ngày 03/11/2026.

- Người vận hành xác nhận đồng hồ `watch -n 1 date -u` ngừng cập nhật trong Pause và chạy lại sau Resume.
- Đã tự tính lại và đối chiếu đủ chín file với `SHA256SUMS` trên Kali; tất cả khớp.
- Lệnh cuối ghi `PAUSE/RESUME HOST CHECK: OK`.
- Pause giữ RAM khi máy thật vẫn hoạt động; không lưu RAM thành file và không loại bỏ tiến trình nghi vấn. Wazuh trong cùng VM cũng bị tạm dừng.

## 6. Kiểm tra sau Resume và ảnh đối chiếu

Lượt guest mới: `/home/csattt3/csattt-lab/setup/isolation-a2-20261102T172441Z-sye37rzt`.

Sau Resume, người vận hành chạy lại cùng công cụ: kiểm tra mạng không có đường ra đạt, ổ backup tiếp tục vắng mặt, baseline 15/15 khớp, Workstation HTTP 15/15 và Dashboard HTTPS 302. Kết thúc lại bằng `NETWORK AND SERVICES: OK`.

Ảnh được giữ nguyên byte ngoài Git tại `outputs/co-lap-vm-a2-20261102-jkgyxdnz/evidence` trong workspace `/home/ndam/Documents/ChatGPT/CSATTT`:

| Ảnh | SHA-256 |
|---|---|
| `isolation-before-pause.png` | `578b2d9bedb4ffa632021f4dc3918a06008c9d5451954f51bbcd4723b3bcc8b8` |
| `pause-resume-and-services.png` | `a406aeefb30274a54e52106893c6f3f580cfde7b70397c7d34a4977d15a8c3b7` |

## 7. Giới hạn và việc tiếp theo

Đạt phạm vi cấu hình đã đọc, các phép thử mạng đã liệt kê, tính toàn vẹn dữ liệu nền, khả dụng dịch vụ và Pause/Resume. Chưa thử chống VM escape, mọi giao thức/đích mạng, malware thật hoặc khả năng log độc lập chống sửa bởi root guest. Sau Resume chưa phát sinh một cảnh báo FIM mới để kiểm tra lại toàn tuyến cảnh báo.

Tiếp theo: chuẩn bị simulator giới hạn trên dữ liệu giả, phép thu RAM/ảnh đĩa/log/PCAP và mốc đo cho lượt sự cố. Giữ nguyên chứng cứ gốc, phục hồi vào môi trường sạch và đo kết quả thực tế trước khi đối chiếu RTO/RPO mục tiêu. Xem [Runbook cô lập](../runbook-co-lap.md).
