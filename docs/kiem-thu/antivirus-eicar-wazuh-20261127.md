# Biên bản kiểm thử ClamAV, cách ly và cảnh báo Wazuh

- **Lượt:** `eicar-20261127T102929Z-49d393df`, ngày 27/11/2026 (UTC).
- **Kết luận:** đạt cả ba mục: phát hiện EICAR, cách ly tệp, và Wazuh Manager tạo đúng một cảnh báo từ kết quả quét thật. Đây là lượt riêng, không dùng để nghiệm thu lại [#40](demo-tich-hop-40-hold-20261127.md).
- **Phạm vi:** một mẫu thử EICAR vô hại và một tệp đối chứng sạch. Quét theo yêu cầu bằng ClamAV `1.4.6`, cơ sở chữ ký `28194`, trên Kali. Chỉ chuyển log đã chuẩn hóa bằng ISO chỉ đọc vào Ubuntu `CSATTT-EICAR-01`; không chuyển mẫu EICAR, không dùng mã độc thật và không nối VM vào mạng ngoài.

## Kết quả

| Mục | Bằng chứng |
|---|---|
| Phát hiện | `clamscan` báo `Eicar-Test-Signature FOUND`, thoát `1` vì phát hiện mẫu. Lệnh quét bắt đầu `10:29:29.283846 UTC`, kết thúc `10:29:33.694131 UTC`. |
| Cách ly | ClamAV dùng `--move` đưa mẫu ra khỏi thư mục đầu vào vào thư mục riêng quyền `0700`. SHA-256 trước/sau khớp `275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f`. Tệp đối chứng báo `OK`, không bị di chuyển và SHA-256 không đổi. |
| Wazuh Manager | Wazuh `4.14.9` theo dõi log JSON. Nạp một lần kết quả quét đã xác minh; `alerts.json` có đúng **1** cảnh báo rule `100550`, mức `8`, khớp mã lượt, chữ ký, mẫu và trạng thái cách ly. Wazuh ghi cảnh báo; ClamAV thực hiện cách ly. |

## Đối chiếu và giới hạn

- Chứng cứ ngoài Git: `CSATTT-Lab/run-eicar-01/payload-fix/SHA256SUMS` xác nhận **5/5** tệp của ISO; `run-eicar-01/serial.log` ghi `WAZUH_CONFIG=VALID`, `EICAR_INPUT=LOADED_ONCE` và `WAZUH_EICAR=PASS`. VM lưu kết quả rút gọn tại `/var/lib/csattt-eicar-01/verdict.txt`. Không đưa mẫu, log thô hoặc ảnh đĩa vào Git.
- Rule ban đầu bị từ chối vì dùng `status` như trường động. Bản sửa bỏ điều kiện đó khỏi XML, nhưng bộ xác minh vẫn đối chiếu `status=FOUND` trong cảnh báo. Lỗi xảy ra trước khi nạp log; không quét lại. Các cảnh báo thiếu danh sách AWS, audit và IOC không thuộc phạm vi kiểm thử.
- Kết quả chỉ xác nhận quét theo yêu cầu, cách ly và cảnh báo tại Manager. Chưa kiểm tra quét thời gian thực, chuyển log tự động, hiển thị Dashboard hoặc SOC nhiều máy.
