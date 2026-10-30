# Xử lý sự cố do ransomware tấn công trong môi trường mô phỏng bằng Docker

Bài tập lớn môn Cơ sở An toàn thông tin — Nhóm 3, đề tài 10.

## Mục tiêu

Xây dựng môi trường mô phỏng để thực hành phát hiện, cô lập,
thu thập chứng cứ, phân tích và khôi phục dữ liệu sau sự cố
có biểu hiện giống ransomware.

## Phạm vi

- Chỉ sử dụng dữ liệu giả phục vụ học tập.
- Nền lab đã triển khai bằng Docker trong VM Ubuntu trên QEMU/KVM; chế độ cô lập cho phiên sự cố còn phải nghiệm thu.
- Demo trực tiếp trên máy chính dự kiến dùng simulator có phạm vi kiểm soát trên tập file giả đã duyệt: đổi tên file, tạo thông báo hoặc kiểm thử mã hóa. Simulator chưa được triển khai; phải ghi rõ đây là mô phỏng.
- Linux.Encoder.1 là case nghiên cứu dự kiến trên máy phụ. Chưa xác minh file mẫu cụ thể hoặc SHA-256, chưa thực thi mẫu thật.
- Chỉ thực nghiệm mẫu thật sau khi đã định danh mẫu, kiểm chứng cô lập, chuẩn bị giám sát, diễn tập nút dừng và thử phục hồi từ bản sao lưu độc lập. Không mang mẫu thật hoặc VM đã nhiễm sang máy chính để chạy demo.
- Không phát triển chức năng tự lây lan hoặc đánh cắp dữ liệu; không tác động dữ liệu cá nhân.
- Mã nguồn được soạn bằng VS Code trên ổ dùng chung Windows/Linux; chuyển bản nguồn xác định vào VM, không chia sẻ trực tiếp thư mục code với môi trường sự cố.

## Kết quả cần đạt

1. Môi trường lab và kịch bản có thể thực hiện lại.
2. Thu thập RAM của máy ảo lab, ảnh đĩa, log và PCAP;
   lập danh mục SHA-256 và nhật ký bàn giao chứng cứ.
3. Phân tích chứng cứ, dựng timeline và xác định dấu hiệu sự cố.
4. Khôi phục từ backup, kiểm tra tính toàn vẹn dữ liệu
   và đo RTO/RPO.
5. Hoàn thiện playbook xử lý sự cố, diễn tập tình huống,
   báo cáo và video demo.

## Thành viên

- Nhữ Duy Anh Minh
- Nguyễn Gia Khánh
- Trần Bảo Minh
- Nguyễn Vũ Tuấn Phong

## Quy tắc làm việc trên GitHub

- Công việc được ghi nhận bằng Issue.
- Mỗi đợt thay đổi cần commit mô tả rõ nội dung và comment
  trong Issue hoặc Pull Request liên quan.
- Comment ghi: đã làm gì, kiểm tra thế nào, còn vướng gì.
- PR của thành viên được Nhữ Duy Anh Minh kiểm tra và merge.
- Với PR do Minh thực hiện, Minh tự kiểm tra thay đổi và bằng chứng trước khi merge; không bắt buộc Phong hoặc thành viên khác review.
- Báo cáo tổng kết quá trình làm nhóm bằng liên kết Issue,
  commit, Pull Request, comment và review thực tế.
- Không đưa mật khẩu, dữ liệu cá nhân hoặc chứng cứ thô lên repo.

Xem [Hướng dẫn làm việc nhóm](CONTRIBUTING.md) để biết cách cài công cụ, nhận việc, commit và gửi Pull Request.

## Trạng thái hiện tại

- Đã triển khai nền lab bằng QEMU/KVM, Ubuntu 24.04.5 và Docker.
- Workstation phục vụ đúng 15 file dữ liệu giả qua HTTP.
- Đã thử thu RAM và phân tích tiến trình kiểm chứng bằng Volatility.
- Đã backup 15 file, tổng 600 B; kiểm tra kho không phát hiện lỗi.
- Restore khớp 15/15 SHA-256; dữ liệu nguồn giữ nguyên.
- Đã nghiệm thu backup/restore qua HTTPS/TLS 1.3 ngày 30/10/2026; CA sai và tên sai bị từ chối.
- Lượt HTTPS vừa hoàn tất; cần dừng backup-server, unmount và tháo lại ổ backup trước phiên sự cố.
- Chưa triển khai giám sát phát hiện, simulator và lượt sự cố.
- Chưa nghiệm thu cô lập cho phiên sự cố, khôi phục môi trường sạch và RTO/RPO.

Xem [Biên bản nghiệm thu nền lab](docs/kiem-thu/nghiem-thu-nen-lab.md).

Xem [Runbook HTTPS](docs/runbook-https-backup.md) và [Biên bản nghiệm thu HTTPS](docs/kiem-thu/https-backup-p3.md).
