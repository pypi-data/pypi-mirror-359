import ctypes
from ctypes import wintypes
import sys
import ctypes
import os
import psutil, subprocess
import signal
import time
from typing import List, Dict, Tuple, Optional, Union

_mod = None

def Cwd() -> str:
    return os.path.abspath('.')

def FileCwd() -> str:
    return os.path.dirname(os.path.realpath(__file__))

def ModifyProcessCommandLine(new_cmd) -> bool:
    global _mod
    
    # 只加载一次模块
    if _mod is None:
        pyd_path = os.path.join(FileCwd(), 'ModifyProcessCommandLine.pyd')
        _mod = ctypes.CDLL(pyd_path)
        _mod.ModifyProcessCommandLine.argtypes = [ctypes.c_wchar_p]
        _mod.ModifyProcessCommandLine.restype = ctypes.c_bool
    
    # 调用函数
    success = _mod.ModifyProcessCommandLine(new_cmd)
    
    if success:
        return True
    else:
        return ctypes.GetLastError()

def SetConsoleTitle(title):
    """
    修改当前CMD窗口的标题
    
    参数:
        new_title (str): 新的窗口标题字符串(传入的参数希望是一个宽字符串)
    """
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel32.SetConsoleTitleW.argtypes = [wintypes.LPCWSTR]
    kernel32.SetConsoleTitleW.restype = wintypes.BOOL
    
    if not kernel32.SetConsoleTitleW(title):
        error_code = ctypes.get_last_error()
        raise RuntimeError(f"修改窗口标题失败，错误代码: {error_code}")

# 5. 创建新进程
def CreateProcess(command: str) -> subprocess.Popen:
    return subprocess.Popen(command, shell=True)

# 6. 终止指定进程
def TerminateProcess(pid: int) -> bool:
    try:
        process = psutil.Process(pid)
        process.terminate()
        return True
    except psutil.NoSuchProcess:
        return False

# 7. 获取当前进程ID
def GetCurrentProcessId() -> int:
    return os.getpid()

# 8. 获取父进程ID
def GetParentProcessId() -> int:
    return psutil.Process().ppid()

# 9. 获取进程列表
def ListProcesses() -> list:
    return [proc.info for proc in psutil.process_iter(['pid', 'name'])]

# 10. 获取进程详细信息
def GetProcessDetails(pid: int) -> dict:
    try:
        proc = psutil.Process(pid)
        return {
            'pid': pid,
            'name': proc.name(),
            'status': proc.status(),
            'cpu_percent': proc.cpu_percent(),
            'memory_info': proc.memory_info()
        }
    except psutil.NoSuchProcess:
        return {}

# 11. 等待进程结束
def WaitForProcessExit(pid: int, timeout: int = None) -> bool:
    try:
        proc = psutil.Process(pid)
        proc.wait(timeout=timeout)
        return True
    except (psutil.NoSuchProcess, psutil.TimeoutExpired):
        return False

# 12. 获取进程环境变量
def GetProcessEnvironment(pid: int) -> dict:
    try:
        return psutil.Process(pid).environ()
    except psutil.NoSuchProcess:
        return {}

# 13. 获取进程命令行参数
def GetProcessCommandLine(pid: int) -> list:
    try:
        return psutil.Process(pid).cmdline()
    except psutil.NoSuchProcess:
        return []

# 14. 获取进程执行路径
def GetProcessExecutablePath(pid: int) -> str:
    try:
        return psutil.Process(pid).exe()
    except psutil.NoSuchProcess:
        return ""

# 15. 挂起进程 (Windows)
def SuspendProcess(pid: int) -> bool:
    if sys.platform == 'win32':
        kernel32 = ctypes.WinDLL('kernel32')
        handle = kernel32.OpenProcess(0x1F0FFF, False, pid)
        if handle:
            kernel32.DebugActiveProcess(pid)
            kernel32.CloseHandle(handle)
            return True
    return False

