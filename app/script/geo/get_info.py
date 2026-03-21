from playwright.sync_api import sync_playwright

url = "https://apps.epa.nsw.gov.au/prpoeoapp/default.aspx?PenaltyNotice=1"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto(url)

    # 选中 radio
    page.check("#optGeneralSearch")
    page.wait_for_timeout(1000)
    page.fill("#ucSuburb3_textSuburb", "ARTARMON")
    page.wait_for_timeout(1000)
    page.click("#btnSeach")
    page.wait_for_timeout(1000)
    page.wait_for_load_state("networkidle")
    # 监听下载
    with page.expect_download() as download_info:
        page.click("#lnkBtnExportExcel")

    download = download_info.value
    # 保存文件
    download.save_as("epa_result.xlsx")
    print("Downloaded:", download.suggested_filename)
    page.wait_for_timeout(5000)
    browser.close()