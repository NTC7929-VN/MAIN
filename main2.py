import os
import subprocess
import time
import sys
import json
import random
import platform
import unicodedata
from curl_cffi import requests
from colorama import init
from googleapiclient.discovery import build
import yt_dlp

init(autoreset=True)

# Constants
API_KEY = "AIzaSyCuG5pSAH3MkO-jZeVDXCCCWJPjbHOHANE"  # YouTube API Key
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
DATA_FILE = "datayoutube.txt"

# [Giữ nguyên các hàm color printing, banner, clear_screen, run_command, get_adb_devices, select_device, get_tiktok_accounts, select_account, get_job_tiktok, skip_job_tiktok, complete_job]
def truecolor_print(text, rgb):
    print(f"\033[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m{text}\033[0m")

def banner_rainbow(text):
    rainbow_colors = [
        (255, 0, 0), (255, 128, 0), (255, 255, 0), (0, 255, 0),
        (0, 255, 255), (0, 0, 255), (128, 0, 255), (255, 0, 255)
    ]
    result = ""
    for i, char in enumerate(text):
        r, g, b = rainbow_colors[i % len(rainbow_colors)]
        result += f"\033[38;2;{r};{g};{b}m{char}\033[0m"
    print(result)

def colored_print(text, color_code=None):
    colors = {
        'reset': '\033[0m', 'red': '\033[91m', 'green': '\033[92m',
        'yellow': '\033[93m', 'blue': '\033[94m', 'purple': '\033[95m',
        'cyan': '\033[96m'
    }
    if color_code and color_code in colors:
        print(f"{colors[color_code]}{text}{colors['reset']}")
    else:
        rainbow_colors = ['\033[91m', '\033[93m', '\033[92m', '\033[96m', '\033[94m', '\033[95m']
        rainbow_text = "".join(f"{rainbow_colors[i % len(rainbow_colors)]}{char}\033[0m" for i, char in enumerate(text))
        print(rainbow_text)

def clear_screen():
    system_name = platform.system()
    if system_name == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def banner():
    banner_text = """
 ██████╗    ████████╗ ██████╗  ██████╗ ██╗     
██╔════╝    ╚══██╔══╝██╔═══██╗██╔═══██╗██║     
██║            ██║   ██║   ██║██║   ██║██║     
██║            ██║   ██║   ██║██║   ██║██║     
╚██████╗       ██║   ╚██████╔╝╚██████╔╝███████╗
 ╚═════╝       ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝
"""
    banner_rainbow(banner_text)
    truecolor_print("Tool By: Thành Công", (122, 235, 255))

def run_command(command, device_id=None):
    try:
        if device_id:
            full_cmd = f"adb -s {device_id} shell {command}"
        else:
            full_cmd = command
        result = subprocess.check_output(full_cmd, shell=True, stderr=subprocess.DEVNULL)
        return result.decode('utf-8').strip()
    except subprocess.CalledProcessError:
        return ""

def get_adb_devices():
    os.system('adb devices')
    output = run_command("adb devices")
    lines = output.strip().split('\n')[1:]  # Skip the first line
    devices = [line.split('\t')[0] for line in lines if 'device' in line]
    if not devices:
        colored_print("KHÔNG TÌM THẤY THIẾT BỊ ADB NÀO!", "red")
        sys.exit(1)
    colored_print(f"Đã tìm thấy {len(devices)} thiết bị ADB:", "green")
    for idx, device in enumerate(devices):
        colored_print(f"{idx + 1}. {device}", "yellow")
    return devices

def select_device(devices):
    colored_print(f"ĐÃ CHỌN THIẾT BỊ: {devices[0]}", "green")
    return devices[0]  # Chỉ chọn thiết bị đầu tiên

