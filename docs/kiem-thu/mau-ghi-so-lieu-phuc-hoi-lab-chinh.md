# Mẫu Ghi Số liệu Thực thi Phục hồi Lab Chính (P5)

- **Trạng thái lượt chạy:** `CHƯA THỰC HIỆN`
- **Runbook áp dụng:** `docs/runbook-phuc-hoi-lab-chinh.md`
- **Issue liên quan:** `#36`
- **Người thực hiện:** `<TEN_NGUOI_THUC_HIEN>`
- **Người xác nhận đầu vào & nghiệm thu:** Nhữ Duy Anh Minh (@Unknown1805)

> **Lưu ý:** Tài liệu này là biểu mẫu chuẩn bị sẵn cho lượt ứng cứu lab chính. Không điền số liệu hoặc mật khẩu từ giai đoạn thử nghiệm P4 vào biểu mẫu này.

---

## 1. Thông tin định danh môi trường và Đầu vào xác nhận

| Hạng mục | Giá trị ghi nhận thực tế | Trạng thái |
| :--- | :--- | :--- |
| **Mã phiên ứng cứu (Run ID)** | `<CHUA_THUC_HIEN>` | Chưa thực hiện |
| **VM sạch phục hồi (Hostname / Machine ID)** | `<CHUA_THUC_HIEN>` | Chưa thực hiện |
| **Nguồn ảnh nền VM sạch (ISO / Template)** | `<CHUA_THUC_HIEN>` | Chưa thực hiện |
| **UUID phân vùng sao lưu (`vdb` / `ext4`)** | `<CHUA_THUC_HIEN>` | Chưa thực hiện |
| **Mã băm SHA-256 gói/kho chuyển giao** | `<CHUA_THUC_HIEN>` | Chưa thực hiện |
| **Full Snapshot ID (64 ký tự hex)** | `<CHUA_THUC_HIEN_CAN_MINH_XAC_NHAN>` | Chưa thực hiện |
| **Thời điểm tạo Snapshot ($T_{\text{snapshot}}$ - UTC)** | `<CHUA_THUC_HIEN>` | Chưa thực hiện |
| **Tệp Manifest đối chiếu (15 tệp / 600 B)** | `<CHUA_THUC_HIEN_CAN_MINH_XAC_NHAN>` | Chưa thực hiện |
| **Thư mục đích phục hồi (`LAB_RESTORE_DIR`)** | `<CHUA_THUC_HIEN>` | Chưa thực hiện |

---

## 2. Bảng Mốc thời gian UTC và Thời lượng Đồng hồ Đơn điệu

| STT | Mốc sự kiện / Công đoạn | Thời điểm thực tế (UTC) | Mốc đơn điệu (`perf_counter` / `CLOCK_MONOTONIC`) | Thời lượng công đoạn (giây) | Ghi chú kỹ thuật |
| :-: | :--- | :--- | :--- | :--- | :--- |
| 1 | **Mốc xảy ra sự cố quy ước ($T_{\text{incident}}$)** | `<CHUA_THUC_HIEN>` | *Không áp dụng* | *Mốc tham chiếu* | Do kịch bản sự cố quy định |
| 2 | **Bắt đầu ứng cứu ($T_{\text{start}}$)** | `<CHUA_THUC_HIEN>` | `<CHUA_THUC_HIEN>` | `0.0000` | Bắt đầu quy trình trên VM sạch |
| 3 | **Hoàn tất `preflight` & `check --read-data`** | `<CHUA_THUC_HIEN>` | `<CHUA_THUC_HIEN>` | `<CHUA_THUC_HIEN>` | Xác minh UUID, TLS 1.3, toàn vẹn kho |
| 4 | **Bắt đầu lệnh `restic restore` ($T_{\text{restore\_start}}$)** | `<CHUA_THUC_HIEN>` | `<CHUA_THUC_HIEN>` | *Mốc đo riêng* | Bắt đầu chạy `restore-worker` |
| 5 | **Kết thúc lệnh `restic restore` ($T_{\text{restore\_end}}$)** | `<CHUA_THUC_HIEN>` | `<CHUA_THUC_HIEN>` | **`<THOI_LUONG_RESTORE_RIENG>`** | **Thời gian lệnh `restore` ghi riêng** |
| 6 | **Hoàn tất xác minh dữ liệu 15/15 (SHA-256)** | `<CHUA_THUC_HIEN>` | `<CHUA_THUC_HIEN>` | `<CHUA_THUC_HIEN>` | Khớp 15 tệp / 600 B với manifest |
| 7 | **HTTP phục hồi hoạt động 15/15 ($T_{\text{HTTP\_15/15}}$)** | `<CHUA_THUC_HIEN>` | `<CHUA_THUC_HIEN>` | `<CHUA_THUC_HIEN>` | `workstation` trả HTTP 200 & khớp hash 15/15 |

