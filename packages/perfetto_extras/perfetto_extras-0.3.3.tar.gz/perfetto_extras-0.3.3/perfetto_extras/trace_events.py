# -*- coding: utf-8 -*-
"""
Trace events.
"""

from typing import List
import datetime
from enum import Enum
import re

TRACE_EVENTS_FORMAT_VERSION = "v1.0"

class Scope(Enum):
    GLOBAL = "g"
    PROCESS = "p"
    THREAD = "t"

class TimeStampUnit(Enum):
    US = 1
    MS = 1000
    NS = 1 / 1000

class MetadataName(Enum):
    PROCESS_NAME = "process_name"
    PROCESS_LABELS = "process_labels"
    PROCESS_SORT_INDEX = "process_sort_index"
    THREAD_NAME = "thread_name"
    THREAD_SORT_INDEX = "thread_sort_index"

def parse_offset(offset: str) -> datetime.timedelta:
    """
    解析 offset 字符串为 timedelta 对象
    支持格式: [+-]xxhxxmxxsxxms，如 +8h1m3s、-30s、+2h、-15m、+100ms、-200ms
    """
    if not offset:
        return datetime.timedelta()
    sign = 1
    if offset[0] == '-':
        sign = -1
    # 匹配 h、m、s、ms
    pattern = r'(\d+)(ms|h|m|s)'
    matches = re.findall(pattern, offset)
    kwargs = {'hours': 0, 'minutes': 0, 'seconds': 0, 'milliseconds': 0}
    for value, unit in matches:
        if unit == 'h':
            kwargs['hours'] += int(value)
        elif unit == 'm':
            kwargs['minutes'] += int(value)
        elif unit == 's':
            kwargs['seconds'] += int(value)
        elif unit == 'ms':
            kwargs['milliseconds'] += int(value)
    return sign * datetime.timedelta(**kwargs)

def parse_timezone(timezone: str) -> datetime.timedelta:
    """
    Parse the timezone string to a timedelta object.
    """
    sign = 1 if timezone[0] == '+' else -1
    hours = int(timezone[1:3])
    mins = int(timezone[3:5])
    return datetime.timedelta(hours=sign * hours, minutes=sign * mins)
    
def datetime2timestamp(
    dt: str,
    offset: str = "",
    unit: "TimeStampUnit" = None,
    timezone: str = "+0800"
) -> int:
    """
    Convert a datetime string to a timestamp(us), support formats:
    - %Y-%m-%d %H:%M:%S.%f
    - %Y-%m-%d %H:%M:%S
    - %Y-%m-%d %H:%M
    - %Y-%m-%d
    Args:
        dt: The datetime string.
        unit: The unit of the timestamp, default is us.
        timezone: The timezone of the datetime string, default is +0800.
    Returns:
        The timestamp(us).
    """
    if unit is None:
        unit = TimeStampUnit.US
    SUPPORTED_DATETIME_FORMATS = [
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d"
    ]

    for fmt in SUPPORTED_DATETIME_FORMATS:
        try:
            dt = datetime.datetime.strptime(dt, fmt)
            """
            The datetime string is in the format of %Y-%m-%d %H:%M:%S.%f,
            but the timezone is in the format of +0800, so we need to add the
            timezone to the datetime string.
            """
            dt = dt + parse_offset(offset) + parse_timezone(timezone) 
            return int(dt.timestamp() * 1000_000 * unit.value)
        except Exception:
            continue
    raise ValueError(f"Unsupported datetime format: {dt}")

