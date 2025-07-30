import cv2
import time
from pathlib import Path
import os
from ping3 import ping
import argparse
import sys
import json
from datetime import datetime
from pprint import pprint

RED = '\033[91m'
GREEN = '\033[92m'
RESET = '\033[0m'  # 用于恢复默认颜色


def print_red(text):
    print(RED + text + RESET)


def print_green(text):
    print(GREEN + text + RESET)


def record_image(cam_url, output_dir, record_num=2, record_interval=100):
    cam = cv2.VideoCapture(cam_url)
    basename = "{}".format(time.strftime("%Y_%m_%d__%H_%M_%S", time.localtime(time.time())))

    for _ in range(record_interval * record_num):
        flag, frame = cam.read()
        if not flag:
            break

        if _ % record_interval != 0:
            continue

        output_img_path = os.path.join(output_dir, basename + "_" + str(_) + ".jpg")
        os.makedirs(str(Path(output_img_path).parent), exist_ok=True)
        cv2.imwrite(output_img_path, frame)
        # cv2.imshow("x", frame)
        # cv2.waitKey()


def check_url_and_download(ip_addr, url_template, output_dir, record_num, record_interval):
    ping_result = ping(ip_addr, timeout=2)
    if ping_result is not None and ping_result != False:
        url = url_template.format(ip_addr)
        print("准备下载 {}".format(url))
        record_image(url, os.path.join(output_dir, ip_addr), record_num=record_num, record_interval=record_interval)


def check_valid_ip_addr(ip_first_segment, ip_second_segment, ip_third_segment, ip_fourth_segment):
    valid_urls = []

    for ip_third_part in range(ip_third_segment[0], ip_third_segment[-1] + 1, 1):
        for ip_fourth_part in range(ip_fourth_segment[0], ip_fourth_segment[-1] + 1, 1):
            ip_addr = "{}.{}.{}.{}".format(ip_first_segment, ip_second_segment, ip_third_part, ip_fourth_part)
            ping_result = ping(ip_addr, timeout=2)
            if ping_result is not None and ping_result != False:
                valid_urls.append(ip_addr)
                print_green("IP地址:{} 测试成功".format(ip_addr))
            else:
                print_red("IP地址:{} 测试失败".format(ip_addr))
    return valid_urls


def main(ip_first_segment, ip_second_segment, ip_third_segment, ip_fourth_segment, output_dir, url_template, record_num, record_interval, time_period, ip_update_interval, **kwargs):
    last_check_time = 0
    valid_ip_addrs = []
    while True:

        current_time = datetime.now()
        if current_time.hour < time_period[0] or current_time.hour > time_period[1]:
            print("当前时间不在指定时间段内，程序将在指定时间段内运行。")
            time.sleep(60)
            continue

        if last_check_time == 0 or ((time.time() - last_check_time) >= (3600*ip_update_interval)):
            print("更新有效IP地址...")
            valid_ip_addrs = check_valid_ip_addr(ip_first_segment, ip_second_segment, ip_third_segment, ip_fourth_segment)
            last_check_time = time.time()
            print("更新完成,有效地址数量为:{}".format(len(valid_ip_addrs)))

        for url in valid_ip_addrs:
            check_url_and_download(url, url_template, output_dir, record_num, record_interval)


def record():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip_first_segment', type=int, help='IP 地址第一段', default=192)
    parser.add_argument('--ip_second_segment', type=int, help='IP 地址第二段', default=168)
    parser.add_argument('--ip_third_segment', type=int, nargs="+", help='IP 地址第三段', default=[21, 36])
    parser.add_argument('--ip_fourth_segment', type=int, nargs="+", help='IP 地址第四段', default=[10, 19])
    parser.add_argument('--output_dir', type=str, help='图片保存目录', default="road_auto_record")
    parser.add_argument('--url_template', type=str, help='流地址模板', default="rtsp://admin:joyson600699@{}/:544/Streaming/Channels/101")
    parser.add_argument('--record_num', type=int, help='连续录制帧数', default=4)
    parser.add_argument('--record_interval', type=int, help='录制间隔', default=500)
    parser.add_argument('--time_period', nargs="+", type=int, help='录制时间', default=[0, 24])
    parser.add_argument('--ip_update_interval', type=int, help='ip地址更新间隔(单位小时)', default=10)
    parser.add_argument('--cfg', type=str, help='配置文件', default='/home/hanson/work/ip_camera_record/configs/ningbo.json')
    args = parser.parse_args(sys.argv[1:])
    args_dict = vars(args)
    if args.cfg != '':
        cfg_dict = json.load(open(args.cfg, 'r', encoding='utf-8'))
        args_dict.update(cfg_dict)
    pprint(args_dict)
    main(**args_dict)


if __name__ == "__main__":
    record()