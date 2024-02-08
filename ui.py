#!/usr/bin/env python3
import glob
import json
import os
import shutil
import subprocess
import sys
# using threading in some function
import threading
import time
# import tk/tcl
import tkinter as tk
import webbrowser
from tkinter import *
from tkinter import scrolledtext
from tkinter import ttk
from tkinter.filedialog import *

# from bs4 import BeautifulSoup
from ttkbootstrap import Style  # use ttkbootstrap theme
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame

# import functions I modified
from pyscripts import utils, ozip_decrypt, vbpatch, imgextractor, sdat2img, fspatch, img2sdat
from pyscripts.utils import gettype

EXECPATH = ".\\bin"  # 临时添加可执行程序目录到系统变量

# Var
AUTHOR = "affggh & ColdWindScholar"
WINDOWTITLE = f"NH4RomTool [版本: 20240208] [作者: {AUTHOR}]"
THEME = "minty"  # 设置默认主题
LOGOICO = ".\\bin\\logo.ico"
TEXTFONT = ['Arial', 10]
LOCALDIR = os.getcwd()

# ui config This is for repack tool to detect
if os.access(LOCALDIR + os.sep + "config.json", os.F_OK):
    with open("config.json", encoding='utf-8') as f:
        UICONFIG = json.load(f)
else:
    print("config.json is missing")
    sys.exit()
if EXECPATH:
    utils.addExecPath(EXECPATH)

style = Style(theme=THEME)

# Begin of window
root = style.master

width = 1240
height = 600

root.geometry("%sx%s" % (width, height))
# root.resizable(0,0) # 设置最大化窗口不可用
root.title(WINDOWTITLE)

# Set images
LOGOIMG = tk.PhotoImage(file=LOCALDIR + ".\\bin\\logo.png")
DEFAULTSTATUS = tk.PhotoImage(file=LOCALDIR + ".\\bin\\processdone.png")

WorkDir = ''

# Var
filename = tk.StringVar()
directoryname = tk.StringVar()
inputvar = tk.StringVar()
USERCMD = tk.StringVar()


# from https://www.i4k.xyz/article/weixin_49317370/108878373
class myStdout:  # 重定向类
    def __init__(self):
        sys.stdout = self
        # sys.stderr = self

    @staticmethod
    def write(info):
        # info信息即标准输出sys.stdout和sys.stderr接收到的输出信息
        # text.insert('end', info)	# 在多行文本控件最后一行插入print信息
        # text.update()	# 更新显示的文本，不加这句插入的信息无法显示
        # text.see(tkinter.END)	# 始终显示最后一行，不加这句，当文本溢出控件最后一行时，不会自动显示最后一行

        text.configure(state='normal')
        text.insert(END, "[%s]" % (utils.get_time()) + "%s" % info)
        text.update()  # 实时返回信息
        text.yview('end')
        text.configure(state='disabled')

    def flush(self):
        ...


class MyThread(threading.Thread):
    def __init__(self, func, *args):
        super().__init__()

        self.func = func
        self.args = args
        self.daemon = True
        self.start()  # 在这里开始

    def run(self):
        self.func(*self.args)


def logo():
    utils.chLocal()
    root.iconbitmap(LOGOICO)


logo()


def VisitMe():
    webbrowser.open("https://github.com/ColdWindScholar/NH4RomTool")


def showinfo(textmsg):
    text.configure(state='normal')
    text.insert(END, "[%s]" % (utils.get_time()) + "%s" % textmsg + "\n")
    text.update()  # 实时返回信息
    text.yview('end')
    text.configure(state='disabled')


def runcmd(cmd):
    try:
        ret = subprocess.Popen(cmd, shell=False,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
        for i in iter(ret.stdout.readline, b""):
            showinfo(i.decode("utf-8", "ignore").strip())
    except subprocess.CalledProcessError as e:
        for i in iter(e.stdout.readline, b""):
            showinfo(i)


def returnoutput(cmd):
    try:
        ret = subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT)
        return ret.decode()
    except subprocess.CalledProcessError as e:
        return str(e)


def cleaninfo():
    text.configure(state='normal')
    text.delete(1.0, END)  # 清空text
    text.configure(state='disabled')


def selectFile():
    filepath = askopenfilename()  # 选择打开什么文件，返回文件名
    filename.set(filepath.replace('/', '\\'))  # 设置变量filename的值
    showinfo("选择文件为: %s" % (filepath.replace('/', '\\')))


def selectDir():
    dirpath = askdirectory()  # 选择文件夹
    directoryname.set(dirpath.replace('/', '\\'))
    showinfo("选择文件夹为: %s" % (dirpath.replace('/', '\\')))


def about():
    root2 = tk.Toplevel()
    curWidth = 300
    curHight = 180
    # 获取屏幕宽度和高度
    scn_w, scn_h = root.maxsize()
    # print(scn_w, scn_h)
    # 计算中心坐标
    cen_x = (scn_w - curWidth) / 2
    cen_y = (scn_h - curHight) / 2
    # print(cen_x, cen_y)

    # 设置窗口初始大小和位置
    size_xy = '%dx%d+%d+%d' % (curWidth, curHight, cen_x, cen_y)
    root2.geometry(size_xy)
    # root2.geometry("300x180")
    root2.resizable(False, False)  # 设置最大化窗口不可用
    root2.title("关于")
    aframe1 = Frame(root2, relief=FLAT, borderwidth=1)
    aframe2 = Frame(root2, relief=FLAT, borderwidth=1)
    aframe1.pack(side=BOTTOM, expand=YES, pady=3)
    aframe2.pack(side=BOTTOM, expand=YES, pady=3)
    ttk.Button(aframe1, text='访问工具主页', command=VisitMe, style='primiary.Outline.TButton').pack(side=LEFT,
                                                                                                     expand=YES, padx=5)
    ttk.Button(aframe1, text='给作者打钱 ', command=VisitMe, style='success.TButton').pack(side=LEFT, expand=YES,
                                                                                           padx=5)
    ttk.Label(aframe2,
              text='沼_Rom工具箱 Version %s\nGUI Written by python tk/tcl\nTheme by ttkbootstrap\n%s Copyright(R) Apache 2.0 LICENSE' % (
                  20240208, AUTHOR)).pack(side=BOTTOM, expand=NO, pady=3)
    utils.chLocal()

    ttk.Label(aframe2, image=LOGOIMG).pack(side=TOP, expand=YES, pady=3)
    root2.mainloop()


