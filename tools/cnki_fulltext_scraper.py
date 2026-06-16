#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import time
import random
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import csv

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

try:
    import undetected_chromedriver as uc
    USE_UC = True
except ImportError:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    USE_UC = False


# ═══════════════════════════════════════════════════════════════
#  用户配置区
# ═══════════════════════════════════════════════════════════════

TOOL_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TOOL_DIR)

CONFIG = {
    # ── 检索式：只修改学科和年份，保留 CSSCI 限制 ───────────────
    # 原条件：
    # SU%=('知识体系' + '学科体系' + '学术体系' + '话语体系')
    # AND SU%='马克思主义'
    # AND FT='术语'
    # AND YE <2018
    "search_query": "SU%=('知识体系' + '学科体系' + '学术体系' + '话语体系') AND SU%='马克思主义' AND FT='术语' AND YE<2018",

    # ── 数据库代码 ────────────────────────────────────────────
    "db_code": "SCDB",

    # ── 只抓前 N 页的文章（每页 20 条）──────────────────────────
    "max_pages": 1,

    # ── 每篇全文等待加载超时（秒）────────────────────────────────
    "fulltext_timeout": 30,

    # ── 输出目录 ─────────────────────────────────────────────
    "output_dir": os.path.join(PROJECT_ROOT, 'outputs', 'cnki_fulltext_output'),

    # ── 请求间隔（秒，针对全文逐篇打开的延迟，建议长一点防反爬）──
    "delay_min": 3.0,
    "delay_max": 6.0,

    # ── 页面加载超时（秒）──────────────────────────────────────
    "page_timeout": 25,
}

# ═══════════════════════════════════════════════════════════════

os.makedirs(CONFIG["output_dir"], exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

log = logging.getLogger(__name__)


@dataclass
class ArticleInfo:
    seq: str = ""
    title: str = ""
    authors: str = ""
    journal: str = ""
    date: str = ""
    html_url: str = ""
    abstract_url: str = ""
    raw_href: str = ""


def create_driver():
    if USE_UC:
        opts = uc.ChromeOptions()
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--window-size=1400,900")

        prefs = {
            "download.default_directory": CONFIG["output_dir"],
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        }

        opts.add_experimental_option("prefs", prefs)
        driver = uc.Chrome(options=opts)

    else:
        opts = Options()
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--window-size=1400,900")

        prefs = {
            "download.default_directory": CONFIG["output_dir"],
            "download.prompt_for_download": False,
        }

        opts.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome(options=opts)

    driver.set_page_load_timeout(60)
    return driver


def wait_login(driver):
    log.info("准备手动登录...")
    driver.get("https://kns.cnki.net/kns8s/defaultresult/index")

    print("\n" + "=" * 60)
    print("请在弹出的浏览器窗口中完成知网账号登录。")
    print("登录完成后，确认页面右上角显示账号信息。")
    print("然后回到此命令行窗口，按回车继续。")
    print("=" * 60)

    input(">>> 已登录并准备就绪，按回车开始自动抓取：")
    log.info("用户确认已登录，开始执行任务...")


def execute_advanced_search(driver, query: str, db_code: str) -> bool:
    try:
        log.info("正在打开专业检索页面...")
        driver.get(f"https://kns.cnki.net/kns8s/AdvSearch?dbcode={db_code}")
        wait = WebDriverWait(driver, 15)

        # 1. 切换到“专业检索”标签
        tab = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'li[name="majorSearch"]'))
        )
        driver.execute_script("arguments[0].click();", tab)
        time.sleep(1)

        # 2. 限制期刊来源为 CSSCI
        log.info("正在设置来源期刊限制：学术期刊 -> CSSCI...")

        try:
            journal_btn = wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//ul[contains(@class, 'doctype-menus')]//a[span[text()='学术期刊']]",
                    )
                )
            )
            driver.execute_script("arguments[0].click();", journal_btn)
            time.sleep(1.5)

            cssci_checkbox = wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//input[@type='checkbox' and @key='CSI' and @value='Y']",
                    )
                )
            )

            if not cssci_checkbox.is_selected():
                driver.execute_script("arguments[0].click();", cssci_checkbox)

            time.sleep(1)
            log.info("已成功勾选 CSSCI 限制。")

        except Exception as e:
            log.warning(f"设置 CSSCI 来源期刊限制时发生异常，请检查网页结构是否变化：{e}")

        # 3. 填写检索式并检索
        textarea = driver.find_element(By.CSS_SELECTOR, "textarea.majorSearch")
        driver.execute_script(
            'arguments[0].style.display="block"; arguments[0].value="";',
            textarea,
        )
        driver.execute_script("arguments[0].value = arguments[1];", textarea, query)

        btn = driver.find_element(By.CSS_SELECTOR, 'input.btn-search[type="button"]')
        driver.execute_script("arguments[0].click();", btn)

        time.sleep(3)
        return True

    except Exception as e:
        log.error(f"专业检索执行失败：{e}")
        return False


