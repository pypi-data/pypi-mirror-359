from tdf_tool.modules.multi_code.flutter.flutter_reflow import FlutterReflow
from tdf_tool.tools.shell_dir import ProjectType, ShellDir
from tdf_tool.modules.translate.flutter.flutter_translate_tools import (
    FlutterTranslateToolsFactory,
)
from tdf_tool.modules.translate.ios.ios_translate import iOSTranslate
from tdf_tool.modules.translate.translate_lint import TranslateLint


class Translate:
    """
    国际化相关：tl translate -h 查看详情
    """

    def __init__(self) -> None:
        self.lint = TranslateLint()
        self.reflow = FlutterReflow()

    def start(
        self,
        all_module=False,
        always_yes=False,
        generate_code=False,
    ):
        """
        国际化相关：通过交互式的方式处理国际化
        """
        ShellDir.goInShellDir()
        projectType = ShellDir.getProjectType()
        if projectType == ProjectType.FLUTTER:
            FlutterTranslateToolsFactory().translate(
                None, all_module, always_yes, generate_code
            )
        elif projectType == ProjectType.IOS:
            iOSTranslate().translate()

    def module(
        self,
        name,
        always_yes=False,
        generate_code=False,
    ):
        """
        国际化相关：指定模块进行国际化
        """
        ShellDir.goInShellDir()
        projectType = ShellDir.getProjectType()
        if projectType == ProjectType.FLUTTER:
            FlutterTranslateToolsFactory().translate_module(
                name, always_yes, generate_code
            )
        elif projectType == ProjectType.IOS:
            iOSTranslate().translate_module(name)
        exit(0)

    def integrate(self):
        """
        国际化相关：整合所有组件的国际化文件到一个文件中，用来维护一份国际化文件
        """
        ShellDir.goInShellDir()
        projectType = ShellDir.getProjectType()
        if projectType == ProjectType.FLUTTER:
            FlutterTranslateToolsFactory().integrate()
        elif projectType == ProjectType.IOS:
            iOSTranslate().integrate()
        exit(0)

    def clearI18nFiles(self):
        """
        国际化相关：删除国际化相关的文件夹
        """
        ShellDir.goInShellDir()
        projectType = ShellDir.getProjectType()
        if projectType == ProjectType.FLUTTER:
            FlutterTranslateToolsFactory().clear_i18n_files()
        elif projectType == ProjectType.IOS:
            pass
        exit(0)

    def find_modules(self):
        """
        国际化相关：找到所有有翻译的库
        """
        ShellDir.goInShellDir()
        projectType = ShellDir.getProjectType()
        if projectType == ProjectType.FLUTTER:
            FlutterTranslateToolsFactory().find_modules()
        elif projectType == ProjectType.IOS:
            pass
        exit(0)
