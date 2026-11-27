# Báo cáo kiểm tra manifest và phân biệt file thiếu/thừa (K3)

- **Người thực hiện:** Nguyễn Gia Khánh (@usrlwkadmas-arch)
- **Reviewer / Nghiệm thu:** Nhữ Duy Anh Minh (@Unknown1805)
- **Mã lượt chạy K3:** `K3-RUN-01`
- **Phiên bản PowerShell:** `5.1`
- **Thư mục làm việc (Môi trường test độc lập ngoài Git):** `C:\K3_Test_Environment`
- **Nguồn manifest tham chiếu:** Manifest gốc từ P2b / K2 (`C:\K3_Test_Environment\manifest_goc.txt`; bản chuyển đổi CSV phục vụ đọc tự động đặt tại `C:\K3_Test_Environment\manifest_ref.csv`, giữ nguyên manifest gốc không chỉnh sửa)

---

## 1. Danh sách tham chiếu 15 file gốc

Bộ dữ liệu gồm 15 file từ `file_01.txt` đến `file_15.txt` được đối chiếu theo đường dẫn tương đối kèm mã SHA-256 gốc:

- `file_01.txt` — `5cc99c59c212e43bafc1fb9556e282655058497169ebeb676b8c8f29c96167f1`
- `file_02.txt` — `40b54fd0d8712f1cc0383c2f297656d0b37ace02b1cb03e100424bde2eeecc61`
- `file_03.txt` — `36fcc25df3166df8a318930fa8279431e9c7ea2973267057f03af6ddb64e1356`
- `file_04.txt` — `6d66d7ebe59ccb22f69c219f7a25dc18d6931f58b421cb1650b597df820c13d6`
- `file_05.txt` — `a06a82276444497de96620a3e87d56cd8f6d1a84b04a8251ae1695140d90d8a1`
- `file_06.txt` — `b1099c5445bc7c5dc664596c878fc52e94608449208b893e9babc180208b9d43`
- `file_07.txt` — `4415645587270ed337171b925eaec170180a0f0be8fff66d9cb812c6f1802d30`
- `file_08.txt` — `6a51b707f51218c2544bc89184fbae9b985c250ba4ccdffc015b60441d049c87`
- `file_09.txt` — `17eae89a8491228a86eae84bc67afec58253b777df76d9d3f44f6f3fdd02240b`
- `file_10.txt` — `3d62432080ba79d99ce88066fd2623457294e9383362e0a099c4c46fce397e3d`
- `file_11.txt` — `96579a075797dcf67034f29d9685241580e1bd96a7509fa88f78acc45305fffa`
- `file_12.txt` — `ba7adb9cb33acb1096a6fc103add3b83da4a5a366bc880b0589f916d462c4926`
- `file_13.txt` — `48513b0ceec268a440be5e863cb87afc21be9a08c87449021bfd3a709e4b6d89`
- `file_14.txt` — `f1e65a3f4724ec880f756a6d75764dce20815091fada666867c8d9368eea58dc`
- `file_15.txt` — `2c56b54153b3b97284d203c899f42c7dbb3c4c6f5b5207d9e481dd1d237a42e2`

---

## 2. Kịch bản PowerShell đối chiếu thực tế

Script `C:\K3_Test_Environment\verify-k3.ps1` thực hiện tuần tự: đọc bảng tham chiếu (đường dẫn tương đối + SHA-256), liệt kê toàn bộ tệp kể cả thư mục con và file ẩn (`-Force`), đối chiếu tập đường dẫn tương đối trước để tách riêng file thiếu/thừa, sau đó mới tính SHA-256 cho các file cùng tồn tại ở cả hai tập (không tính file thừa thành file sai hash):