def wait_for_page_to_load(wait, expected_page: int) -> bool:
    try:
        wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, f"a.cur[data-curpage='{expected_page}']")
            )
        )
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "tbody tr")))
        return True

    except TimeoutException:
        return False


def go_to_page(driver, wait, target_page: int) -> bool:
    log.info(f"  准备翻页至第 {target_page} 页...")
    delay = random.uniform(2.0, 4.0)

    try:
        target_btn = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, f"a[data-curpage='{target_page}']")
            )
        )
        driver.execute_script("arguments[0].click();", target_btn)
        time.sleep(delay)
        return True

    except TimeoutException:
        try:
            next_btn = driver.find_element(By.ID, "PageNext")
            driver.execute_script("arguments[0].click();", next_btn)
            time.sleep(delay)
            return True

        except Exception:
            return False

    except Exception:
        return False


def parse_result_page(html: str) -> list[ArticleInfo]:
    soup = BeautifulSoup(html, "html.parser")
    articles = []

    rows = soup.select("table#gridTable tbody tr, .result-table-list tbody tr, tbody tr")

    for row in rows:
        try:
            art = ArticleInfo()

            seq_td = row.select_one("td.seq")
            if seq_td:
                art.seq = seq_td.get_text(strip=True).strip()

            title_a = row.select_one("td.name a.fz14")
            if title_a:
                art.title = title_a.get_text(strip=True)
                art.raw_href = title_a.get("href", "")

            authors = row.select("td.author a.KnowledgeNetLink")
            art.authors = "；".join(a.get_text(strip=True) for a in authors)

            source_a = row.select_one("td.source a")
            if source_a:
                art.journal = source_a.get_text(strip=True)

            date_td = row.select_one("td.date")
            if date_td:
                art.date = date_td.get_text(strip=True)

            html_a = row.select_one("a.icon-html[href]")
            if html_a:
                art.html_url = "HAS_HTML"

            if art.title:
                articles.append(art)

        except Exception:
            continue

    return articles


