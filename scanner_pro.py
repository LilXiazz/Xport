# 异步版本
import asyncio  # 异步IO支持库
import socket  # 底层网络通信模块
import argparse  # 命令行参数解析模块
from time import time  # 时间测量模块


async def scan_port(ip, port, semaphore, timeout, open_ports):
    """异步扫描单个端口"""
    async with semaphore:  # 通过信号量控制并发数量
        try:
            # 建立异步TCP连接（高级API封装，内部自动创建套接字）
            # 等价于手动创建流程
            # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # sock.setblocking(False)  # 自动设置为非阻塞模式
            conn = asyncio.open_connection(ip, port)
            # 等待连接结果（带超时设置）
            reader, writer = await asyncio.wait_for(conn, timeout=timeout)

            # 连接成功时的处理
            print(f"\033[32m[+] Port {port} is open\033[0m")  # 绿色输出开放端口
            open_ports.append(port)  # 将开放端口加入列表

            # 关闭连接
            writer.close()
            await writer.wait_closed()  # 等待连接完全关闭

        # 异常处理（合并常见网络异常）
        except (socket.gaierror,  # 地址解析错误
                OSError,  # 操作系统错误
                asyncio.TimeoutError,  # 异步超时
                ConnectionRefusedError):  # 连接被拒绝
            pass  # 静默处理常规错误
        except Exception as e:  # 捕获其他未知异常
            print(f"\033[31m[!] Error scanning port {port}: {e}\033[0m")  # 红色错误提示


async def main(ip, start_port, end_port, max_concurrency, timeout):
    """主扫描控制函数"""
    semaphore = asyncio.Semaphore(max_concurrency)  # 创建并发控制信号量
    open_ports = []  # 存储开放端口列表
    tasks = []  # 任务队列

    start_time = time()  # 记录开始时间

    # 创建端口扫描任务
    for port in range(start_port, end_port + 1):
        task = asyncio.create_task(
            scan_port(ip, port, semaphore, timeout, open_ports)
        )
        tasks.append(task)

    # 等待所有任务完成
    await asyncio.gather(*tasks)

    # 输出扫描结果
    print(f"\nScan completed in {time() - start_time:.2f} seconds")
    print(f"Open ports: {sorted(open_ports)} ({len(open_ports)} found)")


if __name__ == "__main__":
    # 法律警告（黄色强调）
    print("\033[1;33m[!] Legal warning: Unauthorized scanning is illegal. Use responsibly.\033[0m")

    # 命令行参数配置
    parser = argparse.ArgumentParser(description="Async Port Scanner")
    parser.add_argument("target_ip", type=str, help="目标IP地址")
    parser.add_argument("start_port", type=int, help="起始端口号")
    parser.add_argument("end_port", type=int, help="结束端口号")
    parser.add_argument("-c", "--concurrency", type=int, default=500,
                        help="最大并发连接数（默认：500）")
    parser.add_argument("-t", "--timeout", type=float, default=1.5,
                        help="连接超时时间（秒，默认：1.5）")
    args = parser.parse_args()

    # 运行主程序
    asyncio.run(main(
        args.target_ip,
        args.start_port,
        args.end_port,
        args.concurrency,
        args.timeout
    ))



# python scanner_pro.py 192.168.1.1 1 1024 -c 1000 -t 2.0
# 支持灵活配置：
# -c/--concurrency：并发连接数
# -t/--timeout：单连接超时时间