def userInputWindow(title='输入文本'):
    inputWindow = tk.Toplevel()
    curWidth = 400
    curHight = 120
    # 获取屏幕宽度和高度
    scn_w, scn_h = root.maxsize()
    # print(scn_w, scn_h)
    # 计算中心坐标
    cen_x = (scn_w - curWidth) / 2
    cen_y = (scn_h - curHight) / 2
    # print(cen_x, cen_y)

    # 设置窗口初始大小和位置
    size_xy = '%dx%d+%d+%d' % (curWidth, curHight, cen_x, cen_y)
    inputWindow.geometry(size_xy)
    # inputWindow.geometry("300x180")
    inputWindow.resizable(False, False)  # 设置最大化窗口不可用
    inputWindow.title(title)
    ent = ttk.Entry(inputWindow, textvariable=inputvar, width=50)
    ent.pack(side=TOP, expand=YES, padx=5)
    ttk.Button(inputWindow, text='确认', command=inputWindow.destroy, style='primiary.Outline.TButton').pack(side=TOP,
                                                                                                             expand=YES,
                                                                                                             padx=5)
    inputWindow.wait_window()


def fileChooseWindow(tips):
    chooseWindow = tk.Toplevel()
    curWidth = 500
    curHight = 180
    # 获取屏幕宽度和高度
    scn_w, scn_h = root.maxsize()
    # print(scn_w, scn_h)
    # 计算中心坐标
    cen_x = (scn_w - curWidth) / 2
    cen_y = (scn_h - curHight) / 2
    # print(cen_x, cen_y)

    # 设置窗口初始大小和位置
    size_xy = '%dx%d+%d+%d' % (curWidth, curHight, cen_x, cen_y)
    chooseWindow.geometry(size_xy)
    # chooseWindow.geometry("300x180")
    chooseWindow.resizable(False, False)  # 设置最大化窗口不可用
    chooseWindow.title(tips)
    ent = ttk.Entry(chooseWindow, textvariable=filename, width=50)
    ent.pack(side=TOP, expand=NO, padx=0, pady=20)
    ttk.Button(chooseWindow, text='确认', width=15, command=chooseWindow.destroy,
               style='primiary.Outline.TButton').pack(side=RIGHT, expand=YES, padx=5, pady=5)
    ttk.Button(chooseWindow, text='选择文件', width=15, command=lambda: [selectFile(), chooseWindow.destroy()],
               style='primiary.TButton').pack(side=RIGHT, expand=YES, padx=5, pady=5)
    chooseWindow.wait_window()


def dirChooseWindow(tips):
    chooseWindow = tk.Toplevel()
    curWidth = 400
    curHight = 120
    # 获取屏幕宽度和高度
    scn_w, scn_h = root.maxsize()
    # print(scn_w, scn_h)
    # 计算中心坐标
    cen_x = (scn_w - curWidth) / 2
    cen_y = (scn_h - curHight) / 2
    # print(cen_x, cen_y)

    # 设置窗口初始大小和位置
    size_xy = '%dx%d+%d+%d' % (curWidth, curHight, cen_x, cen_y)
    chooseWindow.geometry(size_xy)
    # chooseWindow.geometry("300x180")
    chooseWindow.resizable(False, False)  # 设置最大化窗口不可用
    chooseWindow.title(tips)
    ent = ttk.Entry(chooseWindow, textvariable=directoryname, width=50)
    ent.pack(side=TOP, expand=NO, padx=0, pady=20)
    ttk.Button(chooseWindow, text='确认', width=15, command=chooseWindow.destroy,
               style='primiary.Outline.TButton').pack(side=RIGHT, expand=YES, padx=5, pady=5)
    ttk.Button(chooseWindow, text='选择文件夹', width=15, command=lambda: [selectDir(), chooseWindow.destroy()],
               style='primiary.TButton').pack(side=RIGHT, expand=YES, padx=5, pady=5)
    chooseWindow.wait_window()


def change_theme(var):
    showinfo("设置主题为 : " + var)
    style = Style(theme=var)
    style.theme_use()


def getWorkDir():
    for item in table.get_children():
        table.delete(item)
    d = utils.listDirHeader('.\\', 'NH4_')
    for item in d:
        table.insert('', 'end', values=item)


def clearWorkDir():
    if not WorkDir:
        showinfo("当前未选择任何目录")
    else:
        showinfo("将清理: " + WorkDir)
        try:
            removeDir_EX(os.getcwd() + '\\' + WorkDir)
            # showinfo(os.getcwd() + '\\' + WorkDir)
        except IOError:
            showinfo("清理失败, 请检查是否有程序正在占用它...?")
        else:
            showinfo("清理成功, 正在刷新工作目录")


# removeButSaveCurrentDir  add by azwhikaru 20220329
def removeDir_EX(workDirEX):
    for root, dirs, files in os.walk(workDirEX, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))


