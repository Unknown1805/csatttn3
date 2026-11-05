# Biên bản demo tích hợp D1 — gián đoạn HTTP, Wazuh và phục hồi

Ngày thực hiện: **05/11/2026**. Người chuẩn bị, vận hành và review: **Nhữ Duy Anh Minh**. Tiếp nối các phần nền A2, S1, A3 và A4. Phạm vi nghiệm thu: **một lượt D1 đã đi hết chuỗi chức năng**; khả năng chạy lại trọn demo từ đầu chưa nghiệm thu.

## 1. Kết luận

- Trước sự cố, Workstation D1 phục vụ đúng 15 file giả; FIM ghi nhận 15 tên baseline; dry-run giữ dữ liệu nguyên vẹn.
- Simulator và Workstation D1 dùng cùng bản sao. Sau ba lần đổi tên, bộ điều phối Pause simulator: 3 URL tên cũ trả 404, 12 URL còn lại trả 200; nội dung cả 15 file giữ nguyên.
- Wazuh và Dashboard quan sát đúng 7 sự kiện mới. RAM xác nhận tiến trình và dòng lệnh; log/PCAP/ảnh đĩa có manifest và được phân tích đối chiếu.
- Phục hồi đúng snapshot Restic vào đích mới trên VM recovery riêng: 15 file/600 B, SHA-256 15/15 và HTTP 15/15. Người vận hành kiểm tra manifest và mở file_01 trên Firefox thành công.

Đây là simulator đổi tên, không phải ransomware thật hoặc phép thử mã hóa. Pause được điều phối sau ba lần đổi tên; chưa phải Wazuh tự phát hiện rồi diệt ransomware. PCAP được tạo sau containment bằng hai request HTTP kiểm tra có nhãn; không gọi là lưu lượng C2 hay bản ghi tấn công ban đầu.

## 2. Nguồn và môi trường

| Mục | Giá trị của lượt D1 |
|---|---|
| Commit nguồn | `f46ff3290bc46cd63efb20dbb9f558d8b611b196` |
| VM sự cố | `CSATTT-QEMU`, UUID `bd0eab21-9089-4489-a703-b7771e210d5e` |
| Nền sự cố | Ubuntu 24.04.5 LTS, kernel 6.8.0-147-generic; 6 vCPU, 12 GiB RAM, đĩa ảo 70 GiB |
| Project D1 | `csatttn3-d1-8062e27c4236` |
| Bundle D1 | `/home/csattt3/csattt-lab/deploy/d1-f46ff3290bc4-kleoeyr1` |
| Active data | `/home/csattt3/csattt-lab/runtime/fim-probe/sim33-20261105T052825Z-brdrlahd` |
| FIM prefix | `/lab/fim-probe/sim33-20261105T052825Z-brdrlahd/` |
| VM recovery | `CSATTT-RECOVERY-D1`, UUID `2b3b6749-45d6-4518-a953-66d2bdc62fcc`; 2 vCPU, 3 GiB RAM |
| Nguồn OS recovery | Overlay từ checkpoint trước sự cố; không phải cài mới Ubuntu |
| Project phục hồi HTTP | `csatttn3-rfinal-cc6f134b55ce` |
| Workstation image | `csatttn3/workstation:stage1`; dùng image sẵn có, kiểm tra ID/mount/quyền trước start |
| Wazuh | Manager/Indexer/Dashboard 4.14.9 đã ghim digest ở nguồn |
| Công cụ | Restic 0.19.1 trong container; Volatility 3 2.28.2; tcpdump và qemu-img theo biên bản công cụ đi kèm |

VM sự cố được kiểm tra không có NIC ngoài/default route hoặc chia sẻ dữ liệu/clipboard/USB; backup gốc tháo khỏi live/config. Mạng Docker internal vẫn hoạt động trong Ubuntu. Container simulator chỉ nhận bản sao dữ liệu và chương trình đã duyệt, không nhận repo backup hoặc công cụ thu chứng cứ.

Recovery dùng bản sao đĩa backup độc lập, nhận diện bằng serial `D1_BACKUP_COPY` và UUID filesystem `72fd2516-3134-4ff1-abcd-50369a6db1b9`, không chỉ dựa vào tên vda/vdb. Repository mount chỉ đọc; Restic worker dùng `network=none`, chỉ ghi đích `/restore` mới. Workstation recovery phục vụ chính thư mục Restic đã khôi phục trên mạng internal.