def get_tiktok_accounts(headers):
    colored_print("ĐANG LẤY DANH SÁCH TÀI KHOẢN TIKTOK...", "cyan")
    try:
        response = requests.get('https://gateway.golike.net/api/tiktok-account', headers=headers, impersonate="safari_ios").json()
        if 'data' not in response or not response['data']:
            colored_print("KHÔNG TÌM THẤY TÀI KHOẢN TIKTOK!", "red")
            sys.exit(1)
        accounts = [{'id': acc['id'], 'username': acc['unique_username']} for acc in response['data']]
        colored_print("┌───────────────────────────────────────┐", "green")
        colored_print("│       DANH SÁCH TÀI KHOẢN TIKTOK      │", "green")
        colored_print("├───┬───────────────────┬───────────────┤", "green")
        colored_print("│STT│ TÊN NGƯỜI DÙNG    │ ID TÀI KHOẢN  │", "green")
        colored_print("├───┼───────────────────┼───────────────┤", "green")
        for i, acc in enumerate(accounts):
            colored_print(f"│ {i+1:<2}│ {acc['username']:<18}│ {acc['id']:<14}│", "yellow")
        colored_print("└───┴───────────────────┴───────────────┘", "green")
        return accounts
    except Exception as e:
        colored_print(f"LỖI KẾT NỐI API: {str(e)}", "red")
        sys.exit(1)

def select_account(accounts):
    while True:
        try:
            choice = int(input("Chọn tài khoản TikTok (nhập số STT): ")) - 1
            if 0 <= choice < len(accounts):
                colored_print(f"ĐÃ CHỌN TÀI KHOẢN: {accounts[choice]['username']} ID:{accounts[choice]['id']}", "green")
                return accounts[choice]['id']
            colored_print("Vui lòng chọn số thứ tự hợp lệ.", "red")
        except ValueError:
            colored_print("Vui lòng nhập một số hợp lệ.", "red")

def get_job_tiktok(account_id, headers):
    colored_print("ĐANG TÌM NHIỆM VỤ MỚI...", "cyan")
    try:
        response = requests.get(
            'https://gateway.golike.net/api/advertising/publishers/tiktok/jobs',
            params={'account_id': str(account_id), 'data': 'null'},
            headers=headers,
            impersonate='safari_ios'
        ).json()
        if 'data' not in response or 'lock' not in response:
            colored_print("KHÔNG TÌM THẤY NHIỆM VỤ MỚI!", "red")
            time.sleep(5)
            return get_job_tiktok(account_id, headers)
        job_info = {
            'link': response['data']['link'],
            'object_id': response['data']['object_id'],
            'type': response['data']['type'],
            'ads_id': response['lock']['ads_id'],
            'account_id': response['lock']['account_id'],
            'price': response['data']['price_per_after_cost']
        }
        if job_info['type'].lower() == 'comment':
            colored_print("TÌM THẤY NHIỆM VỤ COMMENT - BỎ QUA TỰ ĐỘNG", "yellow")
            skip_job_tiktok(job_info, headers)
            return get_job_tiktok(account_id, headers)
        colored_print("TÌM THẤY NHIỆM VỤ MỚI:", "green")
        colored_print(f"  - LOẠI: {job_info['type']}", "yellow")
        colored_print(f"  - GIÁ TRỊ: {job_info['price']} VND", "yellow")
        return job_info
    except Exception as e:
        colored_print(f"LỖI KHI TÌM NHIỆM VỤ: {str(e)}", "red")
        time.sleep(5)
        return get_job_tiktok(account_id, headers)

def skip_job_tiktok(job_info, headers):
    colored_print("ĐANG BỎ QUA NHIỆM VỤ...", "yellow")
    try:
        response = requests.post(
            'https://gateway.golike.net/api/advertising/publishers/tiktok/skip-jobs',
            headers=headers,
            json={
                'ads_id': int(job_info['ads_id']),
                'object_id': str(job_info['object_id']),
                'account_id': int(job_info['account_id']),
                'type': str(job_info['type']),
            },
            impersonate="safari_ios"
        ).json()
        if response.get('status') == 200:
            colored_print("ĐÃ BỎ QUA NHIỆM VỤ THÀNH CÔNG", "green")
            return True
        colored_print(f"LỖI KHI BỎ QUA NHIỆM VỤ: {response.get('message', 'Unknown error')}", "red")
        return False
    except Exception as e:
        colored_print(f"LỖI KẾT NỐI KHI BỎ QUA NHIỆM VỤ: {str(e)}", "red")
        return False

def complete_job(job_info, headers):
    colored_print(f"ĐANG XÁC NHẬN HOÀN THÀNH NHIỆM VỤ {job_info['type'].upper()}...", "cyan")
    try:
        response = requests.post(
            'https://gateway.golike.net/api/advertising/publishers/tiktok/complete-jobs',
            headers=headers,
            json={
                'ads_id': int(job_info['ads_id']),
                'account_id': int(job_info['account_id']),
                'async': True,
                'data': None,
            },
            impersonate='safari_ios'
        ).json()
        if response['status'] == 200:
            return True
        else:
            skip_job_tiktok(job_info, headers)
            return False
    except Exception as e:
        return False

