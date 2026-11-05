# Runbook A4 — CI và review

## 1. CI làm gì trong dự án

CI là Continuous Integration: GitHub tự chạy bộ kiểm tra cho từng bản thay đổi. Workflow CI chạy trên PR vào develop/main và khi push vào hai nhánh đó. Push một nhánh feature đơn lẻ chưa kích hoạt workflow này; mở PR để có lượt kiểm tra đầu tiên.

Ví dụ: thay cấu hình backup làm mất xác minh CA/tên server thì các test TLS sẽ báo lỗi. Người review mở bước thất bại, kiểm tra nguyên nhân và yêu cầu sửa trước khi merge.

Các bước trong .github/workflows/ci.yml:

| Kiểm tra | Phạm vi và ý nghĩa |
|---|---|
| compileall + Ruff | Cú pháp Python, tên chưa định nghĩa và các lỗi nhóm E9/F63/F7/F82; chưa ép format toàn bộ code cũ |
| Compose config | Parse/interpolate cấu hình nền, backup, monitoring, simulator bằng các file .env.example |
| unittest | Chạy toàn bộ tests/test_*.py; tại đầu A4 có 47 test |
| Bandit | Mã scripts/src, phát hiện mức MEDIUM trở lên với độ tin cậy HIGH; không thay cho review thủ công |
| Gitleaks | Cây nguồn hiện tại và các commit mới của PR/push; che giá trị phát hiện trong log |

Runner là ubuntu-24.04 trên GitHub, Python 3.12. Action được ghim commit SHA; các package Python được ghim phiên bản; binary Gitleaks được kiểm tra SHA-256 trước khi dùng. Workflow chỉ có quyền contents:read và không giữ credential checkout. Không yêu cầu secret của lab.

CI chỉ chạy test với dữ liệu tạm, công cụ phân tích và Compose config. Không chạy Compose up, pull image, simulator --apply, backup/restore thật, mẫu mã độc hoặc VM lab. Các bài nghiệm thu cô lập, Wazuh, acquisition và phục hồi dịch vụ vẫn có bằng chứng riêng.

