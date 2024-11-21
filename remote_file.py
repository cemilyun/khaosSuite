import time
import sys
from itertools import repeat
from multiprocessing import Pool, cpu_count
import subprocess
import socket
import array

def cpu_stress(x, runtime=1, sleeptime=0, busycycles=100000):
    timeout = time.time() + runtime
    cnt = 0
    while True:
        if time.time() > timeout:
            break
        if sleeptime and cnt % busycycles == 0:
            time.sleep(sleeptime)
        x * x
        cnt += 1

def memory_stress(size_in_mb, runtime=1):
    timeout = time.time() + runtime
    total_elements = size_in_mb * 1024 * 1024 // 8  # 8 baytlık double tipi eleman sayısı

    # Belleği verimli bir şekilde allocate etmek için array kullanıyoruz
    memory = array.array('d')  # 'd' double tipini temsil eder
    chunk_size = 1024 * 1024 // 8  # 1 MB'daki eleman sayısı

    index = 0

    while time.time() < timeout:
        # Belleği parça parça allocate ediyoruz
        if len(memory) < total_elements:
            remaining_elements = total_elements - len(memory)
            elements_to_allocate = min(chunk_size, remaining_elements)
            memory.extend([1.0] * elements_to_allocate)

        # Bellek üzerinde işlem yapıyoruz
        end_index = min(index + chunk_size, len(memory))
        for i in range(index, end_index):
            memory[i] *= 1.000001

        index = end_index if end_index < len(memory) else 0

def process_kill(process):
    if isinstance(process, int):
        try:
            subprocess.run(["taskkill", "/f", "/PID", str(process)], check=True)
            print(f"Successfully killed process with PID {process}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to kill process with PID {process}: {e}")
    elif isinstance(process, str):
        try:
            subprocess.run(["taskkill", "/f", "/IM", process], check=True)
            print(f"Successfully killed process with name {process}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to kill process with name {process}: {e}")
    else:
        print("Invalid process identifier. Please provide a process ID (int) or process name (str).")

def shutdown():
    pass
    # shutdown /s /t 0 ile bilgisayarı kapatırız.
    # shutdown /r /t 0 ile bilgisayarı yeniden başlatırız.
    # shutdown /l ile bilgisayarı kilitleriz.

def blackhole(targets, runtime):
    ip_addresses = []
    for target in targets:
        try:
            ip_address = socket.gethostbyname(target)
            ip_addresses.append(ip_address)
        except socket.gaierror:
            print(f"Failed to resolve {target}, skipping...")

    timeout = time.time() + runtime
    try:
        for ip_address in ip_addresses:
            print(f"Blocking {ip_address} for {runtime} seconds...")
            # Use route command to drop packets by adding unreachable route with gateway 0.0.0.0
            subprocess.run(["route", "add", ip_address, "0.0.0.0", "metric", "1"], check=True)
        while time.time() < timeout:
            time.sleep(1)
    except subprocess.CalledProcessError as e:
        print(f"Failed to block target {ip_address}: {e}")
    finally:
        for ip_address in ip_addresses:
            print(f"Unblocking {ip_address}...")
            # Remove the route after the timeout
            subprocess.run(["route", "delete", ip_address], check=True)

def dns():
    pass
    # Gerçekleştirilecek fonksiyon

def latency():
    pass
    # Gerçekleştirilecek fonksiyon

if __name__ == '__main__':
    if '--cpu' in sys.argv:
        runtime = float(sys.argv[sys.argv.index('--cpu') + 1]) if len(sys.argv) > 2 else 5
        processes = cpu_count() if len(sys.argv) <= 3 else int(sys.argv[sys.argv.index('--cpu') + 2])
        processes = min(max(processes, 1), cpu_count())
        print(f'Running CPU stress for {runtime}s using {processes} cores')
        pool = Pool(processes)
        pool.starmap(cpu_stress, zip(range(processes), repeat(runtime)))

    if '--memory' in sys.argv:
        runtime = float(sys.argv[sys.argv.index('--memory') + 1]) if len(sys.argv) > 2 else 5
        mem_size = int(sys.argv[sys.argv.index('--memory') + 2]) if len(sys.argv) > 3 else 1024  # Varsayılan bellek boyutu 1024 MB
        print(f'Running memory stress with {mem_size} MB for {runtime}s')
        memory_stress(mem_size, runtime)

    if '--process_kill' in sys.argv:
        process = sys.argv[sys.argv.index('--process_kill') + 1]
        try:
            process = int(process)
        except ValueError:
            pass
        process_kill(process)

    if '--blackhole' in sys.argv:
        runtime = float(sys.argv[sys.argv.index('--blackhole') + 1])
        targets = sys.argv[sys.argv.index('--blackhole') + 2:]
        print(f'Running blackhole on targets {targets} for {runtime}s')
        blackhole(targets, runtime)
