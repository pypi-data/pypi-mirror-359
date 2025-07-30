import time
from typing import List, Optional, Tuple

class WeiXin:
    """微信自动化操作类，提供60+常用功能函数"""
    
    def __init__(self) -> None:
        """初始化微信窗口控制对象"""
        ...
    
    def OpenWeChat(self) -> None:
        """
        激活微信窗口
        异常：如果微信未启动则抛出EnvironmentError
        """
        ...
    
    def SearchContact(self, name: str) -> bool:
        """
        搜索联系人
        :param name: 联系人名称
        :return: 是否找到该联系人
        """
        ...
    
    def OpenChatWindow(self, name: str) -> None:
        """
        打开指定联系人的聊天窗口
        :param name: 联系人名称
        异常：找不到联系人时抛出LookupError
        """
        ...
    
    def SendTextMessage(self, name: str, message: str) -> None:
        """
        发送文本消息
        :param name: 联系人名称
        :param message: 要发送的文本内容
        """
        ...
    
    # ... (保留之前的所有函数定义) ...
    
    def SetAlias(self, name: str, alias: str) -> None:
        """
        设置微信号别名
        :param name: 联系人名称
        :param alias: 要设置的别名
        注意：此功能需要联系人已设置微信号
        """
        ...
    
    def OpenMoments(self) -> None:
        """打开朋友圈功能"""
        ...
    
    # ... (保留之前的所有函数定义) ...
    
    def SetAlias(self, name: str, alias: str) -> None:
        """
        设置微信号别名
        :param name: 联系人名称
        :param alias: 要设置的别名
        注意：此功能需要联系人已设置微信号
        """
        ...
    
    # ================ 新增15个函数 ================ #
    
    def CreateFavoriteFolder(self, folderName: str) -> None:
        """
        在收藏夹中创建文件夹
        :param folderName: 文件夹名称
        """
        ...
    
    def ForwardMessage(self, sourceName: str, targetName: str, messageIndex: int = 0) -> None:
        """
        转发消息
        :param sourceName: 来源联系人/群聊名称
        :param targetName: 目标联系人/群聊名称
        :param messageIndex: 消息索引(0=最新消息)
        """
        ...
    
    def ViewMomentComments(self, contactName: str, index: int = 0) -> List[str]:
        """
        查看朋友圈评论
        :param contactName: 联系人名称
        :param index: 朋友圈索引(0=最新)
        :return: 评论内容列表
        异常：找不到朋友圈时抛出LookupError
        """
        ...
    
    def PostComment(self, contactName: str, comment: str, index: int = 0) -> None:
        """
        发表朋友圈评论
        :param contactName: 联系人名称
        :param comment: 评论内容
        :param index: 朋友圈索引(0=最新)
        异常：找不到朋友圈时抛出LookupError
        """
        ...
    
    def SetGroupName(self, groupName: str, newName: str) -> None:
        """
        修改群名称
        :param groupName: 原群名称
        :param newName: 新群名称
        注意：需要群主权限
        """
        ...
    
    def SetMyNickname(self, nickname: str) -> None:
        """
        设置我的昵称
        :param nickname: 新昵称
        """
        ...
    
    def SetGender(self, gender: str) -> None:
        """
        设置性别
        :param gender: 性别 ("男" 或 "女")
        """
        ...
    
    def SetRegion(self, province: str, city: str) -> None:
        """
        设置地区
        :param province: 省份
        :param city: 城市
        """
        ...
    
    def SetSignature(self, signature: str) -> None:
        """
        设置个性签名
        :param signature: 签名内容
        """
        ...
    
    def SaveWeChatFiles(self, savePath: str) -> None:
        """
        批量保存微信文件
        :param savePath: 保存目录路径
        注意：此操作会复制所有微信文件
        """
        ...
    
    def CleanWeChatCache(self) -> None:
        """
        清理微信缓存
        """
        ...
    
    def ChangeTheme(self, themeName: str) -> None:
        """
        更换微信主题
        :param themeName: 主题名称 ("默认"、"深色"等)
        """
        ...
    
    def SetMessageRecall(self, enable: bool = True) -> None:
        """
        设置消息撤回功能
        :param enable: True开启撤回功能，False关闭
        """
        ...
    
    def SendRedPacket(self, name: str, amount: float, count: int = 1, note: str = "") -> None:
        """
        发送红包
        :param name: 联系人/群聊名称
        :param amount: 单个红包金额
        :param count: 红包数量(1=个人红包，>1=群红包)
        :param note: 红包备注
        注意：此操作需要用户手动输入支付密码
        """
        ...
    
    def RecallMessage(self, name: str, messageIndex: int = 0) -> bool:
        """
        撤回消息
        :param name: 联系人/群聊名称
        :param messageIndex: 消息索引(0=最新消息)
        :return: 是否撤回成功（2分钟内有效）
        """
        ...
    
    def SetAutoLogin(self, enable: bool = True) -> None:
        """
        设置自动登录
        :param enable: True开启自动登录，False关闭
        """
        ...