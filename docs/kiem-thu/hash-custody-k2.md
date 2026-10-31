# Báo cáo kiểm tra toàn vẹn dữ liệu K2

- **Người thực hiện:** Nguyễn Gia Khánh (@usrlwkadmas-arch)
- **Môi trường / Thư mục thực thi:** Windows 11 / Windows PowerShell (`C:\Users\Admin\OneDrive\Máy tính\gitgit2\p2b_export`)

## 1. Biên bản nhận dữ liệu
- **Người gửi:** Nguyễn Vũ Tuấn Phong
- **Gói dữ liệu:** `p2b_restic_tuanphong.tar.gz`
- **Mã lượt chạy (Snapshot ID):** b4efe585 (Nguồn đối chiếu: Biên bản bàn giao P2b của Phong)
- **Thời điểm nhận (UTC):** Không xác định được chính xác phút nhận bàn giao.
- **Kiểm tra gói nén (Package Hash):**
  - Hash SHA-256 gói do Phong cung cấp: `74a4a535fd75e6e4ecec6bab18302e6d853a39acf50e3b91d15b2fd808da717a`
  - Lệnh PowerShell tự tính:
    ```powershell
    Get-FileHash -Path "p2b_restic_tuanphong.tar.gz" -Algorithm SHA256
    ```
  - Đầu ra thực tế / Giá trị tự tính: `74A4A535FD75E6E4ECEC6BAB18302E6D853A39ACF50E3B91D15B2FD808DA717A`
  - **Kết luận:** Khớp 100% với giá trị Phong cung cấp.

## 2. Số lượng dữ liệu & Lệnh thực thi
- **Số lượng kiểm tra:** Đủ 15 file nguồn (`source`), 15 file phục hồi (`restored`) và 01 file manifest tham chiếu.
- **Lệnh PowerShell đã sử dụng để tính 30 hash:**
  ```powershell
  Get-FileHash -Path ".\source\*" -Algorithm SHA256
  Get-FileHash -Path ".\restored\*" -Algorithm SHA256
  ```

## 3. Bảng đối chiếu 15 cặp file nguồn và khôi phục
Thực hiện chạy lệnh băm và đối chiếu đường dẫn tương đối giữa bộ `source`, `restored` với `manifest` tham chiếu của cùng một lượt chạy:

