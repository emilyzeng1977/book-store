from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
import os

SUBURB = "ARTARMON"
DOWNLOAD_URL = "https://apps.epa.nsw.gov.au/prpoeoapp/default.aspx?PenaltyNotice=1"
DOWNLOAD_DIR = "download"
DATA_DIR = "data"

def download_file():
    url = DOWNLOAD_URL

    # 确保 download 文件夹存在
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url)

        # 选中 radio
        page.check("#optGeneralSearch")
        page.wait_for_timeout(1000)
        page.fill("#ucSuburb3_textSuburb", SUBURB)
        page.wait_for_timeout(1000)
        page.click("#btnSeach")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)

        # 监听下载
        with page.expect_download() as download_info:
            page.click("#lnkBtnExportExcel")
        download = download_info.value

        # 保存下载文件到 download 文件夹
        today = datetime.now().strftime("%Y%m%d")
        file_name = f"{SUBURB}_{today}.xls"
        download_path = os.path.join(DOWNLOAD_DIR, file_name)
        download.save_as(download_path)
        print("Downloaded:", download_path)

        browser.close()
        return download_path

def convert_to_csv(file_path):
    # 读取 HTML / Excel 表格
    tables = pd.read_html(file_path, header=0)  # 读取 HTML 表格
    df = tables[0]

    # 确保 data 文件夹存在
    os.makedirs(DATA_DIR, exist_ok=True)

    # 保存为 CSV
    today = datetime.now().strftime("%Y%m%d")
    output_file = os.path.join(DATA_DIR, f"{SUBURB}_{today}.csv")
    df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print("CSV saved:", output_file)

def main():
    file_path = download_file()
    convert_to_csv(file_path)

if __name__ == "__main__":
    main()