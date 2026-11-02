# Nhật ký thay đổi

Các thay đổi đáng chú ý của dự án được tóm tắt tại đây.
Chi tiết công việc và review được lưu trong Issue/Pull Request.

## [Unreleased]

### Added

- Chuẩn bị simulator rename-only Issue #33, mặc định dry-run và chỉ apply trên 15 file giả đúng mẫu; thêm profile incident dùng image sẵn có, helper tạo bản sao thử mới trong vùng FIM, kiểm thử giới hạn và runbook. Chưa triển khai/nghiệm thu trong VM.

- Bổ sung runbook cô lập và biên bản A2 ngày 03/11/2026: cấu hình live/config, phép thử không có đường mạng ngoài, kiểm tra 15 file nền và Pause/Resume.

- Bổ sung Wazuh 4.14.9 trên mạng internal riêng, bộ mật khẩu/CA riêng và FIM chỉ đọc dữ liệu giả; Dashboard được truy cập trực tiếp từ Ubuntu VM bằng tên nội bộ.
- Bổ sung biên bản nghiệm thu FIM cơ bản ngày 02/11/2026: năm ca vô hại, đủ năm cảnh báo khớp giữa log và Dashboard; đối chứng chỉ đọc 60 giây, 15/15 file nền còn nguyên và log xuất có SHA-256.

- Bổ sung cấu hình HTTPS/TLS 1.3 cho Restic, CA riêng, kiểm tra chứng chỉ và gate backup/restore; đã nghiệm thu trong VM ngày 30/10/2026.

- Bổ sung biên bản nghiệm thu nền lab tại docs/kiem-thu/nghiem-thu-nen-lab.md.
- README mô tả mục tiêu, phạm vi và quy tắc làm việc nhóm.
- .gitattributes quy định kiểu xuống dòng cho các loại file.
- .gitignore loại trừ cấu hình riêng và dữ liệu lab sinh ra.
- Khung thư mục .github, docs, lab, scripts, src và tests.

- Bổ sung CONTRIBUTING.md hướng dẫn cài công cụ và quy trình làm việc nhóm trên GitHub.

### Changed

- Ghi nhận bỏ NIC ngoài, khóa clipboard/truyền file SPICE và USB redirection; sau Resume dịch vụ vẫn đạt HTTP 15/15 và HTTPS 302. Bản khôi phục trước thay đổi lưu riêng trên My Passport.

- Bỏ yêu cầu publish Dashboard 127.0.0.1:8443 không có hiệu lực trên mạng chỉ có internal; hướng dẫn ánh xạ tên wazuh.dashboard tới IP container trong Ubuntu, kiểm tra HTTPS tại cổng 5601 và cập nhật test ranh giới truy cập.

- Sửa probe đọc config Restic dưới dạng byte mã hóa; giới hạn thời gian phép thử CA/tên sai, lưu log và dừng đúng container thử nghiệm khi runner bị ngắt.
- Ghi nhận HTTPS GATE: OK; backup 15 file / 600 B, kho kiểm tra không lỗi, restore snapshot gốc khớp 15/15 SHA-256. Bước restore mất 2.677 giây, chưa phải RTO sự cố.

- Cập nhật VM chính từ thiết kế VirtualBox sang QEMU/KVM và ghi nhận các kết quả nền đã kiểm thử.
- Ghi nhận backup 15 file / 600 B, kiểm tra kho thành công và restore khớp 15/15 SHA-256; 3.649 giây là thời gian bước restore, chưa phải RTO sự cố.
- Lưu kết quả HTTP lịch sử và nghiệm thu HTTPS riêng; các bước cô lập sự cố và phục hồi môi trường sạch còn phải nghiệm thu.
- Đồng bộ quy trình PR: Minh kiểm tra và merge PR của thành viên; PR của Minh được tự kiểm tra và merge, không bắt buộc Phong review.
- Phân biệt demo có kiểm soát trên máy chính với nghiên cứu Linux.Encoder.1 dự kiến trên máy phụ; chưa triển khai simulator hoặc thực thi mẫu thật.
