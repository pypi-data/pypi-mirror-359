# -*- coding: utf-8 -*-
import re
import json
import time
import random
import string
import pymysql
import hashlib
import sqlite3
import requests
import http.cookies
import asyncio
import websockets
from datetime import datetime

class mysqldb():
    def __init__(self,host='',port=3306,db='',user='',passwd='',charset='utf8'):
        self.conn = pymysql.connect(host=host, port=port, db=db, user=user, passwd=passwd,charset=charset,read_timeout=10,write_timeout=10)
        self.cur = self.conn.cursor(cursor = pymysql.cursors.DictCursor)

    def __enter__(self):
        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.cur.close()
        self.conn.close()

class sqlite(object):
    def __init__(self,sqlcmd,db_name):
        self.sqlcmd = sqlcmd
        self.db_name = db_name

    def run(self):
        return self.sqlcommit()

    def sqlcommit(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            sqlex=cursor.execute(self.sqlcmd)
            sqlrc=cursor.rowcount
            sqlfa=cursor.fetchmany(200)
            cursor.close()
            conn.commit()
            conn.close()
            if self.sqlcmd.split(" ")[0]=='select':
                return sqlfa
            else:
                return sqlrc
        except Exception as error:
            return "sqlite数据库执行发生错误:"+str(error)

def mysqlex(sqlcmd, host='', port=3306, db='', user='', passwd='', charset='utf8', args=[]):
    def execute_query(db, sqlcmd, args):
        try:
            if args:
                db.executemany(sqlcmd, args)
            else:
                db.execute(sqlcmd)

            # Trim leading/trailing spaces and check if it starts with SELECT
            sqlcmd_cleaned = sqlcmd.strip().lower()

            if sqlcmd_cleaned.startswith("select"):
                return db.fetchall()  # Return all results for SELECT queries
            else:
                return db.rowcount  # Return affected rows for non-SELECT queries
        except Exception as error:
            return "MySQL database execution error: " + str(error)

    # If no host is provided, assume a local connection
    if host == '':
        with mysqldb() as db:
            return execute_query(db, sqlcmd, args)
    else:
        # If host is provided, create a remote connection
        with mysqldb(host, port, db, user, passwd, charset) as db:
            return execute_query(db, sqlcmd, args)

class date_time:
    def __init__(self):
        self.time = datetime.now()

    def get_year(self):
        return self.time.year

    def get_month(self):
        return self.time.month

    def get_day(self):
        return self.time.day

    def get_hour(self):
        return self.time.hour

    def get_minute(self):
        return self.time.minute

    def get_second(self):
        return self.time.second

    def format_time(self, format_str="%Y-%m-%d %H:%M:%S"):
        return self.time.strftime(format_str)

def send_msg(url,title="默认标题", content="默认消息", **kwargs):
    data = {"title": title, "content": content, **kwargs}
    r = requests.post(url, json=data, timeout=3)
    return r.text

def ding_msg(url,title="默认标题", content="默认消息", **kwargs):
    data={"title": title, "content": content, **kwargs}
    r=requests.post(url,json=data,timeout=3)
    return r.text

def mprint(*args):
    if args:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), *args)

def format_cookie(cookie_str):
    cookie = http.cookies.SimpleCookie(cookie_str)
    cookie_dict = {}
    for key, morsel in cookie.items():
        cookie_dict[key] = morsel.value
    return json.dumps(cookie_dict)

def write_str(Str,File="./temp.log"):
    with open(File, 'a') as File:
        File.write(Str+"\n")
        print ("写入完成！")

def random_agent(user_agent_list=None):
    if user_agent_list is None:
        user_agent_list = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36","Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59 Safari/537.36","Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0"]
    if user_agent_list:
        return random.choice(user_agent_list)
    else:
        return None

def timestamp(timestamp_type=0):
    thistime = time.time()
    return int(thistime) if timestamp_type == 0 else int(thistime * 1000)

def md5_hex(text):
    try:
        md5_hash = hashlib.md5(text.encode()).hexdigest()
        return md5_hash
    except Exception as e:
        print(f"Error calculating MD5 hash: {e}")
        return None

def hex_to_rgb(hex_or_rgb):
    if isinstance(hex_or_rgb, str):
        hex_string = hex_or_rgb.lstrip('#')
        return tuple(int(hex_string[i:i+2], 16) for i in (0, 2, 4))
    elif isinstance(hex_or_rgb, tuple) and len(hex_or_rgb) == 3:
        return hex_or_rgb
    else:
        raise ValueError('Input must be a string in the format "#RRGGBB" or a tuple of 3 integers.')