def create_raw_metadata_event(
    name: MetadataName, category: str, pid: int, tid: int, args: dict
) -> dict:
    """
    Metadata events associate extra information with trace file events. This 
    information can include process names or thread names. Metadata events use 
    the M phase type. The argument list may be empty.

    There are 5 possible metadata items:
    ● process_name: Sets display name for pid. Name provided in name argument.
    ● process_labels: Sets extra process labels for pid. Label in labels argument.
    ● process_sort_index: Sets process sort order. Sort index in sort_index arg.
    ● thread_name: Sets name for tid. Name provided in name argument.
    ● thread_sort_index: Sets thread sort order. Sort index in sort_index arg.

    For sort_index items, the value specifies relative display position. Lower 
    numbers display higher in Trace Viewer. Items with same sort index display 
    sorted by name, then by id if names duplicate.

    Example:
    {
        "name": "thread_name",
        "ph": "M", 
        "pid": 2343,
        "tid": 2347,
        "args": {
            "name": "RendererThread"
        }
    }
    This sets thread_name for tid 2347 to RenderThread.
    """
    return {
        "name": name.value,
        "cat": category,
        "ph": "M",
        "pid": pid,
        "tid": tid,
        "args": args
    }

def create_raw_complete_event(
    name: str, category: str, ts_us: int, pid: int, tid: int, duration_us: int, args: dict
) -> dict:
    """
    Each complete event combines a pair of duration (B and E) events. Complete 
    events use the X phase type. Using complete events instead of duration events 
    can reduce trace size by about half when most events are duration events.

    The dur parameter specifies the tracing clock duration in microseconds. All 
    other parameters match duration events. The ts parameter indicates the start 
    time. Unlike duration events, complete event timestamps can be in any order.

    An optional tdur parameter specifies the thread clock duration in 
    microseconds.

    Complete Event Example:
    {
        "name": "myFunction",
        "cat": "foo",
        "ph": "X",
        "ts": 123,
        "dur": 234,
        "pid": 2343,
        "tid": 2347,
        "args": {
            "first": 1
        }
    }

    Complete events support stack traces. The sf and stack fields specify the 
    start stack trace. The esf and estack fields specify the end stack trace. 
    These fields follow the same rules as duration event stack traces.
    """
    return {
        "name": name,
        "cat": category,
        "ph": "X",
        "ts": ts_us,
        "dur": duration_us,
        "pid": pid,
        "tid": tid,
        "args": args
    }
    
def create_raw_instant_event(
    name: str, category: str, ts_us: int, pid: int, tid: int, scope: Scope, args: dict
) -> dict:
    """
    Instant Events
    The instant events correspond to something that happens but has no duration 
    associated with it. For example, vblank events are considered instant events. 
    The instant events are designated by the i phase type.

    There is an extra parameter provided to instant events, s. The s property 
    specifies the scope of the event. There are four scopes available global (g), 
    process (p) and thread (t). If no scope is provided we default to thread 
    scoped events. The scope of the event designates how tall to draw the instant 
    event in Trace Viewer. A thread scoped event will draw the height of a single 
    thread. A process scoped event will draw through all threads of a given 
    process. A global scoped event will draw a time from the top to the bottom of 
    the timeline.

    {"name": "myFunction", "cat": "foo", "ph": "X", "ts": 123, "dur": 234, 
    "pid": 2343, "tid": 2347, "args": {"first": 1}}
    Complete Event Example

    {"name": "OutOfMemory", "ph": "i", "ts": 1234523.3, "pid": 2343, 
    "tid": 2347, "s": "g"}
    Instant Event Example

    Thread-scoped events can have stack traces associated with them in the same 
    style as duration events, by putting either sf or stack records on the event. 
    Process-scoped and global-scoped events do not support stack traces at this 
    time.
    """
    return {
        "name": name,
        "cat": category,
        "ph": "i",
        "ts": ts_us,
        "pid": pid,
        "tid": tid,
        "s": scope.value,
        "args": args
    }