| STT | Tên file | Hash Nguồn (Source) | Hash Khôi phục (Restored) | Đối chiếu Manifest | Kết luận |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `file_01.txt` | `5CC99C59C212E43BAFC1FB9556E282655058497169EBEB676B8C8F29C96167F1` | `5CC99C59C212E43BAFC1FB9556E282655058497169EBEB676B8C8F29C96167F1` | Khớp | Khớp |
| 2 | `file_02.txt` | `40B54FD0D8712F1CC0383C2F297656D0B37ACE02B1CB03E100424BDE2EEECC61` | `40B54FD0D8712F1CC0383C2F297656D0B37ACE02B1CB03E100424BDE2EEECC61` | Khớp | Khớp |
| 3 | `file_03.txt` | `36FCC25DF3166DF8A318930FA8279431E9C7EA2973267057F03AF6DDB64E1356` | `36FCC25DF3166DF8A318930FA8279431E9C7EA2973267057F03AF6DDB64E1356` | Khớp | Khớp |
| 4 | `file_04.txt` | `6D66D7EBE59CCB22F69C219F7A25DC18D6931F58B421CB1650B597DF820C13D6` | `6D66D7EBE59CCB22F69C219F7A25DC18D6931F58B421CB1650B597DF820C13D6` | Khớp | Khớp |
| 5 | `file_05.txt` | `A06A82276444497DE96620A3E87D56CD8F6D1A84B04A8251AE1695140D90D8A1` | `A06A82276444497DE96620A3E87D56CD8F6D1A84B04A8251AE1695140D90D8A1` | Khớp | Khớp |
| 6 | `file_06.txt` | `B1099C5445BC7C5DC664596C878FC52E94608449208B893E9BABC180208B9D43` | `B1099C5445BC7C5DC664596C878FC52E94608449208B893E9BABC180208B9D43` | Khớp | Khớp |
| 7 | `file_07.txt` | `4415645587270ED337171B925EAEC170180A0F0BE8FFF66D9CB812C6F1802D30` | `4415645587270ED337171B925EAEC170180A0F0BE8FFF66D9CB812C6F1802D30` | Khớp | Khớp |
| 8 | `file_08.txt` | `6A51B707F51218C2544BC89184FBAE9B985C250BA4CCDFFC015B60441D049C87` | `6A51B707F51218C2544BC89184FBAE9B985C250BA4CCDFFC015B60441D049C87` | Khớp | Khớp |
| 9 | `file_09.txt` | `17EAE89A8491228A86EAE84BC67AFEC58253B777DF76D9D3F44F6F3FDD02240B` | `17EAE89A8491228A86EAE84BC67AFEC58253B777DF76D9D3F44F6F3FDD02240B` | Khớp | Khớp |
| 10| `file_10.txt` | `3D62432080BA79D99CE88066FD2623457294E9383362E0A099C4C46FCE397E3D` | `3D62432080BA79D99CE88066FD2623457294E9383362E0A099C4C46FCE397E3D` | Khớp | Khớp |
| 11| `file_11.txt` | `96579A075797DCF67034F29D9685241580E1BD96A7509FA88F78ACC45305FFFA` | `96579A075797DCF67034F29D9685241580E1BD96A7509FA88F78ACC45305FFFA` | Khớp | Khớp |
| 12| `file_12.txt` | `BA7ADB9CB33ACB1096A6FC103ADD3B83DA4A5A366BC880B0589F916D462C4926` | `BA7ADB9CB33ACB1096A6FC103ADD3B83DA4A5A366BC880B0589F916D462C4926` | Khớp | Khớp |
| 13| `file_13.txt` | `48513B0CEEC268A440BE5E863CB87AFC21BE9A08C87449021BFD3A709E4B6D89` | `48513B0CEEC268A440BE5E863CB87AFC21BE9A08C87449021BFD3A709E4B6D89` | Khớp | Khớp |
| 14| `file_14.txt` | `F1E65A3F4724EC880F756A6D75764DCE20815091FADA666867C8D9368EEA58DC` | `F1E65A3F4724EC880F756A6D75764DCE20815091FADA666867C8D9368EEA58DC` | Khớp | Khớp |
| 15| `file_15.txt` | `2C56B54153B3B97284D203C899F42C7DBB3C4C6F5B5207D9E481DD1D237A42E2` | `2C56B54153B3B97284D203C899F42C7DBB3C4C6F5B5207D9E481DD1D237A42E2` | Khớp | Khớp |

- **Tổng hợp số liệu:** 
  - Khớp: **15/15 cặp**
  - Khác: **0**
  - Thiếu: **0**
  - Thừa: **0**

## 4. Kiểm thử phát hiện sửa đổi (Tamper Test)
- **Hành động thực hiện:** 
  1. Tạo một bản sao độc lập của thư mục `restored` thành `restored_test` bằng lệnh: `Copy-Item -Path ".\restored" -Destination ".\restored_test" -Recurse`.
  2. Cố tình chỉnh sửa nội dung bên trong tệp `file_01.txt` (giữ nguyên vẹn đầu vào gốc `source` và `restored`).
  3. Chạy lại lệnh tính hash: `Get-FileHash -Path ".\restored_test\*" -Algorithm SHA256`.
- **Kết quả thực tế ghi nhận:**
  - **Tệp bị thay đổi (`file_01.txt`):**
    - Hash gốc: `5CC99C59C212E43BAFC1FB9556E282655058497169EBEB676B8C8F29C96167F1`
    - Hash sau khi sửa: `71A7194577B3A8118882F11B8AE80500242042C6731F35C5DA7F7FFEA5BC7B8C` -> **Phát hiện khác hash**.
  - **14 tệp còn lại (từ file_02 đến file_15):** Giữ nguyên mã băm, khớp hoàn toàn với bản gốc.
- **Kết luận:** Cơ chế kiểm tra SHA-256 phản hồi chính xác tuyệt đối, phát hiện đúng 01 tệp bị can thiệp nội dung và xác thực đầy đủ 14 tệp còn lại vẫn đảm bảo tính toàn vẹn.