class cartoon:
    def __init__(self):
        ...

    def __enter__(self):
        self.state = False
        self.statusthread = threading.Thread(target=self.__run)
        self.statusthread.start()

    def __run(self):
        while True:
            for i in range(33):  # 33是图片帧数
                photo = PhotoImage(file=LOCALDIR + '\\bin\\processing.gif', format='gif -index %i' % i)
                statusbar['image'] = photo
                time.sleep(1 / 18)
            if self.state:
                break

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.state = True
        self.statusthread.join()
        statusbar['image'] = DEFAULTSTATUS


def SelectWorkDir():
    item_text = ['']
    for item_ in table.selection():
        item_text = table.item(item_, "values")
    if item_text[0] != "":
        global WorkDir
        WorkDir = item_text[0]
        showinfo("选择工作目录为: %s" % WorkDir)


def ConfirmWorkDir():
    if not WorkDir:
        showinfo("Warning : 请选择一个目录")
    else:
        tabControl.select(tab2)


def rmWorkDir():
    if WorkDir:
        showinfo("删除目录: %s" % WorkDir)
        shutil.rmtree(WorkDir)
    else:
        showinfo("Error : 要删除的文件夹不存在")
    getWorkDir()


def mkWorkdir():
    userInputWindow()
    showinfo("用户输入: %s" % (inputvar.get()))
    utils.mkdir("NH4_" + "%s" % (inputvar.get()))
    getWorkDir()


def detectFileType():
    fileChooseWindow("检测文件类型")
    if os.access(filename.get(), os.F_OK):
        showinfo(f"文件格式为 : {gettype(filename.get())}")
    else:
        showinfo("Error : 文件不存在")


def ozipDecrypt():
    fileChooseWindow("解密ozip")
    if os.access(filename.get(), os.F_OK):
        ozip_decrypt.main("%s" % (filename.get()))
    else:
        showinfo("Error : 文件不存在")


def __ozipEncrypt():
    fileChooseWindow("加密ozip")
    if os.access(filename.get(), os.F_OK):
        with cartoon():
            runcmd("zip2ozip " + filename.get())
    else:
        showinfo("Error : 文件不存在")


def __unzipfile():
    if WorkDir:
        if os.access(WorkDir + "\\rom", os.F_OK):
            shutil.rmtree(WorkDir + "\\rom")
        fileChooseWindow("选择要解压的文件")
        if os.access(filename.get(), os.F_OK):
            showinfo("正在解压文件: " + filename.get())
            with cartoon():
                MyThread(utils.unzip_file(filename.get(), WorkDir + "\\rom"))
            showinfo("解压完成")
        else:
            showinfo("Error : 文件不存在")
    else:
        showinfo("Error : 请先选择工作目录")


def __zipcompressfile():
    showinfo("输入生成的文件名")
    userInputWindow()
    if WorkDir:
        showinfo("正在压缩 : " + inputvar.get() + ".zip")
        with cartoon():
            MyThread(utils.zip_file(inputvar.get() + ".zip", WorkDir + "\\rom"))
        showinfo("压缩完成")
    else:
        showinfo("Error : 请先选择工作目录")


def __xruncmd():
    cmd = USERCMD.get()
    runcmd("busybox ash -c \"%s\"" % cmd)
    usercmd.delete(0, 'end')


def patchvbmeta():
    fileChooseWindow("选择vbmeta文件")
    if os.access(filename.get(), os.F_OK):
        if vbpatch.checkMagic(filename.get()):
            flag = vbpatch.readVerifyFlag(filename.get())
            if flag == 0:
                showinfo("检测到AVB为打开状态，正在关闭...")
                vbpatch.disableAVB(filename.get())
            elif flag == 1:
                showinfo("检测到仅关闭了DM校验，正在关闭AVB...")
                vbpatch.disableAVB(filename.get())
            elif flag == 2:
                showinfo("检测AVB校验已关闭，正在开启...")
                vbpatch.restore(filename.get())
            else:
                showinfo("未知错误")
        else:
            showinfo("文件并非vbmeta文件")
    else:
        showinfo("文件不存在")


def patchfsconfig():
    dirChooseWindow("选择你要打包的目录")
    fileChooseWindow("选择fs_config文件")
    fspatch.main(directoryname.get(), filename.get())
    showinfo("修补完成")


def cz(func, *args):
    t = threading.Thread(target=func, args=args, daemon=True)
    t.start()


