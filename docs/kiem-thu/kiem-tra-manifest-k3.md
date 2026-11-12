# Báo cáo kiểm tra manifest và phân biệt file thiếu/thừa (K3)

- **Người thực hiện:** Nguyễn Gia Khánh (@usrlwkadmas-arch)
- **Reviewer / Nghiệm thu:** Nhữ Duy Anh Minh (@Unknown1805)
- **Mã lượt chạy K3:** K3-RUN-01
- **Phiên bản PowerShell:** `5.1`
- **Thư mục làm việc (Môi trường test độc lập):** `C:\K3_Test_Environment`
- **Nguồn manifest tham chiếu:** Manifest gốc từ P2b / K2 (`manifest_goc.txt`)

---

## 1. Danh sách tham chiếu 15 file gốc
Bộ dữ liệu gồm 15 file văn bản từ `file_01.txt` đến `file_15.txt` được đối chiếu theo đường dẫn tương đối kèm mã SHA-256 gốc:
- `file_01.txt` — SHA-256: `5cc99c59c212e43bafc1fb9556e282655058497169ebeb676b8c8f29c96167f1`
- `file_02.txt` — SHA-256: `40b54fd0d8712f1cc0383c2f297656d0b37ace02b1cb03e100424bde2eeecc61`
- `file_03.txt` — SHA-256: `36fcc25df3166df8a318930fa8279431e9c7ea2973267057f03af6ddb64e1356`
- `file_04.txt` — SHA-256: `6d66d7ebe59ccb22f69c219f7a25dc18d6931f58b421cb1650b597df820c13d6`
- `file_05.txt` — SHA-256: `a06a82276444497de96620a3e87d56cd8f6d1a84b04a8251ae1695140d90d8a1`
- `file_06.txt` — SHA-256: `b1099c5445bc7c5dc664596c878fc52e94608449208b893e9babc180208b9d43`
- `file_07.txt` — SHA-256: `4415645587270ed337171b925eaec170180a0f0be8fff66d9cb812c6f1802d30`
- `file_08.txt` — SHA-256: `6a51b707f51218c2544bc89184fbae9b985c250ba4ccdffc015b60441d049c87`
- `file_09.txt` — SHA-256: `17eae89a8491228a86eae84bc67afec58253b777df76d9d3f44f6f3fdd02240b`
- `file_10.txt` — SHA-256: `3d62432080ba79d99ce88066fd2623457294e9383362e0a099c4c46fce397e3d`
- `file_11.txt` — SHA-256: `96579a075797dcf67034f29d9685241580e1bd96a7509fa88f78acc45305fffa`
- `file_12.txt` — SHA-256: `ba7adb9cb33acb1096a6fc103add3b83da4a5a366bc880b0589f916d462c4926`
- `file_13.txt` — SHA-256: `48513b0ceec268a440be5e863cb87afc21be9a08c87449021bfd3a709e4b6d89`
- `file_14.txt` — SHA-256: `f1e65a3f4724ec880f756a6d75764dce20815091fada666867c8d9368eea58dc`
- `file_15.txt` — SHA-256: `2c56b54153b3b97284d203c899f42c7dbb3c4c6f5b5207d9e481dd1d237a42e2`

---

## 2. Kết quả thực hiện 4 ca kiểm thử (K3-01 đến K3-04)

Lệnh liệt kê file được sử dụng trên các bản sao độc lập ngoài Git:
```powershell
$files = Get-ChildItem -Recurse -File -Force
```
Quy trình kiểm tra: Đối chiếu tập đường dẫn tương đối trước, sau đó mới tính hash SHA-256 (`Get-FileHash`) cho các tệp tồn tại ở cả hai tập.

| Ca kiểm thử | Thao tác thực hiện trên bản sao | Thời gian UTC | Lệnh kiểm tra thực tế | Kết quả thực tế ghi nhận |
| :--- | :--- | :--- | :--- | :--- |
| **K3-01** | Giữ nguyên 15 file gốc | `2026-11-01 09:00:00 UTC` | `Get-ChildItem -Recurse -File -Force` | **15 Khớp, 0 Khác, 0 Thiếu, 0 Thừa** |
| **K3-02** | Sửa nội dung file `file_01.txt` | `2026-11-01 09:10:00 UTC` | `Get-FileHash file_01.txt -Algorithm SHA256` | **14 Khớp, 1 Khác** (`file_01.txt`), **0 Thiếu, 0 Thừa** |
| **K3-03** | Xóa file `file_02.txt` trong bản sao | `2026-11-01 09:20:00 UTC` | So sánh đường dẫn tương đối với manifest | **14 Khớp, 0 Khác, 1 Thiếu** (`file_02.txt`), **0 Thừa** |
| **K3-04** | Thêm file `unexpected.txt` và bật thuộc tính Hidden (`Set-ItemProperty -Path ".\unexpected.txt" -Name Attributes -Value Hidden`) | `2026-11-01 09:30:00 UTC` | `Get-ChildItem -Recurse -File -Force` | **15 Khớp, 0 Khác, 0 Thiếu, 1 Thừa** (`unexpected.txt` - Hidden) |

---

## 3. Kiểm tra lại bộ đầu vào gốc
- Sau khi hoàn tất 4 ca thử nghiệm trên các bản sao độc lập ngoài Git, bộ dữ liệu gốc và manifest tại thư mục nguồn đã được kiểm tra lại.
- **Kết quả:** Vẫn giữ nguyên 15 file, khớp 100% với manifest gốc, không bị thay đổi hay hỏng hóc.

---

## 4. Lưu ý phương pháp luận
- Mã băm SHA-256 và việc đối chiếu đường dẫn giúp xác thực tính toàn vẹn cấu trúc và nội dung tệp ở thời điểm kiểm tra.
- **Giới hạn chuyên môn:** Giá trị hash **không** chứng minh file sạch mã độc, không xác định danh tính người tạo hoặc thời điểm tạo tệp thực tế.

---

## 5. Checklist tiếp nhận chứng cứ (Dành cho Lab chính sau này)

| Nội dung kiểm tra | Trạng thái / Giá trị ghi nhận |
| :--- | :--- |
| **Người giao chứng cứ:** | Chưa nhận / Chưa kiểm tra |
| **Người nhận chứng cứ:** | Chưa nhận / Chưa kiểm tra |
| **Thời điểm bàn giao (UTC):** | Chưa nhận / Chưa kiểm tra |
| **Tên gói chứng cứ (Archive):** | Chưa nhận / Chưa kiểm tra |
| **Mã hash gói (Package Hash):** | Chưa nhận / Chưa kiểm tra |
| **Danh sách file tương đối:** | Chưa nhận / Chưa kiểm tra |
| **Kết quả đối chiếu:** | Chưa nhận / Chưa kiểm tra |
| **Phần bất thường / Ghi chú:** | Chưa nhận / Chưa kiểm tra |