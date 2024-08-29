import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from tkinter import Toplevel
from work import TaskManager
import sys
import os
import re
import threading
import json
from datetime import datetime, time as dt_time
import time


class ConfigManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.config = {}
        self.load()

    def load(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r', encoding="utf-8") as file:
                self.config = json.load(file)

    def save(self):
        with open(self.file_path, 'w', encoding="utf-8") as file:
            json.dump(self.config, file, indent=4, ensure_ascii=False)

    def _get_nested_value(self, data, keys):
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current

    def _set_nested_value(self, data, keys, value):
        current = data
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value

    def get(self, key_path, default=None):
        keys = key_path.split('.')
        return self._get_nested_value(self.config, keys) or default

    def set(self, key_path, value):
        keys = key_path.split('.')
        self._set_nested_value(self.config, keys, value)
        self.save()

    def remove(self, key_path):
        keys = key_path.split('.')
        current = self.config
        parent = None
        for key in keys[:-1]:
            if key in current:
                parent = current
                current = current[key]
            else:
                return
        if keys[-1] in current:
            del current[keys[-1]]
            self.save()

    def update(self, new_data):
        self.config.update(new_data)
        self.save()


def create_config(file_path):
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        default_object = {
            "user": {
                "autologon": True,
                "key": ""
            },
            "group": {},
            "thread":{
                "threadCount":20
            }
        }
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(default_object, file, ensure_ascii=False, indent=4)


def runfn(msg):
    new_msg = msg.replace("run_info:", "")
    cleaned_msg = new_msg.replace(" ", "").replace("\n", "")
    truncated_msg = (cleaned_msg[:30] + '...') if len(cleaned_msg) > 30 else cleaned_msg
    status_label.config(text=f"状态: {truncated_msg}", fg="black")
    update_log(new_msg)
    root.update()


def errorfn(msg):
    global status_label, btn_start, btn_pause, error_log_button
    cleaned_msg = msg.replace(" ", "").replace("\n", "")
    truncated_msg = (cleaned_msg[:40] + '...') if len(cleaned_msg) > 40 else msg
    status_label.config(text=f"状态: 执行错误-{truncated_msg}", fg="red")
    btn_start.config(state=tk.NORMAL)
    btn_pause.config(state=tk.DISABLED)
    error_log_button.config(state=tk.NORMAL)
    update_error_log(msg)
    root.update()
    # update_idletasks

def ensure_file_exists(file_path):
    dir_name = os.path.dirname(file_path)
        
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)
        
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write('')

def empty_groups():
    task_manager.empty_groups()
    pass
def clear_group():
    group = config_manager.get("group", default={})
    if group:
        for key in list(group.keys()):
            links = group[key]
            current_timestamp = time.time()
            time_difference = int(current_timestamp) - int(key)
            two_days_in_seconds = 2 * 24 * 60 * 60
            if time_difference > two_days_in_seconds:
                for item in links:
                    task_manager.clear_group(item['id'])
                    time.sleep(0.2)
                config_manager.remove(f'group.{key}')


app_id = 'cli_a60aa656b939100e'
app_secret = 'sarxErZ9gpw2Au6xTVJ2tdEAfZ8sx1s4'
error_file_path = 'logs/error.log'
log_file_path = 'logs/run.log'
config_file_path = 'config/config.json'

ensure_file_exists(config_file_path)
create_config(config_file_path)
config_manager = ConfigManager(config_file_path)
threadCount = config_manager.get("thread.threadCount", default=20)

task_manager = TaskManager(log_file_path, error_file_path, app_id, app_secret,threadCount, runfn, errorfn)
# task_manager.ensure_file_exists(config_file_path)



# class LoadingDialog(Toplevel):
#     def __init__(self, parent, title, message):
#         Toplevel.__init__(self, parent)
#         self.title(title)
#         self.transient(parent)
#         self.grab_set()
#         self.protocol("WM_DELETE_WINDOW", self.on_close)

#         self.label = tk.Label(self, text=message)
#         self.label.pack(padx=20, pady=20)

#         self.update_idletasks()
#         self.center_window()
#         self.lift()  # 提升窗口层级

#     def center_window(self):
#         self.update_idletasks()  # 更新窗口大小
#         screen_width = self.winfo_screenwidth()
#         screen_height = self.winfo_screenheight()
#         window_width = self.winfo_width()
#         window_height = self.winfo_height()