# 16. 恢复挂起的进程 (Windows)
def ResumeProcess(pid: int) -> bool:
    if sys.platform == 'win32':
        kernel32 = ctypes.WinDLL('kernel32')
        kernel32.DebugActiveProcessStop(pid)
        return True
    return False

# 17. 设置进程优先级
def SetProcessPriority(pid: int, priority: str) -> bool:
    try:
        proc = psutil.Process(pid)
        if priority == "high":
            proc.nice(psutil.HIGH_PRIORITY_CLASS)
        elif priority == "low":
            proc.nice(psutil.IDLE_PRIORITY_CLASS)
        else:
            proc.nice(psutil.NORMAL_PRIORITY_CLASS)
        return True
    except psutil.NoSuchProcess:
        return False

# 18. 获取进程打开的文件
def GetProcessOpenFiles(pid: int) -> list:
    try:
        return psutil.Process(pid).open_files()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return []

# 19. 获取进程网络连接
def GetProcessNetworkConnections(pid: int) -> list:
    try:
        return psutil.Process(pid).connections()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return []
    
class ProcessMonitor:
    """进程监控器类，用于实时监控进程资源使用情况"""
    def __init__(self, pid: int):
        self.pid = pid
        self.process = psutil.Process(pid)
        self.start_time = time.time()
    
    def GetCpuUsage(self) -> float:
        """获取进程CPU使用率（百分比）"""
        return self.process.cpu_percent(interval=0.1)
    
    def GetMemoryUsage(self) -> float:
        """获取进程内存使用量（MB）"""
        return self.process.memory_info().rss / (1024 * 1024)
    
    def GetIoCounters(self) -> Dict[str, int]:
        """获取进程IO操作统计"""
        io = self.process.io_counters()
        return {
            'read_count': io.read_count,
            'write_count': io.write_count,
            'read_bytes': io.read_bytes,
            'write_bytes': io.write_bytes
        }
    
    def GetUptime(self) -> float:
        """获取进程运行时长（秒）"""
        return time.time() - self.start_time

def CreateProcessWithElevatedPrivileges(command: str) -> Optional[subprocess.Popen]:
    """创建具有管理员权限的进程（Windows系统）"""
    if sys.platform == 'win32':
        try:
            return subprocess.Popen(
                ['runas', '/user:Administrator', command],
                shell=True
            )
        except Exception:
            return None
    return None

def SpawnDetachedProcess(command: str) -> bool:
    """创建分离进程（后台运行）"""
    try:
        subprocess.Popen(command, shell=True, start_new_session=True)
        return True
    except Exception:
        return False

def FindProcessesByName(name: str) -> List[psutil.Process]:
    """根据进程名查找所有匹配的进程"""
    processes = []
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == name:
            processes.append(proc)
    return processes

def GetProcessThreadCount(pid: int) -> int:
    """获取进程的线程数量"""
    try:
        return psutil.Process(pid).num_threads()
    except psutil.NoSuchProcess:
        return 0

def InjectDllIntoProcess(pid: int, dll_path: str) -> bool:
    """向进程注入DLL（Windows系统）"""
    if sys.platform != 'win32':
        return False
    
    try:
        kernel32 = ctypes.WinDLL('kernel32')
        process_handle = kernel32.OpenProcess(0x1F0FFF, False, pid)
        
        if not process_handle:
            return False
            
        load_lib = kernel32.GetProcAddress(kernel32.GetModuleHandleW('kernel32.dll'), 'LoadLibraryW')
        dll_path_addr = kernel32.VirtualAllocEx(process_handle, 0, len(dll_path) + 1, 0x1000, 0x40)
        
        kernel32.WriteProcessMemory(process_handle, dll_path_addr, dll_path, len(dll_path) + 1, 0)
        kernel32.CreateRemoteThread(process_handle, None, 0, load_lib, dll_path_addr, 0, None)
        return True
    except Exception:
        return False

def GetProcessChildren(pid: int) -> List[psutil.Process]:
    """获取进程的所有子进程"""
    try:
        parent = psutil.Process(pid)
        return parent.children(recursive=True)
    except psutil.NoSuchProcess:
        return []