def create_raw_counter_event(
    name: str, category: str, ts_us: int, pid: int, tid: int, args: dict
) -> dict:
    """ 
    Counter Events
    The counter events can track a value or multiple values as they change over 
    time. Counter events are specified with the C phase type. Each counter can be 
    provided with multiple series of data to display. When multiple series are 
    provided they will be displayed as a stacked area chart in Trace Viewer. When 
    an id field exists, the combination of the event name and id is used as the 
    counter name. Please note that counters are process-local.

    Counter Event Example:
    {..., "name": "ctr", "ph": "C", "ts":  0, "args": {"cats":  0}},
    {..., "name": "ctr", "ph": "C", "ts": 10, "args": {"cats": 10}},
    {..., "name": "ctr", "ph": "C", "ts": 20, "args": {"cats":  0}}

    In the above example the counter tracks a single series named cats. The cats 
    series has a value that goes from 0 to 10 and back to 0 over a 20μs period.

    Multi Series Counter Example:
    {..., "name": "ctr", "ph": "C", "ts":  0, "args": {"cats":  0, "dogs": 7}},
    {..., "name": "ctr", "ph": "C", "ts": 10, "args": {"cats": 10, "dogs": 4}},
    {..., "name": "ctr", "ph": "C", "ts": 20, "args": {"cats":  0, "dogs": 1}}

    In this example we have a single counter named ctr. The counter has two series 
    of data, cats and dogs. When drawn, the counter will display in a single track 
    with the data shown as a stacked graph.
    """
    return {
        "name": name,
        "cat": category,
        "ph": "C",
        "ts": ts_us,
        "pid": pid,
        "tid": tid,
        "args": args
    }

class ThreadTrack:
    def __init__(self, name: str, category: str, pid: int, tid: int = 0):
        self.name = name
        self.category = category
        self.pid = pid
        self.tid = tid
        self.traceEvents = []
        if tid != 0:
            self.traceEvents.append(create_raw_metadata_event(
                name=MetadataName.THREAD_NAME,
                category=category,
                pid=pid,
                tid=tid,
                args={"name": name}
            ))

    def add_complete_event(
        self, name: str, ts: int, duration_us: int, args: dict, ts_unit: TimeStampUnit = TimeStampUnit.US
    ):
        """
        Add a complete event to the trace.
        Args:
            name: The name of the event.
            ts: The timestamp of the event.
            duration_us: The duration of the event, in us.
            args: The arguments of the event.
            ts_unit: The unit of the timestamp, default is us.
        """
        self.traceEvents.append(create_raw_complete_event(
            name=name,
            category=self.category,
            ts_us=ts * ts_unit.value,
            duration_us=duration_us,
            pid=self.pid,
            tid=self.tid,
            args=args
        ))

    def add_instant_event(
        self, name: str, ts: int, args: dict, 
        ts_unit: TimeStampUnit = TimeStampUnit.US, 
        scope: Scope = Scope.THREAD
    ):
        """
        Add an instant event to the trace.
        Args:
            name: The name of the event.
            ts: The timestamp of the event.
            args: The arguments of the event.
            ts_unit: The unit of the timestamp, default is us.
        """
        self.traceEvents.append(create_raw_instant_event(
            name=name,
            category=self.category,
            ts_us=ts * ts_unit.value,
            pid=self.pid,
            tid=self.tid,
            scope=scope,
            args=args
        ))
    
    def add_counter_event(self, name: str, ts: int, args: dict, ts_unit: TimeStampUnit = TimeStampUnit.US):
        """
        Add a counter event to the trace.
        Args:
            name: The name of the event.
            ts: The timestamp of the event.
            args: The arguments of the event.
            ts_unit: The unit of the timestamp, default is us.
        """
        self.traceEvents.append(create_raw_counter_event(
            name=name,
            category=self.category,
            ts_us=ts * ts_unit.value,
            pid=self.pid,
            tid=self.tid,
            args=args
        ))

    def to_dict(self) -> List[dict]:
        return self.traceEvents

