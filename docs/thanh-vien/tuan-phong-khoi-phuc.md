# Nhật ký thực hiện & Kế hoạch khôi phục - Nguyễn Vũ Tuấn Phong

- Họ và tên: Nguyễn Vũ Tuấn Phong
- GitHub Username: nvtp0511
- Vai trò: Đồng phụ trách thực nghiệm (Sao lưu/Khôi phục Restic, đo RTO/RPO, diễn tập Tabletop và Playbook)
- Hệ điều hành: Windows (quản lý Git & tài liệu) / Linux (máy ảo thực nghiệm lab)
- Công cụ kiểm tra: Git, VS Code, Git Credential Manager
- Trạng thái: Kế hoạch dự kiến — chưa thực nghiệm

---

## 1. Checklist chuẩn bị trước sự cố (Baseline và Backup)

Checklist này thực hiện trước khi kích hoạt simulator đổi tên file:

1. [ ] Chuẩn bị dữ liệu mẫu: Tạo thư mục dữ liệu mẫu với các file văn bản có ID tăng dần, timestamp UTC cố định.
2. [ ] Lập manifest và tính mã băm:
   - Liệt kê toàn bộ danh sách file trong thư mục mẫu.
   - Tính mã SHA-256 cho từng file và lưu vào file manifest tham chiếu.
3. [ ] Tạo bản sao lưu (Backup snapshot):
   - Tạm dừng tiến trình ghi (writer) để đảm bảo tính nhất quán dữ liệu.
   - Chạy lệnh sao lưu bằng Restic vào repository: restic -r <repo_path> backup <data_path>.
   - Ghi nhận snapshot_id, thời gian bắt đầu và kết thúc sao lưu.
   - Chạy kiểm tra kho lưu trữ: restic -r <repo_path> check.
4. [ ] Cô lập và bảo vệ bản sao lưu:
   - Đảm bảo tiến trình sao lưu đã dừng hoàn toàn.
   - Unmount và detach (tháo rời) ổ đĩa chứa repository backup ra khỏi VM lab trước khi phiên sự cố bắt đầu.
   - Xác nhận simulator không có quyền truy cập, không có credential và không nhìn thấy volume backup.

---

## 2. Checklist khôi phục sau sự cố (Incident Containment và Recovery)

Checklist này thực hiện sau khi sự cố diễn ra và phiên incident đã được đóng băng thu thập chứng cứ:

1. [ ] Bảo toàn môi trường sự cố: Giữ nguyên trạng thái container và volume bị tác động để phục vụ điều tra pháp chứng số.
2. [ ] Chuẩn bị môi trường sạch:
   - Sử dụng máy ảo (VM) sạch từ bản gốc (snapshot/template sạch) đã kiểm tra trước đó, bảo toàn nguyên vẹn phiên sự cố trước khi kết nối lại backup.
   - Rà soát tiến trình, volume và quyền hạn đảm bảo không còn mã độc/simulator sót lại.
3. [ ] Gắn lại kho sao lưu:
   - Kết nối lại ổ đĩa backup vào môi trường sạch. Quyền mount và cách xử lý cơ chế lock của Restic tuân thủ đúng runbook được duyệt.
   - Chỉ sử dụng tùy chọn --no-lock khi đã bảo đảm chắc chắn không có tiến trình ghi hoặc tác vụ bảo trì repository đồng thời.
   - Kiểm tra tính toàn vẹn dữ liệu kho: restic -r <repo_path> check --read-data.
4. [ ] Chọn và thực hiện khôi phục (Restore):
   - Liệt kê các snapshot: restic -r <repo_path> snapshots.
   - Chọn đúng snapshot hợp lệ ngay trước thời điểm sự cố.
   - Thực hiện lệnh restore sang đích sạch: restic -r <repo_path> restore <snapshot_id> --target <clean_target_path>.
5. [ ] Nghiệm thu và đối chiếu tính toàn vẹn:
   - Chuẩn hóa đường dẫn sau restore.
   - Tính lại mã SHA-256 các file vừa phục hồi, đối chiếu 1:1 với manifest gốc.
   - Chạy thử tác vụ đọc dữ liệu mẫu để xác nhận tính khả dụng thực tế.

---

## 3. Bảng theo dõi và kết quả đo lường thực nghiệm

> Lưu ý: Kế hoạch dự kiến — chưa thực nghiệm. Toàn bộ số liệu sẽ được đo đạc và ghi nhận khi chạy kịch bản lab thực tế.

| Thông số / Tiêu chí | Giá trị kế hoạch / Thực tế | Ghi chú |
| --- | --- | --- |
| Run ID | Chờ thực nghiệm | Mã phiên chạy thực tế |
| Snapshot ID sử dụng | Chờ thực nghiệm | Mã snapshot được chọn từ Restic |
| Thử restore bộ dữ liệu nhỏ trước sự cố | Chưa thực hiện | Kiểm tra khả thi trước phiên chính |
| Thời điểm mất khả dụng (t_loss) | Chờ thực nghiệm | Lúc kiểm tra dữ liệu đầu tiên thất bại |
| Thời điểm phát hiện sự cố (t_detect) | Chờ thực nghiệm | Ghi nhận thời gian phát hiện |
| Thời điểm khôi phục đạt yêu cầu (t_restore_validated) | Chờ thực nghiệm | Lúc đối chiếu SHA-256 và đọc dữ liệu PASS |
| RTO thực đo (t_restore_validated - t_loss) | Chờ thực nghiệm | Thời gian gián đoạn thực tế |
| RPO thực đo | Chờ thực nghiệm | Độ trễ dữ liệu bị mất so với t_loss |
| Kết quả đối chiếu SHA-256 | Chưa thực hiện | Trùng khớp / Có sai lệch |
| Vấn đề / Lỗi phát sinh | Chưa có | Ghi nhận lỗi quyền, mount hoặc lệch đường dẫn |