def lamjob(job_info, device_id, completed_jobs):
    run_command(f"am start -a android.intent.action.VIEW -d {job_info['link']}", device_id)
    time.sleep(random.uniform(5, 7)) 
    if job_info['type'] == 'follow' and follow_count < 200:  
        run_command(f"input tap 288 630", device_id)  
        run_command(f"input tap 288 568", device_id)  
        colored_print(f'[{device_id}] Đã nhấn follow người dùng (Follow: {follow_count + 1}/200, Job: {completed_jobs + 1}/200)', 'purple')
        run_command("input tap 50 100",device_id)
        run_command("input keyevent 4",device_id)
    elif job_info['type'] == 'like':
        run_command(f"input tap 350 375", device_id)
        run_command(f"input tap 350 375", device_id)
        colored_print(f"[{device_id}] ❤️ Đã nhấn like video (Job: {completed_jobs + 1}/)", 'purple')
    if complete_job(job_info, headers):
        STT='0'*(3-len(str(completed_jobs)))+str(completed_jobs)
        colored_print(f"[{STT}]:Hoàn thành nhiệm vụ +{job_info['price']}VND", "green")
        return True
    else:
        skip_job_tiktok(job_info, headers)
        return False



def open_tiktok(device_id):
    run_command("am force-stop com.zhiliaoapp.musically", device_id)
    run_command("monkey -p com.zhiliaoapp.musically -c android.intent.category.LAUNCHER 1", device_id)

def nuoi_acctiktok(device_id, duration,statuscomment=None):
    def tap_lk():
        run_command("input tap 667 946", device_id)
        time.sleep(1)
        run_command("input tap 211 941", device_id)
        run_command('input keyevent 4',device_id)
    def tap_reup():
        run_command("input tap 667 946", device_id)
        time.sleep(1)
        run_command("input tap 32 945", device_id)
        time.sleep(1)
        run_command('input keyevent 4',device_id)
    def swipe_up():
        run_command(f"input swipe 300 1000 300 0 {random.randint(100, 300)}", device_id)
    def swipe_down():
        run_command(f"input swipe 360 200 360 1200 {random.randint(100, 300)}", device_id)
    def tap_like():
        run_command("input tap 375 375", device_id)
        run_command("input tap 375 375", device_id)
    def tap_comment():
        if statuscomment==False:
            return
        noidung = [
                "Video này độc lạ đúng gu tui 👏",
                "Coi mà thú vị luôn á 😂",
            ]
        comment = random.choice(noidung)
        comment_text = unicodedata.normalize('NFD', comment).encode('ascii', 'ignore').decode("utf-8")
        comment_text = comment_text.replace(" ", "%s")
        run_command("input tap 667 787", device_id)
        time.sleep(random.uniform(1, 3))
        run_command("input tap 301 1218", device_id)
        time.sleep(random.uniform(1, 3))
        run_command(f"input text {comment_text}", device_id)
        time.sleep(random.uniform(1, 3))
        run_command("input tap 636 737", device_id)
        time.sleep(random.uniform(1, 3))
        run_command("input tap 377 277", device_id)
        time.sleep(random.uniform(1, 3))
        run_command("input tap 377 277", device_id)
        colored_print(f"[{device_id}] 💬 Đã comment: {comment}", "purple")
        time.sleep(random.uniform(2, 4))
        run_command('input keyevent 4', device_id)
        return
    def tap_hoso():

        run_command("input tap 645 1225",device_id)
        time.sleep(1)
        swipe_down()
        time.sleep(1)
        run_command("input keyevent 4",device_id)
    def tap_hopthu():
        run_command("input ap 507 1225",device_id)
        time.sleep(1)
        swipe_down()
        run_command("input keyevent 4",device_id)
        time.sleep(1)
    start_time = time.time()
    colored_print(f"⏳ Bắt đầu nuôi TikTok trong {duration:.0f} giây...", "cyan")
    while time.time() - start_time < duration:
        action = random.randint(1, 50)
        if action in [1, 2, 3, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]:
            swipe_up()
            for i in range(0,random.randint(10,60)):
                time.sleep(1)
            if time.time() - start_time >=duration:
                break
        elif action in [30, 31, 32, 33, 34, 35, 36, 37, 38]:
            swipe_down()
            for i in range(0,random.randint(1,60)):
                time.sleep(1)
            if time.time() - start_time >=duration:
                break
        if action in [40, 41, 42, 43]:
            tap_like()
            for i in range(0,random.randint(1,60)):
                time.sleep(1)
            if time.time() - start_time >=duration:
                break
        if action in [48, 49]:
            tap_comment()
            for i in range(0,random.randint(1,30)):
                time.sleep(1)
            if time.time() - start_time >=duration:
                break
        if random.randint(1,20)==1:
            tap_lk()
            time.sleep(1)
        if random.randint(1,40)==1:
            tap_reup()
            time.sleep(1)
        if random.randint(1,20)==1:
            tap_hoso()
        if random.randint(1,19)==1:
            tap_hopthu()
    colored_print("✅ Đã hoàn thành phiên nuôi acc", "green")

