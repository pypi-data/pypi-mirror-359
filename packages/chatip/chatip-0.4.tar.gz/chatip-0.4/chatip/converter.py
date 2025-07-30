# 服务器程序封装
def chats():
    # -*- coding: utf-8 -*-
    import socket
    import threading
    import time
    import hashlib
    import os
    import traceback
    import tkinter as tk
    from tkinter import scrolledtext, messagebox, ttk

    # 确保数据目录存在
    DATA_DIR = os.path.expanduser("~/.chat_server")
    os.makedirs(DATA_DIR, exist_ok=True)

    # 日志文件和用户数据文件使用绝对路径
    LOG_FILE = os.path.join(DATA_DIR, "server.log")
    USER_FILE = os.path.join(DATA_DIR, "users.txt")

    # 在线用户字典 {用户名: 客户端socket}
    online_users = {}
    # 锁，用于线程安全
    lock = threading.Lock()

    class ServerApp:
        def __init__(self, root):
            self.root = root
            self.root.title("聊天服务器")
            self.root.geometry("800x600")
            self.root.resizable(True, True)
            
            # 设置字体确保中文正常显示
            self.font = ('SimHei', 10)
            
            # 服务器状态
            self.server_running = False
            self.server_thread = None
            self.server_socket = None
            
            # 默认配置
            self.default_ip = "192.168.31.68"
            self.default_port = "59465"
            
            # 创建界面
            self.create_widgets()
            
            # 初始化日志
            self.log("===== 服务器应用启动 =====")
            
        def create_widgets(self):
            # 顶部框架 - 配置和控制
            top_frame = tk.Frame(self.root)
            top_frame.pack(fill=tk.X, padx=10, pady=10)
            
            # IP和端口设置
            tk.Label(top_frame, text="服务器IP:", font=self.font).grid(row=0, column=0, padx=5, pady=5)
            self.ip_var = tk.StringVar(value=self.default_ip)
            tk.Entry(top_frame, textvariable=self.ip_var, width=15, font=self.font).grid(row=0, column=1, padx=5, pady=5)
            
            tk.Label(top_frame, text="监听端口:", font=self.font).grid(row=0, column=2, padx=5, pady=5)
            self.port_var = tk.StringVar(value=self.default_port)
            tk.Entry(top_frame, textvariable=self.port_var, width=10, font=self.font).grid(row=0, column=3, padx=5, pady=5)
            
            # 启动/停止按钮
            self.start_button = tk.Button(top_frame, text="启动服务器", command=self.toggle_server, font=self.font)
            self.start_button.grid(row=0, column=4, padx=10, pady=5)
            
            # 状态标签
            self.status_var = tk.StringVar(value="状态: 未启动")
            tk.Label(top_frame, textvariable=self.status_var, font=self.font, fg="red").grid(row=0, column=5, padx=10, pady=5)
            
            # 在线用户标签
            self.online_count_var = tk.StringVar(value="在线用户: 0")
            tk.Label(top_frame, textvariable=self.online_count_var, font=self.font).grid(row=0, column=6, padx=10, pady=5)
            
            # 中间框架 - 日志显示
            middle_frame = tk.Frame(self.root)
            middle_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            tk.Label(middle_frame, text="服务器日志:", font=self.font).pack(anchor=tk.W)
            self.log_text = scrolledtext.ScrolledText(middle_frame, wrap=tk.WORD, font=self.font)
            self.log_text.pack(fill=tk.BOTH, expand=True)
            self.log_text.config(state=tk.DISABLED)
            
            # 底部框架 - 在线用户列表
            bottom_frame = tk.Frame(self.root)
            bottom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            tk.Label(bottom_frame, text="在线用户:", font=self.font).pack(anchor=tk.W)
            self.user_list = tk.Listbox(bottom_frame, font=self.font)
            self.user_list.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
            
            # 添加滚动条
            scrollbar = tk.Scrollbar(self.user_list, orient=tk.VERTICAL, command=self.user_list.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.user_list.config(yscrollcommand=scrollbar.set)
            
        def log(self, message):
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            log_message = f"{timestamp} - {message}\n"
            
            # 写入日志文件
            try:
                with open(LOG_FILE, 'a', encoding='utf-8') as f:
                    f.write(log_message)
            except Exception as e:
                print(f"写日志失败: {e}")
            
            # 显示在界面上
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, log_message)
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
        
        def update_user_list(self):
            self.user_list.delete(0, tk.END)
            with lock:
                for user in online_users.keys():
                    self.user_list.insert(tk.END, user)
            self.online_count_var.set(f"在线用户: {len(online_users)}")
        
        def toggle_server(self):
            if not self.server_running:
                # 启动服务器
                try:
                    ip = self.ip_var.get()
                    port = int(self.port_var.get())
                    if not (1024 <= port <= 65535):
                        messagebox.showerror("端口错误", "请输入1024-65535之间的端口号")
                        return
                    
                    self.server_thread = threading.Thread(target=self.run_server, args=(ip, port))
                    self.server_thread.daemon = True
                    self.server_thread.start()
                    
                    self.server_running = True
                    self.start_button.config(text="停止服务器")
                    self.status_var.set("状态: 运行中")
                    self.status_var.set("状态: 运行中")  # 确保显示更新
                    self.status_var.set("状态: 运行中")
                    self.status_var.set("状态: 运行中")
                    self.root.update()
                except ValueError:
                    messagebox.showerror("端口错误", "请输入有效的端口号")
            else:
                # 停止服务器
                self.server_running = False
                if self.server_socket:
                    try:
                        # 关闭服务器套接字，触发accept()异常
                        self.server_socket.close()
                    except:
                        pass
                self.start_button.config(text="启动服务器")
                self.status_var.set("状态: 已停止")
                self.update_user_list()
        
        def run_server(self, ip, port):
            try:
                # 检查并创建必要文件
                if not os.path.exists(USER_FILE):
                    with open(USER_FILE, 'w', encoding='utf-8') as f:
                        self.log(f"创建用户文件: {USER_FILE}")
                
                # 创建服务器套接字
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                
                try:
                    self.server_socket.bind((ip, port))
                except OSError as e:
                    self.log(f"绑定端口失败: {e}")
                    self.root.after(0, lambda: messagebox.showerror("启动失败", f"无法在 {ip}:{port} 上启动服务器"))
                    self.root.after(0, self.toggle_server)  # 切换按钮状态
                    return
                    
                self.server_socket.listen(5)
                self.log(f"服务器已启动，监听 {ip}:{port}，等待连接...")
                
                while self.server_running:
                    try:
                        client_socket, client_address = self.server_socket.accept()
                        client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                        client_thread.daemon = True
                        client_thread.start()
                    except OSError:
                        # 服务器关闭时会触发此异常
                        if self.server_running:
                            self.log("服务器套接字意外关闭")
                        break
                    except Exception as e:
                        self.log(f"接受连接时出错: {e}")
                        self.log(traceback.format_exc())
            
            except Exception as e:
                self.log(f"服务器启动失败: {e}")
                self.log(traceback.format_exc())
                self.root.after(0, lambda: messagebox.showerror("启动失败", str(e)))
                self.root.after(0, self.toggle_server)  # 切换按钮状态
            finally:
                # 清理资源
                if self.server_socket:
                    try:
                        self.server_socket.close()
                    except:
                        pass
                self.server_socket = None
                self.server_running = False
                self.log("服务器已停止")
                self.root.after(0, lambda: self.status_var.set("状态: 已停止"))
                self.root.after(0, lambda: self.start_button.config(text="启动服务器"))
                self.root.after(0, self.update_user_list)
        
        # 初始化用户数据文件
        def init_user_file(self):
            try:
                if not os.path.exists(USER_FILE):
                    with open(USER_FILE, 'w', encoding='utf-8') as f:
                        self.log(f"创建用户文件: {USER_FILE}")
            except Exception as e:
                self.log(f"初始化用户文件失败: {e}")
                raise
        
        # 加载用户数据
        def load_users(self):
            users = {}
            try:
                if os.path.exists(USER_FILE):
                    with open(USER_FILE, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if not line:
                                continue
                            username, password_hash = line.split(':')
                            users[username] = password_hash
                    self.log(f"成功加载 {len(users)} 个用户")
            except Exception as e:
                self.log(f"加载用户数据失败: {e}")
                self.log(traceback.format_exc())  # 记录详细堆栈信息
            return users
        
        # 保存用户数据
        def save_user(self, username, password_hash):
            with lock:
                try:
                    # 先加载现有用户
                    users = self.load_users()
                    # 添加新用户
                    users[username] = password_hash
                    # 保存所有用户
                    with open(USER_FILE, 'w', encoding='utf-8') as f:
                        for username, pwd_hash in users.items():
                            f.write(f"{username}:{pwd_hash}\n")
                    self.log(f"用户 {username} 数据已保存")
                except Exception as e:
                    self.log(f"保存用户数据失败: {e}")
                    self.log(traceback.format_exc())
        
        # 处理客户端请求
        def handle_client(self, client_socket, client_address):
            self.log(f"新连接来自: {client_address}")
            
            try:
                while True:
                    data = client_socket.recv(1024)
                    if not data:
                        self.log(f"客户端 {client_address} 关闭了连接")
                        break
                        
                    message = data.decode('utf-8').strip()
                    self.log(f"收到来自 {client_address} 的消息: {message[:50]}")  # 只记录前50个字符，避免太长
                    
                    # 解析消息类型
                    if message.startswith("LOGIN:"):
                        try:
                            _, username, password_hash = message.split(':', 2)
                            users = self.load_users()
                            
                            if username in users and users[username] == password_hash:
                                # 登录成功
                                with lock:
                                    online_users[username] = client_socket
                                client_socket.send(f"LOGIN_SUCCESS:{username}".encode('utf-8'))
                                self.broadcast(f"{username} 已上线", username)
                                self.log(f"{username} 登录成功")
                                self.root.after(0, self.update_user_list)
                            else:
                                # 登录失败
                                client_socket.send("LOGIN_FAILED".encode('utf-8'))
                                self.log(f"{username} 登录失败")
                        except Exception as e:
                            self.log(f"处理登录请求失败: {e}")
                            self.log(traceback.format_exc())
                            
                    elif message.startswith("REGISTER:"):
                        try:
                            _, username, password_hash = message.split(':', 2)
                            users = self.load_users()
                            
                            if username in users:
                                # 注册失败
                                client_socket.send("REGISTER_FAILED".encode('utf-8'))
                                self.log(f"{username} 注册失败：用户名已存在")
                            else:
                                # 注册成功
                                self.save_user(username, password_hash)
                                client_socket.send("REGISTER_SUCCESS".encode('utf-8'))
                                self.log(f"{username} 注册成功")
                        except Exception as e:
                            self.log(f"处理注册请求失败: {e}")
                            self.log(traceback.format_exc())
                            
                    elif message.startswith("EXIT:"):
                        username = self.find_username_by_socket(client_socket)
                        if username:
                            with lock:
                                if username in online_users:
                                    del online_users[username]
                                    self.broadcast(f"{username} 已下线", username)
                                    self.log(f"{username} 已退出")
                                    self.root.after(0, self.update_user_list)
                        break
                        
                    else:
                        # 普通消息转发
                        try:
                            parts = message.split(':', 1)
                            if len(parts) == 2:
                                recipient, content = parts
                                sender = self.find_username_by_socket(client_socket)
                                
                                if sender:
                                    if recipient:
                                        # 私聊
                                        if recipient in online_users:
                                            self.send_to_user(recipient, f"{sender} 对你说: {content}")
                                            self.log(f"{sender} 私聊消息发送给 {recipient}")
                                        else:
                                            self.send_to_user(sender, f"用户 {recipient} 不在线")
                                            self.log(f"{sender} 尝试联系离线用户 {recipient}")
                                    else:
                                        # 群发
                                        self.broadcast(f"{sender} 说: {content}", sender)
                                        self.log(f"{sender} 发送群聊消息")
                        except Exception as e:
                            self.log(f"处理消息转发失败: {e}")
                            self.log(traceback.format_exc())
            
            except Exception as e:
                self.log(f"处理客户端 {client_address} 时出错: {e}")
                self.log(traceback.format_exc())
            finally:
                # 清理工作
                username = self.find_username_by_socket(client_socket)
                if username:
                    with lock:
                        if username in online_users:
                            del online_users[username]
                            self.broadcast(f"{username} 已下线", username)
                            self.log(f"{username} 连接已关闭")
                            self.root.after(0, self.update_user_list)
                client_socket.close()
                self.log(f"客户端 {client_address} 连接已关闭")
        
        # 根据socket查找用户名
        def find_username_by_socket(self, sock):
            with lock:
                for username, client_sock in online_users.items():
                    if client_sock == sock:
                        return username
            return None
        
        # 广播消息给所有在线用户
        def broadcast(self, message, exclude_user=None):
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            full_message = f"{timestamp}\n{message}\n"
            
            with lock:
                for username, client_sock in list(online_users.items()):
                    if username != exclude_user:
                        try:
                            client_sock.send(full_message.encode('utf-8'))
                        except Exception as e:
                            self.log(f"发送消息给 {username} 失败: {e}")
                            # 移除无法发送的客户端
                            del online_users[username]
                            self.root.after(0, self.update_user_list)
        
        # 发送消息给特定用户
        def send_to_user(self, username, message):
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            full_message = f"{timestamp}\n{message}\n"
            
            with lock:
                if username in online_users:
                    try:
                        online_users[username].send(full_message.encode('utf-8'))
                    except Exception as e:
                        self.log(f"发送消息给 {username} 失败: {e}")
                        # 移除无法发送的客户端
                        del online_users[username]
                        self.root.after(0, self.update_user_list)

    if __name__ == "__main__":
        root = tk.Tk()
        app = ServerApp(root)
        root.mainloop()


# 客户端程序封装
def chatc():
    # -*- coding: utf-8 -*-
    """
    Created on Tue May 12 23:49:20 2020
    Modified: 添加密码登录和注册功能

    @author: LENOVO
    """
    import tkinter
    import socket
    import threading
    import time
    import hashlib

    win = tkinter.Tk()
    win.title("客户端")
    win.geometry("400x400+300+200")
    ck = None
    current_user = ""
    eip = None  # 全局变量声明
    eport = None  # 全局变量声明
    euser = None  # 全局变量声明
    epwd = None  # 全局变量声明
    esend = None  # 全局变量声明
    efriend = None  # 全局变量声明
    text = None  # 全局变量声明

    # 加密函数
    def encrypt_password(password):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    # 接收消息线程
    def getInfo():
        nonlocal current_user
        while True:
            try:
                data = ck.recv(1024)
                if not data:
                    break
                    
                msg = data.decode("utf-8")
                # 处理登录响应
                if msg.startswith("LOGIN_SUCCESS"):
                    current_user = msg.split(":")[1]
                    text.insert(tkinter.INSERT, f"登录成功，欢迎 {current_user}！\n")
                    show_main_window()
                elif msg.startswith("LOGIN_FAILED"):
                    text.insert(tkinter.INSERT, "登录失败，用户名或密码错误！\n")
                # 处理注册响应
                elif msg.startswith("REGISTER_SUCCESS"):
                    text.insert(tkinter.INSERT, "注册成功，请登录！\n")
                elif msg.startswith("REGISTER_FAILED"):
                    text.insert(tkinter.INSERT, "注册失败，用户名已存在！\n")
                # 处理普通消息
                else:
                    text.insert(tkinter.INSERT, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + '\n')
                    text.insert(tkinter.INSERT, msg)
            except Exception as e:
                text.insert(tkinter.INSERT, f"连接已断开: {str(e)}\n")
                show_login_window()
                break

    # 连接服务器
    def connectServer():
        nonlocal ck
        try:
            ipStr = eip.get()  # 现在可以访问全局变量
            portStr = eport.get()
            
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((ipStr, int(portStr)))
            ck = client
            
            t = threading.Thread(target=getInfo)
            t.daemon = True
            t.start()
            
            text.insert(tkinter.INSERT, "已连接到服务器，请登录或注册\n")
        except Exception as e:
            text.insert(tkinter.INSERT, f"连接失败: {str(e)}\n")

    # 登录函数
    def login():
        nonlocal ck
        if not ck:
            text.insert(tkinter.INSERT, "请先连接服务器！\n")
            return
            
        userStr = euser.get()
        pwdStr = epwd.get()
        encrypted_pwd = encrypt_password(pwdStr)
        
        if not userStr or not pwdStr:
            text.insert(tkinter.INSERT, "用户名和密码不能为空！\n")
            return
        
        login_msg = f"LOGIN:{userStr}:{encrypted_pwd}"
        ck.send(login_msg.encode("utf-8"))

    # 注册函数
    def register():
        nonlocal ck
        if not ck:
            text.insert(tkinter.INSERT, "请先连接服务器！\n")
            return
            
        userStr = euser.get()
        pwdStr = epwd.get()
        encrypted_pwd = encrypt_password(pwdStr)
        
        if not userStr or not pwdStr:
            text.insert(tkinter.INSERT, "用户名和密码不能为空！\n")
            return
        
        register_msg = f"REGISTER:{userStr}:{encrypted_pwd}"
        ck.send(register_msg.encode("utf-8"))

    # 发送消息
    def sendMail():
        nonlocal ck
        if not ck:
            text.insert(tkinter.INSERT, "未连接到服务器！\n")
            return
            
        friend = efriend.get()
        sendStr = esend.get()
        
        if not sendStr:
            return
            
        if friend:
            text.insert(tkinter.INSERT, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + '\n' + f'我对{friend}说：{sendStr}\n')
        else:
            text.insert(tkinter.INSERT, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + '\n' + f'我(群发）说：{sendStr}\n')
        
        sendStr = f"{friend}:{sendStr}\n"
        ck.send(sendStr.encode("utf-8"))

    # 退出函数
    def Exit():
        nonlocal ck
        if ck:
            try:
                sendStr = "EXIT:"
                ck.send(sendStr.encode("utf-8"))
                ck.close()
            except:
                pass
            
        win.destroy()

    # 显示登录窗口
    def show_login_window():
        nonlocal eip, eport, euser, epwd, text
        
        # 清空窗口
        for widget in win.winfo_children():
            widget.destroy()
        
        # 服务器连接信息
        tkinter.Label(win, text="服务器IP").grid(row=0, column=0)
        eip_var = tkinter.StringVar(value="192.168.31.68")
        eip = tkinter.Entry(win, textvariable=eip_var)
        eip.grid(row=0, column=1)
        
        tkinter.Label(win, text="端口").grid(row=1, column=0)
        eport_var = tkinter.StringVar(value="59465")
        eport = tkinter.Entry(win, textvariable=eport_var)
        eport.grid(row=1, column=1)
        
        tkinter.Button(win, text="连接服务器", command=connectServer).grid(row=1, column=2)
        
        # 登录信息
        tkinter.Label(win, text="用户名").grid(row=2, column=0)
        euser_var = tkinter.StringVar()
        euser = tkinter.Entry(win, textvariable=euser_var)
        euser.grid(row=2, column=1)
        
        tkinter.Label(win, text="密码").grid(row=3, column=0)
        epwd_var = tkinter.StringVar()
        epwd = tkinter.Entry(win, textvariable=epwd_var, show="*")
        epwd.grid(row=3, column=1)
        
        tkinter.Button(win, text="登录", command=login).grid(row=2, column=2)
        tkinter.Button(win, text="注册", command=register).grid(row=3, column=2)
        
        # 消息显示框
        text = tkinter.Text(win, height=15, width=40)
        tkinter.Label(win, text="消息").grid(row=4, column=0)
        text.grid(row=4, column=1, columnspan=2)
        
        # 退出按钮
        tkinter.Button(win, text="退出", command=Exit).grid(row=5, column=1)

    # 显示主窗口
    def show_main_window():
        nonlocal esend, efriend, text
        
        # 清空窗口
        for widget in win.winfo_children():
            widget.destroy()
        
        # 当前用户信息
        tkinter.Label(win, text=f"当前用户: {current_user}").grid(row=0, column=0, columnspan=2)
        
        # 消息显示框
        text = tkinter.Text(win, height=10, width=40)
        tkinter.Label(win, text="消息").grid(row=1, column=0)
        text.grid(row=1, column=1)
        
        # 发送消息框
        esend_var = tkinter.StringVar()
        esend = tkinter.Entry(win, textvariable=esend_var)
        tkinter.Label(win, text="发送消息").grid(row=2, column=0)
        esend.grid(row=2, column=1)
        
        # 接收人
        efriend_var = tkinter.StringVar()
        efriend = tkinter.Entry(win, textvariable=efriend_var)
        tkinter.Label(win, text="接收人(留空群发)").grid(row=3, column=0)
        efriend.grid(row=3, column=1)
        
        # 按钮
        tkinter.Button(win, text="发送", command=sendMail).grid(row=3, column=2)
        tkinter.Button(win, text="退出", command=Exit).grid(row=4, column=1)

    # 初始化显示登录窗口
    show_login_window()

    win.mainloop()