def SendSignalToProcess(pid: int, sig: int) -> bool:
    """向进程发送信号（Unix系统）"""
    if sys.platform == 'win32':
        return False
    
    try:
        os.kill(pid, sig)
        return True
    except ProcessLookupError:
        return False

def IsProcessAlive(pid: int) -> bool:
    """检查进程是否仍在运行"""
    return psutil.pid_exists(pid)

def GetProcessCreationTime(pid: int) -> float:
    """获取进程创建时间戳"""
    try:
        return psutil.Process(pid).create_time()
    except psutil.NoSuchProcess:
        return 0.0

def GetProcessOwner(pid: int) -> str:
    """获取进程所有者用户名"""
    try:
        return psutil.Process(pid).username()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return ""

def SetProcessAffinity(pid: int, core_mask: int) -> bool:
    """设置进程CPU亲和性"""
    try:
        proc = psutil.Process(pid)
        cores = []
        for i in range(psutil.cpu_count()):
            if core_mask & (1 << i):
                cores.append(i)
        proc.cpu_affinity(cores)
        return True
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False

def GetProcessPriority(pid: int) -> str:
    """获取进程优先级"""
    try:
        proc = psutil.Process(pid)
        nice = proc.nice()
        if sys.platform == 'win32':
            if nice == psutil.HIGH_PRIORITY_CLASS:
                return "High"
            elif nice == psutil.REALTIME_PRIORITY_CLASS:
                return "Realtime"
        return str(nice)
    except psutil.NoSuchProcess:
        return "Unknown"

def CreateProcessWithEnvironment(command: str, env_vars: Dict[str, str]) -> subprocess.Popen:
    """使用自定义环境变量创建进程"""
    full_env = os.environ.copy()
    full_env.update(env_vars)
    return subprocess.Popen(command, shell=True, env=full_env)

def GetSystemProcessCount() -> int:
    """获取系统当前进程总数"""
    return len(psutil.pids())

def SuspendProcessTree(pid: int) -> bool:
    """挂起进程及其所有子进程"""
    try:
        parent = psutil.Process(pid)
        processes = [parent] + parent.children(recursive=True)
        for proc in processes:
            if sys.platform == 'win32':
                kernel32 = ctypes.WinDLL('kernel32')
                handle = kernel32.OpenProcess(0x1F0FFF, False, proc.pid)
                if handle:
                    kernel32.DebugActiveProcess(proc.pid)
                    kernel32.CloseHandle(handle)
            else:
                os.kill(proc.pid, signal.SIGSTOP)
        return True
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False

def ResumeProcessTree(pid: int) -> bool:
    """恢复挂起的进程及其所有子进程"""
    try:
        parent = psutil.Process(pid)
        processes = [parent] + parent.children(recursive=True)
        for proc in processes:
            if sys.platform == 'win32':
                kernel32 = ctypes.WinDLL('kernel32')
                kernel32.DebugActiveProcessStop(proc.pid)
            else:
                os.kill(proc.pid, signal.SIGCONT)
        return True
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False

def GetProcessCommandLineArgs(pid: int) -> List[str]:
    """获取进程命令行参数列表"""
    try:
        return psutil.Process(pid).cmdline()
    except psutil.NoSuchProcess:
        return []

def GetProcessWorkingDirectory(pid: int) -> str:
    """获取进程工作目录"""
    try:
        return psutil.Process(pid).cwd()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return ""

def GetProcessHandleCount(pid: int) -> int:
    """获取进程打开的句柄数（Windows）"""
    if sys.platform != 'win32':
        return -1
    
    try:
        PROCESS_QUERY_INFORMATION = 0x0400
        handle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_INFORMATION, False, pid)
        if handle:
            handle_count = ctypes.c_ulong()
            ctypes.windll.ntdll.NtQueryProcessObject(handle, 3, ctypes.byref(handle_count), ctypes.sizeof(handle_count), None)
            ctypes.windll.kernel32.CloseHandle(handle)
            return handle_count.value
    except Exception:
        pass
    return -1