def get_existing_links():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_links(new_links):
    with open(DATA_FILE, "a", encoding="utf-8") as f:
        for link in new_links:
            f.write(link + "\n")

def get_trending_shorts():
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)
    request = youtube.search().list(
        part="id,snippet",
        q="Việt Nam | Vietnam",
        type="video",
        videoDuration="short",
        maxResults=20,
        regionCode="VN"
    )
    response = request.execute()
    existing_links = get_existing_links()
    new_links = []
    for item in response.get("items", []):
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"].lower()
        description = item["snippet"]["description"].lower()
        if "việt nam" in title or "vietnam" in title or "việt nam" in description or "vietnam" in description:
            link = f"https://www.youtube.com/shorts/{video_id}"
            if link not in existing_links and link not in new_links:
                new_links.append(link)
                colored_print(f"Đã tìm thấy: {link} - {item['snippet']['title']}", "yellow")
    while len(new_links) < 20 and "nextPageToken" in response:
        request = youtube.search().list(
            part="id,snippet",
            q="Việt Nam | Vietnam",
            type="video",
            videoDuration="short",
            maxResults=20,
            pageToken=response["nextPageToken"],
            regionCode="VN"
        )
        response = request.execute()
        for item in response.get("items", []):
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"].lower()
            description = item["snippet"]["description"].lower()
            if "việt nam" in title or "vietnam" in title or "việt nam" in description or "vietnam" in description:
                link = f"https://www.youtube.com/shorts/{video_id}"
                if link not in existing_links and link not in new_links and len(new_links) < 20:
                    new_links.append(link)
                    colored_print(f"Đã tìm thấy: {link} - {item['snippet']['title']}", "yellow")
    return new_links

def ensure_download_path():
    download_path = "/sdcard/Download"
    run_command(f"mkdir -p {download_path}")
    return download_path