Nguồn tham khảo: [GitHub Actions cho Python](https://docs.github.com/en/actions/tutorials/build-and-test-code/python), [Ruff](https://docs.astral.sh/ruff/linter/), [Bandit](https://bandit.readthedocs.io/en/latest/man/bandit.html), [Gitleaks](https://github.com/gitleaks/gitleaks).

## 2. Xem CI trên GitHub

1. Push nhánh đang làm rồi mở PR, chọn base develop.
2. Trong PR mở Checks, hoặc vào Actions rồi chọn workflow CI.
3. Chờ hai job Python, Compose, tests and SAST và Secret scan hoàn thành.
4. Nếu đỏ, mở job và bước đầu tiên thất bại; sửa trên cùng nhánh rồi commit/push. PR hiện tại sẽ có lượt kiểm tra mới.
5. Trước merge, kiểm tra kết quả thuộc đúng commit mới nhất, đọc Files changed và xem phạm vi có đúng Issue không.

Ngày 04/11/2026 đã đối chiếu [workflow run 41804635402](https://github.com/Unknown1805/csatttn3/actions/runs/41804635402) cho PR #39, commit `95a005c67521fc8c76613727274b512a15ec075f`: Python/Compose/tests/SAST đạt trong 17 giây; Secret scan đạt trong 8 giây. PR #39 đã merge thành `080c336600aa5b06557f9f2e57ce9828791fe587`. Đây là kết quả kiểm tra mã nguồn; chưa nghiệm thu demo tích hợp. Chạy lại trên bản chốt demo khi code/cấu hình thay đổi.

## 3. Chạy các kiểm tra trên máy làm code

Chạy tại thư mục repo trên Linux hoặc WSL, có Python 3.12+, OpenSSL và Docker Compose v2. Không cần bật Docker daemon cho các lệnh config trong runbook này. Tạo môi trường công cụ riêng:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r .github/requirements-ci.txt
.venv/bin/python -m compileall -q scripts src tests
.venv/bin/ruff check --select E9,F63,F7,F82 scripts src tests
.venv/bin/python -m unittest discover -s tests -p 'test_*.py' -v
.venv/bin/bandit -r scripts src --severity-level medium --confidence-level high
```

Kiểm tra cấu hình:

```bash
docker compose --env-file lab/.env.example -f lab/compose.yaml config --quiet
docker compose --env-file lab/.env.backup.example -f lab/compose.yaml -f lab/compose.backup.yaml config --quiet
docker compose --env-file lab/.env.monitoring.example -f lab/compose.yaml -f lab/compose.monitoring.yaml config --quiet
docker compose --env-file lab/.env.simulator.example -f lab/compose.yaml -f lab/compose.incident.yaml --profile incident config --quiet
```

Nếu máy đã cài Gitleaks, chạy gitleaks dir --redact=100 --no-banner --ignore-gitleaks-allow . để kiểm tra cây nguồn. CI dùng bản 8.30.1 đã ghim và quét thêm các commit mới. Phiên bản máy cá nhân có thể khác; khi kết quả lệch, đối chiếu bản trên CI trước khi kết luận.

## 4. Xử lý khi kiểm tra thất bại

- Lint/cú pháp: đọc file và dòng được báo; sửa lỗi rồi chạy lại bước tương ứng. Không cần sửa format hàng loạt để làm mất dấu thay đổi thực sự.
- Compose: kiểm tra file .env.example và biểu thức biến; chỉ dùng đường dẫn mẫu trong Git. Parse thành công chưa xác nhận cấu hình đang chạy hoặc an toàn.
- Test: đối chiếu expected/actual; sửa hành vi hoặc test khi yêu cầu đã thay đổi và được giải thích. Không xóa assertion bảo vệ dữ liệu/TLS để có dấu xanh.
- Bandit: đọc rule và luồng dữ liệu, sửa nguyên nhân. Nếu là trường hợp kiểm thử có chủ đích, ghi lý do tại đúng chỗ và chỉ giới hạn rule cần thiết; không tắt toàn bộ scanner.
- Gitleaks: giữ log ở chế độ redact; xác định file/commit, xử lý credential thật nếu có, rồi loại giá trị khỏi thay đổi. Không dán secret vào Issue/PR. Không dùng allowlist rộng hoặc --exit-code 0 để bỏ qua phát hiện.
- Nếu lỗi tải công cụ/network, phân biệt với lỗi mã nguồn và có thể re-run job. Không đổi nhánh/merge chỉ để bỏ qua lượt thất bại.

Lượt quét commit dùng base..head của PR hoặc before..sha của push; lần push khởi tạo không có base chỉ quét commit hiện tại cộng cây nguồn. Đây không phải quét toàn bộ lịch sử. Mật khẩu lab P3/P4 từng có trong lịch sử đã được ghi nhận trong báo cáo P4; CI mới không xóa hay thu hồi lịch sử đó. Tiếp tục giữ chúng ở trạng thái đã lộ và không tái sử dụng.

## 5. Checklist review và bằng chứng A4

- [ ] Issue mô tả đầu ra và phạm vi; PR ghi rõ đã thay đổi gì.
- [ ] Files changed đúng phạm vi; không chứa dữ liệu thật, chứng cứ thô, mật khẩu hoặc khóa riêng.
- [ ] CI của commit mới nhất đạt cả hai job; lưu run URL và SHA.
- [ ] Mọi mục bỏ qua/giới hạn kiểm tra đã có lý do cụ thể.
- [ ] Runbook ghi lệnh, kết quả mong đợi và điều kiện dừng; thành viên được giao có thể thao tác lại phần của mình.
- [ ] Kết quả VM/demo được đối chiếu bằng chứng thực tế; không lấy dấu xanh CI để thay thế.

Nhữ Duy Anh Minh review và merge PR của thành viên; với PR do Minh thực hiện, Minh tự kiểm tra theo checklist, không bắt buộc Phong review.

Comment kết quả khi có lượt chạy thật:

```text
Đã kiểm tra commit: <SHA thực tế>
Workflow run: <URL thật trong Actions>
Python/Compose/tests/SAST: <kết quả>
Secret scan: <kết quả và phạm vi>
Runbook: <phần đã thao tác lại và người thực hiện>
Giới hạn còn lại: <ghi đúng thực tế>
```
