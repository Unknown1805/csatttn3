# Kế hoạch kiểm thử cảnh báo thay đổi file trên Wazuh

## 1. Phạm vi kiểm thử
- Chỉ thực hiện thao tác thử nghiệm trong thư mục `~/csattt-lab/runtime/fim-probe` của VM (tương ứng với đường dẫn `/lab/fim-probe` trong Manager).
- Giữ nguyên 15 file dữ liệu nền, tuyệt đối không thao tác trên các file này.

## 2. Phương pháp và ghi chú đối chiếu
- **Cách ghi nhận:** Ghi lại thời gian UTC trước khi thực hiện thao tác. Sau đó, tìm đúng đường dẫn, loại sự kiện và thời gian tương ứng trong file `alerts.json` và trên Dashboard để đối chiếu.
- **Lưu ý ca đổi tên:** Hệ thống có thể sẽ ghi nhận thành hai sự kiện riêng biệt (xóa đường dẫn cũ và thêm đường dẫn mới). Không bắt buộc phải có một cảnh báo mang tên "đổi tên".
- **Lưu ý ca đối chứng (chỉ đọc):** Cần ghi rõ khoảng thời gian quan sát trên hệ thống (ví dụ: chờ 5-10 phút) trước khi đưa ra kết luận là không có cảnh báo thay đổi nào được sinh ra.
- **Lưu ý chung:** Cảnh báo thay đổi file từ FIM chưa đủ để kết luận chắc chắn hệ thống đang bị ransomware tấn công; bắt buộc phải đối chiếu cảnh báo này với các thao tác thực tế và các log/chứng cứ khác.

## 3. Bảng ca kiểm thử

| Ca kiểm thử | Thao tác dự kiến | Kết quả mong đợi | Thời gian thao tác (UTC) | Thời gian cảnh báo | Đường dẫn file | Mã cảnh báo | Nguồn chứng cứ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1. Tạo file | Tạo mới một file giả trong thư mục thử riêng | Cảnh báo tệp mới được tạo | Chưa thực hiện | Chưa thực hiện | Chưa thực hiện | Chưa thực hiện | Chưa thực hiện |
| 2. Sửa nội dung | Thay đổi nội dung của file giả | Cảnh báo tệp bị sửa đổi nội dung | Chưa thực hiện | Chưa thực hiện | Chưa thực hiện | Chưa thực hiện | Chưa thực hiện |
| 3. Đổi tên | Đổi tên file giả thành tên khác | Cảnh báo tệp bị đổi tên | Chưa thực hiện | Chưa thực hiện | Chưa thực hiện | Chưa thực hiện | Chưa thực hiện |
| 4. Xóa file | Xóa file giả khỏi thư mục thử riêng | Cảnh báo tệp bị xóa | Chưa thực hiện | Chưa thực hiện | Chưa thực hiện | Chưa thực hiện | Chưa thực hiện |
| 5. Đối chứng | Đọc file (ví dụ: dùng lệnh cat/less), không thay đổi nội dung | Không sinh ra cảnh báo thay đổi file | Chưa thực hiện | Chưa thực hiện | Chưa thực hiện | Chưa thực hiện | Chưa thực hiện |