def __smartUnpack():
    with cartoon():
        fileChooseWindow("选择要智能解包的文件")
        if WorkDir:
            if os.access(filename.get(), os.F_OK):
                filetype = gettype(filename.get())
                showinfo("智能识别文件类型为 :  " + filetype)
                unpackdir = os.path.abspath(WorkDir + "/" + filetype)
                if filetype == "ozip":
                    showinfo("正在解密ozip")
                    ozip_decrypt.main(filename.get())
                    showinfo("解密完成")
                # list of create new folder
                if filetype == "ext" or filetype == "erofs":
                    dirname = os.path.basename(filename.get()).split(".")[0]

                    showinfo("在工作目录创建解包目录 : " + dirname)
                    if os.path.isdir(os.path.abspath(WorkDir) + "/" + dirname):
                        showinfo("文件夹存在，正在删除")
                        shutil.rmtree(os.path.abspath(WorkDir) + "/" + dirname)
                    utils.mkdir(os.path.abspath(WorkDir) + "/" + dirname)

                    if filetype == "ext":
                        showinfo("正在解包 : " + filename.get())
                        showinfo("使用imgextractor")
                        imgextractor.Extractor().main(filename.get(), WorkDir + os.sep + dirname + os.sep +
                                                      os.path.basename(filename.get()).split('.')[0])
                    if filetype == "erofs":
                        showinfo("正在解包 : " + filename.get())
                        showinfo("使用extract.erofs")
                        runcmd(f"extract.erofs.exe -i {filename.get()} -o {WorkDir + os.sep + dirname} -x")

                else:

                    for i in ["super", "dtbo", "boot", "payload"]:
                        if filetype == i:
                            showinfo("在工作目录创建解包目录 :  " + i)
                            if os.path.isdir(unpackdir):
                                showinfo("文件夹存在，正在删除")
                                shutil.rmtree(unpackdir)
                            utils.mkdir(unpackdir)
                            if i == "payload":
                                showinfo("正在解包payload")
                                t = threading.Thread(target=runcmd, args=[
                                    "payload-dumper-go.exe -o %s %s\\payload" % (WorkDir, filename.get())],
                                                     daemon=True)
                                t.start()
                                t.join()
                            if i == "boot":
                                showinfo("正在解包boot")
                                os.chdir(unpackdir)
                                runcmd("unpackimg.bat --local %s" % (filename.get()))
                                os.chdir(LOCALDIR)
                            if i == "dtbo":
                                showinfo("使用mkdtboimg解包")
                                runcmd("mkdtboimg.exe dump " + filename.get() + " -b " + unpackdir + "\\dtb")
                            if i == "super":
                                showinfo("使用 lpunpack 解锁")
                                runcmd("lpunpack " + filename.get() + " " + unpackdir)
                    if filetype == "sparse":
                        showinfo("文件类型为sparse, 使用simg2img转换为raw data")

                        utils.mkdir(WorkDir + "\\rawimg")
                        runcmd("simg2img " + filename.get() + " " + WorkDir + "\\rawimg\\" + os.path.basename(
                            filename.get()))
                        showinfo("sparse image 转换结束")
                    if filetype == "dat":
                        showinfo("检测到dat,使用sdat2img 且自动在文件所在目录选择transfer.list文件")
                        pname = os.path.basename(filename.get()).split(".")[0]
                        transferpath = os.path.abspath(
                            os.path.dirname(filename.get())) + os.sep + pname + ".transfer.list"
                        if os.access(transferpath, os.F_OK):
                            with cartoon():
                                sdat2img.main(transferpath, filename.get(), WorkDir + os.sep + pname + ".img")
                                showinfo("sdat已转换为img")
                        else:
                            showinfo("未能在dat文件所在目录找到对应的transfer.list文件")
                    if filetype == "br":
                        showinfo("检测到br格式，使用brotli解压")
                        pname = os.path.basename(filename.get()).replace(".br", "")
                        if os.access(filename.get(), os.F_OK):
                            with cartoon():
                                runcmd("brotli -d " + filename.get() + " " + WorkDir + os.sep + pname)
                            showinfo("已解压br文件")
                        else:
                            showinfo("震惊，文件怎么会不存在？")
                    if filetype == "vbmeta":
                        showinfo("检测到vbmtea,此文件不支持解包打包，请前往其他工具修改")
                    if filetype == "dtb":
                        showinfo("使用device tree compiler 转换反编译dtb --> dts")
                        dtname = os.path.basename(filename.get())
                        runcmd("dtc -q -I dtb -O dts " + filename.get() + " -o " + WorkDir + os.sep + dtname + ".dts")
                        showinfo("反编译dtb完成")
                    if filetype in ["zip", '7z']:
                        showinfo("请不要用这个工具去解包压缩文件，请使用7zip或者winrar")
                    if filetype == "Unknow":
                        showinfo("文件不受支持")
                # os.chdir(unpackdir)
            else:
                showinfo("文件不存在")
        else:
            showinfo("请先选择工作目录")


def repackboot():
    dirChooseWindow("选择你要打包的目录 based on android image kitchen")
    if os.path.isdir(directoryname.get()):
        os.chdir(directoryname.get())
        runcmd("repackimg.bat --local")
        os.chdir(LOCALDIR)
    else:
        showinfo("文件夹不存在")


def __repackextimage():
    if WorkDir:
        dirChooseWindow("选择你要打包的目录 例如 : .\\NH4_test\\vendor\\vendor")
        # Audo choose fs_config
        showinfo("自动搜寻 fs_config")
        isFsConfig = find_fs_con(directoryname.get())
        isFileContexts = find_fs_con(directoryname.get(), t=1)
        if isFsConfig:
            showinfo("自动搜寻 fs_config 完成: " + isFsConfig)
            fsconfig_path = isFsConfig
        if isFileContexts:
            showinfo("自动搜寻 file_contexts 完成" + isFileContexts)
            filecontexts_path = isFileContexts
        else:
            showinfo("自动搜寻 fs_config 失败，请手动选择")
            fileChooseWindow("选择你要打包目录的fs_config文件")
            fsconfig_path = filename.get()
        if os.path.isdir(directoryname.get()):
            showinfo("修补fs_config文件")
            fspatch.main(directoryname.get(), fsconfig_path)
            cmd = "busybox ash -c \""
            MUTIIMGSIZE = 1.2 if os.path.basename(directoryname.get()).find("odm") != -1 else 1.07
            if UICONFIG['AUTOMUTIIMGSIZE']:
                EXTIMGSIZE = int(utils.getdirsize(directoryname.get()) * MUTIIMGSIZE)
            else:
                EXTIMGSIZE = UICONFIG['MODIFIEDIMGSIZE']
            cmd += "MKE2FS_CONFIG=bin/mke2fs.conf E2FSPROGS_FAKE_TIME=1230768000 mke2fs.exe "
            cmd += "-O %s " % (UICONFIG['EXTFUEATURE'])
            cmd += "-L %s " % (os.path.basename(directoryname.get()))
            cmd += "-I 256 "
            cmd += "-M /%s -m 0 " % (os.path.basename(directoryname.get()))  # mount point
            cmd += "-t %s " % (UICONFIG['EXTREPACKTYPE'])
            cmd += "-b %s " % (UICONFIG['EXTBLOCKSIZE'])
            cmd += "%s/output/%s.img " % (WorkDir, os.path.basename(directoryname.get()))
            cmd += "%s\"" % (int(EXTIMGSIZE / 4096))
            showinfo("尝试创建目录output")
            utils.mkdir(WorkDir + os.sep + "output")
            showinfo("开始打包EXT镜像")
            with cartoon():
                showinfo(cmd)
                runcmd(cmd)
                cmd = f"e2fsdroid.exe -e -T 1230768000 -C {fsconfig_path} -S {filecontexts_path} -f {directoryname.get()} -a /{os.path.basename(directoryname.get())} {WorkDir}/output/{os.path.basename(directoryname.get())}.img"
                runcmd(cmd)
                showinfo("打包结束")
    else:
        showinfo("请先选择工作目录")


