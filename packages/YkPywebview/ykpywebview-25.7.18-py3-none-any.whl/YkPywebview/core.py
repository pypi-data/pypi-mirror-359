import webview
import os
import pickle
import toml

global window


class YkWebviewApi:
    def __init__(self) -> None:
        self.mute = False
        self.user_file = 'user.pkl'
        self.window = None

    def setWindow(self):
        global window
        self.window = window

    def printToTerm(self, msg: str, kind='info'):
        """
        打印日志到终端

        :param msg: msg中不能包含'\'等特殊字符串。
        :param kind: 可取值warning info success error system
        :return:
        """
        if self.mute:
            return
        if isinstance(self.window, webview.Window):
            cmd = f'window.printToTerm("{msg}", "{kind}")'
            self.window.evaluate_js(cmd, callback=None)
        else:
            print(f'window不可用, {self.window=}')

    def setTaskBar(self, title: str, progress: int):
        """
        设置任务栏图标和进度条

        :param title: 任务栏标题
        :param progress: 任务栏进度
        """
        if isinstance(self.window, webview.Window):
            cmd = f'window.setTaskBar("{title}", {progress})'
            self.window.evaluate_js(cmd, callback=None)
        else:
            print(f'window不可用, {self.window=}')

    def saveLoginInfo(self, userInfo: dict):
        """
        保存登录信息到本地user.pkl文件

        :param userInfo: 用户信息字典，包含username和password
        """
        try:
            with open(self.user_file, 'wb') as f:
                pickle.dump(userInfo, f)
            return True
        except Exception as e:
            print(f"保存登录信息失败: {e}")
            return False

    def getLoginInfo(self):
        """
        获取登录信息，读取本地文件user.pkl保存的username和password

        :return: 用户名和密码
        """
        if not os.path.exists(self.user_file):
            return None

        try:
            with open(self.user_file, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"读取登录信息失败: {e}")
            return None

    def toggle_fullscreen(self):
        """
        全屏
        """
        if isinstance(self.window, webview.Window):
            self.window.toggle_fullscreen()
            from webview import localization
        else:
            print(f'window不可用, {self.window=}')

    def loadAppSettings(self):
        """
        加载调用项目的settings.app.toml文件

        :return: 返回解析后的TOML对象，如果文件不存在或解析失败则返回None
        """
        try:
            # 获取当前工作目录（调用项目的路径）
            project_path = os.getcwd()
            settings_path = os.path.join(project_path, 'settings.app.toml')

            if not os.path.exists(settings_path):
                print(f"配置文件不存在: {settings_path}")
                return {}

            with open(settings_path, 'r', encoding='utf-8') as f:
                return toml.load(f)

        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return {}

    def loadProjectSettings(self):
        """
        加载调用项目的settings.project.toml文件

        :return: 返回解析后的TOML对象，如果文件不存在则返回空字典，解析失败返回None
        """
        try:
            # 获取当前工作目录（调用项目的路径）
            project_path = os.getcwd()
            settings_path = os.path.join(project_path, 'settings.project.toml')

            if not os.path.exists(settings_path):
                print(f"项目配置文件不存在: {settings_path}")
                return {}

            with open(settings_path, 'r', encoding='utf-8') as f:
                return toml.load(f)

        except Exception as e:
            print(f"加载项目配置文件失败: {e}")
            return None

    def saveAppSettings(self, settings: dict):
        """
        保存配置到调用项目的settings.app.toml文件

        :param settings: 要保存的配置字典
        :return: 成功返回True，失败返回False
        """
        try:
            # 获取当前工作目录（调用项目的路径）
            project_path = os.getcwd()
            settings_path = os.path.join(project_path, 'settings.app.toml')

            # 确保目录存在
            os.makedirs(os.path.dirname(settings_path), exist_ok=True)

            with open(settings_path, 'w', encoding='utf-8') as f:
                toml.dump(settings, f)
            return True

        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False

    def saveProjectSettings(self, settings: dict):
        """
        保存配置到调用项目的settings.project.toml文件

        :param settings: 要保存的配置字典
        :return: 成功返回True，失败返回False
        """
        try:
            # 获取当前工作目录（调用项目的路径）
            project_path = os.getcwd()
            settings_path = os.path.join(project_path, 'settings.project.toml')

            # 确保目录存在
            os.makedirs(os.path.dirname(settings_path), exist_ok=True)

            with open(settings_path, 'w', encoding='utf-8') as f:
                toml.dump(settings, f)
            return True

        except Exception as e:
            print(f"保存项目配置文件失败: {e}")
            return False

    def getProjectSettings(self):
        return self.loadProjectSettings()

    def getAppSettings(self):
        return self.loadAppSettings()


def start(Api, url: str, ssl=True, debug=False, localization=None, title='gf-ui', width=900, height=620,
          text_select=True, confirm_close=True):
    """
    启动webview窗口
    """
    global window
    if localization is None:
        localization = {
            'global.quitConfirmation': u'确定关闭?',
            'global.ok': '确定',
            'global.quit': '退出',
            'global.cancel': '取消',
            'global.saveFile': '保存文件',
            'windows.fileFilter.allFiles': '所有文件',
            'windows.fileFilter.otherFiles': '其他文件类型',
            'linux.openFile': '打开文件',
            'linux.openFiles': '打开文件',
            'linux.openFolder': '打开文件夹',
        }

    api = Api()
    window = webview.create_window(
        title=title,
        url=url,
        width=width,
        height=height,
        resizable=True,
        text_select=text_select,
        confirm_close=confirm_close,
        js_api=api,
        min_size=(900, 620)
    )
    # 启动窗口
    webview.start(localization=localization, ssl=ssl,
                  debug=debug)  # 该语句会阻塞，直到程序关闭后才会继续执行后续代码