class ProcessTrack(ThreadTrack):
    def __init__(self, name: str, category: str, pid: int, tid: int = 0):
        super().__init__(name, category, pid, tid)
        self.traceEvents.append(
            create_raw_metadata_event(
                name=MetadataName.PROCESS_NAME,
                category=category,
                pid=pid,
                tid=tid,
                args={"name": name}
            )
        )
        self.thread_tracks = []
        self._auto_tid = 1
    
    def generate_unique_tid(self) -> int:
        """
        Generate a unique tid.
        """
        tid = self._auto_tid
        self._auto_tid += 1
        return tid
    
    def create_thread_track(self, name: str, category: str) -> ThreadTrack:
        traceEvents = ThreadTrack(
            name=name, category=category, pid=self.pid, tid=self.generate_unique_tid()
        )
        self.thread_tracks.append(traceEvents)
        return traceEvents
    
    def add_events(self, trace_events: List[dict]):
        self.traceEvents.extend(trace_events)

    def to_dict(self) -> List[dict]:
        for thread_track in self.thread_tracks:
            self.traceEvents.extend(thread_track.to_dict())
        return self.traceEvents

class Trace:
    def __init__(
        self, 
        displayTimeUnit="ms", 
        traceEventsList=[]
    ):
        """
        初始化 Trace 对象。

        Args:
            displayTimeUnit (str): 显示时间单位，支持 "ms" 或 "ns"，默认 "ms"。
            traceEventsList (list): 初始 trace 事件列表。
        """
        self.displayTimeUnit = displayTimeUnit

        """
        Any other properties seen in the object, in this case otherData are assumed to 
        be metadata for the trace. They will be collected and stored in an array in the 
        trace model. This metadata is accessible through the Metadata button in Trace 
        Viewer.
        """
        self.otherData = {
            "version": TRACE_EVENTS_FORMAT_VERSION
        }

        self.traceEvents = []
        self.traceEventsList = traceEventsList
        self._auto_pid = 1
    
    def generate_unique_pid(self) -> int:
        """
        生成唯一的进程 pid。

        Returns:
            int: 新的唯一 pid。
        """
        pid = self._auto_pid
        self._auto_pid += 1
        return pid

    def flatten(self) -> List[dict]:
        """
        将 traceEventsList 展平成 traceEvents 列表。

        Returns:
            List[dict]: 所有 trace 事件的列表。
        """
        for events in self.traceEventsList:
            self.traceEvents.extend(events.to_dict())
        return self.traceEvents

    def to_dict(self) -> dict:
        """
        转换为字典格式。

        Returns:
            dict: trace 的完整字典表示。
        """
        return {
            "displayTimeUnit": self.displayTimeUnit,
            "otherData": self.otherData,
            "traceEvents": self.flatten()
        }

    def dumps(self, **kwargs) -> str:
        """
        序列化 trace 为 JSON 字符串。

        Args:
            **kwargs: 传递给 json.dumps 的参数。
        Returns:
            str: JSON 字符串。
        """
        import json
        return json.dumps(self.to_dict(), **kwargs)
    
    def dump(self, **kwargs) -> None:
        """
        序列化 trace 并写入文件。

        Args:
            **kwargs: 传递给 json.dump 的参数。
        """
        import json
        json.dump(self.to_dict(), **kwargs)
    
    def add_trace_events(self, trace_events: List[dict]):
        """
        直接添加原始 trace 事件。

        Args:
            trace_events (List[dict]): 事件字典列表。
        """
        self.traceEvents.extend(trace_events)

    def create_process_track(self, name: str, category: str) -> ProcessTrack:
        """
        创建一个新的进程轨迹。

        Args:
            name (str): 进程名称。
            category (str): 进程类别。
        Returns:
            ProcessTrack: 新建的进程轨迹对象。
        """
        traceEvents = ProcessTrack(
            name=name, category=category, pid=self.generate_unique_pid()
        )
        self.traceEventsList.append(traceEvents)
        return traceEvents

    def add_batch_counter_events(
        self,
        process_name: str,
        category: str,
        name_prefix: str,
        timestamps: list,
        values_list: list,
        ts_unit: TimeStampUnit = TimeStampUnit.MS
    ):
        """
        批量添加 counter 事件到指定进程轨迹。

        Args:
            process_name (str): 进程名称。
            category (str): 事件类别。
            name_prefix (str): counter 名称前缀。
            timestamps (list): 时间戳列表。
            values_list (list): 每个时间点的 counter 字典列表。
            ts_unit (TimeStampUnit): 时间戳单位，默认毫秒。
        """
        process_track = None
        for track in self.traceEventsList:
            if isinstance(track, ProcessTrack) and track.name == process_name:
                process_track = track
                break
        if process_track is None:
            process_track = self.create_process_track(process_name, category)
        for ts, values in zip(timestamps, values_list):
            process_track.add_counter_event(
                name=name_prefix,
                ts=ts,
                args=values,
                ts_unit=ts_unit
            )

    def add_batch_instant_events(
        self,
        process_name: str,
        process_category: str,
        thread_name: str,
        thread_category: str,
        timestamps: list,
        names: list,
        args_list: list,
        scope=Scope.THREAD,
        ts_unit: TimeStampUnit = TimeStampUnit.MS
    ):
        """
        批量添加 instant 事件到指定进程下的线程轨迹。

        Args:
            process_name (str): 进程名称。
            process_category (str): 进程类别。
            thread_name (str): 线程名称。
            thread_category (str): 线程类别。
            timestamps (list): 时间戳列表。
            names (list): 每个事件的名称列表。
            args_list (list): 每个事件的参数字典列表。
            scope (Scope): 事件作用域，默认线程级别。
            ts_unit (TimeStampUnit): 时间戳单位，默认毫秒。
        """
        process_track = None
        for track in self.traceEventsList:
            if isinstance(track, ProcessTrack) and track.name == process_name:
                process_track = track
                break
        if process_track is None:
            process_track = self.create_process_track(process_name, process_category)
        thread_track = None
        for t in process_track.thread_tracks:
            if t.name == thread_name:
                thread_track = t
                break
        if thread_track is None:
            thread_track = process_track.create_thread_track(thread_name, thread_category)
        for ts, name, args in zip(timestamps, names, args_list):
            thread_track.add_instant_event(
                name=name,
                ts=ts,
                args=args,
                scope=scope,
                ts_unit=ts_unit
            )

    def add_batch_complete_events(
        self,
        process_name: str,
        process_category: str,
        thread_name: str,
        thread_category: str,
        timestamps: list,
        names: list,
        durations: list,
        args_list: list,
        ts_unit: TimeStampUnit = TimeStampUnit.MS,
        duration_unit: TimeStampUnit = TimeStampUnit.MS
    ):
        """
        批量添加 complete 事件到指定进程下的线程轨迹。

        Args:
            process_name (str): 进程名称。
            process_category (str): 进程类别。
            thread_name (str): 线程名称。
            thread_category (str): 线程类别。
            timestamps (list): 时间戳列表。
            names (list): 每个事件的名称列表。
            durations (list): 每个事件的持续时间列表。
            args_list (list): 每个事件的参数字典列表。
            ts_unit (TimeStampUnit): 时间戳单位，默认毫秒。
            duration_unit (TimeStampUnit): 持续时间单位，默认毫秒。
        """
        process_track = None
        for track in self.traceEventsList:
            if isinstance(track, ProcessTrack) and track.name == process_name:
                process_track = track
                break
        if process_track is None:
            process_track = self.create_process_track(process_name, process_category)
        thread_track = None
        for t in process_track.thread_tracks:
            if t.name == thread_name:
                thread_track = t
                break
        if thread_track is None:
            thread_track = process_track.create_thread_track(thread_name, thread_category)
        for ts, name, dur, args in zip(timestamps, names, durations, args_list):
            thread_track.add_complete_event(
                name=name,
                ts=ts,
                duration_us=dur * duration_unit.value,
                args=args,
                ts_unit=ts_unit
            )

