import requests
from bs4 import BeautifulSoup
import re
import os
import click

@click.command()
@click.argument('exam')
def download_images(exam):
    """Tải toàn bộ ảnh trong thread từ FuOverflow theo EXAM ID"""
    base_url = "https://fuoverflow.com/threads/"
    thread_url = base_url + exam
    folder = f"Data_{exam}"

    print(f"🔍 Đang kiểm tra thread ID: {exam}")
    response = requests.get(thread_url)
    print(f"📶 HTTP status: {response.status_code}")

    if response.status_code != 200:
        print("❌ Không thể tải trang, kiểm tra lại mã thread hoặc kết nối mạng.")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    tags = soup.find_all('a', class_="file-preview")
    ids = []

    for tag in tags:
        href = tag.get("data-lb-sidebar-href")
        if href:
            match = re.search(r'webp\.([0-9]+)\/\?', href)
            if match:
                ids.append(match.group(1))

    if not ids:
        print("⚠️ Không tìm thấy ID nào trong thread.")
        return

    print(f"✅ Đã tìm thấy {len(ids)} ảnh: {ids}")

    if not os.path.exists(folder):
        os.makedirs(folder)

    for i, id in enumerate(ids, 1):
        file_url = f"https://fuoverflow.com/media/{id}/full"
        resp = requests.get(file_url)
        if resp.status_code == 200:
            file_path = os.path.join(folder, f"{id}.jpg")
            with open(file_path, 'wb') as f:
                f.write(resp.content)
            print(f"[{i}] ✅ {file_path}")
        else:
            print(f"[{i}] ❌ Lỗi tải {file_url} (status: {resp.status_code})")
