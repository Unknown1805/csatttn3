# Xử lý sự cố do ransomware tấn công trong môi trường mô phỏng bằng Docker

Bài tập lớn môn Cơ sở An toàn thông tin — Nhóm 3, đề tài 10.

## Mục tiêu

Xây dựng môi trường mô phỏng để thực hành phát hiện, cô lập,
thu thập chứng cứ, phân tích và khôi phục dữ liệu sau sự cố
có biểu hiện giống ransomware.

## Phạm vi

- Chỉ sử dụng dữ liệu giả phục vụ học tập.
- Nền lab đã triển khai bằng Docker trong VM Ubuntu trên QEMU/KVM; đã kiểm chứng cô lập nền và Pause/Resume theo phạm vi A2, phải kiểm tra lại trước mỗi lượt sự cố.
- Demo trên máy chính dùng simulator chỉ đổi tên đúng 15 file giả và tạo note ghi rõ mô phỏng; không mã hóa nội dung. Đã nghiệm thu dry-run/apply S1 ngày 03/11/2026 (Issue #33) và hoàn thành một lượt demo tích hợp D1 ngày 05/11/2026: khống chế sau 3/15 lần đổi tên, thu/phân tích chứng cứ và phục hồi HTTP/hash 15/15 trên VM recovery riêng.
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

## Kiểm tra mã nguồn

Workflow CI tự kiểm tra Python, Compose, unit test, SAST và secret cho PR vào develop/main và push hai nhánh đó. Xem [Runbook CI và review](docs/runbook-ci-review.md). A4 đã có [lượt CI GitHub thành công](https://github.com/Unknown1805/csatttn3/actions/runs/41804635402) ngày 04/11/2026 trên commit `95a005c67521fc8c76613727274b512a15ec075f`; hai job đều đạt và PR #39 đã merge vào develop. CI không thay cho nghiệm thu VM hoặc demo.

## Trạng thái hiện tại

- Đã triển khai nền lab bằng QEMU/KVM, Ubuntu 24.04.5 và Docker.
- Đã kiểm thử Workstation phục vụ đúng 15 file dữ liệu giả qua HTTP.
- Đã thử thu RAM và phân tích tiến trình kiểm chứng bằng Volatility.
- Đã backup 15 file, tổng 600 B; kiểm tra kho không phát hiện lỗi.
- Restore khớp 15/15 SHA-256; dữ liệu nguồn giữ nguyên.
- Đã nghiệm thu backup/restore qua HTTPS/TLS 1.3 ngày 30/10/2026; CA sai và tên sai bị từ chối.
- Sau lượt HTTPS ngày 30/10/2026 đã dừng backup-server, unmount và tháo ổ backup khỏi live/config; phải kiểm tra lại trước mỗi phiên sự cố.
- Đã chạy Wazuh 4.14.9 gồm Manager, Indexer và Dashboard; đăng nhập admin qua HTTPS tại `https://wazuh.dashboard:5601` trong Ubuntu VM.
- Đã nghiệm thu FIM cơ bản với năm ca vô hại: tạo, sửa, đổi tên, chỉ đọc trong 60 giây và xóa. Log và Dashboard khớp đủ năm cảnh báo; kiểm tra lại 15/15 file nền đạt.
- Xem [Runbook giám sát](docs/runbook-giam-sat.md) và [Biên bản kiểm thử FIM](docs/kiem-thu/giam-sat-fim-stage4.md).
- Đã nghiệm thu simulator Issue #33 trên bản sao thử: dry-run không đổi dữ liệu; apply đổi tên 15/15 file sang .simlocked và tạo note mô phỏng, nội dung giữ nguyên; sample_data vẫn 15/15 nguyên vẹn.
- Wazuh ghi nhận đủ tên cũ bị mất, tên mới và note xuất hiện; Dashboard hiển thị các cặp added/deleted đúng lượt thử. Đây là quan sát FIM, chưa phải phân loại hoặc ngăn chặn ransomware tự động.
- Xem [Runbook simulator](docs/runbook-simulator.md) và [Biên bản kiểm thử simulator S1](docs/kiem-thu/simulator-s1.md).
- Đã nghiệm thu thu/đọc chứng cứ nền A3 ngày 04/11/2026: RAM nhận PID 6309 (`csattt-a3`); PCAP kiểm chứng HTTP có nhãn; ảnh QCOW2 khớp hash nguồn trước/sau và đọc được dữ liệu, log S1. Xem [Biên bản A3](docs/kiem-thu/thu-chung-cu-a3.md).
- Đã chạy trọn một lượt D1 ngày 05/11/2026: Workstation/simulator cùng dùng bản sao; 3 URL tên cũ trả 404, 12 URL còn lại trả 200; Wazuh có 7 sự kiện mới. Containment được điều phối sau ba lần đổi tên, chưa phải Wazuh tự ngăn chặn ransomware.
- RAM D1 xác nhận PID 27840 và dòng lệnh simulator; log, PCAP HTTP kiểm tra sau cô lập và ảnh QCOW2 được kiểm tra hash/phân tích.
- Phục hồi đúng snapshot Restic trên VM recovery từ checkpoint trước sự cố: dữ liệu 15 file/600 B, hash và HTTP 15/15; người vận hành đã kiểm tra manifest và trang file_01 trên Firefox. Xem [Biên bản D1](docs/kiem-thu/demo-tich-hop-d1.md) và [Runbook D1](docs/runbook-demo.md).
- Đã kiểm chứng A2 ngày 03/11/2026: bỏ NIC ngoài, khóa clipboard/truyền file SPICE và USB redirection; các đích TCP đã thử không có đường đi.
- Đã diễn tập Pause/Resume, ghi nhận paused → running và kiểm tra lại Workstation HTTP 15/15, baseline 15/15, Dashboard HTTPS 302.
- Xem [Runbook cô lập](docs/runbook-co-lap.md) và [Biên bản A2](docs/kiem-thu/co-lap-vm-a2.md).
- Đã chạy tiếp D2 từ bản chuẩn bị mới tới phục hồi hash/HTTP 15/15; script recovery 12.202 giây theo ảnh terminal. Runtime ghi 3 file đổi tên, đĩa sau shutdown có 4; toàn bộ nội dung giữ nguyên. Xem [Biên bản D2](docs/kiem-thu/demo-chay-lai-d2.md). Người vận hành đã xác nhận manifest recovery 28/28 và xem file_01 trên Firefox. Phần thao tác trình diễn gọn còn chờ nghiệm thu.
- Các thời gian script/bước restore không phải RTO/RPO sản xuất. Giữ riêng chứng cứ D1/D2; chưa nghiệm thu launcher/reset cho buổi trình bày.

Xem [Biên bản nghiệm thu nền lab](docs/kiem-thu/nghiem-thu-nen-lab.md).

Xem [Runbook HTTPS](docs/runbook-https-backup.md) và [Biên bản nghiệm thu HTTPS](docs/kiem-thu/https-backup-p3.md).