def extract_fulltext(driver, timeout: int = 30) -> Optional[str]:
    """
    提取当前激活标签页的 HTML 全文内容。
    兼容知网新老两版 HTML 阅读器。
    """

    try:
        time.sleep(3)

        content_selectors = [
            "#paperRead",
            ".ChapterContainer",
            ".article-content",
            ".rd-article-wr",
            "#article-content",
            ".body-main",
            ".CTNFont",
            "article",
            ".content-wrapper",
            "main",
        ]

        loaded = False

        for sel in content_selectors:
            try:
                WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, sel))
                )
                loaded = True
                break

            except TimeoutException:
                continue

        if not loaded:
            time.sleep(5)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        for tag in soup.select(
            "nav, header, footer, script, style, "
            ".nav, .menu, .toolbar, .sidebar, .btn, button, .read-btn-box"
        ):
            tag.decompose()

        text_parts = []

        paper_read = soup.select_one("#paperRead")

        if paper_read:
            text_parts.append(paper_read.get_text(separator="\n", strip=True))

            refs = soup.select_one(".references-box")
            if refs:
                text_parts.append("\n\n" + "=" * 30 + " 参考文献 " + "=" * 30)
                text_parts.append(refs.get_text(separator="\n", strip=True))

        else:
            body_candidates = soup.select(
                ".article-content, .rd-article-wr, #article-content, "
                ".body-main, .CTNFont, article, .content-wrapper"
            )

            if body_candidates:
                for block in body_candidates:
                    text_parts.append(block.get_text(separator="\n", strip=True))
            else:
                body = soup.find("body")
                if body:
                    text_parts.append(body.get_text(separator="\n", strip=True))

        full_text = "\n\n".join(text_parts)
        full_text = re.sub(r"\n{3,}", "\n\n", full_text).strip()

        if len(full_text) < 100:
            log.warning("  ⚠ 提取文本过短，可能未成功加载正文")
            return None

        return full_text

    except Exception as e:
        log.error(f"全文提取失败：{e}")
        return None


