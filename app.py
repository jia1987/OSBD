import sys,os

import core.const

print(f"当前工作目录: {os.getcwd()}")
print(f"EXE 文件位置: {sys.executable}")
print(f"EXE 所在目录: {os.path.dirname(sys.executable)}")
IS_FROZEN = getattr(sys, 'frozen', False)

import multiprocessing,logging
multiprocessing.freeze_support()

import sys
import logging
import traceback

# 配置日志
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('error.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def handle_global_exception(exc_type, exc_value, exc_traceback):
    """
    全局异常处理函数 - 记录日志后退出
    """
    if issubclass(exc_type, KeyboardInterrupt):
        # 不处理键盘中断，直接退出
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    # 记录错误日志
    logger.critical(
        "未捕获的异常，程序将退出:",
        exc_info=(exc_type, exc_value, exc_traceback)
    )
    if IS_FROZEN:
        print("全局异常信息：")
        print("异常类型：", exc_type)
        print("异常值：", exc_value)
        print("异常追踪：", exc_traceback)
        input("确定退出...")
    # 调用原始异常处理器，显示错误并退出
    sys.__excepthook__(exc_type, exc_value, exc_traceback)
    exit(1)

# 设置全局异常处理器
sys.excepthook = handle_global_exception

# 获取.exe所在目录
if IS_FROZEN:
    # 如果是打包后的程序
    app_path = os.path.dirname(sys.executable)
    os.chdir(app_path)  # 更改工作目录

if __name__ == '__main__':
    print("[System] init app...")
    from PyQt5.QtWidgets import QApplication, QMessageBox
    app = QApplication(sys.argv)

    # ==========验证程序===========
    from core.utils.machine_id import get_machine_fingerprint, verify_license
    from core.const import Text
    with open('config/pub_key', 'rb') as f:
        pub = f.read()
    with open('config/license', 'r') as f:
        license = f.read()
    mid = get_machine_fingerprint(extra_salt=Text.APP_NAME)
    with open('config/mid', 'w', encoding='utf8') as f:
        f.write(mid)
    ok, msg = verify_license(pub, license,extra_salt=Text.APP_NAME)
    if ok or True:
        from view import Window

        print("[System] init window...")
        view = Window()
        print("[System] load qss...")
        # with open(os.path.join(core.const.Path.RC_DIR,'style','MaterialDark.qss'),'r',) as f:
        #     qss = f.read()
        # view.setStyleSheet(qss)
        # start
        from core import faultDetectionPipeline

        faultDetectionPipeline.start()
        view.show()
        print("[System] show...")
        sys.exit(app.exec_())
    else:
        # 验证失败
        QMessageBox.warning(None,
                            "Error",
                            f"验证失败:\n"
                            f"  {msg}\n"
                            f"机器码:{mid}",
                            QMessageBox.Ok)
