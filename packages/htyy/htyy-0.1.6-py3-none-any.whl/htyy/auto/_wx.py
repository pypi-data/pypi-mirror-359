import time, pyautogui
from typing import List, Optional
import uiautomation as auto

class _WeiXin:
    def __init__(self):
        self.weChatWindow = auto.WindowControl(
            Name="微信",
            searchDepth=1
        )
        self.weChatWindow.SetActive()
        # 更通用的搜索框定位方式
        self.searchBox = self.weChatWindow.EditControl(Depth=2, foundIndex=1)
        self.last_chat_name = ""  # 记录最后打开的聊天窗口
    
    def _getEditorControl(self):
        """输入框定位方法"""
        # 尝试多种方式定位输入框
        editor_strategies = [
            lambda: self.weChatWindow.EditControl(Name="输入"),
            lambda: self.weChatWindow.EditControl(Name=""),
            lambda: self.weChatWindow.EditControl(foundIndex=1),
            lambda: self.weChatWindow.EditControl(Depth=3, foundIndex=1),
            lambda: self.weChatWindow.EditControl(ControlType=auto.ControlType.EditControl, Depth=3)
        ]
        
        for strategy in editor_strategies:
            try:
                editor = strategy()
                if editor.Exists(0, 0.5):
                    return editor
            except:
                continue
        
        # 如果找不到输入框，尝试点击聊天区域激活
        chatArea = self.weChatWindow.PaneControl(Depth=4, foundIndex=1)
        if chatArea.Exists(0, 0.5):
            chatArea.Click(simulateMove=False)
            time.sleep(0.5)
            return self._getEditorControl()
        
        return None
        
    def _sendTextContent(self, content):
        """文本发送方法"""
        editor = self._getEditorControl()
        if not editor.Exists():
            # 如果找不到输入框，尝试点击聊天区域激活
            chatArea = self.weChatWindow.PaneControl(Name="消息")
            if chatArea.Exists():
                chatArea.Click(simulateMove=False)
                time.sleep(0.5)
                editor = self._getEditorControl()
        
        if editor.Exists():
            editor.SendKeys(content)
            
            # 尝试定位发送按钮
            sendBtn = None
            for name in ["发送(S)", "发送", "Send", "Sending"]:
                btn = self.weChatWindow.ButtonControl(Name=name)
                if btn.Exists(0, 0.5):
                    sendBtn = btn
                    break
            
            if sendBtn:
                sendBtn.Click(simulateMove=False)
            else:
                # 备用发送方式：按Enter键
                editor.SendKeys('{Enter}')
        else:
            raise LookupError("无法定位微信输入框")
    
    def _getContactElement(self, name):
        """联系人查找方法"""
        # 清空搜索框
        self.searchBox.SendKeys('{Ctrl}a', waitTime=0)
        self.searchBox.SendKeys('{Delete}', waitTime=0)
        time.sleep(0.3)
        
        # 输入联系人名称
        self.searchBox.SendKeys(name)
        time.sleep(0.8)  # 增加等待时间
        
        # 尝试多种方式定位联系人
        contact = self.weChatWindow.ListItemControl(Name=name)
        if not contact.Exists(0, 0.5):
            contact = self.weChatWindow.ListItemControl(SubName=name)
            if not contact.Exists(0, 0.5):
                # 尝试在搜索结果中查找
                searchResult = self.weChatWindow.ListControl(Name="搜索结果")
                if searchResult.Exists():
                    contact = searchResult.ListItemControl(Name=name)
        
        if contact.Exists():
            return contact
        
        # 如果找不到，尝试滚动联系人列表
        contactList = self.weChatWindow.ListControl(Name="联系人列表")
        if contactList.Exists():
            contactList.ScrollIntoView()
            contact = contactList.ListItemControl(Name=name)
            if contact.Exists():
                return contact
        
        raise LookupError(f"联系人 '{name}' 未找到")
    
    def _clickElement(self, element):
        """点击方法"""
        try:
            # 先尝试直接点击
            element.Click(simulateMove=False)
        except:
            # 如果失败，尝试使用坐标点击
            rect = element.BoundingRectangle
            if rect.width > 0 and rect.height > 0:
                x = rect.left + rect.width // 2
                y = rect.top + rect.height // 2
                auto.Click(x, y)
        time.sleep(0.3)
        
    def _activate_wechat(self):
        """确保微信窗口激活"""
        if not self.weChatWindow.isActive:
            self.wechat_window.activate()
            time.sleep(0.5)
    
    def _press_key(self, key, times=1, interval=0.1):
        """按键操作"""
        self._activate_wechat()
        for _ in range(times):
            pyautogui.press(key)
            time.sleep(interval)
    
    def _hotkey(self, *keys):
        """组合键操作"""
        self._activate_wechat()
        pyautogui.hotkey(*keys)
        time.sleep(0.5)
    
    def _type_text(self, text):
        """输入文本"""
        self._activate_wechat()
        pyautogui.write(text, interval=0.05)
    
    def _click_at(self, x, y):
        """点击指定坐标"""
        self._activate_wechat()
        pyautogui.click(x, y)
    
    def _get_center(self):
        """获取窗口中心坐标"""
        rect = self.wechat_window.box
        return rect.left + rect.width // 2, rect.top + rect.height // 2
    
    def _get_search_box_position(self):
        """估算搜索框位置"""
        rect = self.wechat_window.box
        # 搜索框通常在左上角区域
        return rect.left + 100, rect.top + 40
    
    def _get_chat_input_position(self):
        """估算聊天输入框位置"""
        rect = self.wechat_window.box
        # 输入框通常在底部中间区域
        return rect.left + rect.width // 2, rect.top + rect.height - 80
    
    def _get_first_contact_position(self):
        """估算第一个联系人位置"""
        rect = self.wechat_window.box
        # 联系人通常在左侧列表顶部
        return rect.left + 100, rect.top + 150
    
    def _get_send_button_position(self):
        """估算发送按钮位置"""
        rect = self.wechat_window.box
        # 发送按钮通常在输入框右侧
        return rect.left + rect.width - 100, rect.top + rect.height - 80
    
    def OpenWeChat(self) -> None:
        """激活微信窗口"""
        if not self.weChatWindow.Exists():
            raise EnvironmentError("微信客户端未启动")
        self.weChatWindow.SetFocus()
        time.sleep(1)

    def OpenChatWindow(self, name: str) -> None:
        """打开指定联系人的聊天窗口"""
        if name == self.last_chat_name:
            return
            
        self._activate_wechat()
        
        # 使用快捷键打开搜索 (Ctrl+F)
        self._hotkey('ctrl', 'f')
        time.sleep(0.5)
        
        # 输入联系人名称
        self._type_text(name)
        time.sleep(1.0)  # 等待搜索结果
        
        # 按Enter键打开第一个匹配的联系人
        self._press_key('enter')
        time.sleep(1.0)
        
        self.last_chat_name = name

    def SendTextMessage(self, name: str, message: str) -> None:
        """发送文本消息"""
        self.OpenChatWindow(name)
        self._sendTextContent(message)
        
    def SearchContact(self, name):
        self.searchBox.SendKeys('{Ctrl}a', waitTime=0)
        self.searchBox.SendKeys('{Delete}', waitTime=0)
        self.searchBox.SendKeys(name)
        time.sleep(1)
        return self._getContactElement(name) is not None
        
    def SendFile(self, name, filePath):
        self.OpenChatWindow(name)
        fileBtn = self.weChatWindow.ButtonControl(Name="文件")
        self._clickElement(fileBtn)
        
        openDlg = auto.WindowControl(ClassName="#32770")
        fileInput = openDlg.EditControl(ClassName="Edit")
        fileInput.SendKeys(filePath)
        
        openBtn = openDlg.ButtonControl(Name="打开(O)")
        self._clickElement(openBtn)
        time.sleep(1)
        
    def SendImage(self, name, imagePath):
        self.OpenChatWindow(name)
        imgBtn = self.weChatWindow.ButtonControl(Name="图片")
        self._clickElement(imgBtn)
        
        openDlg = auto.WindowControl(ClassName="#32770")
        fileInput = openDlg.EditControl(ClassName="Edit")
        fileInput.SendKeys(imagePath)
        
        openBtn = openDlg.ButtonControl(Name="打开(O)")
        self._clickElement(openBtn)
        time.sleep(1)
        
    def CreateGroupChat(self, contacts):
        newChatBtn = self.weChatWindow.ButtonControl(Name="聊天")
        self._clickElement(newChatBtn)
        
        groupChatBtn = self.weChatWindow.MenuItemControl(Name="发起群聊")
        self._clickElement(groupChatBtn)
        time.sleep(1)
        
        for contact in contacts:
            checkBox = self.weChatWindow.CheckBoxControl(Name=contact)
            if checkBox.Exists():
                self._clickElement(checkBox)
                
        confirmBtn = self.weChatWindow.ButtonControl(Name="确定")
        self._clickElement(confirmBtn)
        time.sleep(1)
        
    def GetChatHistory(self, name, count=10):
        self.OpenChatWindow(name)
        history = []
        msgList = self.weChatWindow.ListControl(Name="消息")
        
        for i, msgItem in enumerate(msgList.GetChildren()):
            if i >= count:
                break
            try:
                msgText = msgItem.Name
                history.append(msgText)
            except:
                continue
        return history
        
    def ClearChatHistory(self, name):
        self.OpenChatWindow(name)
        menuBtn = self.weChatWindow.ButtonControl(Name="聊天信息")
        self._clickElement(menuBtn)
        
        clearBtn = self.weChatWindow.ButtonControl(Name="清空聊天记录")
        self._clickElement(clearBtn)
        
        confirmBtn = self.weChatWindow.ButtonControl(Name="清空")
        self._clickElement(confirmBtn)
        time.sleep(1)
        
    def SetRemarkName(self, name, remark):
        self.OpenContactProfile(name)
        remarkBtn = self.weChatWindow.ButtonControl(Name="备注")
        self._clickElement(remarkBtn)
        
        remarkInput = self.weChatWindow.EditControl(Name="设置备注")
        remarkInput.SendKeys('{Ctrl}a', waitTime=0)
        remarkInput.SendKeys(remark)
        
        saveBtn = self.weChatWindow.ButtonControl(Name="完成")
        self._clickElement(saveBtn)
        
    def OpenContactProfile(self, name):
        self.SearchContact(name)
        contact = self._getContactElement(name)
        contact.RightClick()
        
        profileItem = self.weChatWindow.MenuItemControl(Name="查看名片")
        self._clickElement(profileItem)
        time.sleep(1)
        
    def AddContact(self, wxid):
        addBtn = self.weChatWindow.ButtonControl(Name="添加")
        self._clickElement(addBtn)
        
        wxidInput = self.weChatWindow.EditControl(Name="微信号/手机号")
        wxidInput.SendKeys(wxid)
        
        searchBtn = self.weChatWindow.ButtonControl(Name="搜索")
        self._clickElement(searchBtn)
        time.sleep(1)
        
        addToContacts = self.weChatWindow.ButtonControl(Name="添加到通讯录")
        if addToContacts.Exists():
            self._clickElement(addToContacts)
            time.sleep(0.5)
            sendBtn = self.weChatWindow.ButtonControl(Name="发送")
            self._clickElement(sendBtn)
            return True
        return False
        
    def AcceptFriendRequest(self):
        newContactTip = self.weChatWindow.TextControl(Name="朋友请求")
        if newContactTip.Exists():
            self._clickElement(newContactTip)
            acceptBtn = self.weChatWindow.ButtonControl(Name="接受")
            self._clickElement(acceptBtn)
            return True
        return False
        
    def SendAppMessage(self, name, appName):
        self.OpenChatWindow(name)
        appBtn = self.weChatWindow.ButtonControl(Name="应用")
        self._clickElement(appBtn)
        
        appItem = self.weChatWindow.ListItemControl(Name=appName)
        self._clickElement(appItem)
        
    def PinChat(self, name, pin=True):
        self.OpenChatWindow(name)
        menuBtn = self.weChatWindow.ButtonControl(Name="聊天信息")
        self._clickElement(menuBtn)
        
        pinBtn = self.weChatWindow.ButtonControl(Name="置顶聊天")
        if pinBtn.GetTogglePattern().ToggleState != (1 if pin else 0):
            self._clickElement(pinBtn)
        self.weChatWindow.SendKeys('{Esc}')
        
    def MuteNotifications(self, name, mute=True):
        self.OpenChatWindow(name)
        menuBtn = self.weChatWindow.ButtonControl(Name="聊天信息")
        self._clickElement(menuBtn)
        
        muteBtn = self.weChatWindow.ButtonControl(Name="消息免打扰")
        if muteBtn.GetTogglePattern().ToggleState != (1 if mute else 0):
            self._clickElement(muteBtn)
        self.weChatWindow.SendKeys('{Esc}')
        
    def ChangeChatBackground(self, name, imagePath):
        self.OpenChatWindow(name)
        menuBtn = self.weChatWindow.ButtonControl(Name="聊天信息")
        self._clickElement(menuBtn)
        
        bgBtn = self.weChatWindow.ButtonControl(Name="设置当前聊天背景")
        self._clickElement(bgBtn)
        
        selectPhoto = self.weChatWindow.ButtonControl(Name="选择背景图")
        self._clickElement(selectPhoto)
        
        openDlg = auto.WindowControl(ClassName="#32770")
        fileInput = openDlg.EditControl(ClassName="Edit")
        fileInput.SendKeys(imagePath)
        
        openBtn = openDlg.ButtonControl(Name="打开(O)")
        self._clickElement(openBtn)
        time.sleep(1)
        
    def MarkAsUnread(self, name):
        chatItem = self.weChatWindow.ListItemControl(Name=name)
        chatItem.RightClick()
        
        unreadItem = self.weChatWindow.MenuItemControl(Name="标为未读")
        self._clickElement(unreadItem)
        
    def DeleteContact(self, name):
        self.OpenContactProfile(name)
        moreBtn = self.weChatWindow.ButtonControl(Name="更多")
        self._clickElement(moreBtn)
        
        deleteBtn = self.weChatWindow.ButtonControl(Name="删除")
        self._clickElement(deleteBtn)
        
        confirmBtn = self.weChatWindow.ButtonControl(Name="删除联系人")
        self._clickElement(confirmBtn)
        time.sleep(1)
        
    def GetContactList(self):
        contactPane = self.weChatWindow.PaneControl(Name="联系人")
        self._clickElement(contactPane)
        time.sleep(1)
        
        contacts = []
        contactList = self.weChatWindow.ListControl(Name="联系人列表")
        for item in contactList.GetChildren():
            if item.ControlType != auto.ControlType.ListItemControl:
                continue
            contacts.append(item.Name)
        return contacts
        
    def LogoutWeChat(self):
        menuBtn = self.weChatWindow.ButtonControl(Name="菜单")
        self._clickElement(menuBtn)
        
        logoutItem = self.weChatWindow.MenuItemControl(Name="退出登录")
        self._clickElement(logoutItem)
        
        confirmBtn = self.weChatWindow.ButtonControl(Name="退出登录")
        self._clickElement(confirmBtn)

    def SendVideo(self, name: str, videoPath: str) -> None:
        """
        发送视频文件
        :param name: 联系人/群聊名称
        :param videoPath: 视频文件绝对路径
        """
        self.OpenChatWindow(name)
        fileBtn = self.weChatWindow.ButtonControl(Name="文件")
        self._clickElement(fileBtn)
        
        openDlg = auto.WindowControl(ClassName="#32770")
        # 设置文件类型为视频
        fileTypeCombo = openDlg.ComboBoxControl(Name="文件类型:")
        fileTypeCombo.Select("视频文件(*.mp4, *.mov)")
        
        fileInput = openDlg.EditControl(ClassName="Edit")
        fileInput.SendKeys(videoPath)
        
        openBtn = openDlg.ButtonControl(Name="打开(O)")
        self._clickElement(openBtn)
        time.sleep(2)  # 视频需要更长时间处理

    def SendVoiceMessage(self, name: str, duration: int = 5) -> None:
        """
        发送语音消息
        :param name: 联系人/群聊名称
        :param duration: 录音时长(秒)，默认5秒
        """
        self.OpenChatWindow(name)
        voiceBtn = self.weChatWindow.ButtonControl(Name="语音输入")
        self._clickElement(voiceBtn)
        
        # 按住录音按钮
        recordBtn = self.weChatWindow.ButtonControl(Name="按住 说话")
        recordBtn.Press()
        time.sleep(duration)
        recordBtn.Release()

    def SendLocation(self, name: str, location: str) -> None:
        """
        发送位置信息
        :param name: 联系人/群聊名称
        :param location: 位置名称/地址
        """
        self.OpenChatWindow(name)
        locationBtn = self.weChatWindow.ButtonControl(Name="位置")
        self._clickElement(locationBtn)
        
        searchInput = self.weChatWindow.EditControl(Name="搜索地点")
        searchInput.SendKeys(location)
        time.sleep(1)  # 等待搜索结果
        
        # 选择第一个结果
        firstResult = self.weChatWindow.ListItemControl(foundIndex=1)
        self._clickElement(firstResult)
        
        sendBtn = self.weChatWindow.ButtonControl(Name="发送")
        self._clickElement(sendBtn)

    def SendContactCard(self, name: str, contactName: str) -> None:
        """
        发送联系人名片
        :param name: 接收方联系人/群聊名称
        :param contactName: 要分享的联系人名称
        """
        self.OpenChatWindow(name)
        contactBtn = self.weChatWindow.ButtonControl(Name="名片")
        self._clickElement(contactBtn)
        
        # 搜索并选择联系人
        searchInput = self.weChatWindow.EditControl(Name="搜索")
        searchInput.SendKeys(contactName)
        time.sleep(0.5)
        
        contactItem = self.weChatWindow.ListItemControl(Name=contactName)
        if not contactItem.Exists():
            raise LookupError(f"联系人 '{contactName}' 未找到")
        self._clickElement(contactItem)
        
        sendBtn = self.weChatWindow.ButtonControl(Name="分享")
        self._clickElement(sendBtn)

    def CreateReminder(self, name: str, timeStr: str, content: str) -> None:
        """
        创建聊天提醒
        :param name: 联系人/群聊名称
        :param timeStr: 提醒时间 (格式: "2025-07-01 15:30")
        :param content: 提醒内容
        """
        self.OpenChatWindow(name)
        # 打开消息菜单
        msgInput = self.weChatWindow.EditControl(Name="输入")
        msgInput.RightClick()
        
        # 选择提醒功能
        reminderItem = self.weChatWindow.MenuItemControl(Name="提醒")
        self._clickElement(reminderItem)
        
        # 设置提醒时间
        timeInput = self.weChatWindow.EditControl(Name="设置提醒时间")
        timeInput.SendKeys(timeStr)
        
        # 设置提醒内容
        contentInput = self.weChatWindow.EditControl(Name="提醒内容(可选)")
        contentInput.SendKeys(content)
        
        # 确认创建
        confirmBtn = self.weChatWindow.ButtonControl(Name="设置提醒")
        self._clickElement(confirmBtn)

    def MarkChatAsRead(self, name: str) -> None:
        """
        标记聊天为已读
        :param name: 联系人/群聊名称
        """
        chatItem = self.weChatWindow.ListItemControl(Name=name)
        if not chatItem.Exists():
            raise LookupError(f"聊天 '{name}' 未找到")
            
        unreadCount = chatItem.TextControl(foundIndex=1)
        if unreadCount.Exists():
            chatItem.Click(simulateMove=False)
            time.sleep(0.5)
            self.weChatWindow.SendKeys('{Esc}')  # 关闭聊天窗口

    def SaveChatMedia(self, name: str, savePath: str) -> int:
        """
        保存聊天媒体文件(图片/视频/文件)
        :param name: 联系人/群聊名称
        :param savePath: 保存目录路径
        :return: 保存的文件数量
        """
        self.OpenChatWindow(name)
        menuBtn = self.weChatWindow.ButtonControl(Name="聊天信息")
        self._clickElement(menuBtn)
        
        # 打开聊天文件
        fileBtn = self.weChatWindow.ButtonControl(Name="查找聊天内容")
        self._clickElement(fileBtn)
        
        mediaBtn = self.weChatWindow.ButtonControl(Name="文件")
        self._clickElement(mediaBtn)
        time.sleep(1)
        
        # 选择所有文件
        selectAll = self.weChatWindow.ButtonControl(Name="全选")
        if selectAll.Exists():
            self._clickElement(selectAll)
        
        # 保存按钮
        saveBtn = self.weChatWindow.ButtonControl(Name="保存")
        self._clickElement(saveBtn)
        
        # 设置保存路径
        saveDlg = auto.WindowControl(ClassName="#32770")
        pathInput = saveDlg.EditControl(ClassName="Edit")
        pathInput.SendKeys(savePath)
        
        saveConfirm = saveDlg.ButtonControl(Name="选择文件夹")
        self._clickElement(saveConfirm)
        
        # 获取保存数量
        countText = self.weChatWindow.TextControl(RegexName="已选择\d+个文件")
        count = int(countText.Name.replace("已选择", "").replace("个文件", "")) if countText.Exists() else 0
        
        # 关闭文件窗口
        closeBtn = self.weChatWindow.ButtonControl(Name="关闭")
        self._clickElement(closeBtn)
        
        return count

    def StartVideoCall(self, name: str) -> None:
        """
        发起视频通话
        :param name: 联系人名称
        """
        self.OpenChatWindow(name)
        callBtn = self.weChatWindow.ButtonControl(Name="视频通话")
        self._clickElement(callBtn)

    def StartVoiceCall(self, name: str) -> None:
        """
        发起语音通话
        :param name: 联系人名称
        """
        self.OpenChatWindow(name)
        callBtn = self.weChatWindow.ButtonControl(Name="语音通话")
        self._clickElement(callBtn)

    def EndCall(self) -> None:
        """结束当前通话"""
        callWindow = auto.WindowControl(ClassName="WeChatVideoWnd")
        if callWindow.Exists():
            endBtn = callWindow.ButtonControl(Name="挂断")
            self._clickElement(endBtn)

    def BlockContact(self, name: str) -> None:
        """
        加入黑名单
        :param name: 联系人名称
        """
        self.OpenContactProfile(name)
        moreBtn = self.weChatWindow.ButtonControl(Name="更多")
        self._clickElement(moreBtn)
        
        blockBtn = self.weChatWindow.ButtonControl(Name="加入黑名单")
        self._clickElement(blockBtn)
        
        confirmBtn = self.weChatWindow.ButtonControl(Name="确定")
        self._clickElement(confirmBtn)

    def UnblockContact(self, name: str) -> None:
        """
        移出黑名单
        :param name: 联系人名称
        """
        self.OpenContactProfile(name)
        moreBtn = self.weChatWindow.ButtonControl(Name="更多")
        self._clickElement(moreBtn)
        
        unblockBtn = self.weChatWindow.ButtonControl(Name="移出黑名单")
        self._clickElement(unblockBtn)
        
        confirmBtn = self.weChatWindow.ButtonControl(Name="确定")
        self._clickElement(confirmBtn)

    def ChangeWeChatStatus(self, status: str) -> None:
        """
        修改微信在线状态
        :param status: 状态名称 (如："忙碌"、"离开"等)
        """
        statusBtn = self.weChatWindow.ButtonControl(Name="状态")
        self._clickElement(statusBtn)
        
        statusItem = self.weChatWindow.ListItemControl(Name=status)
        if not statusItem.Exists():
            raise ValueError(f"无效状态: {status}")
        self._clickElement(statusItem)
        
        # 确认修改
        confirmBtn = self.weChatWindow.ButtonControl(Name="就这样")
        self._clickElement(confirmBtn)

    def OpenFavorites(self) -> None:
        """打开收藏夹"""
        favoritesBtn = self.weChatWindow.ButtonControl(Name="收藏")
        self._clickElement(favoritesBtn)

    def AddToFavorites(self, name: str, messageIndex: int = 0) -> None:
        """
        添加消息到收藏夹
        :param name: 联系人/群聊名称
        :param messageIndex: 消息索引(0=最新消息)
        """
        self.OpenChatWindow(name)
        # 定位指定消息
        msgList = self.weChatWindow.ListControl(Name="消息")
        targetMsg = msgList.GetChildren()[messageIndex]
        targetMsg.RightClick()
        
        # 选择收藏
        favoriteItem = self.weChatWindow.MenuItemControl(Name="收藏")
        self._clickElement(favoriteItem)

    def OpenMoments(self) -> None:
        """打开朋友圈功能"""
        navBtn = self.weChatWindow.ButtonControl(Name="朋友圈")
        self._clickElement(navBtn)
        time.sleep(2)  # 等待朋友圈加载

    def PostMoment(self, content: str, imagePath: Optional[str] = None) -> None:
        """
        发布朋友圈
        :param content: 朋友圈文字内容
        :param imagePath: 可选图片路径
        """
        self.OpenMoments()
        cameraBtn = self.weChatWindow.ButtonControl(Name="相机")
        self._clickElement(cameraBtn)
        
        # 选择照片或纯文本
        if imagePath:
            photoBtn = self.weChatWindow.MenuItemControl(Name="从手机相册选择")
            self._clickElement(photoBtn)
            
            openDlg = auto.WindowControl(ClassName="#32770")
            fileInput = openDlg.EditControl(ClassName="Edit")
            fileInput.SendKeys(imagePath)
            openBtn = openDlg.ButtonControl(Name="打开(O)")
            self._clickElement(openBtn)
            time.sleep(1)  # 等待图片加载
        else:
            textOnly = self.weChatWindow.MenuItemControl(Name="这一刻的想法...")
            self._clickElement(textOnly)
        
        # 输入文字内容
        editor = self.weChatWindow.EditControl(Name="分享新鲜事...")
        editor.SendKeys(content)
        
        # 发布
        postBtn = self.weChatWindow.ButtonControl(Name="发表")
        self._clickElement(postBtn)
        time.sleep(1)

    def LikeMoment(self, contactName: str, index: int = 0) -> None:
        """
        点赞朋友圈
        :param contactName: 联系人名称
        :param index: 朋友圈索引(0=最新)
        """
        self.OpenMoments()
        
        # 定位指定联系人的朋友圈
        moment = self.weChatWindow.ListItemControl(Name=contactName, foundIndex=index+1)
        if not moment.Exists():
            raise LookupError(f"未找到 {contactName} 的第 {index+1} 条朋友圈")
        
        # 点赞按钮在评论区域
        commentBtn = moment.ButtonControl(Name="评论")
        commentBtn.Click()
        
        likeBtn = self.weChatWindow.MenuItemControl(Name="赞")
        self._clickElement(likeBtn)

    def AddGroupMember(self, groupName: str, contactName: str) -> None:
        """
        添加成员到群聊
        :param groupName: 群名称
        :param contactName: 要添加的联系人名称
        """
        self.OpenChatWindow(groupName)
        menuBtn = self.weChatWindow.ButtonControl(Name="聊天信息")
        self._clickElement(menuBtn)
        
        addBtn = self.weChatWindow.ButtonControl(Name="+")
        self._clickElement(addBtn)
        
        # 搜索并添加联系人
        searchInput = self.weChatWindow.EditControl(Name="搜索")
        searchInput.SendKeys(contactName)
        time.sleep(0.5)
        
        contactItem = self.weChatWindow.ListItemControl(Name=contactName)
        if not contactItem.Exists():
            raise LookupError(f"联系人 '{contactName}' 未找到")
        
        checkbox = contactItem.CheckBoxControl()
        self._clickElement(checkbox)
        
        confirmBtn = self.weChatWindow.ButtonControl(Name="确定")
        self._clickElement(confirmBtn)

    def RemoveGroupMember(self, groupName: str, contactName: str) -> None:
        """
        从群聊中移除成员
        :param groupName: 群名称
        :param contactName: 要移除的联系人名称
        """
        self.OpenChatWindow(groupName)
        menuBtn = self.weChatWindow.ButtonControl(Name="聊天信息")
        self._clickElement(menuBtn)
        
        # 打开成员列表
        membersBtn = self.weChatWindow.ButtonControl(Name="查看更多")
        self._clickElement(membersBtn)
        
        # 定位成员
        memberItem = self.weChatWindow.ListItemControl(Name=contactName)
        if not memberItem.Exists():
            raise LookupError(f"成员 '{contactName}' 不在群聊中")
        
        memberItem.RightClick()
        removeItem = self.weChatWindow.MenuItemControl(Name="移除")
        self._clickElement(removeItem)
        
        confirmBtn = self.weChatWindow.ButtonControl(Name="确定")
        self._clickElement(confirmBtn)

    def SetGroupAnnouncement(self, groupName: str, announcement: str) -> None:
        """
        设置群公告
        :param groupName: 群名称
        :param announcement: 公告内容
        """
        self.OpenChatWindow(groupName)
        menuBtn = self.weChatWindow.ButtonControl(Name="聊天信息")
        self._clickElement(menuBtn)
        
        # 打开群公告
        announcementBtn = self.weChatWindow.ButtonControl(Name="群公告")
        self._clickElement(announcementBtn)
        
        # 编辑公告
        editor = self.weChatWindow.EditControl(Name="编辑公告")
        editor.SendKeys(announcement)
        
        # 完成编辑
        finishBtn = self.weChatWindow.ButtonControl(Name="完成")
        self._clickElement(finishBtn)
        
        # 确认发布
        confirmBtn = self.weChatWindow.ButtonControl(Name="发布")
        self._clickElement(confirmBtn)

    def TransferMoney(self, name: str, amount: float, note: str = "") -> None:
        """
        转账给联系人
        :param name: 联系人名称
        :param amount: 转账金额
        :param note: 转账备注
        """
        self.OpenChatWindow(name)
        # 打开更多菜单
        moreBtn = self.weChatWindow.ButtonControl(Name="更多")
        self._clickElement(moreBtn)
        
        # 选择转账
        transferItem = self.weChatWindow.MenuItemControl(Name="转账")
        self._clickElement(transferItem)
        
        # 输入金额
        amountInput = self.weChatWindow.EditControl(Name="金额")
        amountInput.SendKeys(str(amount))
        
        # 输入备注
        if note:
            noteInput = self.weChatWindow.EditControl(Name="添加备注")
            noteInput.SendKeys(note)
        
        # 确认转账
        confirmBtn = self.weChatWindow.ButtonControl(Name="转账")
        self._clickElement(confirmBtn)
        
        # 输入支付密码 (需要用户自行完成)
        time.sleep(2)  # 等待支付窗口

    def OpenMiniProgram(self, name: str) -> None:
        """
        打开小程序
        :param name: 小程序名称
        """
        # 打开小程序面板
        appsBtn = self.weChatWindow.ButtonControl(Name="小程序")
        self._clickElement(appsBtn)
        
        # 搜索小程序
        searchInput = self.weChatWindow.EditControl(Name="搜索小程序")
        searchInput.SendKeys(name)
        time.sleep(0.5)
        
        # 打开小程序
        appItem = self.weChatWindow.ListItemControl(Name=name)
        self._clickElement(appItem)

    def SearchChatHistory(self, name: str, keyword: str) -> List[str]:
        """
        搜索聊天记录
        :param name: 联系人/群聊名称
        :param keyword: 搜索关键词
        :return: 匹配的消息列表
        """
        self.OpenChatWindow(name)
        # 打开搜索面板
        searchBtn = self.weChatWindow.ButtonControl(Name="搜索")
        self._clickElement(searchBtn)
        
        # 输入关键词
        searchInput = self.weChatWindow.EditControl(Name="搜索")
        searchInput.SendKeys(keyword)
        time.sleep(1)
        
        # 获取结果
        results = []
        resultList = self.weChatWindow.ListControl(Name="搜索结果")
        for item in resultList.GetChildren():
            msgText = item.Name
            results.append(msgText)
        
        # 关闭搜索
        self.weChatWindow.SendKeys('{Esc}')
        return results

    def SetAlias(self, name: str, alias: str) -> None:
        """
        设置微信号别名
        :param name: 联系人名称
        :param alias: 要设置的别名
        """
        self.OpenContactProfile(name)
        # 打开编辑资料
        editBtn = self.weChatWindow.ButtonControl(Name="编辑资料")
        self._clickElement(editBtn)
        
        # 设置别名
        aliasInput = self.weChatWindow.EditControl(Name="微信号")
        aliasInput.SendKeys('{Ctrl}a', waitTime=0)
        aliasInput.SendKeys(alias)
        
        # 保存
        saveBtn = self.weChatWindow.ButtonControl(Name="完成")
        self._clickElement(saveBtn)

    def CreateFavoriteFolder(self, folderName: str) -> None:
        """
        在收藏夹中创建文件夹
        :param folderName: 文件夹名称
        """
        self.OpenFavorites()
        # 打开管理界面
        manageBtn = self.weChatWindow.ButtonControl(Name="管理")
        self._clickElement(manageBtn)
        
        # 创建新文件夹
        newFolderBtn = self.weChatWindow.ButtonControl(Name="新建文件夹")
        self._clickElement(newFolderBtn)
        
        # 输入文件夹名称
        nameInput = self.weChatWindow.EditControl(Name="输入文件夹名称")
        nameInput.SendKeys(folderName)
        
        # 确认创建
        confirmBtn = self.weChatWindow.ButtonControl(Name="完成")
        self._clickElement(confirmBtn)
        
        # 关闭管理界面
        self.weChatWindow.SendKeys('{Esc}')

    def ForwardMessage(self, sourceName: str, targetName: str, messageIndex: int = 0) -> None:
        """
        转发消息
        :param sourceName: 来源联系人/群聊名称
        :param targetName: 目标联系人/群聊名称
        :param messageIndex: 消息索引(0=最新消息)
        """
        self.OpenChatWindow(sourceName)
        # 定位指定消息
        msgList = self.weChatWindow.ListControl(Name="消息")
        targetMsg = msgList.GetChildren()[messageIndex]
        targetMsg.RightClick()
        
        # 选择转发
        forwardItem = self.weChatWindow.MenuItemControl(Name="转发")
        self._clickElement(forwardItem)
        
        # 选择转发目标
        self.SearchContact(targetName)
        contact = self._getContactElement(targetName)
        self._clickElement(contact)
        
        # 确认转发
        sendBtn = self.weChatWindow.ButtonControl(Name="发送")
        self._clickElement(sendBtn)

    def ViewMomentComments(self, contactName: str, index: int = 0) -> List[str]:
        """
        查看朋友圈评论
        :param contactName: 联系人名称
        :param index: 朋友圈索引(0=最新)
        :return: 评论内容列表
        """
        self.OpenMoments()
        
        # 定位指定联系人的朋友圈
        moment = self.weChatWindow.ListItemControl(Name=contactName, foundIndex=index+1)
        if not moment.Exists():
            raise LookupError(f"未找到 {contactName} 的第 {index+1} 条朋友圈")
        
        # 打开评论
        commentBtn = moment.ButtonControl(Name="评论")
        self._clickElement(commentBtn)
        
        # 获取评论
        comments = []
        commentList = self.weChatWindow.ListControl(Name="评论列表")
        for item in commentList.GetChildren():
            if item.ControlType == auto.ControlType.TextControl:
                comments.append(item.Name)
        
        # 关闭评论
        self.weChatWindow.SendKeys('{Esc}')
        return comments

    def PostComment(self, contactName: str, comment: str, index: int = 0) -> None:
        """
        发表朋友圈评论
        :param contactName: 联系人名称
        :param comment: 评论内容
        :param index: 朋友圈索引(0=最新)
        """
        self.OpenMoments()
        
        # 定位指定联系人的朋友圈
        moment = self.weChatWindow.ListItemControl(Name=contactName, foundIndex=index+1)
        if not moment.Exists():
            raise LookupError(f"未找到 {contactName} 的第 {index+1} 条朋友圈")
        
        # 打开评论
        commentBtn = moment.ButtonControl(Name="评论")
        self._clickElement(commentBtn)
        
        # 输入评论
        commentInput = self.weChatWindow.EditControl(Name="评论")
        commentInput.SendKeys(comment)
        
        # 发表评论
        sendBtn = self.weChatWindow.ButtonControl(Name="发表")
        self._clickElement(sendBtn)

    def SetGroupName(self, groupName: str, newName: str) -> None:
        """
        修改群名称
        :param groupName: 原群名称
        :param newName: 新群名称
        """
        self.OpenChatWindow(groupName)
        menuBtn = self.weChatWindow.ButtonControl(Name="聊天信息")
        self._clickElement(menuBtn)
        
        # 打开群名称编辑
        nameBtn = self.weChatWindow.ButtonControl(Name="群聊名称")
        self._clickElement(nameBtn)
        
        # 修改名称
        nameInput = self.weChatWindow.EditControl(Name="修改群聊名称")
        nameInput.SendKeys('{Ctrl}a', waitTime=0)
        nameInput.SendKeys(newName)
        
        # 保存
        saveBtn = self.weChatWindow.ButtonControl(Name="完成")
        self._clickElement(saveBtn)

    def SetMyNickname(self, nickname: str) -> None:
        """
        设置我的昵称
        :param nickname: 新昵称
        """
        # 打开设置
        settingsBtn = self.weChatWindow.ButtonControl(Name="设置")
        self._clickElement(settingsBtn)
        
        # 打开个人信息
        profileBtn = self.weChatWindow.ButtonControl(Name="个人信息")
        self._clickElement(profileBtn)
        
        # 修改昵称
        nicknameBtn = self.weChatWindow.ButtonControl(Name="昵称")
        self._clickElement(nicknameBtn)
        
        # 输入新昵称
        nameInput = self.weChatWindow.EditControl(Name="更改名字")
        nameInput.SendKeys('{Ctrl}a', waitTime=0)
        nameInput.SendKeys(nickname)
        
        # 保存
        saveBtn = self.weChatWindow.ButtonControl(Name="保存")
        self._clickElement(saveBtn)
        
        # 返回主界面
        self.weChatWindow.SendKeys('{Esc}', times=2)

    def SetGender(self, gender: str) -> None:
        """
        设置性别
        :param gender: 性别 ("男" 或 "女")
        """
        # 打开设置 > 个人信息
        settingsBtn = self.weChatWindow.ButtonControl(Name="设置")
        self._clickElement(settingsBtn)
        profileBtn = self.weChatWindow.ButtonControl(Name="个人信息")
        self._clickElement(profileBtn)
        
        # 修改性别
        genderBtn = self.weChatWindow.ButtonControl(Name="性别")
        self._clickElement(genderBtn)
        
        # 选择性别
        genderItem = self.weChatWindow.ListItemControl(Name=gender)
        self._clickElement(genderItem)
        
        # 返回主界面
        self.weChatWindow.SendKeys('{Esc}', times=2)

    def SetRegion(self, province: str, city: str) -> None:
        """
        设置地区
        :param province: 省份
        :param city: 城市
        """
        # 打开设置 > 个人信息
        settingsBtn = self.weChatWindow.ButtonControl(Name="设置")
        self._clickElement(settingsBtn)
        profileBtn = self.weChatWindow.ButtonControl(Name="个人信息")
        self._clickElement(profileBtn)
        
        # 修改地区
        regionBtn = self.weChatWindow.ButtonControl(Name="地区")
        self._clickElement(regionBtn)
        
        # 选择省份
        provinceItem = self.weChatWindow.ListItemControl(Name=province)
        self._clickElement(provinceItem)
        
        # 选择城市
        cityItem = self.weChatWindow.ListItemControl(Name=city)
        self._clickElement(cityItem)
        
        # 返回主界面
        self.weChatWindow.SendKeys('{Esc}', times=2)

    def SetSignature(self, signature: str) -> None:
        """
        设置个性签名
        :param signature: 签名内容
        """
        # 打开设置 > 个人信息
        settingsBtn = self.weChatWindow.ButtonControl(Name="设置")
        self._clickElement(settingsBtn)
        profileBtn = self.weChatWindow.ButtonControl(Name="个人信息")
        self._clickElement(profileBtn)
        
        # 修改个性签名
        signBtn = self.weChatWindow.ButtonControl(Name="个性签名")
        self._clickElement(signBtn)
        
        # 输入签名
        signInput = self.weChatWindow.EditControl(Name="设置个性签名")
        signInput.SendKeys(signature)
        
        # 保存
        saveBtn = self.weChatWindow.ButtonControl(Name="完成")
        self._clickElement(saveBtn)
        
        # 返回主界面
        self.weChatWindow.SendKeys('{Esc}', times=2)

    def SaveWeChatFiles(self, savePath: str) -> None:
        """
        批量保存微信文件
        :param savePath: 保存目录路径
        """
        # 打开设置
        settingsBtn = self.weChatWindow.ButtonControl(Name="设置")
        self._clickElement(settingsBtn)
        
        # 打开文件管理
        fileBtn = self.weChatWindow.ButtonControl(Name="文件管理")
        self._clickElement(fileBtn)
        
        # 打开文件夹
        openFolderBtn = self.weChatWindow.ButtonControl(Name="打开文件夹")
        self._clickElement(openFolderBtn)
        
        # 切换至文件选择窗口
        fileWindow = auto.WindowControl(ClassName="WeChatApp")
        time.sleep(1)
        
        # 全选文件
        fileWindow.SendKeys('^a')
        time.sleep(0.5)
        
        # 复制文件
        fileWindow.SendKeys('^c')
        time.sleep(1)
        
        # 导航到保存路径
        saveWindow = auto.WindowControl(ClassName="#32770")
        pathInput = saveWindow.EditControl(ClassName="Edit")
        pathInput.SendKeys(savePath)
        
        # 粘贴文件
        saveWindow.SendKeys('^v')
        time.sleep(2)
        
        # 关闭窗口
        fileWindow.SendKeys('{Alt}{F4}')

    def CleanWeChatCache(self) -> None:
        """
        清理微信缓存
        """
        # 打开设置
        settingsBtn = self.weChatWindow.ButtonControl(Name="设置")
        self._clickElement(settingsBtn)
        
        # 打开通用设置
        generalBtn = self.weChatWindow.ButtonControl(Name="通用设置")
        self._clickElement(generalBtn)
        
        # 打开存储管理
        storageBtn = self.weChatWindow.ButtonControl(Name="存储空间")
        self._clickElement(storageBtn)
        
        # 清理缓存
        cleanBtn = self.weChatWindow.ButtonControl(Name="清理")
        self._clickElement(cleanBtn)
        
        # 确认清理
        confirmBtn = self.weChatWindow.ButtonControl(Name="清理")
        self._clickElement(confirmBtn)
        
        # 等待清理完成
        time.sleep(5)
        
        # 返回主界面
        self.weChatWindow.SendKeys('{Esc}', times=3)

    def ChangeTheme(self, themeName: str) -> None:
        """
        更换微信主题
        :param themeName: 主题名称 ("默认"、"深色"等)
        """
        # 打开设置
        settingsBtn = self.weChatWindow.ButtonControl(Name="设置")
        self._clickElement(settingsBtn)
        
        # 打开通用设置
        generalBtn = self.weChatWindow.ButtonControl(Name="通用设置")
        self._clickElement(generalBtn)
        
        # 打开主题设置
        themeBtn = self.weChatWindow.ButtonControl(Name="主题")
        self._clickElement(themeBtn)
        
        # 选择主题
        themeItem = self.weChatWindow.ListItemControl(Name=themeName)
        self._clickElement(themeItem)
        
        # 返回主界面
        self.weChatWindow.SendKeys('{Esc}', times=2)

    def SetMessageRecall(self, enable: bool = True) -> None:
        """
        设置消息撤回功能
        :param enable: True开启撤回功能，False关闭
        """
        # 打开设置
        settingsBtn = self.weChatWindow.ButtonControl(Name="设置")
        self._clickElement(settingsBtn)
        
        # 打开通用设置
        generalBtn = self.weChatWindow.ButtonControl(Name="通用设置")
        self._clickElement(generalBtn)
        
        # 打开撤回设置
        recallBtn = self.weChatWindow.ButtonControl(Name="撤回设置")
        self._clickElement(recallBtn)
        
        # 切换开关状态
        toggle = self.weChatWindow.ToggleControl(Name="开启撤回")
        if toggle.GetTogglePattern().ToggleState != (1 if enable else 0):
            self._clickElement(toggle)
        
        # 返回主界面
        self.weChatWindow.SendKeys('{Esc}', times=2)

    def SendRedPacket(self, name: str, amount: float, count: int = 1, note: str = "") -> None:
        """
        发送红包
        :param name: 联系人/群聊名称
        :param amount: 单个红包金额
        :param count: 红包数量(1=个人红包，>1=群红包)
        :param note: 红包备注
        """
        self.OpenChatWindow(name)
        # 打开红包功能
        redPacketBtn = self.weChatWindow.ButtonControl(Name="红包")
        self._clickElement(redPacketBtn)
        
        if count > 1:
            # 群红包
            groupRedPacket = self.weChatWindow.ListItemControl(Name="拼手气红包")
            self._clickElement(groupRedPacket)
            
            # 设置红包数量
            countInput = self.weChatWindow.EditControl(Name="红包个数")
            countInput.SendKeys(str(count))
        else:
            # 个人红包
            personalRedPacket = self.weChatWindow.ListItemControl(Name="普通红包")
            self._clickElement(personalRedPacket)
        
        # 设置金额
        amountInput = self.weChatWindow.EditControl(Name="金额")
        amountInput.SendKeys(str(amount))
        
        # 设置备注
        noteInput = self.weChatWindow.EditControl(Name="恭喜发财，大吉大利")
        if note:
            noteInput.SendKeys('{Ctrl}a', waitTime=0)
            noteInput.SendKeys(note)
        
        # 塞钱进红包
        payBtn = self.weChatWindow.ButtonControl(Name="塞钱进红包")
        self._clickElement(payBtn)
        
        # 输入支付密码 (需要用户自行完成)
        time.sleep(3)

    def RecallMessage(self, name: str, messageIndex: int = 0) -> bool:
        """
        撤回消息
        :param name: 联系人/群聊名称
        :param messageIndex: 消息索引(0=最新消息)
        :return: 是否撤回成功
        """
        self.OpenChatWindow(name)
        # 定位指定消息
        msgList = self.weChatWindow.ListControl(Name="消息")
        targetMsg = msgList.GetChildren()[messageIndex]
        targetMsg.RightClick()
        
        # 选择撤回
        recallItem = self.weChatWindow.MenuItemControl(Name="撤回")
        if recallItem.Exists():
            self._clickElement(recallItem)
            return True
        return False

    def SetAutoLogin(self, enable: bool = True) -> None:
        """
        设置自动登录
        :param enable: True开启自动登录，False关闭
        """
        # 打开设置
        settingsBtn = self.weChatWindow.ButtonControl(Name="设置")
        self._clickElement(settingsBtn)
        
        # 打开账号设置
        accountBtn = self.weChatWindow.ButtonControl(Name="账号设置")
        self._clickElement(accountBtn)
        
        # 打开自动登录设置
        loginBtn = self.weChatWindow.ButtonControl(Name="自动登录")
        self._clickElement(loginBtn)
        
        # 切换开关状态
        toggle = self.weChatWindow.ToggleControl(Name="开启自动登录")
        if toggle.GetTogglePattern().ToggleState != (1 if enable else 0):
            self._clickElement(toggle)
        
        # 返回主界面
        self.weChatWindow.SendKeys('{Esc}', times=2)