def find_fs_con(path, t=0):
    parent_path = os.path.dirname(path)
    current_path = os.path.basename(parent_path)
    if t == 0:
        f_ = "_fs_config"
    else:
        f_ = "_file_contexts"
    if os.path.exists(os.path.join(parent_path, 'config', current_path + f_)):
        return str(os.path.join(parent_path, 'config', current_path + f_))
    else:
        return ''


def __repackerofsimage():
    if WorkDir:
        dirChooseWindow("选择你要打包的目录 例如 : .\\NH4_test\\vendor\\vendor")
        # Audo choose fs_config
        showinfo("自动搜寻 fs_config")
        is_fs_config = find_fs_con(directoryname.get())
        is_file_contexts = find_fs_con(directoryname.get(), t=1)
        if is_fs_config:
            showinfo("自动搜寻 fs_config 完成: " + is_fs_config)
            fsconfig_path = is_fs_config
        else:
            showinfo("自动搜寻 fs_config 失败，请手动选择")
            fileChooseWindow("选择你要打包目录的fs_config文件")
            fsconfig_path = filename.get()
        if is_file_contexts:
            showinfo("自动搜寻 file_contexts 完成" + is_file_contexts)
            filecontexts_path = is_file_contexts
        with cartoon():
            fspatch.main(directoryname.get(), fsconfig_path)
            cmd = "mkfs.erofs.exe %s/output/%s.img %s -z\"%s\" -T\"1230768000\" --mount-point=/%s --fs-config-file=%s --file-contexts=%s" % (
                WorkDir, os.path.basename(directoryname.get()), directoryname.get().replace("\\", "/"),
                UICONFIG['EROFSCOMPRESSOR'], os.path.basename(directoryname.get()), fsconfig_path, filecontexts_path)
            print(cmd)
            runcmd(cmd)
    else:
        showinfo("请先选择工作目录")


def __repackDTBO():
    if WorkDir:
        dirChooseWindow("选择dtbo文件夹")
        if not os.path.isdir(WorkDir + os.sep + "output"):
            utils.mkdir(WorkDir + os.sep + "output")
        cmd = "mkdtboimg.exe create %s\\output\\dtbo.img " % WorkDir
        for i in range(len(glob.glob(directoryname.get() + os.sep + "*"))):
            cmd += "%s\\dtb.%s " % (directoryname.get(), i)
        runcmd(cmd)
        showinfo("打包结束")
    else:
        showinfo("请先选择工作目录")


def __repackSparseImage():
    if WorkDir:
        # 只将 EXT 转为 SIMG 而不是重新打包一次
        fileChooseWindow("选择要转换为 SIMG 的 IMG 文件")
        imgFilePath = filename.get()
        if not os.path.exists(imgFilePath):
            showinfo("文件不存在: " + imgFilePath)
        elif gettype(imgFilePath) != "ext":
            showinfo("选中的文件并非 EXT 镜像，请先转换")
            return
        else:
            showinfo("开始转换")
            with cartoon():
                cmd = "%s %s %s/output/%s_sparse.img" % (
                    UICONFIG['SPARSETOOL'], imgFilePath, WorkDir, os.path.basename(directoryname.get()))
                runcmd(cmd)
                showinfo("转换结束")
    else:
        showinfo("请先选择工作目录")


def __compressToBr():
    if WorkDir:
        fileChooseWindow("选择要转换为 BR 的 DAT 文件")
        imgFilePath = filename.get()
        if not os.path.exists(imgFilePath):
            showinfo("文件不存在: " + imgFilePath)
        elif gettype(imgFilePath) != "dat":
            showinfo("选中的文件并非 DAT，请先转换")
            return
        else:
            showinfo("开始转换")
            with cartoon():
                th = threading.Thread(target=runcmd("brotli.exe -q 6 " + imgFilePath))
                th.start()
            showinfo("转换完毕，脱出到相同文件夹")
    else:
        showinfo("请先选择工作目录")