#         x = (screen_width // 2) - (window_width // 2)
#         y = (screen_height // 2) - (window_height // 2)
#         self.geometry(f"+{x}+{y}")

#     def on_close(self):
#         self.destroy()

class LoadingDialog(Toplevel):
    def __init__(self, parent, title, message):
        super().__init__(parent)
        self.title(title)
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.label = tk.Label(self, text=message)
        self.label.pack(padx=20, pady=20)

        self.update_idletasks()
        self.center_window()
        self.lift()  

    
        self.close_event = threading.Event()

        self.task_thread = threading.Thread(target=self.long_running_task)
        self.task_thread.start()

    def center_window(self):
        self.update_idletasks()  
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = self.winfo_width()
        window_height = self.winfo_height()

        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.geometry(f"+{x}+{y}")

    def on_close(self):
        self.close_event.set()
    def long_running_task(self):
        while not self.close_event.is_set():
            time.sleep(0.1)
        self.destroy()

def validate_key():
    key = entry_key.get().strip()
    if key:
        loading_dialog = LoadingDialog(root, "验证中", "验证中，请稍候...")
        root.update()
        if task_manager.test_key(key):
            loading_dialog.on_close()
            messagebox.showinfo("验证", "密钥验证通过")
            if task_manager.user_id and task_manager.feishuAPI.owner_id and task_manager.user_id  == task_manager.feishuAPI.owner_id:
                btn_dismiss_groups.pack(side=tk.LEFT, padx=10)
            else:
                btn_dismiss_groups.pack_forget()
            entry_key.config(state=tk.DISABLED)
            btn_validate.config(state=tk.DISABLED)
            config_manager.set("user.key", key)
            enable_step(2)
        else:
            loading_dialog.on_close()
            messagebox.showwarning("验证", "请输入密钥")
    else:
        messagebox.showwarning("验证", "请输入密钥")

def reset():
    entry_key.config(state=tk.NORMAL)
    entry_key.delete(0, tk.END)
    btn_validate.config(state=tk.NORMAL)
    wechat_feishu_login_var.set(0)
    wechat_feishu_login_cb.config(state=tk.DISABLED)
    btn_pause.config(state=tk.DISABLED)
    btn_reset.config(state=tk.NORMAL)
    status_label.config(text="状态: 等待", fg="black")
    manual_order_entry.delete(1.0, tk.END)
    manual_order_place_btn.config(state=tk.DISABLED)
    step_completed[2] = step_completed[3] = step_completed[4] = False
    
    btn_dismiss_groups.config(state=tk.NORMAL)  # 重置后启用解散群聊按钮
    btn_dismiss_groups.pack_forget()

def wechat_feishu_login():
    if wechat_feishu_login_var.get():
        messagebox.showinfo("微信和飞书登录", "请确认微信和飞书已打开并处于登录状态。")
        task_manager.open_wechat()
        wechat_feishu_login_cb.config(state=tk.DISABLED)
        enable_step(3)


def on_radio_select():
    if not step_completed[3]:
        messagebox.showwarning("步骤未完成", "请先完成微信和飞书登录步骤。")
        return

    group = config_manager.get("group", default={})
    links = []
    loading_dialog = LoadingDialog(root, "加入中", "群聊加入中，请稍候...")
    root.update()
    current_timestamp = time.time()
    current_timestamp = int(current_timestamp)
    max_key = current_timestamp

    if not group:
        links = task_manager.create_fs_group_link()
        group[current_timestamp] = links
        config_manager.set("group", group)
    else:
        max_key = max(group)
        links = group[max_key]

        given_time = datetime.fromtimestamp(int(max_key))
  
        today = datetime.today().date()
        
        today_6am = datetime.combine(today, dt_time(6, 0, 0))
        
        if today_6am > given_time:
            links = task_manager.create_fs_group_link()
            group[current_timestamp] = links
            config_manager.set("group", group)
            max_key = current_timestamp
    step_completed[4] = True
    loading_dialog.on_close()
    chat_1 = links[0]['id']
    chat_2 = links[1]['id']
    chat_3 = links[2]['id']
    chat_4 = links[3]['id']
    task_manager.setChat_id(chat_1,chat_2,chat_3,chat_4)
    messagebox.showinfo("加入成功", "加入群聊成功。")
    btn_start.config(state=tk.NORMAL)
    btn_dismiss_groups.config(state=tk.DISABLED)  # 加入群聊后禁用解散群聊按钮
    thread = threading.Thread(target=clear_group)
    thread.start()
    thread.join()

