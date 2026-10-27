# Xử lý sự cố do ransomware tấn công trong môi trường mô phỏng bằng Docker

Bài tập lớn môn Cơ sở An toàn thông tin — Nhóm 3, đề tài 10.

## Mục tiêu

Xây dựng môi trường mô phỏng để thực hành phát hiện, cô lập,
thu thập chứng cứ, phân tích và khôi phục dữ liệu sau sự cố
có biểu hiện giống ransomware.

## Phạm vi

- Chỉ sử dụng dữ liệu giả phục vụ học tập.
- Simulator chỉ đổi tên file mẫu và tạo thông báo mô phỏng.
- Không sử dụng ransomware thật, không mã hóa dữ liệu,
  không triển khai chức năng tự lây lan.
- Dự kiến chạy Docker bên trong máy ảo Linux được cô lập.
- Mã nguồn được soạn bằng VS Code trên ổ dùng chung Windows/Linux.

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
- Pull Request cần ít nhất một thành viên khác review trước khi merge.
- Báo cáo tổng kết quá trình làm nhóm bằng liên kết Issue,
  commit, Pull Request, comment và review thực tế.
- Không đưa mật khẩu, dữ liệu cá nhân hoặc chứng cứ thô lên repo.

Xem [Hướng dẫn làm việc nhóm](CONTRIBUTING.md) để biết cách cài công cụ, nhận việc, commit và gửi Pull Request.

## Trạng thái hiện tại

Đang chuẩn bị cấu trúc nền của repository.
Lab chưa được triển khai; các kết quả phía trên là mục tiêu
cần thực hiện và kiểm chứng.