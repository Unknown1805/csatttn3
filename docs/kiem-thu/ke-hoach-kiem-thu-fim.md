# Kế hoạch kiểm thử cảnh báo  thay đổi file trên Wazuh

**Ghi chú đối chiếu:** Cảnh báo thay đổi file từ FIM chưa đủ để kết luận chắc chắn hệ thống đang bị ransomware tấn công; cần phải đối chiếu cảnh báo này với các thao tác thực tế và các log/chứng cứ khác trên hệ thống.

## Bảng ca kiểm thử

| Ca kiểm thử | Thao tác dự kiến | Kết quả mong đợi | Thời gian thao tác (UTC) | Thời gian cảnh báo | Đường dẫn file | Mã cảnh báo | Nguồn chứng cứ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1. Tạo file | Tạo mới một file giả trong thư mục thử riêng | Cảnh báo tệp mới được tạo | Chưa thực hiện | Chưa thực hiện | Chưa thực hiện | Chưa thực hiện | Chưa thực hiện |
| 2. Sửa nội dung | Thay đổi nội dung của file giả | Cảnh báo tệp bị sửa đổi nội dung | Chưa thực hiện | Chưa thực hiện | Chưa thực hiện | Chưa thực hiện | Chưa thực hiện |
| 3. Đổi tên | Đổi tên file giả thành tên khác | Cảnh báo tệp bị đổi tên | Chưa thực hiện | Chưa thực hiện | Chưa thực hiện | Chưa thực hiện | Chưa thực hiện |
| 4. Xóa file | Xóa file giả khỏi thư mục thử riêng | Cảnh báo tệp bị xóa | Chưa thực hiện | Chưa thực hiện | Chưa thực hiện | Chưa thực hiện | Chưa thực hiện |
| 5. Đối chứng | Đọc file (ví dụ: dùng lệnh cat/less), không thay đổi nội dung | Không sinh ra cảnh báo thay đổi file | Chưa thực hiện | Chưa thực hiện | Chưa thực hiện | Chưa thực hiện | Chưa thực hiện |