def download_youtube_short(url):
    try:
        save_path = ensure_download_path()
        ydl_opts = {
            'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
            'format': 'best',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        colored_print(f"Tải hoàn tất! Video được lưu tại: {save_path}", "green")
    except Exception as e:
        colored_print(f"Đã xảy ra lỗi: {e}", "red")

def check_account_status(device_id):
    colored_print(f"[{device_id}] ĐANG KIỂM TRA TRẠNG THÀI TÀI KHOẢN...", "cyan")
    run_command(f"input swipe 300 1000 300 0 {random.randint(100, 300)}", device_id)
    time.sleep(random.uniform(10, 30))
    return True  # Thay bằng logic kiểm tra API nếu có

def mode_1():
    clear_screen()
    banner()
    devices = get_adb_devices()
    device_id = select_device(devices)
    authorization = 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOlwvXC9nYXRld2F5LmdvbGlrZS5uZXRcL2FwaVwvbG9naW4iLCJpYXQiOjE3NDczNjc3NjUsImV4cCI6MTc3ODkwMzc2NSwibmJmIjoxNzQ3MzY3NzY1LCJqdGkiOiJhMGhZS0FGS3BsZlZVMFNkIiwic3ViIjozMDExNzY0LCJwcnYiOiJiOTEyNzk5NzhmMTFhYTdiYzU2NzA0ODdmZmYwMWUyMjgyNTNmZTQ4In0.KHzbILi89K2OzLKfrAsgi7uoA_ta5qkRbMZjTxMQ5Qs'
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'vi,en;q=0.9',
        'authorization': authorization,
        'content-type': 'application/json;charset=utf-8',
        'origin': 'https://app.golike.net',
        'priority': 'u=1, i',
        'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        't': 'VFZSak1FOUVaM3BOUkZFelRVRTlQUT09',
        'user-agent': 'Mozilla/5.0 (Linux; Android 13; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
    }
    accounts = get_tiktok_accounts(headers)
    account_id = select_account(accounts)
    statuscomments=input("Có comment khi nuôi acc không (y/n): ")
    if statuscomments=='n':
        statuscomment=False
    else:
        statuscomment=None
    print("Sẽ làm mặc định 200 job")
    total_jobs = 200
    completed_jobs = 0 
    colored_print("ĐANG MỞ TIKTOK...", "cyan")
    open_tiktok(device_id)
    time.sleep(randomr.randint(5,10))
    clear_screen()
    banner()
    time_nuoiacc=0
    tgdu=180
    while completed_jobs < total_jobs:
        time_start=time.time()
        if completed_jobs >= total_jobs:
            break
        colored_print(f'Đang làm job thứ {completed_jobs + 1}/{total_jobs} ', 'purple')
        job_info = get_job_tiktok(account_id, headers)
        if lamjob(job_info, device_id,completed_jobs):
            completed_jobs+=1
        time_end=time.time()
        tglamjob=time_end-time_start
        if tgdu==180:
            tgdu=tgdu-tglamjob
            time_nuoiacc=random.randint(30,tgdu-50)
            tgdu-=time_nuoiacc
        elif tgdu != 180:
            time_nuoiacc=tgdu-tglamjob
            tgdu=180
        nuoi_acctiktok(device_id,time_nuoiacc,statuscomment)
    colored_print(f"ĐÃ HOÀN THÀNH {completed_jobs} JOB VÀ SẼ CHUYỂN QUA NUÔI ACC...", "green")
    open_tiktok(device_id)
    nuoi_acctiktok(device_id, 99999999999999999)

def mode_2():
    clear_screen()
    banner()
    devices = get_adb_devices()
    device_id = select_device(devices)
    statuscomments=input("Có comment khi nuôi acc không (y/n): ")
    if statuscomments=='n':
        statuscomment=False
    else:
        statuscomment=None
    open_tiktok(device_id)
    nuoi_acctiktok(device_id, 99999999999999999,statuscomment)

def mode_3():
    clear_screen()
    banner()
    url = input("Nhập URL YouTube Shorts: ")
    download_youtube_short(url)

def mode_4():
    clear_screen()
    banner()
    colored_print("Đang tìm kiếm 20 link YouTube Shorts từ Việt Nam...", "cyan")
    new_links = get_trending_shorts()
    if new_links:
        colored_print(f"\nTìm thấy {len(new_links)} link mới:", "green")
        for link in new_links:
            colored_print(link, "yellow")
            download_youtube_short(link)
            save_links(link)
        colored_print(f"\nĐã lưu link vào {DATA_FILE}", "green")
    else:
        colored_print("Không tìm thấy link mới nào!", "red")

def mode_5():
    colored_print("ĐANG THOÁT TOOL...", "red")
    sys.exit(0)

def main():
    while True:
        clear_screen()
        banner()
        colored_print("=== MENU CHỌN CHẾ ĐỘ ===", "cyan")
        colored_print("1. Làm job TikTok và nuôi account", "yellow")
        colored_print("2. Nuôi account TikTok đến khi dừng tool", "yellow")
        colored_print("3. Tải video YouTube Shorts", "yellow")
        colored_print("4. Tìm và tải video Shorts ngẫu nhiên", "yellow")
        colored_print("5. Thoát", "red")
        choice = input("\nNhập lựa chọn (1-5): ")
        if choice == '1':
            mode_1()
        elif choice == '2':
            mode_2()
        elif choice == '3':
            mode_3()
        elif choice == '4':
            mode_4()
        elif choice == '5':
            mode_5()
        else:
            colored_print("Lựa chọn không hợp lệ! Vui lòng chọn lại.", "red")
if __name__ == "__main__":
    main()