def __repackDat():
    if WorkDir:
        # TO-DO: 打包后自动定位转换好的 simg   20220331
        # TO-DO: 自动识别Android版本   20220331
        fileChooseWindow("选择要转换为 DAT 的 IMG 文件")
        imgFilePath = filename.get()
        if not os.path.exists(imgFilePath):
            showinfo("文件不存在: " + imgFilePath)
        elif gettype(imgFilePath) != "sparse":
            showinfo("选中的文件并非 SPARSE，请先转换")
            return
        else:
            showinfo("警告: 只接受大版本输入，例如 7.1.2 请直接输入 7.1！")
            userInputWindow("输入Android版本")
            inputVersion = float(inputvar.get())
            if inputVersion == 5.0:  # Android 5
                showinfo("已选择: Android 5.0")
                currentVersion = 1
            elif inputVersion == 5.1:  # Android 5.1
                showinfo("已选择: Android 5.1")
                currentVersion = 2
            elif 6.0 <= inputVersion < 7.0:  # Android 6.X
                showinfo("已选择: Android 6.X")
                currentVersion = 3
            elif inputVersion >= 7.0:  # Android 7.0+
                showinfo("已选择: Android 7.X+")
                currentVersion = 4
            else:
                currentVersion = 0
            # PREFIX
            inputvar.set("")
            showinfo("提示: 输入分区名 (例如 system、vendor、odm)")
            userInputWindow("输入分区名")
            partitionName = inputvar.get()
            if currentVersion == 0:
                showinfo("Android 版本输入错误，请查看提示重新输入！")
                return
            elif partitionName == 0 or partitionName == "":
                showinfo("分区名输入错误，请查看提示重新输入！")
                return
            # img2sdat <image file> <output dir> <version|1=5.0|2=5.1|3=6.0|4=7.0+> <prefix>
            showinfo("开始转换")
            with cartoon():
                threading.Thread(
                    target=img2sdat.main(imgFilePath, WorkDir + "/output/", currentVersion, partitionName)).start()
            showinfo("转换完毕，脱出到工作目录下 output 文件夹")
    else:
        showinfo("请先选择工作目录")


def __repackdtb():
    if WorkDir:
        fileChooseWindow("选择dts文件，输出到dtb文件夹")
        if os.access(filename.get(), os.F_OK):
            if not os.path.isdir(WorkDir + os.sep + "dtb"):
                utils.mkdir(WorkDir + os.sep + "dtb")
            with cartoon():
                runcmd("dtc -I dts -O dtb %s -o %s\\dtb\\%s.dtb" % (
                    filename.get(), WorkDir, os.path.basename(filename.get()).replace(".dts", ".dtb")))
            showinfo("编译为dtb完成")
        else:
            showinfo("文件不存在")
    else:
        showinfo("请先选择工作目录")


def __repackSuper():
    if WorkDir:
        packtype = tk.StringVar()
        packsize = tk.StringVar()
        packsize.set("9126805504")
        sparse = tk.IntVar()
        showinfo("打包super镜像")
        w = tk.Toplevel()
        cur_width = 400
        cur_hight = 180
        # 获取屏幕宽度和高度
        scn_w, scn_h = root.maxsize()
        # 计算中心坐标
        cen_x = (scn_w - cur_width) / 2
        cen_y = (scn_h - cur_hight) / 2
        # 设置窗口初始大小和位置
        size_xy = '%dx%d+%d+%d' % (cur_width, cur_hight, cen_x, cen_y)
        w.geometry(size_xy)
        w.resizable(False, False)  # 设置最大化窗口不可用
        w.title("选择你的打包的类型：")
        l1 = ttk.LabelFrame(w, text="选择打包类型", labelanchor="nw", relief=GROOVE, borderwidth=1)
        ttk.Radiobutton(l1, variable=packtype, value='VAB', text='VAB').pack(side=LEFT, expand=YES, padx=5)
        ttk.Radiobutton(l1, variable=packtype, value='AB', text='AB').pack(side=LEFT, expand=YES, padx=5)
        ttk.Radiobutton(l1, variable=packtype, value='A-only', text='A-only').pack(side=LEFT, expand=YES, padx=5)
        l1.pack(side=TOP, ipadx=10, ipady=10)
        ttk.Label(w, text="请输入super分区大小(字节数,常见9126805504)").pack(side=TOP)
        ttk.Entry(w, textvariable=packsize, width=50).pack(side=TOP, padx=10, pady=10, expand=YES, fill=BOTH)
        ttk.Checkbutton(w, text="Sparse", variable=sparse).pack(side=TOP, padx=10, pady=10)
        w.wait_window()
        if packtype.get() == "":
            showinfo("没有获取到选项")
        else:
            dirChooseWindow("选择super分区镜像文件所在目录")
            superdir = directoryname.get()
            showinfo("super分区镜像所在目录：" + superdir)
            if sparse.get():
                showinfo("启用sparse参数")
            cmd = "lpmake "
            showinfo("打包类型 ： " + packtype.get())
            cmd += "--metadata-size 65536 --super-name super "
            if packtype.get() == 'VAB':
                cmd += "--virtual-ab "
            if sparse.get():
                cmd += "--sparse "
            cmd += "--metadata-slots 2 "
            cmd += "--device super:%s " % (packsize.get())
            showinfo(cmd)

    else:
        showinfo("请先选择工作目录")


