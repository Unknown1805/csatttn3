# Nhật ký thay đổi

Các thay đổi đáng chú ý của dự án được tóm tắt tại đây.
Chi tiết công việc và review được lưu trong Issue/Pull Request.

## [Unreleased]

### Added

- Bổ sung cấu hình HTTPS/TLS 1.3 cho Restic, CA riêng, kiểm tra chứng chỉ và gate backup/restore; chờ nghiệm thu trong VM.

- Bổ sung biên bản nghiệm thu nền lab tại docs/kiem-thu/nghiem-thu-nen-lab.md.
- README mô tả mục tiêu, phạm vi và quy tắc làm việc nhóm.
- .gitattributes quy định kiểu xuống dòng cho các loại file.
- .gitignore loại trừ cấu hình riêng và dữ liệu lab sinh ra.
- Khung thư mục .github, docs, lab, scripts, src và tests.

- Bổ sung CONTRIBUTING.md hướng dẫn cài công cụ và quy trình làm việc nhóm trên GitHub.

### Changed

- Cập nhật VM chính từ thiết kế VirtualBox sang QEMU/KVM và ghi nhận các kết quả nền đã kiểm thử.
- Ghi nhận backup 15 file / 600 B, kiểm tra kho thành công và restore khớp 15/15 SHA-256; 3.649 giây là thời gian bước restore, chưa phải RTO sự cố.
- Ghi rõ giới hạn HTTP/TLS, các bước cô lập và phục hồi môi trường sạch còn phải nghiệm thu.
- Đồng bộ quy trình PR: Minh kiểm tra và merge PR của thành viên; PR của Minh được tự kiểm tra và merge, không bắt buộc Phong review.
- Phân biệt demo có kiểm soát trên máy chính với nghiên cứu Linux.Encoder.1 dự kiến trên máy phụ; chưa triển khai simulator hoặc thực thi mẫu thật.