## 3. Diễn biến và kết quả

| Kiểm tra | Kết quả |
|---|---|
| Ready/dry-run | HTTP 15/15, FIM 15 tên, bản gốc và active copy 15/15 nguyên vẹn |
| Apply/containment | Đổi tên file_01, file_02, file_03 sang `.simlocked`; Pause được xác nhận lúc 10:18:20.649926 UTC |
| HTTP ảnh hưởng | Ba URL tên cũ trả 404, 12 URL còn lại trả 200; mốc 404 quan sát đầu tiên 10:18:20.686277 UTC |
| FIM | 22 bản ghi: 15 baseline và 7 mới = 3 deleted tên cũ + 3 added tên mới + 1 added note |
| RAM | Thu 11:42:21–11:43:46 UTC; PID 27840, PPID 27802, UID/GID 1000, COMM python, ARGS `python /app/simulator.py --apply` |
| PCAP sau containment | Thu 12:10:55–12:11:05 UTC; file_01 → 404, file_04 → 200/40 B, nhãn `CSATTT-D1-POST-CONTAINMENT-CONTROL/...` |
| Đĩa | Copy lúc hai VM tắt, 12:29:49–12:34:44 UTC; QCOW2 check đạt, nguồn trước/sau/bản sao cùng SHA-256 |
| Phân tích đĩa | Đọc QCOW2/LVM/ext4 ở chế độ chỉ đọc; ba file đổi tên, nội dung 15/15 nguyên vẹn; kiểm tra manifest và đối chiếu log/FIM/PCAP |
| Phục hồi | `postincident_restore_and_http_ok`; đúng snapshot, đích mới, hash 15/15, HTTP 15/15 |
| Kiểm tra vận hành | Người vận hành đã chạy SHA256SUMS, toàn bộ 28 file có kết quả OK; Firefox hiện đúng dữ liệu file_01 từ HTTP recovery |

Volatility chạy offline bằng ISF Ubuntu 6.8.0-147-generic đã cache từ nguồn bên thứ ba, khớp banner và có hash trong biên bản symbol. PsList và PsAux đều thoát 0. Trạng thái container Paused được ghi từ runtime; hai plugin không tự chứng minh containment hoặc phân loại mã độc.

## 4. Snapshot và phép đo thời gian

Snapshot phục hồi:

```text
f54b7415a7237e538dc9733ad0f17ce09a305832592e10c86005b90dce56ab70
```

Snapshot time: `2026-10-30T03:45:55.285507536Z`. Recovery đọc repository offline trên bản sao chỉ đọc; bước này không sử dụng kênh HTTPS backup đã nghiệm thu riêng ở nền.

| Số đo | Kết quả | Cách hiểu |
|---|---|---|
| Bước Restic restore | 1.163 giây | 13:13:50.328041 → 13:13:51.491212 UTC |
| Script recovery | 12.179 giây | Kiểm tra kho/snapshot, restore, hash và HTTP; không gồm khởi động VM |
| Dịch vụ phục hồi được xác minh | 13:13:58.216742 UTC | Đã kiểm tra đủ HTTP 15/15 |
| Khoảng gián đoạn quan sát | 10537.530 giây, khoảng 2 giờ 55 phút 37,530 giây | Từ 404 quan sát đầu tiên đến đủ HTTP 15/15; gồm thu chứng cứ/chờ thao tác |
| Tuổi snapshot tại mốc 404 | 541945.401 giây, khoảng 6 ngày 6 giờ 32 phút 25,401 giây | Tuổi bản sao, không tự đồng nhất với RPO sản xuất |

Không ghi 1.163 hoặc 12.179 giây là RTO toàn bộ sự cố. Khoảng gián đoạn quan sát có mốc rõ nhưng là lượt vận hành tương tác dài, chưa phải benchmark phục hồi lặp lại hoặc đánh giá một mục tiêu RTO đã đặt. Mốc 404 là lúc phép kiểm tra quan sát lỗi, không phải tuyên bố xác định chính xác byte đầu tiên mất khả dụng.