if __name__ == '__main__':
    myStdout()
    # 在中心打开主窗口
    screenwidth = root.winfo_screenwidth()  # 屏幕宽度
    screenheight = root.winfo_screenheight()  # 屏幕高度
    root.geometry(
        '{}x{}+{}+{}'.format(width, height, int((screenwidth - width) / 2), int((screenheight - height) / 2)))  # 大小以及位置

    menuBar = tk.Menu(root)
    root.config(menu=menuBar)
    menu1 = tk.Menu(menuBar, tearoff=False)
    menuItem = ["关于", "退出"]
    for item in menuItem:
        if item == "关于":
            menu1.add_command(label=item, command=about)
        if item == "退出":
            menu1.add_command(label=item, command=sys.exit)
    menuBar.add_cascade(label="菜单", menu=menu1)
    menu2 = tk.Menu(menuBar, tearoff=False)
    menuItem = ["cosmo", "flatly", "journal", "literal", "lumen", "minty", "pulse", "sandstone", "united", "yeti",
                "cyborg", "darkly", "solar", "vapor", "superhero"]
    for item in menuItem:
        menu2.add_command(label=item, command=lambda n=item: change_theme(n))
    menuBar.add_cascade(label="主题", menu=menu2)

    # define labels
    frame = ttk.LabelFrame(root, text="NH4 Rom Tool", labelanchor="nw", relief=GROOVE, borderwidth=1)
    frame1 = ttk.LabelFrame(frame, text="功能区", labelanchor="nw", relief=SUNKEN, borderwidth=1)
    frame2 = ttk.LabelFrame(frame, text="信息反馈", labelanchor="nw", relief=SUNKEN, borderwidth=1)

    # Notebook
    tabControl = ttk.Notebook(frame1)
    # tab
    tab1 = ttk.Frame(tabControl)
    tab2 = ttk.Frame(tabControl)
    tab3 = ttk.Frame(tabControl)
    tab33 = ScrolledFrame(tab3, autohide=True, width=220)
    tab4 = ttk.Frame(tabControl)
    # tab44 = ScrolledFrame(tab4, autohide=True, width=220)

    tabControl.add(tab1, text="工作目录")
    tabControl.add(tab2, text="打包解包")
    tabControl.add(tab3, text="其他工具")
    # tabControl.add(tab4, text="设置")

    tab33.pack(side=LEFT, expand=YES, fill=BOTH)

    # Treeview  use to list work dir
    tab11 = ttk.Frame(tab1)

    columns = ["Workdir"]
    table = ttk.Treeview(
        tab11,  # 父容器
        height=10,  # 表格显示的行数,height行
        columns=columns,  # 显示的列
        show='headings',  # 隐藏首列
    )
    table.column('Workdir', width=100, anchor='center')
    table.heading('Workdir', text='工作目录')
    table.pack(side=TOP, fill=BOTH, expand=YES)
    table.bind('<ButtonRelease-1>', lambda *x_: SelectWorkDir())
    getWorkDir()

    # Buttons under Treeview
    tab12 = ttk.Frame(tab1)
    ttk.Button(tab12, text='确认目录', width=10, command=ConfirmWorkDir, style='primiary.Outline.TButton').grid(row=0,
                                                                                                                column=0,
                                                                                                                padx=10,
                                                                                                                pady=8)
    ttk.Button(tab12, text='删除目录', width=10, command=rmWorkDir, style='primiary.Outline.TButton').grid(row=0,
                                                                                                           column=1,
                                                                                                           padx=10,
                                                                                                           pady=8)
    ttk.Button(tab12, text='新建目录', width=10, command=mkWorkdir, style='primiary.Outline.TButton').grid(row=1,
                                                                                                           column=0,
                                                                                                           padx=10,
                                                                                                           pady=8)
    ttk.Button(tab12, text='刷新目录', width=10, command=getWorkDir, style='primiary.Outline.TButton').grid(row=1,
                                                                                                            column=1,
                                                                                                            padx=10,
                                                                                                            pady=8)
    ttk.Button(tab12, text='清理目录', width=10, command=clearWorkDir, style='primiary.Outline.TButton').grid(row=2,
                                                                                                              column=0,
                                                                                                              padx=10,
                                                                                                              pady=8)

    # Pack Buttons
    tab12.pack(side=BOTTOM, fill=BOTH, expand=YES, anchor=CENTER)

    # pack Notebook
    tabControl.pack(fill=BOTH, expand=YES)
    tab11.pack(side=TOP, fill=BOTH, expand=YES)

    # tab21 // Unpack
    tab21 = ttk.LabelFrame(tab2, text="解包", labelanchor="nw", relief=SUNKEN, borderwidth=1)
    ttk.Button(tab21, text='解压', width=10, command=lambda: cz(__unzipfile), style='primiary.Outline.TButton').grid(
        row=0, column=0,
        padx=10,
        pady=8)
    ttk.Button(tab21, text='万能解包', width=10, command=lambda: cz(__smartUnpack),
               style='primiary.Outline.TButton').grid(row=0,
                                                      column=1,
                                                      padx=10,
                                                      pady=8)

    # tab22 // Repack
    tab22 = ttk.LabelFrame(tab2, text="打包", labelanchor="nw", relief=SUNKEN, borderwidth=1)
    ttk.Button(tab22, text='压缩', width=10, command=lambda: cz(__zipcompressfile),
               style='primiary.Outline.TButton').grid(row=0,
                                                      column=0,
                                                      padx=10,
                                                      pady=8)
    ttk.Button(tab22, text='BOOT', width=10, command=repackboot, style='primiary.Outline.TButton').grid(row=0, column=1,
                                                                                                        padx=10,
                                                                                                        pady=8)
    ttk.Button(tab22, text='EXT', width=10, command=lambda: cz(__repackextimage),
               style='primiary.Outline.TButton').grid(row=1,
                                                      column=0,
                                                      padx=10,
                                                      pady=8)
    ttk.Button(tab22, text='EROFS', width=10, command=lambda: cz(__repackerofsimage),
               style='primiary.Outline.TButton').grid(row=1,
                                                      column=1,
                                                      padx=10,
                                                      pady=8)
    ttk.Button(tab22, text='DTS2DTB', width=10, command=lambda: cz(__repackdtb), style='primiary.Outline.TButton').grid(
        row=2,
        column=0,
        padx=10,
        pady=8)
    ttk.Button(tab22, text='DTBO', width=10, command=lambda: cz(__repackDTBO), style='primiary.Outline.TButton').grid(
        row=2, column=1,
        padx=10,
        pady=8)
    ttk.Button(tab22, text='SUPER', width=10, command=lambda: cz(__repackSuper), style='primiary.Outline.TButton').grid(
        row=3,
        column=0,
        padx=10,
        pady=8)
    ttk.Button(tab22, text='EXT->SIMG', width=10, command=lambda: cz(__repackSparseImage),
               style='primiary.Outline.TButton').grid(
        row=3, column=1, padx=10, pady=8)
    ttk.Button(tab22, text='IMG->DAT', width=10, command=lambda: cz(__repackDat),
               style='primiary.Outline.TButton').grid(row=4,
                                                      column=0,
                                                      padx=10,
                                                      pady=8)
    ttk.Button(tab22, text='DAT->BR', width=10, command=lambda: cz(__compressToBr),
               style='primiary.Outline.TButton').grid(row=4,
                                                      column=1,
                                                      padx=10,
                                                      pady=8)

    # pack tab2
    tab21.pack(side=TOP, fill=BOTH, expand=NO)
    tab22.pack(side=TOP, fill=BOTH, expand=YES)

    # tab3
    ttk.Button(tab33, text='检测文件格式', width=10, command=detectFileType, bootstyle="link").pack(side=TOP, expand=NO,
                                                                                                    fill=X, padx=8)
    ttk.Separator(tab33).pack(side=TOP, expand=NO, fill=X, padx=8)
    ttk.Button(tab33, text='OZIP 解密', width=10, command=ozipDecrypt, bootstyle="link").pack(side=TOP, expand=NO,
                                                                                              fill=X, padx=8)
    ttk.Separator(tab33).pack(side=TOP, expand=NO, fill=X, padx=8)
    ttk.Button(tab33, text='OZIP 加密', width=10, command=lambda: cz(__ozipEncrypt), bootstyle="link").pack(side=TOP,
                                                                                                            expand=NO,
                                                                                                            fill=X,
                                                                                                            padx=8)
    ttk.Separator(tab33).pack(side=TOP, expand=NO, fill=X, padx=8)
    ttk.Separator(tab33).pack(side=TOP, expand=NO, fill=X, padx=8)

    s = ttk.Style()
    s.configure('Button.parsePayload', font=('Helvetica', '5'))
    ttk.Separator(tab33).pack(side=TOP, expand=NO, fill=X, padx=8)
    ttk.Button(tab33, text='关闭 VBMETA 校验', width=10, command=patchvbmeta, bootstyle="link").pack(side=TOP,
                                                                                                     expand=NO, fill=X,
                                                                                                     padx=8)
    ttk.Separator(tab33).pack(side=TOP, expand=NO, fill=X, padx=8)
    ttk.Button(tab33, text='修补 FS_CONFIG 文件', width=10, command=patchfsconfig, bootstyle="link").pack(side=TOP,
                                                                                                          expand=NO,
                                                                                                          fill=X,
                                                                                                          padx=8)
    ttk.Separator(tab33).pack(side=TOP, expand=NO, fill=X, padx=8)

    # ScrolledText
    text = scrolledtext.ScrolledText(frame2, width=180, height=18, font=TEXTFONT, relief=SOLID)  # 信息展示 文本框
    text.pack(side=TOP, expand=YES, fill=BOTH, padx=4, pady=2)
    # table.bind('<ButtonPress-1>', showinfo("请点击确认目录"))
    frame22 = ttk.LabelFrame(frame2, text="输入自定义命令", labelanchor="nw", relief=SUNKEN, borderwidth=1)
    usercmd = ttk.Entry(frame22, textvariable=USERCMD, width=25)
    usercmd.pack(side=LEFT, expand=YES, fill=X, padx=2, pady=2)
    usercmd.bind('<Return>', lambda *x: __xruncmd)
    ttk.Button(frame22, text='运行', command=__xruncmd, style='primary.Outline.TButton').pack(side=LEFT, expand=NO,
                                                                                              fill=X, padx=2,
                                                                                              pady=2)
    # pack frames
    frame.pack(side=TOP, expand=YES, fill=BOTH, padx=2, pady=2)
    frame1.pack(side=LEFT, expand=YES, fill=BOTH, padx=5, pady=2)
    frame2.pack(side=LEFT, expand=YES, fill=BOTH, padx=5, pady=2)
    frame22.pack(side=TOP, expand=NO, fill=BOTH, padx=5, pady=2)

    # bottom labels
    framebotm = ttk.Frame(root, relief=FLAT, borderwidth=0)
    ttk.Button(framebotm, text='清理信息', command=cleaninfo, style='secondary.TButton').pack(side=RIGHT, expand=NO,
                                                                                              padx=5, pady=0)
    # Status bar

    statusbar = ttk.Label(framebotm, relief='flat', anchor=tk.E, bootstyle="info")
    statusbar.pack(side=RIGHT, fill=tk.X, ipadx=12)
    statusbar['image'] = DEFAULTSTATUS


    def SHOWSHIJU():
        shiju = utils.getShiju()
        shiju_font = ('微软雅黑', 12)
        shijuLable = ttk.Label(framebotm, text="%s —— %s  《%s》" % (shiju['content'], shiju['author'], shiju['origin']),
                               font=shiju_font)
        shijuLable.pack(side=LEFT, padx=8)


    cz(SHOWSHIJU)
    framebotm.pack(side=BOTTOM, expand=NO, fill=X, padx=8, pady=12)
    root.mainloop()