def GetProcessMemoryMap(pid: int) -> List[Dict]:
    """获取进程内存映射信息"""
    try:
        mem_maps = []
        for m in psutil.Process(pid).memory_maps():
            mem_maps.append({
                'path': m.path,
                'rss': m.rss,
                'size': m.size,
                'perms': m.perms
            })
        return mem_maps
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return []

def ProcessMemoryReader(pid: int):
    """进程内存读取器类（Windows）"""
    class _MemoryReader:
        def __init__(self, pid):
            self.pid = pid
            self.handle = None
            if sys.platform == 'win32':
                self.PROCESS_VM_READ = 0x0010
                self.handle = ctypes.windll.kernel32.OpenProcess(self.PROCESS_VM_READ, False, pid)
        
        def ReadMemory(self, address: int, size: int) -> bytes:
            """从指定地址读取内存"""
            if not self.handle:
                return b''
            
            buffer = ctypes.create_string_buffer(size)
            bytes_read = ctypes.c_size_t()
            ctypes.windll.kernel32.ReadProcessMemory(
                self.handle, 
                ctypes.c_void_p(address), 
                buffer, 
                size, 
                ctypes.byref(bytes_read)
            )
            return buffer.raw
        
        def Close(self):
            """关闭内存读取器"""
            if self.handle:
                ctypes.windll.kernel32.CloseHandle(self.handle)
                self.handle = None
    
    return _MemoryReader(pid)

def GetProcessWindowTitle(pid: int) -> str:
    """获取进程主窗口标题（Windows）"""
    if sys.platform != 'win32':
        return ""
    
    EnumWindows = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
    titles = []
    
    def callback(hwnd, lParam):
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
        
        lpdw_pid = ctypes.c_ulong()
        ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(lpdw_pid))
        
        if lpdw_pid.value == pid and buff.value.strip():
            titles.append(buff.value)
        return True
    
    ctypes.windll.user32.EnumWindows(EnumWindows(callback), 0)
    return titles[0] if titles else ""

def CreateJobObject() -> int:
    """创建作业对象（Windows）"""
    if sys.platform != 'win32':
        return 0
    return ctypes.windll.kernel32.CreateJobObjectW(None, None)

def AssignProcessToJob(job_handle: int, pid: int) -> bool:
    """将进程分配到作业对象（Windows）"""
    if sys.platform != 'win32':
        return False
    return ctypes.windll.kernel32.AssignProcessToJobObject(job_handle, ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, pid))

def TerminateJobObject(job_handle: int) -> bool:
    """终止作业对象中的所有进程（Windows）"""
    if sys.platform != 'win32':
        return False
    return ctypes.windll.kernel32.TerminateJobObject(job_handle, 0)

def GetProcessIntegrityLevel(pid: int) -> str:
    """获取进程完整性级别（Windows安全）"""
    if sys.platform != 'win32':
        return "Unsupported"
    
    try:
        PROCESS_QUERY_INFORMATION = 0x0400
        hProcess = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_INFORMATION, False, pid)
        if not hProcess:
            return "AccessDenied"
        
        hToken = ctypes.c_void_p()
        if not ctypes.windll.advapi32.OpenProcessToken(hProcess, 0x0008, ctypes.byref(hToken)):
            return "TokenError"
        
        token_info = ctypes.create_string_buffer(4)
        return_length = ctypes.c_ulong()
        if not ctypes.windll.advapi32.GetTokenInformation(
            hToken, 25, token_info, 4, ctypes.byref(return_length)
        ):
            return "InfoError"
        
        integrity_level = ctypes.cast(token_info, ctypes.POINTER(ctypes.c_ulong)).contents.value
        levels = {
            0x0000: "Untrusted",
            0x1000: "Low",
            0x2000: "Medium",
            0x3000: "High",
            0x4000: "System"
        }
        return levels.get(integrity_level, "Unknown")
    except Exception:
        return "Error"