Bộ 15 file giả không thay đổi nội dung giữa snapshot và lượt D1, nên khôi phục khớp 15/15. Điều này không chứng minh RPO = 0 cho dữ liệu khác hoặc dữ liệu đã thay đổi sau snapshot.

## 5. Danh mục chứng cứ

Đường dẫn dưới đây là vị trí của lượt chạy; raw evidence, screenshot và secret được giữ ngoài Git.

| Bộ chứng cứ | Vị trí |
|---|---|
| Incident | `d1-incident-20261105T101817Z-4jrzgf9s` dưới bundle D1 |
| Log/FIM/PCAP | `d1-evidence-20261105T121055Z-2lwchvng` dưới bundle D1 |
| RAM D1 | `/run/media/ndam/New Volume/CSATTT-Lab/ram-d1-20261105T114221Z-nUHRgK` |
| Cold disk D1 | `/run/media/ndam/New Volume/CSATTT-Lab/disk-d1-20261105T122949Z-wsgdktct` |
| Phân tích RAM | `/home/ndam/Documents/ChatGPT/CSATTT/outputs/demo-d1-ram-analysis-20261105-3atjsig1` |
| Phân tích đĩa | `/home/ndam/Documents/ChatGPT/CSATTT/outputs/demo-d1-disk-analysis-20261105-F44yvqtF` |
| Kết quả recovery | `/home/csattt3/csattt-lab/runtime/recovery-final-20261105T131346Z-jwrfr735` trong VM recovery |
| Chương trình recovery | `/home/ndam/Documents/ChatGPT/CSATTT/outputs/demo-d1-recovery-final-20261105-FAAB7hE6` |

SHA-256 các nguồn chính:

```text
ram.elf
1bc85d19545892288559ed31ed721e2e2fc35e57b33a297ccf5fcf85b7801322

disk.qcow2
df243b13660830d4870a83e19b30e02305d7eb277fe2645996b5e57bfc2cd601

postcontainment-http-control.pcap
9a9fccb86577ed0ea16ba3a18e3ef29cdbc0c6e0d5fa9bc1f85b5d253a82a6bc

fim-events.jsonl
56d135fc0c2c7b83bfbaa7a7e9051f3f315067e6c7b78b2c9177b5f11dc80e1b
```

RAM: manifest 9 file đã kiểm tra trên Kali; cold disk: manifest 13 file gồm toàn bộ QCOW2 đã kiểm tra lại trước phân tích. Manifest nội bộ của incident có 21 file và runtime evidence có 22 file được đối chiếu từ bản chụp đĩa. File/dữ liệu phân tích được trích xuất vào workspace riêng; không boot/mount/repair ảnh chứng cứ.

Kết quả recovery được đối chiếu bằng ảnh người vận hành cung cấp: toàn bộ result.json đang hiển thị, kiểm tra SHA256SUMS và trang Firefox. Các số thời gian được chép từ ảnh và kiểm tra lại phép trừ UTC. Raw result/manifest recovery chưa được xuất về Kali, nên không ghi rằng chúng đã được tái tính hash độc lập trên Kali. IP `172.23.0.2` chỉ thuộc lượt recovery này.

## 6. Phần còn lại trước khi chốt khả năng trình bày lại

- Ghi nhận biên bản và runbook trong Git bằng commit/PR; CI của PR mới cần được kiểm tra riêng.
- Tạo lượt diễn tập tiếp theo với dữ liệu/project/đích restore mới; không ghi đè chứng cứ hoặc xóa marker một lần để ép chạy lại.
- Nghiệm thu chạy liên tục Ready → Incident → Evidence → Recovery và cách reset cho buổi trình bày; giữ màn hình SOC.
- Nếu cần bàn giao, xuất metadata/manifest recovery sang vùng chứng cứ ngoài Git và để người nhận kiểm tra hash; giữ nguyên nguồn trong VM.

Giữ VM sự cố tắt và giữ checkpoint `checkpoint-d1-20261105T060137Z-eorcagzm`: overlay recovery đang phụ thuộc vào bản này. Không di chuyển/xóa/sửa checkpoint hoặc gộp overlay vào base trong lúc giữ bộ chứng cứ.

Tham chiếu: [Runbook D1](../runbook-demo.md), [A2](co-lap-vm-a2.md), [S1](simulator-s1.md), [A3](thu-chung-cu-a3.md), [HTTPS backup](https-backup-p3.md).
