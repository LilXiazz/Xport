# 同步版本
import socket  # 网络通信模块
import argparse  # 命令行参数解析
from concurrent.futures import ThreadPoolExecutor  # 线程池实现
import time  # 时间测量


def scan_port(ip, port):
    """执行单端口扫描"""
    try:
        # 创建TCP套接字（IPv4）
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(2)  # 设置2秒超时
            # connect_ex返回错误码而非抛出异常（0表示成功）
            result = sock.connect_ex((ip, port))
            if result == 0:
                return port  # 返回开放端口号
    except Exception as e:
        print(f"扫描端口 {port} 出错: {e}")
    return None  # 端口关闭或出错时返回None


def main(ip, start_port, end_port):
    """主控制函数"""
    start_time = time.time()  # 记录开始时间
    open_ports = []  # 开放端口列表

    # 创建线程池（最大200个工作线程）
    with ThreadPoolExecutor(max_workers=200) as executor:
        # 创建任务映射：{future对象: 端口号}
        futures = {
            executor.submit(scan_port, ip, port): port
            for port in range(start_port, end_port + 1)
        }

        # 遍历完成的任务
        for future in futures:
            port = futures[future]  # 获取对应端口号
            result = future.result()
            if result is not None:  # 当端口开放时
                open_ports.append(result)
                print(f"端口 {result} 开放")  # 实时输出开放端口

    # 结果汇总输出
    print(f"\n扫描完成！耗时：{time.time() - start_time:.2f}秒")
    print(f"开放端口总数：{len(open_ports)}")
    print("开放端口列表：", sorted(open_ports))


if __name__ == "__main__":
    # 法律声明
    print("警告：仅限合法授权测试！未经许可扫描他人网络属违法行为。")

    # 命令行参数配置
    parser = argparse.ArgumentParser(description='多线程端口扫描器')
    parser.add_argument('target_ip', type=str, help='目标IP地址')
    parser.add_argument('start_port', type=int, help='起始端口号')
    parser.add_argument('end_port', type=int, help='结束端口号')
    args = parser.parse_args()

    # 执行主程序
    main(args.target_ip, args.start_port, args.end_port)



# 使用方式
# python scanner.py 106.13.245.216 1 1024