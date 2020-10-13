import re
import urllib.request
import lxml.html
import sys
from concurrent.futures import *
from pathlib import Path

retry_limit = 8
download_thread_num = 256

def download_img(img_url, file_name):
    retry_count = 0
    while retry_count < retry_limit:
        try:
            urllib.request.urlretrieve(img_url, file_name)
            return True
        except Exception as e:
            retry_count += 1
            print(f'exception for {img_url}: {str(e)}')
    return False

if __name__ == "__main__":
    Path("img").mkdir(parents=True, exist_ok=True)
    html_file = sys.argv[1]
    f = open(html_file, 'r')
    html_content = f.read()
    f.close()
    print(f'started processing backup file {html_file}')

    img_url_date_map = {}
    html_doc = lxml.html.parse(html_file).getroot()

    for item_div in html_doc.cssselect('div.item'):
        date_div_elements = item_div.cssselect('div.date')
        repost_div_elements = item_div.cssselect('div.repost-content')
        date_str = ''
        if (len(date_div_elements) == 2 and len(repost_div_elements) > 0):
            date_str = date_div_elements[1].text_content()
        if (len(date_div_elements) == 1 and len(repost_div_elements) == 0):
            date_str = date_div_elements[0].text_content()
        date_str = date_str.strip().replace(' ', '-').replace(':', '_')
        for img_div in item_div.cssselect('img'):
            img_link = img_div.get('src')
            img_url_date_map[img_link] = date_str

    print(f'read {len(img_url_date_map)} image links.')

    executor = ThreadPoolExecutor(max_workers=download_thread_num)
    download_futures = []
    start_count = 0
    for img_url, img_date_str in img_url_date_map.items():
        img_id_search = re.search('mblogpic/(.+)/2000', img_url)
        if img_id_search:
            img_id = img_id_search.group(1)
            img_name = f'img/{img_date_str}_{img_id}.jpg'
            html_content = html_content.replace(img_url, img_name)
            download_futures.append(executor.submit(download_img, img_url, img_name))
            start_count += 1
            print(f'downloading image {start_count}/{len(img_url_date_map)} {img_name}')

    success_count = 0
    fail_count = 0
    for future in as_completed(download_futures):
        if future.result():
            success_count += 1
        else:
            fail_count += 1
    executor.shutdown(wait=True)

    new_html_file = html_file.replace('.html', '_local_img.html')
    with open(html_file + '.rep', 'w') as f:
        f.write(html_content)

    print(f'finished. success={success_count}, fail={fail_count}')
