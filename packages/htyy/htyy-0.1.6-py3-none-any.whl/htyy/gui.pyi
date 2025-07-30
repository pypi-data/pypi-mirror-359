"""
H GUI 库 - Python 接口定义
版本: 1.0
作者: Huang Yiyi
描述: 基于Qt6的跨平台GUI库
注: 目录下的 D3Dcompiler_47.dll, Qt6Widgets.dll, Qt6Gui.dll, Qt6Core.dll 等等都是这个模块的依赖
"""

import typing

def HInit(plugins_path) -> None:
    """
    初始化GUI系统
    
    注意:
      - 必须在其他GUI函数前调用
      - 唯一的一个参数是plugins,就是你安装的Qt路径下的MSVC下的plugins文件夹
    """
    ...

def HCreateWindow(title: str = "H GUI") -> int:
    """
    创建主窗口
    
    参数:
      title: 窗口标题 (可选)
    
    返回:
      窗口ID (用于后续操作)
    """
    ...

def HCreateLabel(text: str = "", parent_id: int = 0) -> int:
    """
    创建标签控件
    
    参数:
      text: 初始文本 (可选)
      parent_id: 父容器ID (可选，默认为主窗口)
    
    返回:
      标签ID
    """
    ...

def HCreateButton(text: str = "", parent_id: int = 0) -> int:
    """
    创建按钮控件
    
    参数:
      text: 按钮文本 (可选)
      parent_id: 父容器ID (可选)
    
    返回:
      按钮ID
    """
    ...

def HCreateTextBox(text: str = "", parent_id: int = 0) -> int:
    """
    创建文本框控件
    
    参数:
      text: 初始文本 (可选)
      parent_id: 父容器ID (可选)
    
    返回:
      文本框ID
    """
    ...

def HCreateHBoxLayout(parent_id: int = 0) -> int:
    """
    创建水平布局容器
    
    参数:
      parent_id: 父容器ID (可选)
    
    返回:
      布局ID
    """
    ...

def HCreateVBoxLayout(parent_id: int = 0) -> int:
    """
    创建垂直布局容器
    
    参数:
      parent_id: 父容器ID (可选)
    
    返回:
      布局ID
    """
    ...

def HLayoutAddWidget(layout_id: int, widget_id: int) -> None:
    """
    向布局添加控件
    
    参数:
      layout_id: 布局容器ID
      widget_id: 要添加的控件ID
    """
    ...

def HSetText(widget_id: int, text: str) -> None:
    """
    设置控件文本
    
    支持类型: 标签/按钮/文本框
    
    参数:
      widget_id: 控件ID
      text: 要设置的文本
    """
    ...

def HGetText(widget_id: int) -> str:
    """
    获取控件文本
    
    支持类型: 标签/按钮/文本框
    
    参数:
      widget_id: 控件ID
    
    返回:
      控件当前文本
    """
    ...

def HSetGeometry(widget_id: int, x: int, y: int, width: int, height: int) -> None:
    """
    设置控件位置和大小
    
    参数:
      widget_id: 控件ID
      x: 水平位置
      y: 垂直位置
      width: 宽度
      height: 高度
    """
    ...

def HShowWidget(widget_id: int) -> None:
    """
    显示控件
    
    参数:
      widget_id: 要显示的控件ID
    """
    ...

def HSetCallback(widget_id: int, event: str, callback: typing.Callable[[int], None]) -> None:
    """
    设置事件回调函数
    
    支持事件:
      - "clicked": 按钮点击事件
    
    参数:
      widget_id: 控件ID
      event: 事件类型
      callback: 回调函数 (接受控件ID作为参数)
    """
    ...

def HShowMessage(title: str = "Message", message: str = "") -> None:
    """
    显示消息对话框
    
    参数:
      title: 对话框标题 (可选)
      message: 消息内容 (可选)
    """
    ...

def HRun() -> None:
    """
    启动GUI主循环
    
    注意: 必须在所有界面创建完成后调用
    """
    ...

def HCreateTabWidget(parent_id: int = 0) -> int:
    """
    创建标签页控件
    
    参数:
      parent_id: 父容器ID (可选)
    
    返回:
      标签页控件ID
    """
    ...

def HAddTab(tab_widget_id: int, widget_id: int, label: str) -> None:
    """
    添加标签页
    
    参数:
      tab_widget_id: 标签页控件ID
      widget_id: 要添加的控件ID
      label: 标签页标题
    """
    ...

def HCreateProgressBar(parent_id: int = 0) -> int:
    """
    创建进度条控件
    
    参数:
      parent_id: 父容器ID (可选)
    
    返回:
      进度条ID
    """
    ...

def HSetProgressValue(progress_id: int, value: int) -> None:
    """
    设置进度条值
    
    参数:
      progress_id: 进度条ID
      value: 进度值 (0-100)
    """
    ...

def HCreateMenuBar(parent_id: int = 0) -> int:
    """
    创建菜单栏
    
    参数:
      parent_id: 父窗口ID (可选)
    
    返回:
      菜单栏ID
    """
    ...

def HAddMenu(menu_bar_id: int, title: str) -> int:
    """
    添加菜单到菜单栏
    
    参数:
      menu_bar_id: 菜单栏ID
      title: 菜单标题
    
    返回:
      菜单ID
    """
    ...

def HAddMenuItem(menu_id: int, text: str) -> int:
    """
    添加菜单项到菜单
    
    参数:
      menu_id: 菜单ID
      text: 菜单项文本
    
    返回:
      菜单项ID
    """
    ...

def HSetMenuCallback(menu_item_id: int, callback: typing.Callable[[int], None]) -> None:
    """
    设置菜单项回调
    
    参数:
      menu_item_id: 菜单项ID
      callback: 回调函数 (接受菜单项ID作为参数)
    """
    ...