from stv_utils import is_ch
from stv_create_file.utils.GetConfig import start_process
from sys import argv as sys_argv
import os


configer = start_process()
use_chinese = False
if configer.lang.lower() == "zh-cn" \
     or configer.lang.lower() == "chinese":
    use_chinese = True
if configer.lang.lower() == "en-uk" \
    or configer.lang.lower() == "english":
    def is_ch()->bool:
        return False


def parse_text(function_name: str=None, args: str= "")->dict:
    if function_name is None:
        return {}
    func = globals().get(function_name)
    if func and callable(func):
        return func(args)
    return {}


def stv_parse(*args, **kwargs)->dict:
    if is_ch() or use_chinese:
        text = {
            "description": "本程序以用户指定的编码格式创建一些文件",
            "path": "指定一个或多个文件路径",
            "encoding": "指定被创建文件的编码",
            "prefix": "创建文件时第一行的前缀, 可用于注释元数据",
            "left_paren": "文件元数据的左标签",
            "right_paren": "文件元数据的右标签",
            "monopolize": "是否启用独占模式",
            "coding_check": "是否在创建后检测文件编码",
            "version": "输出项目版本号",
            "license": "输出项目许可证",
            "verbose": "创建文件时使用详细模式输出结果",
            "lang": "设置程序提示信息语言",
            "epilog": "您可以使用\"#n\"来表示\"\\n\", 以此来在元数据中加入新的换行符."
                      f"您还可以使用 {os.path.basename(sys_argv[0])} --whats-new latest来查看最新更新",
            "author": "在元数据末尾增加一行作者信息",
            "whats_new": "显示程序更新日志"
        }
    else:
        text = {
            "description": "Create some files with the specified encoding format",
            "path": "Specify one or more file paths",
            "encoding": "Specify the encoding of the created files",
            "prefix": "The prefix of the first line when creating files, which can be used for metadata comments",
            "left_paren": "The left label of the file metadata",
            "right_paren": "The right label of the file metadata",
            "monopolize": "Whether to enable exclusive mode",
            "coding_check": "Whether to detect file encoding after creation",
            "version": "Output project version number",
            "license": "Output project license",
            "verbose": "Output results in detailed mode when creating files",
            "lang": "Set the language of the program prompt information",
            "epilog": "You can use \"#n\" to represent \"\\n\", so as to add a new line in the metadata",
            "author": "Add a line of author information at the end of the metadata",
            "whats_new": "Show program update log"
        }
    return text


def auto(*args, **kwargs)->dict:
    if is_ch() or use_chinese:
        text = {
            "new": "创建器已启动",
            "del": "创建器已关闭"
        }
    else:
        text = {
            "new": "File creator started",
            "del": "File creator closed"
        }
    return text


def initialize(*args, **kwargs)->dict:
    if is_ch() or use_chinese:
        text = {
            "coding": {
                "Err": "不支持的编码: ",
                "Tips": "是否以 UTF-8 编码继续创建文件？(y/n) "
            },
            "prefix": {
                "Err": "前缀包含非 ASCII 字符: ",
                "Tips": "是否以新前缀继续创建文件？(y/n) ",
                "default": "是否以默认前缀 '#' 继续创建文件？(y/n) ",
                "new_prefix": "请输入新前缀: "
            },
            "folder": {
                "Err": [
                    "文件: ",
                    " 的所属目录 ",
                    " 不存在"
                ],
                "Tips": "是否创建对应文件夹？(y/n) ",
                "Dev": "新目录: ",
                "INFO": "已创建目录: ",
                "Exception": "发生未预期到的错误: "
            }
        }
    else:
        text = {
            "coding": {
                "Err": "Unsupported encoding: ",
                "Tips": "Continue creating files with UTF-8 encoding? (y/n) "
            },
            "prefix": {
                "Err": "Prefix contains non-ASCII characters: ",
                "Tips": "Continue creating files with new prefix? (y/n) ",
                "default": "Continue creating files with default prefix '#'? (y/n) ",
                "new_prefix": "Please enter new prefix: "
            },
            "folder": {
                "Err": [
                    "The file: ",
                    " 's directory ",
                    " does not exist."
                ],
                "Tips": "Create the corresponding folder? (y/n) ",
                "Dev": "New directory: ",
                "INFO": "Directory created: ",
                "Exception": "An unexpected error occurred: "
            }
        }
    return text


def file_coding_check(*args, **kwargs)->dict:
    if is_ch() or use_chinese:
        text = {
            "coding": [
                "文件: ",
                " 的编码为: "
            ],
            "confidence": "检测置信度: ",
        }
    else:
        text = {
            "coding": [
                "The file: ",
                " 's encoding is: "
            ],
            "confidence": "Detection confidence: ",
        }
    return text


def create_one_file(*args, **kwargs)->dict:
    if is_ch() or use_chinese:
        text = {
            "creating": "正在创建文件: ",
            "created": "文件创建成功: ",
            "FileExistsError": "文件已存在: ",
            "PermissionError": "没有权限在此处创建文件: ",
            "Exception": "发生未预期到的错误: "
        }
    else:
        text = {
            "creating": "Creating file: ",
            "created": "File created successfully: ",
            "FileExistsError": "File already exists: ",
            "PermissionError": "No permission to create files here: ",
            "Exception": "An unexpected error occurred: "
        }
    return text


def whats_new(version: str="")->dict or None:
    if is_ch() or use_chinese:
        update_info = {
            "0.0.1": "项目的初始版本，无改动",
            "0.0.2": "修复了元数据行尾换行符的问题",
            "0.0.3": "增加了修改语言的参数方法, 修复了一些已知问题, 然后吃了排骨",
            "0.0.4": "修复了提示文本索引异常的问题\n新增了\"添加作者功能\"\n新增了\"WHat's New?\"(就是你看到的这个)\n然后吃了小葱拌豆腐就米饭",
            "0.0.5": "累积修复版本, 修改了部分文本格式显示不美观的问题\n修复了注释检测时机\n吃了青椒鸡蛋饼"
        }
        # 你问我为什么要发癫嘛？安啦安啦，反正没人看
    else:
        update_info = {
            "0.0.1": "The initial version of the project, no changes",
            "0.0.2": "Fixed the problem of metadata line ending newline character",
            "0.0.3": "Added a method to modify the language parameter, fixed some known problems, and then ate pork ribs",
            "0.0.4": "Fixed the problem of prompt text index exception\nAdded \"Add author function\"\nAdded \"WHat's New?\"(which is what you see now)\nThen ate small onion stir-fried tofu with rice",
            "0.0.5": "Cumulative repair version, modified some text format display problems\nFixed the comment detection timing\nAte green pepper egg pancake"
        }
    if version in update_info:
        return update_info[version]
    return None