def rgb_to_hex(rgb):
    if isinstance(rgb, str):
        rgb = tuple(map(int, (rgb.replace("(","").replace(")","")).split(',')))
    r, g, b = rgb
    return f"#{r:02X}{g:02X}{b:02X}"

def gen_uid(length=32):
    try:
        # Customize random string based on parameters
        characters = string.ascii_letters
        characters += string.digits
        ret_length = length if length is not None else random.randint(1, 100)
        random_string = ''.join(random.sample(characters, 40))
        # Generate UID
        timestamp_part = timestamp(1)
        uid = md5_hex(random_string + str(timestamp_part))
        if ret_length >len(uid):
            return uid
        else:
            return uid[0:ret_length]
    except Exception as e:
        print(f"Error generating unique ID: {e}")
        return None

def link_str(str1, str2, lstr=''):
    if str(str1) == '':
        return str(str2)
    else:
        return f"{str1}{lstr}{str2}"

def find_string(string,pattern):
    return re.compile(pattern).findall(str(string))

def find_substring(string, pattern):
    """
    Find the first substring in the string that matches the pattern and return it.

    Args:
    string (str): The string to search in.
    pattern (str): The regular expression pattern to match.

    Returns:
    str or None: The first matched substring or None if no match is found.
    """
    match = re.search(pattern, string)
    if match:
        return match.group()
    else:
        return None

def get_url(string):
    pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    url = re.findall(pattern,string)
    return url

def cut_string(string, length):
    str_len = len(string)
    list=[]
    for i in range(0, str_len, length):
        list.append(string[i:i+length])
    return list

def beautiful_number(ens):
    ens=str(ens)
    ens_type='normal'
    is_digital=re.compile('^[0-9]{1,20}$').match(ens)
    if is_digital!=None:
        if len(ens)<=3:
            ens_type='999 Club'
        elif len(ens)<=4:
            ens_type='10K Club'
            if find_string(ens,'([0-9])\\1{3,}')!=[]:
                ens_type='AAAA'
            elif find_string(ens,'([0-9])\\1{2,}')!=[]:
                ens_type='AAAB'
            elif len(find_string(ens,'([0-9])\\1{1,}'))>=2:
                ens_type='AABB'
        elif len(ens)<=5:
            ens_type='100K Club'
            if find_string(ens,'([0-9])\\1{4,}')!=[]:
                ens_type='AAAAA'
            elif find_string(ens,'([0-9])\\1{3,}')!=[]:
                ens_type='AAAAB'
            elif find_string(ens,'([0-9])\\1{2,}')!=[]:
                ens_type='AAABC'
    else:
        len_ens=len(ens)
        if len_ens==3:
            ens_type='3L'
            if find_string(ens,'([0-9a-zA-Z])\\1{2,}')!=[]:
                ens_type='EEE'
        elif len_ens==4:
            ens_type='4L'
            if find_string(ens,'([0-9a-zA-Z])\\1{3,}')!=[]:
                ens_type='EEEE'
            elif find_string(ens,'([0-9a-zA-Z])\\1{2,}')!=[]:
                ens_type='EEEF'
            elif len(find_string(ens,'([0-9a-zA-Z])\\1{1,}'))>=2:
                ens_type='EEFF'
    return str(ens_type).lower()

def get_this_ip():
    try:
        response = requests.get('https://httpbin.org/ip',timeout=5)
        response.raise_for_status()
        my_ip = response.json()['origin']
    except Exception as e1:
        try:
            my_ip = requests.get('http://jsonip.com',timeout=5).json()['ip']
            mprint(f'Error in get_this_ip: {e1}')
        except Exception as e2:
            my_ip = requests.get('https://api.ipify.org/?format=json',timeout=5).json()['ip']
            mprint(f'Error in get_this_ip: {e1}, {e2}')
    return my_ip