def save_fulltext(art: ArticleInfo, fulltext: str, out_dir: Path):
    safe_title = re.sub(r'[\\/:*?"<>|]', "_", art.title)[:50]
    filename = f"{art.seq}_{safe_title}.txt"
    filepath = out_dir / filename

    header = (
        f"标题：{art.title}\n"
        f"作者：{art.authors}\n"
        f"来源：{art.journal}\n"
        f"时间：{art.date}\n"
        + "=" * 60
        + "\n\n"
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(header)
        f.write(fulltext)

    log.info(f"  ✓ 成功保存：{filename}  ({len(fulltext):,} 字符)")
    return filepath


def main():
    cfg = CONFIG
    out_dir = Path(cfg["output_dir"])

    driver = create_driver()
    wait = WebDriverWait(driver, cfg["page_timeout"])

    success_count = 0
    skip_count = 0
    fail_count = 0

    failed_records = []
    error_file = out_dir / "failed_and_skipped_articles.csv"

    try:
        wait_login(driver)

        log.info("开始执行复杂检索式...")

        if not execute_advanced_search(driver, cfg["search_query"], cfg["db_code"]):
            return

        main_window = driver.current_window_handle

        for page in range(1, cfg["max_pages"] + 1):
            log.info(f"\n========== 正在处理第 {page} 页 ==========")

            if not wait_for_page_to_load(wait, page):
                log.warning(f"第 {page} 页加载超时或无数据，停止翻页。")
                break

            page_arts = parse_result_page(driver.page_source)

            if not page_arts:
                log.info("本页未发现文献记录，停止提取。")
                break

            html_count = sum(1 for a in page_arts if a.html_url)

            log.info(
                f"本页共发现 {len(page_arts)} 篇，其中带 HTML 的有 {html_count} 篇。开始逐篇抓取..."
            )

            for art in page_arts:
                if not art.html_url:
                    log.info(f"  ⏭ [{art.seq}] {art.title[:30]}... 无 HTML，跳过")

                    failed_records.append(
                        [
                            art.seq,
                            art.title,
                            art.authors,
                            art.journal,
                            art.date,
                            "跳过：无 HTML 全文",
                        ]
                    )

                    skip_count += 1
                    continue

                log.info(f"  ⬇ [{art.seq}] {art.title[:30]}... 开始提取")

                try:
                    # 1. 点击题名，进入详情页
                    try:
                        title_btn = driver.find_element(By.XPATH, f"//a[@href='{art.raw_href}']")
                        driver.execute_script("arguments[0].click();", title_btn)

                    except NoSuchElementException:
                        xpath = (
                            f"//tr[td[contains(@class, 'seq') and normalize-space(text())='{art.seq}']]"
                            f"//a[contains(@class, 'fz14')]"
                        )
                        title_btn = driver.find_element(By.XPATH, xpath)
                        driver.execute_script("arguments[0].click();", title_btn)

                    time.sleep(2)

                    windows = driver.window_handles

                    if len(windows) < 2:
                        raise Exception("详情页未成功弹出")

                    detail_window = windows[-1]
                    driver.switch_to.window(detail_window)

                    # 2. 在详情页点击 HTML 阅读按钮
                    try:
                        html_btn = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located(
                                (
                                    By.XPATH,
                                    "//li[contains(@class, 'btn-html')]/a | //a[contains(text(), 'HTML阅读')]",
                                )
                            )
                        )
                        driver.execute_script("arguments[0].click();", html_btn)

                    except TimeoutException:
                        log.warning("详情页未找到 HTML 阅读按钮，可能已下架。")

                        failed_records.append(
                            [
                                art.seq,
                                art.title,
                                art.authors,
                                art.journal,
                                art.date,
                                "失败：详情页无 HTML 阅读按钮",
                            ]
                        )

                        fail_count += 1
                        continue

                    time.sleep(2.5)

                    # 3. 切换到最终 HTML 阅读器页面
                    windows = driver.window_handles

                    if len(windows) < 3:
                        raise Exception("阅读页未成功弹出，可能被浏览器拦截")

                    reader_window = windows[-1]
                    driver.switch_to.window(reader_window)

                    # 4. 提取全文
                    fulltext = extract_fulltext(driver, cfg["fulltext_timeout"])

                    if fulltext:
                        save_fulltext(art, fulltext, out_dir)
                        success_count += 1

                    else:
                        failed_records.append(
                            [
                                art.seq,
                                art.title,
                                art.authors,
                                art.journal,
                                art.date,
                                "失败：正文解析为空或加载超时",
                            ]
                        )

                        fail_count += 1

                except Exception as e:
                    log.error(f"  ✗ 窗口切换或提取时发生异常：{e}")

                    error_msg = str(e).split("\n")[0][:50]

                    failed_records.append(
                        [
                            art.seq,
                            art.title,
                            art.authors,
                            art.journal,
                            art.date,
                            f"失败：发生异常：{error_msg}",
                        ]
                    )

                    fail_count += 1

                finally:
                    # 关闭所有新打开的详情页和阅读页，回到主列表页
                    for handle in driver.window_handles:
                        if handle != main_window:
                            try:
                                driver.switch_to.window(handle)
                                driver.close()
                            except Exception:
                                pass

                    driver.switch_to.window(main_window)
                    time.sleep(1)

                delay = random.uniform(cfg["delay_min"], cfg["delay_max"])
                time.sleep(delay)

            if page < cfg["max_pages"]:
                if not go_to_page(driver, wait, page + 1):
                    log.info("无法定位翻页按钮，可能已到达末页或被反爬拦截。")
                    break

    except KeyboardInterrupt:
        log.info("\n收到中断信号 Ctrl+C，安全退出。")

    finally:
        driver.quit()

        if failed_records:
            try:
                with open(error_file, "w", encoding="utf-8-sig", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["序号", "题名", "作者", "来源", "时间", "跳过/失败原因"])
                    writer.writerows(failed_records)

            except Exception as e:
                log.error(f"保存失败记录 CSV 文件时出错：{e}")

    print("\n" + "=" * 50)
    print("全文采集结束！")
    print(f"  成功保存：{success_count} 篇")
    print(f"  跳过，无 HTML：{skip_count} 篇")
    print(f"  提取失败：{fail_count} 篇")
    print(f"  输出目录：{out_dir.resolve()}")

    if failed_records:
        print(f"  未成功提取的文献明细已保存至：{error_file.name}")

    print("=" * 50)


if __name__ == "__main__":
    main()
