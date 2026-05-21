# xsmb-auto-v2

Hệ thống lấy kết quả XSMB độc lập, chạy song song với repo cũ.

## Chức năng

- Tự lấy kết quả XSMB hằng ngày.
- Ghi dữ liệu vào `data/`:
  - `data/latest.json`: kết quả mới nhất.
  - `data/xsmb-history.json`: lịch sử đầy đủ.
  - `data/xsmb-2-digits.json`: dữ liệu 2 số cuối, tiện cho lô/đề.
- Kiểm tra dữ liệu trước khi ghi.
- Chạy tự động bằng GitHub Actions lúc 18:40 và 18:55 giờ Việt Nam.
- Có thể chạy thủ công bằng nút `Run workflow`.
- Có thể gửi Telegram nếu cấu hình secrets.

## Chạy thủ công

Vào tab `Actions` → chọn `Update XSMB v2` → `Run workflow`.

Nếu muốn lấy một ngày cụ thể, nhập `xsmb_date` theo định dạng:

```text
YYYY-MM-DD
```

Ví dụ:

```text
2026-05-21
```

Nếu để trống, hệ thống tự chọn ngày cần lấy theo giờ Việt Nam.

## Cấu hình Telegram

Vào `Settings` → `Secrets and variables` → `Actions` → `New repository secret`.

Thêm 2 secret:

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

Nếu chưa có 2 secret này, workflow vẫn chạy và cập nhật dữ liệu, chỉ bỏ qua bước gửi Telegram.