class WebSocketClient:
    """
    高性能 WebSocket 客户端工具类
    基于 websockets 库，提供异步连接、监听、发送消息和错误处理功能
    支持自动重连和持续连接，优化了消息处理吞吐量和线程安全性
    """
    
    def __init__(self, url, on_message=None, on_error=None, on_close=None, on_open=None, 
                 auto_reconnect=True, reconnect_interval=5, max_reconnect_attempts=10,
                 message_queue_size=10000, batch_size=100):
        """
        初始化 WebSocket 客户端
        
        Args:
            url (str): WebSocket 服务器地址
            on_message (callable): 消息接收回调函数
            on_error (callable): 错误处理回调函数
            on_close (callable): 连接关闭回调函数
            on_open (callable): 连接建立回调函数
            auto_reconnect (bool): 是否自动重连
            reconnect_interval (int): 重连间隔（秒）
            max_reconnect_attempts (int): 最大重连次数，-1表示无限重连
            message_queue_size (int): 消息队列大小
            batch_size (int): 批量处理消息数量
        """
        import threading
        import queue
        import weakref
        
        self.url = url
        self.websocket = None
        self._is_connected = False
        self.is_running = False
        self.loop = None
        self.task = None
        self.thread = None
        
        # 线程安全锁
        self._lock = threading.RLock()
        self._state_lock = threading.RLock()
        
        # 重连相关参数
        self.auto_reconnect = auto_reconnect
        self.reconnect_interval = reconnect_interval
        self.max_reconnect_attempts = max_reconnect_attempts
        self.reconnect_attempts = 0
        self.should_reconnect = True
        
        # 消息处理优化
        self.message_queue_size = message_queue_size
        self.batch_size = batch_size
        self.message_queue = queue.Queue(maxsize=message_queue_size)
        self.message_processor_thread = None
        self.message_processor_running = False
        
        # 使用弱引用避免循环引用导致的内存泄漏
        self.on_message_callback = weakref.ref(on_message) if on_message else None
        self.on_error_callback = weakref.ref(on_error) if on_error else None
        self.on_close_callback = weakref.ref(on_close) if on_close else None
        self.on_open_callback = weakref.ref(on_open) if on_open else None
        
        # 资源清理标志
        self._cleanup_done = False
    
    def __del__(self):
        """析构函数，确保资源清理"""
        try:
            if not getattr(self, '_cleanup_done', True):
                self._cleanup_resources()
        except:
            pass
    
    @property
    def is_connected(self):
        """线程安全的连接状态获取"""
        with self._state_lock:
            return self._is_connected
    
    @is_connected.setter
    def is_connected(self, value):
        """线程安全的连接状态设置"""
        with self._state_lock:
            self._is_connected = value
    
    def _safe_callback(self, callback_ref, *args, **kwargs):
        """安全调用回调函数，处理弱引用"""
        if callback_ref is None:
            return
        
        callback = callback_ref() if hasattr(callback_ref, '__call__') and callback_ref() else callback_ref
        if callback and callable(callback):
            try:
                callback(*args, **kwargs)
            except Exception as e:
                mprint(f"回调函数执行错误: {e}")
    
    def _default_on_message(self, message):
        """默认消息处理函数"""
        mprint(f"收到消息: {message}")
    
    def _default_on_error(self, error):
        """默认错误处理函数"""
        mprint(f"WebSocket 错误: {error}")
    
    def _default_on_close(self, close_status_code, close_msg):
        """默认连接关闭处理函数"""
        self.is_connected = False
        mprint(f"WebSocket 连接关闭: {close_status_code} - {close_msg}")
    
    def _default_on_open(self):
        """默认连接建立处理函数"""
        self.is_connected = True
        mprint("WebSocket 连接已建立")
    
    def _message_processor(self):
        """消息处理器线程，批量处理消息以提高吞吐量"""
        import queue
        
        batch = []
        while self.message_processor_running:
            try:
                # 尝试获取消息，超时1秒
                try:
                    message = self.message_queue.get(timeout=1)
                    batch.append(message)
                except queue.Empty:
                    # 处理现有批次
                    if batch:
                        self._process_message_batch(batch)
                        batch = []
                    continue
                
                # 如果批次达到指定大小，立即处理
                if len(batch) >= self.batch_size:
                    self._process_message_batch(batch)
                    batch = []
                    
            except Exception as e:
                mprint(f"消息处理器错误: {e}")
        
        # 处理剩余消息
        if batch:
            self._process_message_batch(batch)
    
    def _process_message_batch(self, batch):
        """批量处理消息"""
        for message in batch:
            try:
                if self.on_message_callback:
                    self._safe_callback(self.on_message_callback, message)
                else:
                    self._default_on_message(message)
            except Exception as e:
                mprint(f"批量消息处理错误: {e}")
            finally:
                # 标记任务完成
                try:
                    self.message_queue.task_done()
                except:
                    pass
    
    async def _connect_and_listen(self):
        """异步连接和监听消息，优化了消息处理吞吐量"""
        while self.should_reconnect and not self._cleanup_done:
            websocket_ref = None
            try:
                # 建立连接
                self.websocket = await websockets.connect(self.url)
                websocket_ref = self.websocket
                self.is_connected = True
                self.reconnect_attempts = 0  # 重置重连计数
                
                # 启动消息处理器线程
                if not self.message_processor_running:
                    self.message_processor_running = True
                    import threading
                    self.message_processor_thread = threading.Thread(
                        target=self._message_processor,
                        daemon=True
                    )
                    self.message_processor_thread.start()
                
                # 调用连接建立回调
                if self.on_open_callback:
                    self._safe_callback(self.on_open_callback)
                else:
                    self._default_on_open()
                
                # 高效消息接收循环
                async for message in self.websocket:
                    if self._cleanup_done:
                        break
                    
                    try:
                        # 将消息放入队列进行批量处理
                        self.message_queue.put_nowait(message)
                    except:
                        # 队列满时直接处理消息
                        try:
                            if self.on_message_callback:
                                self._safe_callback(self.on_message_callback, message)
                            else:
                                self._default_on_message(message)
                        except Exception as e:
                            mprint(f"直接消息处理错误: {e}")
                        
            except websockets.exceptions.ConnectionClosed as e:
                self.is_connected = False
                if self.on_close_callback:
                    self._safe_callback(self.on_close_callback, e.code, str(e))
                else:
                    self._default_on_close(e.code, str(e))
                mprint(f"连接关闭，代码: {e.code}, 原因: {e}")
                
            except Exception as e:
                self.is_connected = False
                if self.on_error_callback:
                    self._safe_callback(self.on_error_callback, e)
                else:
                    self._default_on_error(e)
                mprint(f"连接错误: {e}")
                
            finally:
                # 安全关闭连接
                if websocket_ref:
                    try:
                        await websocket_ref.close()
                    except Exception as e:
                        mprint(f"关闭连接错误: {e}")
                    finally:
                        websocket_ref = None
                
                self.is_connected = False
                self.websocket = None
            
            # 检查是否需要重连
            if not self.should_reconnect or self._cleanup_done:
                break
                
            if not self.auto_reconnect:
                break
                
            if self.max_reconnect_attempts != -1 and self.reconnect_attempts >= self.max_reconnect_attempts:
                mprint(f"达到最大重连次数 {self.max_reconnect_attempts}，停止重连")
                break
            
            self.reconnect_attempts += 1
            mprint(f"尝试重连 ({self.reconnect_attempts}/{self.max_reconnect_attempts if self.max_reconnect_attempts != -1 else '∞'})，等待 {self.reconnect_interval} 秒...")
            
            try:
                await asyncio.sleep(self.reconnect_interval)
            except asyncio.CancelledError:
                break
        
        # 停止消息处理器
        self.message_processor_running = False
    
    def connect(self, timeout=10):
        """
        连接到 WebSocket 服务器（线程安全）
        
        Args:
            timeout (int): 连接超时时间（秒）
        
        Returns:
            bool: 连接是否成功
        """
        with self._lock:
            if self.is_connected:
                mprint("WebSocket 已连接")
                return True
            
            try:
                self.should_reconnect = True
                self.is_running = True
                self._cleanup_done = False
                
                # 创建新的事件循环
                self.loop = asyncio.new_event_loop()
                
                # 启动异步任务
                self.task = self.loop.create_task(self._connect_and_listen())
                
                # 在新线程中运行事件循环
                import threading
                self.thread = threading.Thread(target=self._run_loop, daemon=True)
                self.thread.start()
                
                # 等待连接建立或超时
                start_time = time.time()
                while not self.is_connected and (time.time() - start_time) < timeout:
                    time.sleep(0.05)  # 减少检查间隔，提高响应速度
                
                return self.is_connected
                
            except Exception as e:
                mprint(f"连接失败: {e}")
                self._cleanup_resources()
                return False
    
    def _run_loop(self):
        """在新线程中运行事件循环"""
        try:
            self.loop.run_until_complete(self.task)
        except Exception as e:
            mprint(f"事件循环错误: {e}")
    
    async def _send_async(self, message):
        """异步发送消息"""
        if self.websocket and self.is_connected:
            await self.websocket.send(message)
            return True
        return False
    
    def send(self, message):
        """
        发送消息（线程安全）
        
        Args:
            message (str): 要发送的消息
        
        Returns:
            bool: 发送是否成功
        """
        with self._lock:
            if not self.is_connected or not self.websocket:
                return False
            
            try:
                if self.loop and not self.loop.is_closed():
                    future = asyncio.run_coroutine_threadsafe(
                        self._send_async(message), self.loop
                    )
                    future.result(timeout=3)  # 减少超时时间
                    return True
            except Exception as e:
                mprint(f"发送消息失败: {e}")
                return False
            return False
    
    def send_json(self, data):
        """
        发送 JSON 格式消息
        
        Args:
            data (dict): 要发送的数据
        
        Returns:
            bool: 发送是否成功
        """
        try:
            json_message = json.dumps(data, ensure_ascii=False)
            return self.send(json_message)
        except Exception as e:
            mprint(f"JSON 序列化失败: {e}")
            return False
    
    def close(self):
        """关闭 WebSocket 连接（线程安全，完整资源清理）"""
        with self._lock:
            self._cleanup_resources()
    
    def _cleanup_resources(self):
        """完整的资源清理，避免内存泄漏"""
        if self._cleanup_done:
            return
        
        self._cleanup_done = True
        self.should_reconnect = False
        self.is_running = False
        
        # 停止消息处理器
        self.message_processor_running = False
        
        # 清空消息队列
        try:
            while not self.message_queue.empty():
                try:
                    self.message_queue.get_nowait()
                    self.message_queue.task_done()
                except:
                    break
        except:
            pass
        
        # 关闭 WebSocket 连接
        if self.websocket and self.is_connected:
            try:
                if self.loop and not self.loop.is_closed():
                    future = asyncio.run_coroutine_threadsafe(
                        self.websocket.close(), self.loop
                    )
                    future.result(timeout=3)
            except Exception as e:
                mprint(f"关闭连接错误: {e}")
            finally:
                self.is_connected = False
                self.websocket = None
        
        # 取消异步任务
        if self.task and not self.task.done():
            try:
                if self.loop and not self.loop.is_closed():
                    future = asyncio.run_coroutine_threadsafe(
                        self._cancel_task(), self.loop
                    )
                    future.result(timeout=3)
            except Exception as e:
                mprint(f"取消任务错误: {e}")
        
        # 停止事件循环
        if self.loop and not self.loop.is_closed():
            try:
                self.loop.call_soon_threadsafe(self.loop.stop)
                # 等待线程结束
                if self.thread and self.thread.is_alive():
                    self.thread.join(timeout=2)
            except Exception as e:
                mprint(f"停止事件循环错误: {e}")
        
        # 等待消息处理器线程结束
        if self.message_processor_thread and self.message_processor_thread.is_alive():
            try:
                self.message_processor_thread.join(timeout=2)
            except Exception as e:
                mprint(f"等待消息处理器线程结束错误: {e}")
        
        # 清理引用
        self.loop = None
        self.task = None
        self.thread = None
        self.message_processor_thread = None
        
        # 清理回调引用
        self.on_message_callback = None
        self.on_error_callback = None
        self.on_close_callback = None
        self.on_open_callback = None
        
        mprint("WebSocket 连接已关闭，资源已清理")
    
    async def _cancel_task(self):
        """取消异步任务"""
        if self.task and not self.task.done():
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
    
    def get_connection_status(self):
        """检查连接状态（避免与属性名冲突）"""
        return self.is_connected
    
    def ping(self):
        """发送 ping 消息"""
        return self.send("ping")
    
    def get_status(self):
        """获取连接状态信息"""
        with self._state_lock:
            return {
                "url": self.url,
                "connected": self.is_connected,
                "running": self.is_running,
                "auto_reconnect": self.auto_reconnect,
                "reconnect_attempts": self.reconnect_attempts,
                "max_reconnect_attempts": self.max_reconnect_attempts,
                "message_queue_size": self.message_queue.qsize() if hasattr(self, 'message_queue') else 0,
                "message_processor_running": getattr(self, 'message_processor_running', False),
                "cleanup_done": getattr(self, '_cleanup_done', False)
            }
    
    def stop_reconnect(self):
        """停止自动重连"""
        self.should_reconnect = False
        mprint("已停止自动重连")
    
    def start_reconnect(self):
        """开始自动重连"""
        self.should_reconnect = True
        mprint("已开始自动重连")

def create_websocket_client(url, **kwargs):
    """
    创建 WebSocket 客户端的便捷函数
    
    Args:
        url (str): WebSocket 服务器地址
        **kwargs: 其他参数传递给 WebSocketClient
    
    Returns:
        WebSocketClient: WebSocket 客户端实例
    """
    return WebSocketClient(url, **kwargs)