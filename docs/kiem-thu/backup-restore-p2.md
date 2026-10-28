# Báo cáo kiểm thử sao lưu và khôi phục bằng Restic (P2)

- Người thực hiện: Nguyễn Vũ Tuấn Phong (@nvtp0511)
- Reviewer: Nhữ Duy Anh Minh (@Unknown1805)
- Ngày thực hiện: 28/10/2026
- Nhiệm vụ: [P2] Thử sao lưu và khôi phục dữ liệu giả bằng Restic (#8)

---

## 1. Môi trường và công cụ

- Hệ điều hành: Linux (Kali Linux trên máy ảo)
- Phiên bản Restic: `restic 0.19.1 compiled with go1.26.4 on linux/amd64`
- Backend repository: Local backend (thư mục cục bộ `~/lab-restic/repo_backup`)

---

## 2. Vị trí lưu trữ và cấu trúc dữ liệu

- Thư mục dữ liệu nguồn: `~/lab-restic/data_source`
- Thư mục repository sao lưu: `~/lab-restic/repo_backup`
- Thư mục đích khôi phục: `~/lab-restic/data_restored`
- Vị trí lưu manifest gốc: `~/lab-restic/manifest/manifest_goc.txt`
- Số lượng file mẫu: 15 file văn bản từ `file_01.txt` đến `file_15.txt`.

---

## 3. Nhật ký thực thi lệnh và mốc thời gian

- Khởi tạo kho: `restic init --repo ./repo_backup` (Thành công)
- Thời gian bắt đầu sao lưu (UTC): `Wed Oct 28 08:49:30 AM UTC 2026`
- Lệnh sao lưu: `restic -r ./repo_backup backup ./data_source`
- Thời gian kết thúc sao lưu (UTC): `Wed Oct 28 08:49:53 AM UTC 2026`
- Snapshot ID tạo ra: `b4efe585`
- Kiểm tra kho lưu trữ (`restic check --read-data`):
  - Kết quả: `no errors were found` (Toàn bộ các khối dữ liệu trong kho nguyên vẹn 100%).
- Lệnh khôi phục: `restic -r ./repo_backup restore b4efe585 --target ./data_restored` (Thành công)

---

## 4. Bảng đối chiếu kết quả trước và sau khôi phục

| Đường dẫn tương đối | SHA-256 nguồn (Manifest gốc) | SHA-256 sau Restore | Trạng thái đối chiếu | Kiểm tra khả dụng (Đọc nội dung) |
| --- | --- | --- | --- | --- |
| file_01.txt | 5cc99c59c212e43bafc1fb9556e282655058497169ebeb676b8c8f29c96167f1 | 5cc99c59c212e43bafc1fb9556e282655058497169ebeb676b8c8f29c96167f1 | Trùng khớp | Đọc tốt, đúng định dạng |
| file_02.txt | 40b54fd0d8712f1cc0383c2f297656d0b37ace02b1cb03e100424bde2eeecc61 | 40b54fd0d8712f1cc0383c2f297656d0b37ace02b1cb03e100424bde2eeecc61 | Trùng khớp | Đọc tốt, đúng định dạng |
| file_03.txt | 36fcc25df3166df8a318930fa8279431e9c7ea2973267057f03af6ddb64e1356 | 36fcc25df3166df8a318930fa8279431e9c7ea2973267057f03af6ddb64e1356 | Trùng khớp | Đọc tốt, đúng định dạng |
| file_04.txt | 6d66d7ebe59ccb22f69c219f7a25dc18d6931f58b421cb1650b597df820c13d6 | 6d66d7ebe59ccb22f69c219f7a25dc18d6931f58b421cb1650b597df820c13d6 | Trùng khớp | Đọc tốt, đúng định dạng |
| file_05.txt | a06a82276444497de96620a3e87d56cd8f6d1a84b04a8251ae1695140d90d8a1 | a06a82276444497de96620a3e87d56cd8f6d1a84b04a8251ae1695140d90d8a1 | Trùng khớp | Đọc tốt, đúng định dạng |
| file_06.txt | b1099c5445bc7c5dc664596c878fc52e94608449208b893e9babc180208b9d43 | b1099c5445bc7c5dc664596c878fc52e94608449208b893e9babc180208b9d43 | Trùng khớp | Đọc tốt, đúng định dạng |
| file_07.txt | 4415645587270ed337171b925eaec170180a0f0be8fff66d9cb812c6f1802d30 | 4415645587270ed337171b925eaec170180a0f0be8fff66d9cb812c6f1802d30 | Trùng khớp | Đọc tốt, đúng định dạng |
| file_08.txt | 6a51b707f51218c2544bc89184fbae9b985c250ba4ccdffc015b60441d049c87 | 6a51b707f51218c2544bc89184fbae9b985c250ba4ccdffc015b60441d049c87 | Trùng khớp | Đọc tốt, đúng định dạng |
| file_09.txt | 17eae89a8491228a86eae84bc67afec58253b777df76d9d3f44f6f3fdd02240b | 17eae89a8491228a86eae84bc67afec58253b777df76d9d3f44f6f3fdd02240b | Trùng khớp | Đọc tốt, đúng định dạng |
| file_10.txt | 3d62432080ba79d99ce88066fd2623457294e9383362e0a099c4c46fce397e3d | 3d62432080ba79d99ce88066fd2623457294e9383362e0a099c4c46fce397e3d | Trùng khớp | Đọc tốt, đúng định dạng |
| file_11.txt | 96579a075797dcf67034f29d9685241580e1bd96a7509fa88f78acc45305fffa | 96579a075797dcf67034f29d9685241580e1bd96a7509fa88f78acc45305fffa | Trùng khớp | Đọc tốt, đúng định dạng |
| file_12.txt | ba7adb9cb33acb1096a6fc103add3b83da4a5a366bc880b0589f916d462c4926 | ba7adb9cb33acb1096a6fc103add3b83da4a5a366bc880b0589f916d462c4926 | Trùng khớp | Đọc tốt, đúng định dạng |
| file_13.txt | 48513b0ceec268a440be5e863cb87afc21be9a08c87449021bfd3a709e4b6d89 | 48513b0ceec268a440be5e863cb87afc21be9a08c87449021bfd3a709e4b6d89 | Trùng khớp | Đọc tốt, đúng định dạng |
| file_14.txt | f1e65a3f4724ec880f756a6d75764dce20815091fada666867c8d9368eea58dc | f1e65a3f4724ec880f756a6d75764dce20815091fada666867c8d9368eea58dc | Trùng khớp | Đọc tốt, đúng định dạng |
| file_15.txt | 2c56b54153b3b97284d203c899f42c7dbb3c4c6f5b5207d9e481dd1d237a42e2 | 2c56b54153b3b97284d203c899f42c7dbb3c4c6f5b5207d9e481dd1d237a42e2 | Trùng khớp | Đọc tốt, đúng định dạng |

- Tổng số file nguồn: 15 file.
- Tổng số file phục hồi: 15 file.
- Tỷ lệ trùng khớp mã băm SHA-256: 100% (15/15 file).

---

## 5. Lỗi phát sinh, cách xử lý và kết luận

- Vấn đề gặp phải: Khi chạy lệnh `restore`, Restic mặc định giữ nguyên cấu trúc thư mục nguồn bên dưới thư mục đích (cụ thể file nằm tại `./data_restored/data_source/file_*.txt`). Do đó, khi viết script tự động hóa đối chiếu mã băm cần lưu ý trỏ đúng đường dẫn thư mục con.
- Kết luận: Kiểm chứng thành công. Quy trình tạo snapshot, kiểm tra tính toàn vẹn kho và khôi phục dữ liệu bằng Restic hoạt động ổn định, bảo toàn nguyên vẹn 100% dữ liệu gốc.