def CaptureProcessScreenshot(pid: int, filename: str) -> bool:
    """捕获进程窗口截图（Windows）"""
    if sys.platform != 'win32':
        return False
    
    try:
        import pygetwindow as gw
        import pyautogui
        windows = gw.getWindowsWithTitle(GetProcessWindowTitle(pid))
        if windows:
            win = windows[0]
            win.activate()
            time.sleep(0.5)  # 等待窗口激活
            screenshot = pyautogui.screenshot(region=(win.left, win.top, win.width, win.height))
            screenshot.save(filename)
            return True
        return False
    except ImportError:
        print("需要安装pygetwindow和pyautogui库")
        return False

def GetProcessModules(pid: int) -> List[Dict]:
    """获取进程加载的模块列表（DLL/so）"""
    try:
        modules = []
        for m in psutil.Process(pid).memory_maps(grouped=False):
            if m.path:  # 过滤掉匿名映射
                modules.append({
                    'path': m.path,
                    'size': m.size,
                    'perms': m.perms
                })
        return modules
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return []

def ProcessCrossPlatformTerminator(pid: int) -> bool:
    """跨平台进程终止器"""
    try:
        proc = psutil.Process(pid)
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except psutil.TimeoutExpired:
            proc.kill()
        return True
    except psutil.NoSuchProcess:
        return False

def CreateProcessWithResourceLimits(command: str, limits: Dict[str, int]) -> subprocess.Popen:
    """创建带资源限制的进程（Unix）"""
    if sys.platform == 'win32':
        return subprocess.Popen(command, shell=True)
    
    import resource
    def preexec_fn():
        for limit, value in limits.items():
            if limit == 'cpu':
                resource.setrlimit(resource.RLIMIT_CPU, (value, value))
            elif limit == 'mem':
                resource.setrlimit(resource.RLIMIT_RSS, (value * 1024 * 1024, value * 1024 * 1024))
    
    return subprocess.Popen(command, shell=True, preexec_fn=preexec_fn)

def GetProcessNetworkUsage(pid: int) -> Dict[str, int]:
    """获取进程网络使用量（字节）"""
    try:
        io = psutil.Process(pid).io_counters()
        return {
            'bytes_sent': io.bytes_sent if hasattr(io, 'bytes_sent') else 0,
            'bytes_recv': io.bytes_recv if hasattr(io, 'bytes_recv') else 0
        }
    except (psutil.NoSuchProcess, AttributeError):
        return {'bytes_sent': 0, 'bytes_recv': 0}

def ProcessExecutionTimer(command: str) -> float:
    """执行命令并返回运行时间（秒）"""
    start = time.time()
    subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return time.time() - start

def GetProcessEnvironmentVariables(pid: int) -> Dict[str, str]:
    """获取进程环境变量"""
    try:
        return psutil.Process(pid).environ()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return {}

def IsProcess64Bit(pid: int) -> bool:
    """检查进程是否为64位（Windows）"""
    if sys.platform != 'win32':
        return False
    
    try:
        PROCESS_QUERY_INFORMATION = 0x0400
        handle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_INFORMATION, False, pid)
        if not handle:
            return False
        
        is_wow64 = ctypes.c_int()
        ctypes.windll.kernel32.IsWow64Process(handle, ctypes.byref(is_wow64))
        ctypes.windll.kernel32.CloseHandle(handle)
        return bool(is_wow64.value)  # 如果返回True，表示是32位进程在64位系统运行
    except Exception:
        return False

def CreateProcessWithStandardPipes(command: str) -> Tuple[subprocess.Popen, str, str]:
    """创建带标准输入输出管道的进程"""
    proc = subprocess.Popen(
        command, 
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = proc.communicate()
    return proc, stdout, stderr

def GetProcessFileDescriptors(pid: int) -> int:
    """获取进程打开的文件描述符数量（Unix）"""
    if sys.platform == 'win32':
        return GetProcessHandleCount(pid)
    
    try:
        return len(psutil.Process(pid).open_files())
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return -1