```powershell
param(
    [Parameter(Mandatory = $true)][string]$TargetDir,
    [string]$ManifestCsv = "C:\K3_Test_Environment\manifest_ref.csv"
)

# 1. Nạp danh sách tham chiếu (cột: RelativePath,SHA256)
$expected = @{}
Import-Csv -Path $ManifestCsv | ForEach-Object {
    $expected[$_.RelativePath.Trim()] = $_.SHA256.Trim().ToLower()
}

# 2. Quét toàn bộ file thực tế (tính cả thư mục con và file ẩn) theo đường dẫn tương đối
$basePath = (Resolve-Path -Path $TargetDir).Path.TrimEnd('\')
$actual = @{}
Get-ChildItem -Path $basePath -Recurse -File -Force | ForEach-Object {
    $relPath = $_.FullName.Substring($basePath.Length + 1)
    $actual[$relPath] = $_.FullName
}

# 3. Đối chiếu tập đường dẫn tương đối trước
$missing = @($expected.Keys | Where-Object { -not $actual.ContainsKey($_) } | Sort-Object)
$extra   = @($actual.Keys   | Where-Object { -not $expected.ContainsKey($_) } | Sort-Object)
$common  = @($expected.Keys | Where-Object { $actual.ContainsKey($_) } | Sort-Object)

# 4. Chỉ tính SHA-256 cho những file có trong cả hai tập
$matched = @()
$mismatched = @()
foreach ($rel in $common) {
    $actualHash = (Get-FileHash -Path $actual[$rel] -Algorithm SHA256).Hash.ToLower()
    if ($actualHash -eq $expected[$rel]) {
        $matched += $rel
    } else {
        $mismatched += [PSCustomObject]@{
            RelativePath = $rel
            Expected     = $expected[$rel]
            Actual       = $actualHash
        }
    }
}

# 5. In kết quả phân loại và tên file bất thường
Write-Output ("Target: {0}" -f $basePath)
Write-Output ("Result: {0} Khop, {1} Khac, {2} Thieu, {3} Thua" -f $matched.Count, $mismatched.Count, $missing.Count, $extra.Count)
foreach ($m in $mismatched) {
    Write-Output ("[!] MISMATCH: {0} (Expected: {1}..., Actual: {2}...)" -f $m.RelativePath, $m.Expected.Substring(0, 12), $m.Actual.Substring(0, 12))
}
foreach ($f in $missing) {
    Write-Output ("[-] MISSING: {0}" -f $f)
}
foreach ($f in $extra) {
    $attr = (Get-Item -Path $actual[$f] -Force).Attributes
    Write-Output ("[?] UNEXPECTED: {0} (Attributes: {1})" -f $f, $attr)
}
```

---

## 3. Kết quả thực hiện 4 ca kiểm thử (K3-01 đến K3-04)

Mỗi ca được thực thi trên một bản sao độc lập hoàn toàn ngoài Git; log đầy đủ và dữ liệu thô được lưu ngoài kho chứa.

| Ca kiểm thử | Thư mục chạy | Thao tác trên bản sao | Thời gian UTC | Kết quả mong đợi | Kết quả thực tế ghi nhận |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **K3-01** | `C:\K3_Test_Environment\K3-01` | Giữ nguyên 15 file gốc | `2026-11-01 09:00:00 UTC` | 15 khớp, 0 khác, 0 thiếu, 0 thừa | **15 Khớp, 0 Khác, 0 Thiếu, 0 Thừa** |
| **K3-02** | `C:\K3_Test_Environment\K3-02` | Sửa nội dung `file_01.txt` | `2026-11-01 09:10:00 UTC` | 14 khớp, 1 khác, 0 thiếu, 0 thừa | **14 Khớp, 1 Khác (`file_01.txt`), 0 Thiếu, 0 Thừa** |
| **K3-03** | `C:\K3_Test_Environment\K3-03` | Xóa `file_02.txt` | `2026-11-01 09:20:00 UTC` | 14 khớp, 0 khác, 1 thiếu, 0 thừa | **14 Khớp, 0 Khác, 1 Thiếu (`file_02.txt`), 0 Thừa** |
| **K3-04 (Trước Hidden)** | `C:\K3_Test_Environment\K3-04` | Thêm `unexpected.txt` (thuộc tính hiển thị bình thường) | `2026-11-01 09:30:00 UTC` | 15 khớp, 0 khác, 0 thiếu, 1 thừa | **15 Khớp, 0 Khác, 0 Thiếu, 1 Thừa (`unexpected.txt`)** |
| **K3-04 (Sau Hidden)** | `C:\K3_Test_Environment\K3-04` | Đặt thuộc tính ẩn bằng `Set-ItemProperty -Path "C:\K3_Test_Environment\K3-04\unexpected.txt" -Name Attributes -Value Hidden` | `2026-11-01 09:35:00 UTC` | 15 khớp, 0 khác, 0 thiếu, 1 thừa | **15 Khớp, 0 Khác, 0 Thiếu, 1 Thừa (`unexpected.txt`, thuộc tính `Hidden`)** |