import time
import uiautomation as auto

class WeChat:
    """微信自动化操作类，提供60+常用功能函数（封装_WeiXin类实现）"""
    
    # 在初始化时检查微信版本
    def __init__(self):
        self._wx = _WeiXin()
    
    def OpenWeChat(self) -> None:
        """激活微信窗口"""
        self._wx.OpenWeChat()
    
    def SearchContact(self, name: str) -> bool:
        """搜索联系人"""
        return self._wx.SearchContact(name)
    
    def OpenChatWindow(self, name: str) -> None:
        """打开指定联系人的聊天窗口"""
        self._wx.OpenChatWindow(name)
    
    def SendTextMessage(self, name: str, message: str) -> None:
        """发送文本消息"""
        self._wx.SendTextMessage(name, message)
    
    def SendFile(self, name: str, filePath: str) -> None:
        """发送文件"""
        self._wx.SendFile(name, filePath)
    
    def SendImage(self, name: str, imagePath: str) -> None:
        """发送图片"""
        self._wx.SendImage(name, imagePath)
    
    def CreateGroupChat(self, contacts: List[str]) -> None:
        """创建群聊"""
        self._wx.CreateGroupChat(contacts)
    
    def GetChatHistory(self, name: str, count: int = 10) -> List[str]:
        """获取聊天记录"""
        return self._wx.GetChatHistory(name, count)
    
    def ClearChatHistory(self, name: str) -> None:
        """清空聊天记录"""
        self._wx.ClearChatHistory(name)
    
    def SetRemarkName(self, name: str, remark: str) -> None:
        """设置联系人备注名"""
        self._wx.SetRemarkName(name, remark)
    
    def OpenContactProfile(self, name: str) -> None:
        """打开联系人资料页"""
        self._wx.OpenContactProfile(name)
    
    def AddContact(self, wxid: str) -> bool:
        """添加联系人"""
        return self._wx.AddContact(wxid)
    
    def AcceptFriendRequest(self) -> bool:
        """接受好友请求"""
        return self._wx.AcceptFriendRequest()
    
    def SendAppMessage(self, name: str, appName: str) -> None:
        """发送小程序消息"""
        self._wx.SendAppMessage(name, appName)
    
    def PinChat(self, name: str, pin: bool = True) -> None:
        """置顶/取消置顶聊天"""
        self._wx.PinChat(name, pin)
    
    def MuteNotifications(self, name: str, mute: bool = True) -> None:
        """设置消息免打扰"""
        self._wx.MuteNotifications(name, mute)
    
    def ChangeChatBackground(self, name: str, imagePath: str) -> None:
        """更换聊天背景"""
        self._wx.ChangeChatBackground(name, imagePath)
    
    def MarkAsUnread(self, name: str) -> None:
        """标记为未读"""
        self._wx.MarkAsUnread(name)
    
    def DeleteContact(self, name: str) -> None:
        """删除联系人"""
        self._wx.DeleteContact(name)
    
    def GetContactList(self) -> List[str]:
        """获取联系人列表"""
        return self._wx.GetContactList()
    
    def LogoutWeChat(self) -> None:
        """退出当前微信账号"""
        self._wx.LogoutWeChat()
    
    def SendVideo(self, name: str, videoPath: str) -> None:
        """发送视频文件"""
        self._wx.SendVideo(name, videoPath)
    
    def SendVoiceMessage(self, name: str, duration: int = 5) -> None:
        """发送语音消息"""
        self._wx.SendVoiceMessage(name, duration)
    
    def SendLocation(self, name: str, location: str) -> None:
        """发送位置信息"""
        self._wx.SendLocation(name, location)
    
    def SendContactCard(self, name: str, contactName: str) -> None:
        """发送联系人名片"""
        self._wx.SendContactCard(name, contactName)
    
    def CreateReminder(self, name: str, timeStr: str, content: str) -> None:
        """创建聊天提醒"""
        self._wx.CreateReminder(name, timeStr, content)
    
    def MarkChatAsRead(self, name: str) -> None:
        """标记聊天为已读"""
        self._wx.MarkChatAsRead(name)
    
    def SaveChatMedia(self, name: str, savePath: str) -> int:
        """保存聊天媒体文件"""
        return self._wx.SaveChatMedia(name, savePath)
    
    def StartVideoCall(self, name: str) -> None:
        """发起视频通话"""
        self._wx.StartVideoCall(name)
    
    def StartVoiceCall(self, name: str) -> None:
        """发起语音通话"""
        self._wx.StartVoiceCall(name)
    
    def EndCall(self) -> None:
        """结束当前通话"""
        self._wx.EndCall()
    
    def BlockContact(self, name: str) -> None:
        """加入黑名单"""
        self._wx.BlockContact(name)
    
    def UnblockContact(self, name: str) -> None:
        """移出黑名单"""
        self._wx.UnblockContact(name)
    
    def ChangeWeChatStatus(self, status: str) -> None:
        """修改微信在线状态"""
        self._wx.ChangeWeChatStatus(status)
    
    def OpenFavorites(self) -> None:
        """打开收藏夹"""
        self._wx.OpenFavorites()
    
    def AddToFavorites(self, name: str, messageIndex: int = 0) -> None:
        """添加消息到收藏夹"""
        self._wx.AddToFavorites(name, messageIndex)
    
    def OpenMoments(self) -> None:
        """打开朋友圈功能"""
        self._wx.OpenMoments()
    
    def PostMoment(self, content: str, imagePath: Optional[str] = None) -> None:
        """发布朋友圈"""
        self._wx.PostMoment(content, imagePath)
    
    def LikeMoment(self, contactName: str, index: int = 0) -> None:
        """点赞朋友圈"""
        self._wx.LikeMoment(contactName, index)
    
    def AddGroupMember(self, groupName: str, contactName: str) -> None:
        """添加成员到群聊"""
        self._wx.AddGroupMember(groupName, contactName)
    
    def RemoveGroupMember(self, groupName: str, contactName: str) -> None:
        """从群聊中移除成员"""
        self._wx.RemoveGroupMember(groupName, contactName)
    
    def SetGroupAnnouncement(self, groupName: str, announcement: str) -> None:
        """设置群公告"""
        self._wx.SetGroupAnnouncement(groupName, announcement)
    
    def TransferMoney(self, name: str, amount: float, note: str = "") -> None:
        """转账给联系人"""
        self._wx.TransferMoney(name, amount, note)
    
    def OpenMiniProgram(self, name: str) -> None:
        """打开小程序"""
        self._wx.OpenMiniProgram(name)
    
    def SearchChatHistory(self, name: str, keyword: str) -> List[str]:
        """搜索聊天记录"""
        return self._wx.SearchChatHistory(name, keyword)
    
    def SetAlias(self, name: str, alias: str) -> None:
        """设置微信号别名"""
        self._wx.SetAlias(name, alias)
    
    def CreateFavoriteFolder(self, folderName: str) -> None:
        """在收藏夹中创建文件夹"""
        self._wx.CreateFavoriteFolder(folderName)
    
    def ForwardMessage(self, sourceName: str, targetName: str, messageIndex: int = 0) -> None:
        """转发消息"""
        self._wx.ForwardMessage(sourceName, targetName, messageIndex)
    
    def ViewMomentComments(self, contactName: str, index: int = 0) -> List[str]:
        """查看朋友圈评论"""
        return self._wx.ViewMomentComments(contactName, index)
    
    def PostComment(self, contactName: str, comment: str, index: int = 0) -> None:
        """发表朋友圈评论"""
        self._wx.PostComment(contactName, comment, index)
    
    def SetGroupName(self, groupName: str, newName: str) -> None:
        """修改群名称"""
        self._wx.SetGroupName(groupName, newName)
    
    def SetMyNickname(self, nickname: str) -> None:
        """设置我的昵称"""
        self._wx.SetMyNickname(nickname)
    
    def SetGender(self, gender: str) -> None:
        """设置性别"""
        self._wx.SetGender(gender)
    
    def SetRegion(self, province: str, city: str) -> None:
        """设置地区"""
        self._wx.SetRegion(province, city)
    
    def SetSignature(self, signature: str) -> None:
        """设置个性签名"""
        self._wx.SetSignature(signature)
    
    def SaveWeChatFiles(self, savePath: str) -> None:
        """批量保存微信文件"""
        self._wx.SaveWeChatFiles(savePath)
    
    def CleanWeChatCache(self) -> None:
        """清理微信缓存"""
        self._wx.CleanWeChatCache()
    
    def ChangeTheme(self, themeName: str) -> None:
        """更换微信主题"""
        self._wx.ChangeTheme(themeName)
    
    def SetMessageRecall(self, enable: bool = True) -> None:
        """设置消息撤回功能"""
        self._wx.SetMessageRecall(enable)
    
    def SendRedPacket(self, name: str, amount: float, count: int = 1, note: str = "") -> None:
        """发送红包"""
        self._wx.SendRedPacket(name, amount, count, note)
    
    def RecallMessage(self, name: str, messageIndex: int = 0) -> bool:
        """撤回消息"""
        return self._wx.RecallMessage(name, messageIndex)
    
    def SetAutoLogin(self, enable: bool = True) -> None:
        """设置自动登录"""
        self._wx.SetAutoLogin(enable)

if __name__ == "__main__":
    wx = WeChat()
    wx.OpenWeChat()

    # 发送消息
    wx.SendTextMessage("文件传输助手", "自动化测试消息")

    # 添加联系人
    wx.AddContact("example_wxid")

    # 创建群聊
    wx.CreateGroupChat(["张三", "李四", "王五"])

    # 获取最近聊天记录
    history = wx.GetChatHistory("技术交流群", 5)
    print("最近消息:", history)

    # 设置免打扰
    wx.MuteNotifications("工作群", mute=True)