# On-Demand Kindle Scribe News Reader & Delivery

On-demand delivery of **The Times of India**, **The Irish Times**, and **Irish Independent** directly to your **Amazon Kindle Scribe** over Wi-Fi.

---

## 1. How to Trigger On-Demand Delivery

Whenever you want the latest edition sent to your Kindle:

### Method A: From your Mobile Phone (GitHub App)
1. Open the **GitHub app** on your phone (iOS / Android).
2. Go to your repository: **`Tech33/kindle-scribe-news`**.
3. Tap **Actions** &rarr; tap **On-Demand Kindle News Delivery**.
4. Tap **Run workflow**.
5. Choose which paper you want:
   - `all` (Times of India + Irish Times + Irish Independent)
   - `toi` (The Times of India only)
   - `irishtimes` (The Irish Times only)
   - `independent` (Irish Independent only)
6. Tap **Run**. In ~2 minutes, the edition is delivered to your Kindle Scribe over Wi-Fi!

### Method B: From your Web Browser
1. Open [https://github.com/Tech33/kindle-scribe-news/actions](https://github.com/Tech33/kindle-scribe-news/actions).
2. Select **On-Demand Kindle News Delivery** on the left.
3. Click **Run workflow** dropdown on the right &rarr; select paper &rarr; click **Run workflow**.

---

## 2. Reading on your Kindle Scribe
1. Turn on your Kindle Scribe and ensure Wi-Fi is connected.
2. Swipe down from the top edge and tap **Sync**.
3. Go to your **Library** and make sure the filter is set to **Docs** or **All** (Amazon places personal document deliveries under "Docs", not "Books").

---

## 3. Repository Secrets (Already Configured)
The workflow securely reads credentials from GitHub repository secrets:
- `KINDLE_EMAIL`: Your `@kindle.com` address.
- `SMTP_USER`: Your sender Gmail address.
- `SMTP_PASS`: Your 16-character Google App Password.

---

## 4. Re-enabling Scheduled Delivery (Optional)
If you ever want to re-enable automated morning delivery in the future, edit `.github/workflows/kindle_news.yml` and add back the schedule trigger:
```yaml
on:
  schedule:
    - cron: '30 5 * * *'  # 05:30 UTC
  workflow_dispatch:
    ...
```
