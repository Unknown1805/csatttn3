# Runbook cô lập VM và dừng khẩn cấp — A2

Áp dụng cho lab mô phỏng của Minh: `CSATTT-QEMU` trên Kali, Ubuntu hostname `csattt3`. Liên quan Issue #19; [kết quả nghiệm thu](kiem-thu/co-lap-vm-a2.md).

## 1. Hiểu đúng thao tác

Kali quản lý máy ảo bằng libvirt. Ubuntu bên trong VM là Docker host; Workstation và ba dịch vụ Wazuh chạy trong Ubuntu. Tháo card mạng ngoài của VM vẫn giữ các mạng Docker nội bộ và đường Ubuntu → Dashboard.

Trong chế độ diễn tập: không có NIC ngoài, shared filesystem, USB passthrough/redirection; clipboard và truyền file SPICE bị tắt. Chuột/bàn phím/hiển thị vẫn hoạt động. Lệnh dài được đưa vào VM bằng ISO chỉ đọc có kiểm tra hash.

`virsh suspend` tạm dừng CPU của toàn VM và giữ RAM khi Kali còn chạy. Vì vậy cả Workstation, Wazuh và đồng hồ Terminal đều ngừng cập nhật. Đây là biện pháp giữ trạng thái để xử lý tiếp, không phải diệt mã độc hoặc khôi phục dữ liệu.

## 2. Chuẩn bị trước phiên

1. Đứng đúng checkout và kiểm tra `git status --short --branch`.
2. Kiểm tra dung lượng trên Kali, ổ D và Ubuntu. Dừng thử nghiệm nếu vùng chứa dữ liệu còn dưới 15 GiB; dự trù thêm RAM dump 12 GiB và ảnh đĩa.
3. Có bản nền trước sự cố: khi VM tắt, lưu đĩa qcow2 và XML sang vùng dự phòng, chạy `qemu-img check` không có `-r`, đối chiếu nội dung bằng `qemu-img compare`, lập SHA-256. Không tự dùng bản đang chạy để sao chép đĩa.
4. Đĩa backup đã unmount trong guest và tháo khỏi cả live/config; không khởi động backup-server khi đĩa vắng mặt.
5. Kiểm tra đúng tên/UUID VM. Lệnh libvirt chạy trên **Kali**, lệnh Docker chạy trong **Ubuntu**.

## 3. Chuẩn bị cấu hình cô lập khi VM tắt

Lưu XML trước thay đổi bằng `virsh --readonly -c qemu:///system dumpxml CSATTT-QEMU --inactive`. Tạo file ứng viên riêng; giữ nguyên UUID, đĩa, CPU/RAM và các thiết bị không thuộc thay đổi:

- Bỏ các `devices/interface` nối VM ra mạng ngoài.
- Bỏ `devices/redirdev` và cấu hình USB redirection liên quan.
- Trong graphics SPICE, đặt:

```xml
<clipboard copypaste='no'/>
<filetransfer enable='no'/>
```

Kiểm tra schema bằng `virt-xml-validate`, đối chiếu diff và bảo đảm VM vẫn tắt trước `virsh define FILE --validate`. Sau boot, đọc lại cả XML live và persistent. File định nghĩa chỉ mô tả phần cứng/cấu hình; ảnh đĩa mới chứa Ubuntu và dữ liệu.

Bộ trước/sau của lượt A2 nằm ngoài Git trong gói được ghi ở biên bản; không ghi đè các file này khi làm lượt khác. Muốn quay lại chế độ chuẩn bị có mạng, cần tắt VM, xem lại các thay đổi phát sinh sau mốc cũ rồi mới áp dụng cấu hình đã duyệt. Không bật lại mạng ngoài trong lúc đang xử lý sự cố.

## 4. Kiểm tra guest và dịch vụ

Gắn ISO kiểm tra vào CD sda, không phải đĩa vda. Trên Ubuntu, mount với `ro,nosuid,nodev,noexec`; có thể dùng Python đọc script từ ISO dù mount có `noexec`.

Gói công cụ đã chạy A2 có mã và hash được ghi trong biên bản. Nếu dùng lại, kiểm tra lại đích đối chứng theo IP Kali hiện tại và tạo gói mới nếu IP thay đổi; không tự sửa ISO lịch sử. Công cụ guest thực hiện:

1. Đối chiếu hash payload, đúng hostname/UID/UUID VM.
2. Không có NIC phần cứng hoặc default route IPv4/IPv6; kiểm tra kết nối với đích có ghi nhận đối chứng. `ECONNREFUSED` hoặc timeout không được tự coi là chứng minh cô lập.
3. Không có UUID/mount ổ backup; không có dịch vụ backup đang chạy trong project.
4. Đủ đúng 15 file mẫu, không symlink/thừa và khớp từng byte trước/sau.
5. Đọc cấu hình container, chỉ xuất trường cần thiết, không in môi trường chứa mật khẩu.
6. Khởi động đúng bốn container có sẵn, kiểm tra mạng internal, mount, quyền cơ bản và actual port bindings.
7. Workstation HTTP 15/15, Dashboard HTTPS với CA và tên hợp lệ. Cho phép khởi động có mã 000/503 trong cửa sổ chờ hữu hạn; không dùng `curl -k` để bỏ kiểm tra chứng chỉ.

Tên `wazuh.dashboard` trỏ IP container trong Ubuntu. Nếu IP đổi, đối chiếu lại `/etc/hosts`; không thêm mạng có Internet chỉ để mở Dashboard. Không xóa volume, tạo lại secret hoặc dùng prune để sửa lỗi khởi động.

## 5. Diễn tập Pause/Resume vô hại

Trên Ubuntu mở một tiến trình quan sát:

```bash
watch -n 1 date -u
```

Trên Kali, kiểm tra đúng VM đang chạy, ghi UTC và trạng thái. Sau đó:

```bash
sudo virsh -c qemu:///system suspend CSATTT-QEMU
LC_ALL=C virsh --readonly -c qemu:///system domstate CSATTT-QEMU --reason
```

Cần thấy `paused (user)` và đồng hồ Ubuntu ngừng cập nhật. Ghi thời điểm, chụp ảnh/ghi nhận quan sát. Chỉ trong lượt diễn tập vô hại, sau khi đã quan sát đủ mới chủ động chạy:

```bash
sudo virsh -c qemu:///system resume CSATTT-QEMU
LC_ALL=C virsh --readonly -c qemu:///system domstate CSATTT-QEMU --reason
```

Xác nhận `running (unpaused)`, đồng hồ chạy lại; dừng watch bằng Ctrl+C và kiểm tra lại mạng, baseline, HTTP và HTTPS. Lập hash nhật ký trên Kali. Nếu Terminal đóng trong lúc Pause, VM vẫn paused; thao tác resume vẫn phải thực hiện từ Kali.

Script `pause-drill.sh` của lượt A2 có trong gói nghiệm thu ngoài Git, có kiểm tra UUID, chờ ít nhất 15 giây và yêu cầu Enter từ người vận hành trước Resume. Không dùng script diễn tập này làm cơ chế tự tiếp tục một VM đang nghi bị xâm nhập.

## 6. Khi phát hiện tác động ngoài phạm vi

1. Dừng thao tác mô phỏng, Pause VM từ Kali và xác nhận trạng thái; không gắn lại backup hoặc mở mạng.
2. Giữ VM paused để người vận hành thu RAM và bảo quản chứng cứ theo kế hoạch đã thử. Pause không tự tạo RAM dump, và RAM không bền khi máy thật mất điện/reboot.
3. Nếu nghi tác động tới máy thật, ngắt kết nối mạng của máy thật và dừng buổi diễn tập; không coi ranh giới VM là bảo đảm tuyệt đối.
4. Nếu không thể giữ VM dưới kiểm soát và phải tắt nguồn khẩn cấp, chấp nhận mất RAM/chứng cứ dễ bay hơi và ghi lý do. Không tự chuyển sang tắt nguồn hoặc khởi động lại chỉ vì cửa sổ VM đứng trong trạng thái paused.
5. Bảo toàn VM/chứng cứ hiện có; khôi phục trên môi trường sạch. Không Resume VM nghi vấn chỉ để tiếp tục trình bày.

## 7. Kết thúc phiên

Giữ mã lượt chạy, UTC, nguồn công cụ, cấu hình trước/sau, kết quả và SHA-256. Dữ liệu thô, XML gốc, ISO công cụ, đĩa, RAM và secrets ở ngoài Git; báo cáo chỉ trích metadata đã rà soát. Gói công cụ và bản sao trên My Passport chứa dữ liệu lab cần được giữ riêng, không công bố công khai.

Cô lập nền và Pause/Resume đã đạt trong lượt A2. Simulator, phát hiện trong lượt sự cố, acquisition/phân tích, phục hồi sạch và RTO/RPO của lab tích hợp là các mốc tiếp theo.
