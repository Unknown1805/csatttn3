# Hướng dẫn đóng góp và làm việc nhóm CSATTT N3

Repo: [Unknown1805/csatttn3](https://github.com/Unknown1805/csatttn3). Đề tài: Pháp chứng số và xử lý sự cố do ransomware tấn công trong môi trường mô phỏng bằng Docker.

## 1 Quy tắc và phân công của nhóm

Nhữ Duy Anh Minh (`Unknown1805`) phụ trách kỹ thuật chính, giao Issue và duyệt tích hợp. Mỗi thành viên dùng tài khoản riêng, sửa đúng file được giao, cập nhật tiến độ và trình bày được phần mình làm.

| Người | Phần việc chính |
| --- | --- |
| Nhữ Duy Anh Minh | VM/Docker và mạng, simulator an toàn, RAM/ảnh đĩa, CI và tích hợp |
| Nguyễn Vũ Tuấn Phong | Backup/restore, đo RTO/RPO, chạy lại runbook và review phần được giao |
| Trần Bảo Minh | Log/PCAP, timeline có nguồn chứng cứ và kiểm tra cô lập theo runbook |
| Nguyễn Gia Khánh | Tự kiểm tra SHA-256 trên bản sao, manifest, bàn giao và minh chứng GitHub |

Mỗi công việc: Issue → nhánh feature từ develop → commit và comment → PR vào develop → người khác review → sửa góp ý → Minh merge và nghiệm thu. Không push trực tiếp vào main hoặc develop theo quy định của nhóm. PR do Minh viết cần Phong hoặc thành viên khác review trong phạm vi hiểu được.

Luồng khuyến nghị: Phong/Bảo Minh dùng Git và VS Code; Khánh bắt đầu bằng GitHub web. Các bạn mới chỉ nhận việc nhỏ trước; lab dùng dữ liệu giả, simulator chỉ đổi tên file và tạo thông báo, không mã hóa hoặc tự lây lan.

## 2 Tài khoản GitHub, lời mời và quyền cộng tác

Mỗi người dùng một tài khoản GitHub riêng để lịch sử thể hiện đúng người làm. Gửi Minh username, không gửi mật khẩu, mã xác thực, token hoặc khóa SSH riêng. Chưa có tài khoản thì đăng ký tại [GitHub](https://github.com/signup), xác minh email và ghi lại cách khôi phục tài khoản của mình.

Minh mở repo `Unknown1805/csatttn3`, vào Settings → Collaborators → Add people, tìm đúng username rồi gửi lời mời. Thành viên đăng nhập đúng tài khoản được mời, mở thông báo hoặc email và chấp nhận. Chỉ gửi đường dẫn repo chưa thay cho việc mời vào repo riêng tư. GitHub Free cho phép thêm cộng tác viên vào repo riêng tư; nhóm không cần mua Pro để cùng sửa file và tạo PR. [Hướng dẫn mời thành viên](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/repository-access-and-collaboration/inviting-collaborators-to-a-personal-repository)

Sau khi nhận lời mời, mở repo trên trình duyệt. Khi xem được danh sách file và Issue được giao, comment xác nhận đã vào được. Nếu gặp 404, kiểm tra tài khoản và trạng thái lời mời trước khi báo Minh; đừng tạo repo khác để làm thay.

Quy định của nhóm là chỉ Minh merge và không sửa thẳng `main` hoặc `develop`. Với repo cá nhân riêng tư dùng Free, đây là quy định tự tuân thủ; tài liệu không khẳng định GitHub đã cưỡng chế chặn push hoặc bắt buộc review. Tính năng bảo vệ nhánh riêng tư cần gói hỗ trợ tương ứng. [Phạm vi bảo vệ nhánh](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)

Quyền thành viên của repo, đăng nhập Git trên máy và quyền kết nối ứng dụng đọc repo là ba việc khác nhau. Hoàn tất một việc chưa chứng minh hai việc còn lại đã đủ quyền.

Repo cá nhân có hai mức owner và collaborator, không có vai trò Maintainer riêng. Nhữ Duy Anh Minh chốt với giảng viên cách đáp ứng yêu cầu Maintainer của đề bài trước khi thay đổi loại repo hoặc gói dịch vụ. Việc mời collaborator chưa tự hoàn thành mọi yêu cầu GitHub của đề bài. [Quyền repo cá nhân](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/repository-access-and-collaboration/permission-levels-for-a-personal-account-repository)

## 3 Vai trò, nhánh và file mỗi người phụ trách

Minh làm kỹ thuật chính: chuẩn bị nền, viết phần mã quan trọng, giao việc, cung cấp đầu vào, kiểm tra và tích hợp. Thành viên nhận một đầu ra nhỏ, hiểu được nội dung mình nộp và sửa theo góp ý. Không giao chỉ tiêu tạo thật nhiều commit hoặc comment hình thức.

- Tuấn Phong ưu tiên học Git local và trực tiếp chạy backup, restore, đo RTO/RPO theo runbook đã review. Phong có thể review tài liệu hoặc thay đổi phù hợp do Minh viết.
- Bảo Minh dùng Git local sau khi tập một vòng cùng Minh; phụ trách timeline, nguồn log và phần kiểm tra nhỏ được giao rõ.
- Gia Khánh bắt đầu bằng GitHub web, tạo bảng danh mục chứng cứ và nhật ký tiếp nhận. Git local là bước học thêm, chưa phải điều kiện nhận việc đầu tiên.

Mỗi Issue ghi đúng file được sửa, ví dụ lần lượt là `docs/thanh-vien/tuan-phong-khoi-phuc.md`, `bao-minh-timeline.md` và `gia-khanh-chung-cu.md` trong cùng thư mục. Minh quản lý chính README, CHANGELOG, `src/`, `lab/`, `scripts/` và `.github/`; sửa thêm phải được giao cụ thể.

`main` giữ bản ổn định; `develop` nhận các phần đã review; `feature/<số-issue>-<tên-ngắn>` dành cho một công việc. Một nhánh Git không phải một thư mục mới: đổi nhánh làm Git đổi trạng thái file trong cùng thư mục làm việc. Nhánh không cách ly chương trình đang chạy hoặc dữ liệu ngoài Git. [Khái niệm nhánh Git](https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell)

Luồng nhóm là nhận Issue → nhánh riêng → commit và comment → PR vào `develop` → review → Minh merge. Khi chốt mốc, tạo PR riêng từ `develop` vào `main`. Mỗi người giữ tài khoản riêng ngay cả khi cùng xem một buổi lab.

## 4 Chuẩn bị Git và VS Code trên Windows

Phong và Bảo Minh chọn mục này nếu dùng Windows. Khánh làm bằng trình duyệt có thể bỏ qua. Trước khi cài, mở terminal và kiểm tra từng lệnh:

```text
git --version
code --version
git credential-manager --version
```

Nếu Git, VS Code và GCM đã chạy, không cần cài lại. Git có sẵn nhưng thiếu GCM thì cần bổ sung/cấu hình trước clone HTTPS. Nếu thiếu Git, tải bộ cài phù hợp từ [trang Git cho Windows](https://git-scm.com/install/windows), giữ khả năng dùng Git từ terminal và Git Credential Manager. Đóng rồi mở terminal mới sau cài để nhận PATH.

VS Code tải từ [trang chính thức](https://code.visualstudio.com/download). Với máy cá nhân có thể dùng User Installer; mở bộ cài, đọc các lựa chọn và bật lệnh `code` trong PATH khi được cung cấp. Sau cài mở VS Code, không cần cài thêm extension hoặc mua Copilot để sửa tài liệu. [Hướng dẫn Windows](https://code.visualstudio.com/docs/setup/windows)

Luồng mặc định cho máy mới là HTTPS và đăng nhập bằng trình duyệt qua Git Credential Manager. Git for Windows có kèm GCM. Khi thao tác repo yêu cầu xác thực, đăng nhập đúng tài khoản đã nhận lời mời và hoàn tất xác thực hai bước nếu tài khoản bật tính năng đó. [GCM trên Windows](https://docs.github.com/en/get-started/git-basics/caching-your-github-credentials-in-git?platform=windows)

Không nhập mật khẩu tài khoản GitHub vào ô Password của Git terminal. Nếu chỉ xuất hiện câu hỏi Username/Password mà không có luồng trình duyệt, dừng để Minh kiểm tra credential helper; không nhét token vào URL hoặc gửi token qua chat. Nhóm không yêu cầu mọi thành viên tạo SSH key. Minh đang dùng SSH thành công có thể giữ cách đó cho máy của mình.

## 5 Chuẩn bị trên Linux hoặc Kali

Chỉ làm mục này trên máy Linux. Mở terminal, kiểm tra công cụ hiện có; bản cài Git trên Windows không tự trở thành Git của Kali:

```text
git --version
code --version
```

Nếu Git và VS Code đã có, không cài lại; vẫn hoàn tất phần xác thực ở cuối mục trước khi clone. Nếu thiếu Git trên Kali, người dùng tự chạy từng lệnh sau:

```text
sudo apt update
sudo apt install git
```

Đọc danh sách gói trước khi xác nhận cài. Kali dùng trình quản lý APT; Git cũng công bố cách cài theo bản phân phối Linux. [Hướng dẫn Git trên Linux](https://git-scm.com/download/linux)

Nếu thiếu VS Code, tải gói `.deb` đúng kiến trúc từ trang VS Code rồi dùng trình cài đồ họa, hoặc nhờ Minh hướng dẫn cài đúng tên file. Lệnh mẫu dưới phải thay `TEN_GOI_CODE.deb` bằng tên gói thật và chạy tại thư mục chứa gói:

```text
sudo apt install ./TEN_GOI_CODE.deb
```

Đọc câu hỏi của bộ cài về nguồn cập nhật; không chạy thêm script lấy từ trang lạ. [Hướng dẫn VS Code trên Linux](https://code.visualstudio.com/docs/setup/linux)

Với HTTPS, nếu GCM đã hoạt động thì dùng cấu hình có sẵn. Máy Linux chưa có GCM có thể chọn GitHub CLI, làm riêng luồng sau:

```text
gh --version
```

Nếu thiếu `gh`, trên Kali chạy `sudo apt install gh` sau khi đã cập nhật APT; bản phân phối khác dùng [hướng dẫn cài GitHub CLI](https://github.com/cli/cli/blob/trunk/docs/install_linux.md). Sau đó từng bước:

```text
gh auth login --hostname github.com --git-protocol https --web
gh auth setup-git --hostname github.com
gh auth status
```

Làm theo trình duyệt bằng tài khoản được mời; mã xác thực chỉ nhập tại trang GitHub chính thức. Nếu CLI báo lưu token dạng plaintext do thiếu kho credential, dừng và nhờ Minh thiết lập nơi lưu an toàn trước khi tiếp tục. Không gửi mã đăng nhập/token lên nhóm; không dùng `sudo git clone`. [GitHub CLI authentication](https://docs.github.com/en/github-cli/github-cli/authenticating-with-github-cli)

## 6 Clone repo và đặt tên tác giả commit

Clone là lấy repo về máy, thường chỉ làm một lần cho một thư mục. Repo của nhóm là riêng tư; URL HTTPS không làm nó thành repo công khai. Repo công khai thường cho phép clone không đăng nhập, còn repo nhóm cần tài khoản có quyền và cơ chế xác thực đã chuẩn bị. [Hướng dẫn clone](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository)

Tạo hoặc mở thư mục cha muốn chứa dự án bằng trình quản lý file, rồi mở terminal tại đó. Thư mục đích `csatttn3` phải chưa tồn tại hoặc đang trống. Chạy:

```text
git clone https://github.com/Unknown1805/csatttn3.git
cd csatttn3
git remote -v
```

Nếu GCM mở trình duyệt, đăng nhập đúng tài khoản và hoàn tất yêu cầu xác thực. Nếu bị hỏi mật khẩu trong terminal, dừng và báo Minh. Khi đã clone, không chạy lại `git init` hoặc thêm `origin` lần nữa. Nếu Git báo thư mục đã tồn tại, kiểm tra bản repo có sẵn; không xóa thư mục chỉ để clone lại.

Trong repo, thay hai chuỗi viết hoa dưới đây bằng thông tin của chính bạn trước khi chạy:

```text
git config --local user.name "HO TEN CUA BAN"
git config --local user.email "EMAIL CUA BAN"
git config --get user.name
git config --get user.email
```

Tên và email dùng ghi tác giả commit, không đăng nhập hay cấp quyền repo. Dùng email đã liên kết với GitHub hoặc địa chỉ `noreply` GitHub cung cấp. `--local` áp dụng riêng repo; `--global` đặt mặc định cho các repo của cùng tài khoản hệ điều hành. Cấu hình local được ưu tiên. Kiểm tra tại máy, không cần gửi email lên nhóm. [Cấu hình Git](https://git-scm.com/docs/git-config)

## 7 Mở repo trong VS Code và hiểu trạng thái file

Từ terminal đang ở thư mục `csatttn3`, chạy:

```text
code .
```

Dấu chấm nghĩa là thư mục hiện tại. Nếu không nhận lệnh, mở VS Code rồi chọn File → Open Folder và chọn đúng thư mục repo; không cần tạo dự án mới. Trên Linux tên lệnh cũng là `code`, không phải tên một thư mục. [Mở mã nguồn bằng VS Code](https://code.visualstudio.com/docs/getstarted/getting-started)

Explorer bên trái phải hiện thư mục gốc `csatttn3`, README và các thư mục dự án. Terminal tích hợp mở bằng Terminal → New Terminal. Trước khi chạy lệnh Git, nhìn đường dẫn và kiểm tra:

```text
git status --short --branch
```

Dòng `##` cho biết nhánh. `??` là file mới chưa theo dõi; ` M` là file đã theo dõi vừa sửa nhưng chưa add; `A ` là file mới đã chọn để commit. Chấm trắng trên tab VS Code thường báo nội dung chưa lưu. Ctrl+S lưu file; commit ghi một mốc lịch sử; push gửi commit lên GitHub. [Đọc trạng thái Git](https://git-scm.com/docs/git-status)

Thành viên chỉ sửa đúng file ghi trong Issue. Tài liệu `.md` có thể xem bằng Ctrl+Shift+V. Dùng UTF-8 cho tiếng Việt và LF cho mã nguồn theo `.gitattributes`; các lựa chọn này hiện ở thanh trạng thái của VS Code. LF là `\n`, còn CRLF là `\r\n`. [Thuộc tính xuống dòng](https://git-scm.com/docs/gitattributes)

Với checkout dùng chung Windows/Kali của Minh, kiểm tra đúng ổ gắn và nhánh mỗi lần đổi hệ điều hành. Giữ credential riêng cho từng hệ điều hành; không để hai công cụ Git thao tác đồng thời lên cùng checkout. Đọc `.git` như phần Git tự quản lý, không sửa thủ công bên trong.

## 8 Nhận Issue và bắt đầu một nhánh local sạch

Đọc Issue trước khi sửa: ai làm, đầu vào nào được dùng, file nào được sửa, hạn gửi bản đầu và tiêu chí nghiệm thu. Comment nhận việc, hỏi ngay phần còn thiếu. Chỉ Issue #1 đã được xác nhận trong bước chuẩn bị; **Issue #7 và mọi tên nhánh dưới đây là ví dụ**, phải thay bằng nhiệm vụ thật.

Trong terminal ở repo, thực hiện từng lệnh và dừng nếu có lỗi:

```text
git status --short --branch
```

Nếu có file sửa, file chưa theo dõi, nội dung chưa commit hoặc xung đột, giữ nguyên và báo Minh. Chỉ khi trạng thái sạch mới tiếp tục:

```text
git switch develop
git pull --ff-only origin develop
git status --short --branch
```

Sau pull, cần thấy `## develop...origin/develop`, không có ahead/behind và không có dòng file thay đổi. `--ff-only` tránh tự tạo một lần gộp khi lịch sử đã phân kỳ; nếu lệnh từ chối, gửi lỗi cho Minh. Không tự đổi thành reset hoặc force push. [Cập nhật nhánh bằng pull](https://git-scm.com/docs/git-pull)

Khi checkpoint đạt, tạo nhánh của Issue:

```text
git switch -c feature/7-danh-muc-chung-cu
```

Nhánh mới bắt đầu từ `develop` vừa đồng bộ. Nếu nhánh đã tồn tại, đừng tạo tên khác để né lỗi; hỏi Minh hoặc chuyển về đúng nhánh đang làm sau khi kiểm tra trạng thái. Nhánh `feature/1-huong-dan-github` từng được tạo cho việc hướng dẫn, nên người đang tiếp tục Issue #1 phải xem trạng thái hiện tại trước.

Sửa và lưu đúng file trong VS Code. Một việc mới dùng nhánh mới; góp ý cho PR đang mở tiếp tục ở cùng nhánh. Việc tạo nhánh chưa tạo file, chưa commit và chưa gửi thay đổi lên GitHub. [Quản lý nhánh](https://docs.github.com/en/pull-requests/how-tos/commit-changes/managing-branches-within-your-repository)

## 9 Chọn file, commit, push và gửi PR để review

Ví dụ này tiếp tục dùng Issue #7 giả định. Sau khi lưu file, chọn đích danh file của nhiệm vụ, rồi đọc phần sắp commit:

```text
git status --short
git add -- docs/thanh-vien/gia-khanh-chung-cu.md
git --no-pager diff --cached --stat
git --no-pager diff --cached
git --no-pager diff --cached --check
```

`git add` chọn nội dung đã lưu; nếu sửa tiếp thì cần add lại. `--cached` xem bản đã chọn. `--check` không in gì chỉ có nghĩa không phát hiện lỗi khoảng trắng hoặc dấu xung đột; vẫn phải đọc nội dung và đối chiếu yêu cầu. [Git add](https://git-scm.com/docs/git-add), [Git diff](https://git-scm.com/docs/git-diff)

Khi đã kiểm tra và không có file lạ, chạy:

```text
git commit -m "docs: tạo danh mục chứng cứ (#7)"
git push -u origin feature/7-danh-muc-chung-cu
```

Mở GitHub → Pull requests → New pull request. Chọn **base: develop**, **compare: nhánh feature của mình**; xem Files changed trước khi tạo. Ghi “Liên quan #7”, nội dung đã làm, kiểm tra thật sự thực hiện và phần còn thiếu; mời `Unknown1805` review. Dán PR vào Issue và comment sau mỗi đợt thay đổi. [Tạo PR](https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/creating-a-pull-request)

Sau góp ý, sửa cùng nhánh, add đúng file, commit mới và push; PR tự cập nhật. Minh đọc Files changed, comment hoặc Request changes, Approve khi đạt rồi merge. PR do Minh viết được Phong review trong phạm vi hiểu được; cần thêm người kiểm tra khi vượt khả năng. Tác giả không tự Approve PR của mình. [Duyệt PR](https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/approving-a-pull-request-with-required-reviews)

Với `main` là default branch, PR vào `develop` không tự đóng Issue bằng `Closes #7`. Minh nghiệm thu, dẫn PR đã merge và đóng thủ công. [Điều kiện đóng Issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue)

## 10 Luồng GitHub web cho Khánh và người mới

Luồng này chỉ cần trình duyệt, phù hợp các biểu mẫu tài liệu đầu tiên của Khánh. Bảo Minh hoặc Phong cũng có thể dùng khi chưa chuẩn bị máy local. Không cần cài Git, cấu hình SSH hay chạy lệnh push để sửa tài liệu trên web.

1. Mở repo bằng tài khoản đã được mời, vào Issues và đọc việc được giao. Comment xác nhận đã nhận đầu vào và hạn gửi bản đầu.
2. Vào Code, chọn `develop` trong ô nhánh; đợi danh sách file tải lại. Từ đó tạo nhánh của Issue, ví dụ `feature/7-danh-muc-chung-cu`. Số 7 chỉ là minh họa.
3. Kiểm tra ô nhánh đã hiện tên feature. Chọn Add file → Create new file, nhập đường dẫn Minh giao từ thư mục gốc, chẳng hạn `docs/thanh-vien/gia-khanh-chung-cu.md`.
4. Điền biểu mẫu, xem Preview và đối chiếu các cột. Dữ liệu chưa có thì ghi “Đang chờ đầu vào”; không tự điền số liệu để bảng trông hoàn chỉnh.
5. Bấm Commit changes, viết thông điệp tiếng Việt có số Issue. Khi đã đứng trên feature của mình, chọn commit trực tiếp vào **chính nhánh feature đó**. Commit web đã nằm trên GitHub, không cần push riêng. [Chỉnh sửa file trên web](https://docs.github.com/en/repositories/working-with-files/managing-files/editing-files)
6. Mở PR với base `develop`, compare đúng feature; mô tả đã làm và cách kiểm tra, nhắc Minh review. Không bấm Merge.
7. Khi có góp ý, mở lại file trên cùng feature, sửa và commit thêm; trả lời comment rồi chờ Minh kiểm tra lại.

Sau mỗi đợt, comment vào Issue: file thay đổi, điều đã làm, đã kiểm tra gì, còn vướng gì và liên kết commit hoặc PR. Một người sửa một file riêng giúp dễ review; sửa README hoặc file người khác chỉ khi Issue giao rõ. Nếu thấy trang đề nghị fork, dừng để kiểm tra quyền trước khi tạo bản repo khác.

## 11 Gặp lỗi, báo vướng và xác nhận hoàn thành

Giữ nguyên trạng thái khi gặp lỗi và báo đúng bước đang làm. Một thông báo lỗi chưa cho phép kết luận file đã mất hoặc repo bị hỏng. Dùng bảng sau để chọn việc đầu tiên:

| Dấu hiệu | Việc cần làm |
| --- | --- |
| 404, không thấy repo | Kiểm tra tài khoản, lời mời và repo được mở; báo Minh. |
| Clone báo thư mục đã tồn tại | Mở bản có sẵn, kiểm tra trạng thái; không xóa để làm lại. |
| Terminal chỉ hỏi Password | Kiểm tra GCM và luồng đăng nhập; không nhập mật khẩu GitHub. |
| Push bị rejected | Gửi nguyên lỗi; không dùng force push để ép ghi đè. |
| Có conflict hoặc dấu `<<<<<<<` | Dừng để Minh cùng đối chiếu; chưa commit bản có dấu xung đột. |
| Terminal dừng ở `:` hoặc END | Nhấn `q`; lần sau dùng `git --no-pager diff ...`. |
| PR có file ngoài nhiệm vụ | Chưa merge; báo tên file để thu hẹp thay đổi. |

Mẫu báo vướng, thay các chỗ trong ngoặc vuông trước khi gửi:

```text
Issue: [số hoặc liên kết thật]
Người làm: [họ tên và username]
Máy và cách làm: [Windows/Linux; web hay Git local]
Nhánh hiện tại: [tên nhánh]
Bước hoặc lệnh vừa chạy: [nội dung]
Lỗi hiển thị: [nguyên văn hoặc ảnh đã che thông tin riêng]
Thay đổi chưa lưu/chưa commit: [có, không hoặc chưa rõ]
Đã kiểm tra: [việc thực sự làm]
```

Không gửi `.env`, token, private key, RAM dump, backup, PCAP thô hoặc ổ máy ảo qua repo; `.gitignore` không thay cho kiểm tra file upload bằng web. Khi nộp tài liệu, ghi rõ nguồn và phần chưa xác nhận.

Chỉ báo hoàn thành khi PR đúng base `develop`, đã sửa góp ý, Minh đã nghiệm thu và merge. Sau đó người dùng local về `develop` sạch, pull `--ff-only` và dùng nhánh mới cho Issue khác. Minh lưu liên kết Issue, commit, comment, PR, review cùng ngày thực tế để viết báo cáo nhóm.

## 12 Mẫu commit comment và mô tả PR

Giữ nhãn Conventional Commits; phần mô tả viết tiếng Việt và tham chiếu Issue thật. `docs` dùng cho tài liệu, `feat` cho chức năng, `fix` cho sửa lỗi, `lab` cho cấu hình lab, `test` cho kiểm thử và `chore` cho bảo trì. Ví dụ `docs: bổ sung hướng dẫn làm việc nhóm (#1)` tham chiếu Issue #1 đã có.

Comment sau mỗi đợt thay đổi có ý nghĩa, không phải từng lần gõ hoặc lưu file:

```text
Đã làm: [file và nội dung thực tế]
Đã kiểm tra: [Preview, diff hoặc phép kiểm tra đã thực hiện]
Kết quả: [đạt gì, còn thiếu gì]
Vướng mắc: [không có hoặc cần đầu vào từ ai]
Liên kết: [commit và PR thật]
```

Mô tả PR cần có:

```text
Liên quan #[số Issue thật]
Thay đổi: [nội dung và lý do]
Kiểm tra đã thực hiện: [cách kiểm tra và kết quả]
Phần chưa hoàn thành: [nếu có]
Đề nghị review: [username người khác]
```

Reviewer đọc Files changed, đối chiếu Issue và bằng chứng, hỏi lại chỗ thiếu. Chỉ Approve phần đã hiểu và kiểm tra; việc merge do Minh thực hiện sau nghiệm thu. Các hạn làm việc, độ khó và lịch thực nghiệm được ghi ở Issue, milestone và Project theo kế hoạch nhóm.