---

## 3. Bảng Kiểm tra Toàn vẹn Dữ liệu và Dịch vụ HTTP

| Hạng mục kiểm tra | Tiêu chí đạt | Kết quả thực tế | Trạng thái |
| :--- | :--- | :--- | :--- |
| **Cô lập sự cố** | Không mount kho backup vào VM sự cố | `<CHUA_THUC_HIEN>` | Chưa thực hiện |
| **Kiểm tra kho (`check --read-data`)** | Exit code `0`, `no errors were found` | `<CHUA_THUC_HIEN>` | Chưa thực hiện |
| **Số lượng & kích thước tệp restore** | Đúng `15` tệp, tổng `600 B`, không tệp rác/ẩn lạ | `<CHUA_THUC_HIEN>` | Chưa thực hiện |
| **Đối chiếu SHA-256 dữ liệu phục hồi** | `15/15` tệp khớp manifest của lab chính | `<CHUA_THUC_HIEN>` | Chưa thực hiện |
| **Khởi động HTTP** | Dịch vụ được chọn phục vụ đúng thư mục đã phục hồi; ghi rõ HTTP loopback hay Workstation/Compose | `<CHUA_THUC_HIEN>` | Chưa thực hiện |
| **Kiểm tra truy cập HTTP 15/15** | `15/15` tệp trả HTTP `200` và khớp SHA-256 qua HTTP | `<CHUA_THUC_HIEN>` | Chưa thực hiện |
| **Bảo toàn nguồn & chứng cứ** | Kho gốc, VM sự cố và log được giữ nguyên vẹn | `<CHUA_THUC_HIEN>` | Chưa thực hiện |

---

## 4. Tổng hợp Chỉ số RTO / RPO (Điền sau khi chạy thực tế)

- **Thời lượng thực thi riêng lệnh `restic restore`:** `<CHUA_THUC_HIEN>` giây *(không phải RTO sự cố)*.
- **Tổng thời lượng ứng cứu trên VM sạch ($T_{\text{HTTP\_15/15}} - T_{\text{start}}$):** `<CHUA_THUC_HIEN>` giây.
- **RTO thực tế ($T_{\text{HTTP\_15/15}} - T_{\text{incident}}$):** `<CHUA_THUC_HIEN>` *(Chỉ tính khi có mốc $T_{\text{incident}}$ quy ước)*.
- **Đánh giá RPO:**
  - Thời điểm tạo snapshot ($T_{\text{snapshot}}$): `<CHUA_THUC_HIEN>`
  - Thời điểm xảy ra sự cố ($T_{\text{incident}}$): `<CHUA_THUC_HIEN>`
  - Phiên bản dữ liệu trước sự cố: `<CHUA_THUC_HIEN>`
  - Kết luận RPO (mất mát dữ liệu giữa $T_{\text{snapshot}}$ và $T_{\text{incident}}$): `<CHUA_THUC_HIEN>` *(Không tự ghi `0` chỉ dựa vào việc khớp hash snapshot)*.