def on_start():
    if not step_completed[4]:
        messagebox.showwarning("步骤未完成", "请先完成加入群聊步骤。")
        return

    status_label.config(text="状态: 开始运行", fg="black")
    task_manager.go()
    log_button.config(state=tk.NORMAL)
    error_log_button.config(state=tk.NORMAL)
    btn_start.config(state=tk.DISABLED)
    btn_pause.config(state=tk.NORMAL)
    btn_reset.config(state=tk.DISABLED)
    manual_order_query_btn.config(state=tk.NORMAL)


def on_pause():
    status_label.config(text="状态: 暂停", fg="black")
    task_manager.pause()
    messagebox.showinfo("暂停", "系统已暂停")
    btn_start.config(state=tk.NORMAL)
    btn_pause.config(state=tk.DISABLED)
    manual_order_query_btn.config(state=tk.NORMAL)


def show_log():
    log_window = Toplevel(root)
    log_window.title("日志")
    log_window.geometry("600x400")
    log_text = tk.Text(log_window, wrap=tk.NONE)
    log_text.pack(fill=tk.BOTH, expand=True)
    scrollbar = ttk.Scrollbar(log_window, command=log_text.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    log_text.config(yscrollcommand=scrollbar.set)
    log_text.insert(tk.END, log_content.get())
    log_window.lift()  # 提升窗口层级


def show_error_log():
    error_log_window = Toplevel(root)
    error_log_window.title("错误日志")
    error_log_window.geometry("600x400")
    error_log_text = tk.Text(error_log_window, wrap=tk.NONE)
    error_log_text.pack(fill=tk.BOTH, expand=True)
    scrollbar = ttk.Scrollbar(error_log_window, command=error_log_text.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    error_log_text.config(yscrollcommand=scrollbar.set)
    error_log_text.insert(tk.END, error_log_content.get())
    error_log_window.lift()  # 提升窗口层级


def update_log(msg):
    log_content.set(log_content.get() + msg + "\n")


def update_error_log(msg):
    error_log_content.set(error_log_content.get() + msg + "\n")


def enable_step(step):
    step_completed[step] = True
    if step == 2:
        wechat_feishu_login_cb.config(state=tk.NORMAL)
    elif step == 3:
        on_radio_select()


def center_window(root, width, height):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2)
    root.geometry(f'{width}x{height}+{int(x)}+{int(y)}')


def manual_order_query():
    if task_manager.status == 'init':
        messagebox.showwarning("查询错误", "任务开始之后才能查询订单")
        return

    query_text = manual_order_entry.get(1.0, tk.END).strip()
    if query_text:
        loading_dialog = LoadingDialog(root, "查询中", "订单查询中，请稍候...")
        root.update()

        def query_order():
            task_manager.order_push(query_text)
            result = task_manager.result_queue.get()
            answer = ''
            res = '【无可预约时间】'
            if result:
                res = result['res']
                answer = result['answer']
                res_list = re.findall('###.+?###', answer, re.DOTALL)
                # 循环提取到的任务
                _list = []
                for _res in res_list:
                    work_name_re = re.findall('###客户姓名：(.+?)；', _res)[0]
                    work_phone_re = re.findall('客户电话：(.+?)；', _res)[0]
                    
                    work_time_re = re.findall('预约时间：(.+?)；', _res)[0]
                    work_addr_re = re.findall('预约地址：(.+?)；', _res, re.DOTALL)[0]
                    # work_addr_re = ['\n'] + work_addr_re
                    
                    
                    if work_phone_re == '空':
                        work_phone_re = ''
                    _str = f'{work_name_re} {work_phone_re}\n{work_addr_re}\n\n{work_time_re}'
                    
                    _list.append(_str)
                answer = '\n'.join(_list)
            def update_ui():
                loading_dialog.on_close()
                manual_order_result.config(state=tk.NORMAL)
                manual_order_result.delete(1.0, tk.END)
                manual_order_result.insert(tk.END, answer)
                manual_order_result.config(state=tk.DISABLED)
                query_result_text.config(state=tk.NORMAL)
                query_result_text.delete(1.0, tk.END)
                if "无可预约时间" in res:
                    query_result_text.insert(tk.END, res, "red")
                elif "当前时间可预约" in res:
                    query_result_text.insert(tk.END, res, "green")  
                else:
                    query_result_text.insert(tk.END, res, "black")  
                query_result_text.config(state=tk.DISABLED)
            root.after(0, update_ui)

        thread = threading.Thread(target=query_order)
        thread.start()
    else:
        messagebox.showwarning("查询错误", "请输入订单信息")


def manual_order_place():
    messagebox.showinfo("下单", "订单已成功下单")


def copy_query_result():
    root.clipboard_clear()
    root.clipboard_append(manual_order_result.get(1.0, tk.END).strip())
    messagebox.showinfo("复制", "查询结果已复制到剪贴板")


def on_closing():
    if messagebox.askokcancel("退出", "退出之后所有的工作将关闭，确定退出吗?"):
        root.destroy()
        task_manager.destroy()
        sys.exit(1)


def confirm_dismiss_groups():
    if messagebox.askyesno("确认解散群聊", "该操作会解散创建的所有群聊，是否继续？"):
        loading_dialog = LoadingDialog(root, "解散中", "群聊解散中，请稍候...")
        root.update()

        def dismiss_groups():
            empty_groups()
            loading_dialog.on_close()
            messagebox.showinfo("解散完成", "所有群聊已解散完成")

        thread = threading.Thread(target=dismiss_groups)
        thread.start()


def add_to_whitelist():
    item = simpledialog.askstring("添加白名单", "请输入要添加到白名单的内容：")
    if item:
        whitelist = config_manager.get("whitelist", default=[])
        whitelist.append(item)
        config_manager.set("whitelist", whitelist)
        messagebox.showinfo("添加成功", f"{item} 已添加到白名单")


def add_to_blacklist():
    item = simpledialog.askstring("添加黑名单", "请输入要添加到黑名单的内容：")
    if item:
        blacklist = config_manager.get("blacklist", default=[])
        blacklist.append(item)
        config_manager.set("blacklist", blacklist)
        messagebox.showinfo("添加成功", f"{item} 已添加到黑名单")

def main():
    global entry_key, btn_validate, wechat_feishu_login_cb, wechat_feishu_login_var, root, btn_start, btn_pause, btn_reset, step_completed, status_label, log_button, error_log_button, manual_order_entry, manual_order_query_btn, manual_order_place_btn, log_content, error_log_content, auto_validate_var, auto_validate_cb, manual_order_result,query_result_text, btn_dismiss_groups, whitelist_text, blacklist_text

    step_completed = {2: False, 3: False, 4: False}

    root = tk.Tk()
    root.title("管理系统")
    root.resizable(True, True)

    window_width = 650
    window_height = 500
    center_window(root, window_width, window_height)
    
    
    def show_right_click_menu(event):
        if event:
            text_widget = event.widget
            # 检查是否有文本被选中
            if text_widget.tag_ranges(tk.SEL):
                right_click_menu.entryconfig("粘贴", state=tk.DISABLED)
                right_click_menu.entryconfig("复制", state=tk.NORMAL)
                right_click_menu.entryconfig("剪切", state=tk.NORMAL)
            else:
                right_click_menu.entryconfig("粘贴", state=tk.NORMAL)
                right_click_menu.entryconfig("复制", state=tk.DISABLED)
                right_click_menu.entryconfig("剪切", state=tk.DISABLED)
            right_click_menu.post(event.x_root, event.y_root)

    def copy_selected_text(event):
        if event:
            text_widget = event.widget
            if text_widget.tag_ranges(tk.SEL):
                selected_text = text_widget.selection_get()
                root.clipboard_clear()
                root.clipboard_append(selected_text)
                root.update()  


    def paste_text(event):
        if event:
            text_widget = event.widget
            if text_widget.cget('state') == tk.NORMAL:
                try:
                    clipboard_data = root.clipboard_get()
                    insert_pos = text_widget.index(tk.INSERT)
                    
    
                    text_widget.delete(insert_pos, insert_pos + " +1c")
      
                    text_widget.insert(tk.INSERT, clipboard_data)
                except tk.TclError:
                    pass 

    def cut_selected_text(event):
        if event:
            text_widget = event.widget
            if text_widget.tag_ranges(tk.SEL):
                selected_text = text_widget.selection_get()
                text_widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                root.clipboard_clear()
                root.clipboard_append(selected_text)
                root.update()  
 

    right_click_menu = tk.Menu(root, tearoff=0)
    right_click_menu.add_command(label="复制", command=lambda: copy_selected_text(event=None))
    right_click_menu.add_command(label="粘贴", command=lambda: paste_text(event=None))
    right_click_menu.add_command(label="剪切", command=lambda: cut_selected_text(event=None))
    
    def show_right_click_menu(event):
        text_widget = event.widget
        if text_widget.tag_ranges(tk.SEL):
            right_click_menu.entryconfig("粘贴", state=tk.DISABLED)
            right_click_menu.entryconfig("复制", state=tk.NORMAL)
            right_click_menu.entryconfig("剪切", state=tk.NORMAL)
        else:
            right_click_menu.entryconfig("粘贴", state=tk.NORMAL)
            right_click_menu.entryconfig("复制", state=tk.DISABLED)
            right_click_menu.entryconfig("剪切", state=tk.DISABLED)
        right_click_menu.post(event.x_root, event.y_root)
        
        
    with open('logs/run.log', 'w', encoding='utf-8') as file:
        file.write('')
    with open('logs/error.log', 'w', encoding='utf-8') as file:
        file.write('')

    frame_top = tk.Frame(root, pady=10)
    frame_top.pack(fill=tk.X)
    tk.Label(frame_top, text="1. 输入密钥:", font=('Arial', 12)).pack(side=tk.LEFT, padx=10)
    entry_key = tk.Entry(frame_top, font=('Arial', 12))
    entry_key.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
    saved_key = config_manager.get('user.key')
    if saved_key:
        entry_key.insert(0, saved_key)

    auto_validate_var = tk.BooleanVar(value=config_manager.get("user.autologon"))
    auto_validate_cb = tk.Checkbutton(frame_top, text="自动验证", variable=auto_validate_var,
                                      command=lambda: [messagebox.showinfo("自动验证", "自动验证已开启" if auto_validate_var.get() else "自动验证已关闭"), config_manager.set("user.autologon", auto_validate_var.get())],
                                      font=('Arial', 12))
    auto_validate_cb.pack(side=tk.LEFT, padx=10)
    btn_validate = tk.Button(frame_top, text="验证", command=validate_key, font=('Arial', 12))
    btn_validate.pack(side=tk.LEFT, padx=10)
    btn_reset = tk.Button(frame_top, text="重置", command=reset, font=('Arial', 12))
    btn_reset.pack(side=tk.LEFT, padx=10)
    btn_dismiss_groups = tk.Button(frame_top, text="解散群聊", command=confirm_dismiss_groups, font=('Arial', 12))
    btn_dismiss_groups.pack_forget() 
    # btn_dismiss_groups.pack(side=tk.LEFT, padx=10)

    frame_logins = tk.Frame(root, pady=10)
    frame_logins.pack(fill=tk.X)
    tk.Label(frame_logins, text="2. 微信和飞书登录:", font=('Arial', 12)).pack(side=tk.LEFT, padx=10)
    wechat_feishu_login_var = tk.IntVar()
    wechat_feishu_login_cb = tk.Checkbutton(frame_logins, text="已登录", variable=wechat_feishu_login_var, command=wechat_feishu_login, font=('Arial', 12), state=tk.DISABLED)
    wechat_feishu_login_cb.pack(side=tk.LEFT, padx=10)

    manual_order_frame = tk.LabelFrame(root, text="3. 手动订单查询", font=('Arial', 12))
    manual_order_frame.pack(fill=tk.X, padx=20, pady=10)

    manual_order_input_frame = tk.Frame(manual_order_frame)
    manual_order_input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)



    manual_order_entry = tk.Text(manual_order_input_frame, height=5, font=('Arial', 12))
    manual_order_entry.grid(row=0, column=0, sticky='nsew', padx=(0, 5))
    
    
    # manual_order_entry.bind("<Button-3>", show_right_click_menu)
    # manual_order_entry.bind("<Control-c>", copy_selected_text)
    # manual_order_entry.bind("<Control-v>", paste_text)
    # manual_order_entry.bind("<Control-x>", cut_selected_text)

    query_result_frame = tk.LabelFrame(manual_order_input_frame, text="查询结果")
    query_result_frame.grid(row=0, column=1, sticky='nsew', padx=(5, 5))



    query_result_text = tk.Text(query_result_frame, height=5, font=('Arial', 12), state=tk.DISABLED)
    query_result_text.pack(fill=tk.BOTH, expand=True)
    
    
    query_result_text.tag_configure("green", foreground="green")
    query_result_text.tag_configure("red", foreground="red")
    query_result_text.tag_configure("black", foreground="black")
    
    
    manual_order_result = tk.Text(manual_order_input_frame, height=5, font=('Arial', 12), state=tk.DISABLED)
    manual_order_result.grid(row=0, column=2, sticky='nsew', padx=(5, 0))
    
    
    # manual_order_result.bind("<Button-3>", show_right_click_menu)
    # manual_order_result.bind("<Control-c>", copy_selected_text)
    # manual_order_result.bind("<Control-v>", paste_text)
    # manual_order_result.bind("<Control-x>", cut_selected_text)
    
    

    manual_order_input_frame.columnconfigure(0, weight=1)
    manual_order_input_frame.columnconfigure(1, weight=1)
    manual_order_input_frame.columnconfigure(2, weight=1)
    manual_order_input_frame.rowconfigure(0, weight=1)

    manual_order_query_btn = tk.Button(manual_order_frame, text="查询", command=manual_order_query, font=('Arial', 12))
    manual_order_query_btn.pack(side=tk.LEFT, padx=10, pady=10)

    manual_order_place_btn = tk.Button(manual_order_frame, text="下单", command=manual_order_place, font=('Arial', 12))
    
    manual_order_place_btn.pack(side=tk.LEFT, padx=10, pady=10)
    manual_order_place_btn.config(state=tk.DISABLED)

    copy_result_btn = tk.Button(manual_order_frame, text="复制结果", command=copy_query_result, font=('Arial', 12))
    copy_result_btn.pack(side=tk.LEFT, padx=10, pady=10)

    status_frame = tk.Frame(root)
    status_frame.pack(fill=tk.X, pady=10)

    status_label = tk.Label(status_frame, text="状态: 等待", font=('Arial', 12), fg="black")
    status_label.pack(pady=10)

    log_button = tk.Button(status_frame, text="查看日志", command=show_log, font=('Arial', 12))
    log_button.pack(side=tk.LEFT, padx=10)

    error_log_button = tk.Button(status_frame, text="查看错误日志", command=show_error_log, font=('Arial', 12))
    error_log_button.pack(side=tk.LEFT, padx=10)

    btn_start = tk.Button(status_frame, text="开始", command=on_start, font=('Arial', 12))
    btn_start.pack(side=tk.LEFT, padx=10)

    btn_pause = tk.Button(status_frame, text="暂停", command=on_pause, font=('Arial', 12))
    
    btn_pause.pack(side=tk.LEFT, padx=10)
    
    btn_pause.config(state=tk.DISABLED)
    
    
    # add_whitelist_btn = tk.Button(status_frame, text="添加白名单", command=add_to_whitelist, font=('Arial', 12))
    # add_whitelist_btn.pack(side=tk.LEFT, padx=10)

    # add_blacklist_btn = tk.Button(status_frame, text="添加黑名单", command=add_to_blacklist, font=('Arial', 12))
    # add_blacklist_btn.pack(side=tk.LEFT, padx=10)

    
    root.protocol("WM_DELETE_WINDOW", on_closing)

    log_content = tk.StringVar()
    error_log_content = tk.StringVar()

    sizegrip = ttk.Sizegrip(root)
    sizegrip.pack(side=tk.BOTTOM, anchor=tk.SE)

    # whitelist = config_manager.get("whitelist", default=[])
    # blacklist = config_manager.get("blacklist", default=[])
    # whitelist_text.insert(tk.END, "\n".join(whitelist))
    # blacklist_text.insert(tk.END, "\n".join(blacklist))
    if config_manager.get("user.key") and config_manager.get("user.autologon"):
        root.after(1000, validate_key)
    root.mainloop()


if __name__ == "__main__":
    main()