"""Own the lifetime of an interactive stdio MCP process and its descendants.

Windows starts the server suspended, assigns it to a kill-on-close Job, then
resumes it. A root exit never abandons descendants. POSIX uses a process group.
This is process ownership, not filesystem/network isolation.
"""
from __future__ import annotations

import ctypes
import os
import signal
import subprocess
import time


class McpProcess:
    def __init__(self, argv, *, cwd, env=None):
        self.process = None
        self.job = None
        self.kernel = None
        self.cleanup = None
        try:
            flags = 0
            if os.name == 'nt':
                from ctypes import wintypes as w
                self.kernel = ctypes.WinDLL('kernel32', use_last_error=True)
                kernel = self.kernel
                kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, w.LPCWSTR]
                kernel.CreateJobObjectW.restype = w.HANDLE
                kernel.SetInformationJobObject.argtypes = [w.HANDLE, ctypes.c_int, ctypes.c_void_p, w.DWORD]
                kernel.AssignProcessToJobObject.argtypes = [w.HANDLE, w.HANDLE]
                kernel.TerminateJobObject.argtypes = [w.HANDLE, w.UINT]
                kernel.QueryInformationJobObject.argtypes = [w.HANDLE, ctypes.c_int, ctypes.c_void_p, w.DWORD, ctypes.c_void_p]
                kernel.CloseHandle.argtypes = [w.HANDLE]

                class Basic(ctypes.Structure):
                    _fields_ = [('process_time', ctypes.c_longlong), ('job_time', ctypes.c_longlong),
                                ('flags', w.DWORD), ('min_ws', ctypes.c_size_t), ('max_ws', ctypes.c_size_t),
                                ('active', w.DWORD), ('affinity', ctypes.c_size_t), ('priority', w.DWORD), ('scheduling', w.DWORD)]
                class Counters(ctypes.Structure):
                    _fields_ = [(name, ctypes.c_ulonglong) for name in ('read_ops', 'write_ops', 'other_ops', 'read_bytes', 'write_bytes', 'other_bytes')]
                class Limits(ctypes.Structure):
                    _fields_ = [('basic', Basic), ('io', Counters), ('process_limit', ctypes.c_size_t),
                                ('job_limit', ctypes.c_size_t), ('peak_process', ctypes.c_size_t), ('peak_job', ctypes.c_size_t)]
                self.job = kernel.CreateJobObjectW(None, None)
                if not self.job:
                    raise ctypes.WinError(ctypes.get_last_error())
                limits = Limits()
                limits.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
                if not kernel.SetInformationJobObject(self.job, 9, ctypes.byref(limits), ctypes.sizeof(limits)):
                    raise ctypes.WinError(ctypes.get_last_error())
                flags = subprocess.CREATE_NO_WINDOW | 0x4  # CREATE_SUSPENDED
            self.process = subprocess.Popen(argv, cwd=cwd, env=env,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                **({'creationflags': flags} if os.name == 'nt' else {'start_new_session': True}))
            if self.job:
                if not self.kernel.AssignProcessToJobObject(self.job, int(self.process._handle)):
                    raise ctypes.WinError(ctypes.get_last_error())
                native = ctypes.WinDLL('ntdll')
                native.NtResumeProcess.argtypes = [w.HANDLE]
                native.NtResumeProcess.restype = ctypes.c_long
                if native.NtResumeProcess(int(self.process._handle)) != 0:
                    raise OSError('Cannot resume contained MCP server')
        except BaseException:
            self._force_close()
            if self.process is not None:
                for stream in (self.process.stdin, self.process.stdout, self.process.stderr):
                    if stream is not None:
                        stream.close()
            raise

    def _wait_empty_job(self, timeout=3):
        from ctypes import wintypes as w
        class Accounting(ctypes.Structure):
            _fields_ = [('total_user', ctypes.c_longlong), ('total_kernel', ctypes.c_longlong),
                        ('period_user', ctypes.c_longlong), ('period_kernel', ctypes.c_longlong),
                        ('page_faults', w.DWORD), ('total_processes', w.DWORD),
                        ('active_processes', w.DWORD), ('terminated_processes', w.DWORD)]
        deadline = time.monotonic() + timeout
        while True:
            accounting = Accounting()
            if not self.kernel.QueryInformationJobObject(self.job, 1, ctypes.byref(accounting), ctypes.sizeof(accounting), None):
                raise ctypes.WinError(ctypes.get_last_error())
            if accounting.active_processes == 0:
                return
            if time.monotonic() >= deadline:
                raise TimeoutError('Owned MCP Job still contains active processes after termination')
            time.sleep(.01)

    def _force_close(self):
        try:
            if self.job:
                if not self.kernel.TerminateJobObject(self.job, 0):
                    raise ctypes.WinError(ctypes.get_last_error())
                self._wait_empty_job()
            elif self.process is not None and os.name != 'nt':
                try:
                    os.killpg(self.process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        finally:
            if self.job:
                self.kernel.CloseHandle(self.job)
                self.job = None
            if self.process is not None:
                if self.process.poll() is None:
                    self.process.kill()
                self.process.wait(timeout=3)

    def close(self, *, grace_seconds=3):
        if self.cleanup is not None:
            return self.cleanup
        try:
            if self.process.stdin and not self.process.stdin.closed:
                try:
                    self.process.stdin.close()
                except BrokenPipeError:
                    pass
            try:
                self.process.wait(timeout=grace_seconds)
            except subprocess.TimeoutExpired:
                pass
            self._force_close()
            self.cleanup = {'status': 'verified' if os.name == 'nt' else 'observed',
                            'scope': 'owned Windows Job active-process count zero before close' if os.name == 'nt' else
                                     'owned POSIX process group signalled; root invocation reaped',
                            'root_returncode': self.process.returncode}
        except (OSError, subprocess.SubprocessError) as exc:
            self.cleanup = {'status': 'unknown', 'reason': str(exc)}
            raise
        return self.cleanup