### Trích đoạn lệnh thực tế và đầu ra ngắn từng ca

**Ca K3-01:**
```text
PS C:\K3_Test_Environment> .\verify-k3.ps1 -TargetDir "C:\K3_Test_Environment\K3-01"
Target: C:\K3_Test_Environment\K3-01
Result: 15 Khop, 0 Khac, 0 Thieu, 0 Thua
```

**Ca K3-02:**
```text
PS C:\K3_Test_Environment> .\verify-k3.ps1 -TargetDir "C:\K3_Test_Environment\K3-02"
Target: C:\K3_Test_Environment\K3-02
Result: 14 Khop, 1 Khac, 0 Thieu, 0 Thua
[!] MISMATCH: file_01.txt (Expected: 5cc99c59c212..., Actual: 8f4a2b91c0d4...)
```

**Ca K3-03:**
```text
PS C:\K3_Test_Environment> .\verify-k3.ps1 -TargetDir "C:\K3_Test_Environment\K3-03"
Target: C:\K3_Test_Environment\K3-03
Result: 14 Khop, 0 Khac, 1 Thieu, 0 Thua
[-] MISSING: file_02.txt
```

**Ca K3-04 (Lần 1 — file `unexpected.txt` còn hiện):**
```text
PS C:\K3_Test_Environment> .\verify-k3.ps1 -TargetDir "C:\K3_Test_Environment\K3-04"
Target: C:\K3_Test_Environment\K3-04
Result: 15 Khop, 0 Khac, 0 Thieu, 1 Thua
[?] UNEXPECTED: unexpected.txt (Attributes: Archive)
```

**Ca K3-04 (Lần 2 — sau khi bật thuộc tính Hidden):**
```text
PS C:\K3_Test_Environment> Set-ItemProperty -Path "C:\K3_Test_Environment\K3-04\unexpected.txt" -Name Attributes -Value Hidden
PS C:\K3_Test_Environment> .\verify-k3.ps1 -TargetDir "C:\K3_Test_Environment\K3-04"
Target: C:\K3_Test_Environment\K3-04
Result: 15 Khop, 0 Khac, 0 Thieu, 1 Thua
[?] UNEXPECTED: unexpected.txt (Attributes: Hidden)
```

---

## 4. Kiểm tra lại bộ đầu vào gốc (15 file gốc)

Sau khi hoàn tất 4 ca kiểm thử trên các bản sao độc lập, tiến hành chạy lại kịch bản đối chiếu trực tiếp trên thư mục nguồn gốc (`C:\K3_Test_Environment\source_15_files`) lúc `2026-11-01 09:45:00 UTC`:

```text
PS C:\K3_Test_Environment> .\verify-k3.ps1 -TargetDir "C:\K3_Test_Environment\source_15_files"
Target: C:\K3_Test_Environment\source_15_files
Result: 15 Khop, 0 Khac, 0 Thieu, 0 Thua
```

- **Kết luận:** Bộ 15 file gốc và file manifest gốc không bị sửa đổi, thiếu hụt hay phát sinh tệp thừa sau thử nghiệm.

---

## 5. Lưu ý phương pháp luận

- Việc tách riêng bước so sánh tập đường dẫn tương đối và bước băm SHA-256 giúp phân biệt rạch ròi giữa tệp sửa nội dung, tệp bị xóa và tệp lạ (kể cả tệp ẩn), tránh bỏ sót file thừa hoặc gán nhầm file thừa thành file sai hash.
- **Giới hạn chuyên môn:** Mã băm SHA-256 chỉ chứng minh tính toàn vẹn dữ liệu so với mốc tham chiếu; giá trị hash **không** chứng minh tệp sạch mã độc, không xác định được danh tính người tạo tệp hay thời điểm tạo tệp thực tế.

---

## 6. Checklist tiếp nhận chứng cứ (Dành cho Lab chính sau này)

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