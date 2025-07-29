FROM ubuntu:20.04

LABEL maintainer=qixiaoqi

# 将 docker 默认 shell 由 sh 改为 bash
SHELL ["/bin/bash", "-c"]

# 查看构建使用的用户 root
RUN whoami

WORKDIR /app

# 通常用于某些脚本或工具检测是否运行在 Docker 容器中
ENV container=docker
# 安装软件时跳过交互式提示（如确认对话框）。但它的生效时机是在 RUN apt-get install 执行时
ENV DEBIAN_FRONTEND=noninteractive

# 清理 不再需要的依赖包 缓存 以减小镜像体积
ENV CLEAN_CMD "apt-get -y autoremove && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*"

# py库 pynput 构建依赖
RUN apt-get update && apt install -y \
  # 包含编译 C/C++ 程序所需的基础工具
  build-essential \
  # 提供 Linux 输入设备（如键盘、鼠标、触摸板等）的抽象层开发库
  libevdev-dev \
  # 安装与当前运行的内核版本匹配的内核头文件和开发包。
  linux-headers-generic \
  && eval $CLEAN_CMD

# 默认情况下，apt-get install 会安装软件包​​必需的依赖项（Depends）​​，以及​​推荐的依赖项（Recommends）​​。
# 使用 --no-install-recommends 后，​​只会安装必需的依赖项​​，而不会安装推荐的依赖项。
RUN apt-get update && apt-get install -y --no-install-recommends \
  sudo \
  passwd \
  # 类似 wget 的命令行工具，但更灵活，支持多种协议（HTTP/HTTPS/FTP/SCP 等），常用于 API 调用或脚本中下载资源
  curl \
  # 强大的命令行文本编辑器
  vim \
  git \
  # 用于配置系统语言和区域设置（如日期格式、字符编码），安装后需运行 locale-gen 生成具体语言环境
  locales \
  # 包包含了世界各地的时区数据，并允许系统配置本地时间
  tzdata \
  # pyperclip 需要额外的工具如 xclip 或 xsel 来访问系统的剪贴板
  xclip \
  && eval $CLEAN_CMD

# 设置时区
ENV TZ=Asia/Shanghai
RUN ln -fs /usr/share/zoneinfo/$TZ /etc/localtime \
  && dpkg-reconfigure -f noninteractive tzdata

# 设置系统语言为中文
RUN echo "zh_CN.UTF-8 UTF-8" >> /etc/locale.gen && \
  locale-gen && \
  update-locale LANG=zh_CN.UTF-8
ENV LANG zh_CN.UTF-8
ENV LANGUAGE=zh_CN:zh
ENV LC_ALL=zh_CN.UTF-8

# unminimize 是 Ubuntu 提供的一个工具，用于 ​​恢复最小化安装中被移除的组件（如 man 手册页、终端、登录界面、桌面环境等）
# yes 是一个 Linux 命令，它会 ​​无限输出 y（即 "yes"） 自动回答 unminimize 的所有确认提示为 "yes"​​
RUN yes | unminimize

# 安装 GNOME 桌面环境
# 如果你想要更纯净的 GNOME，使用: "apt-get install -y --no-install-recommends gnome-session gnome-terminal"
# ubuntu-desktop 包含 gnome-session （会话管理器​​，负责启动和管理 GNOME 桌面环境（包括窗口管理、任务栏、通知等）。） gnome-terminal （终端模拟器​​，提供命令行界面）
RUN apt-get update && apt-get install -y \
  # GNOME 依赖 ubuntu-desktop 元包
  ubuntu-desktop \
  # 输入法配置工具​​，用于配置 Fcitx（一个流行的输入法框架，支持中文、日文等输入法）
  fcitx-config-gtk \
  # GNOME 桌面定制工具​​，提供高级设置选项 类似 Windows 的"控制面板"
  gnome-tweaks \
  # 系统资源监控工具​​ CPU、内存、磁盘、网络使用情况
  gnome-usage \
  # [禁用欢迎屏幕](https://askubuntu.com/q/1028822/206608)
  && apt-get purge -y --autoremove gnome-initial-setup \
  && eval $CLEAN_CMD

# 禁用 ubuntu 更新通知 [参考](https://askubuntu.com/questions/1435766/how-to-make-ubuntu-stop-offering-to-upgrade-from-20-04-5-to-22-04-1)
RUN sed -i 's/lts$/never/g' /etc/update-manager/release-upgrades

# 安装 systemd 服务管理器 管理服务、日志（journald）、用户会话
RUN apt-get update && apt-get install -y \
  # systemd 依赖 dbus​​
  # dbus（Desktop Bus）​​ 是一个 ​​进程间通信（IPC）系统​​，用于 Linux 桌面环境和系统服务之间的消息传递。它允许不同的应用程序和服务（如 GNOME、KDE、systemd、NetworkManager）相互通信
  dbus \
  # D-Bus 的 X11 扩展，用于进程间通信（IPC），支持图形界面和桌面环境的消息传递（如通知、剪贴板共享）
  dbus-x11 \
  # 用于支持 GUI 应用（如 GNOME）或需要 systemd 的服务
  systemd \
  # 修复 udevadm 的兼容性问题（因为容器没有完整的 udev 系统）
  && dpkg-divert --local --rename --add /sbin/udevadm && ln -s /bin/true /sbin/udevadm \
  && eval $CLEAN_CMD

# 移除不必要的系统目标服务 以减少容器启动时的资源消耗和潜在问题
RUN rm -f \
  # 容器没有完整的 udev 系统，移除可减少资源占用，但可能影响某些设备驱动加载。
  /lib/systemd/system/sockets.target.wants/*udev* \
  # 容器使用 systemd，不需要 initctl。
  /lib/systemd/system/sockets.target.wants/*initctl* \
  # 容器通常不需要复杂的临时文件管理。
  /lib/systemd/system/sysinit.target.wants/systemd-tmpfiles-setup* \
  # 容器不需要审计功能。
  /lib/systemd/system/systemd-update-utmp* \
  # 容器通常使用宿主机的 DNS 或直接配置 /etc/resolv.conf。
  /lib/systemd/system/systemd-resolved.service

# 挂载必要的文件系统
VOLUME ["/sys/fs/cgroup"]
# STOPSIGNAL 是 Docker 的一个指令，用于指定 ​​容器停止时发送的信号​​（类似 kill 命令的信号）。
# SIGRTMIN+3 是 systemd 的"友好停止"信号，确保：systemd 先停止所有子服务（如 nginx、mysql）。 再停止 systemd 自身。
STOPSIGNAL SIGRTMIN+3
# 确保容器以 --privileged 或 --cap-add=SYS_ADMIN 运行（因为 systemd 需要特权）
CMD ["/sbin/init"]

# 创建非特权用户 vnc不建议以root用户身份运行图形界面
# 创建一个用户 -U 创建了对应的主组 -m 自动创建home目录（默认是/home/<name>） -s 默认shell是bash
ENV WORK_USER work
ENV WORK_HOME /home/$WORK_USER
RUN useradd -Ums /bin/bash $WORK_USER \
  # 配置用户无需密码即可使用 sudo 的权限 ALL=(ALL) 可以在任何主机上以任何用户身份执行命令 NOPASSWD: ALL 执行所有命令时不需要输入密码
  && echo "${WORK_USER} ALL=(ALL) NOPASSWD: ALL" > "/etc/sudoers.d/${WORK_USER}" \
  # 只有 root 用户可以读写该文件，其他用户不可访问 防止普通用户篡改 sudo 权限
  && chmod 440 "/etc/sudoers.d/${WORK_USER}"

# vnc 链接密码
ENV VNC_PASSWD 123456
# vnc 启动需要这个环境变量
# ENV USER $(whoami)
# 安装 TigerVNC服务器
# [选择 tigervnc 是因为XKB扩展支持](https://github.com/i3/i3/issues/1983)
RUN apt-get update && apt-get install -y \
  # 是 TigerVNC 的独立服务器，用于提供 VNC 服务
  tigervnc-standalone-server \
  # TigerVNC 的公共文件和配置文件
  tigervnc-common \
  # 这个组件允许你在 TigerVNC 会话中进行屏幕截图和屏幕录制
  tigervnc-scraping-server \
  # # 是客户端软件，用于连接到 VNC 服务器
  # tigervnc-viewer \
  # 增强了 TigerVNC 与 Xorg 桌面环境的兼容性和功能性
  tigervnc-xorg-extension \
  # VNC 剪贴板桥接工具
  autocutsel \
  && eval $CLEAN_CMD

# 配置 vnc 到 systemctl
COPY tigervnc.work@.service /etc/systemd/system/tigervnc@.service
# COPY tigervnc.root@.service /etc/systemd/system/tigervnc@.service
ARG VNC_DISPLAY_NUM=1
# 开机自启
RUN systemctl enable tigervnc@:${VNC_DISPLAY_NUM}
# pyautogui依赖于mouseinfo，而mouseinfo需要访问X Window System的显示服务器 Chrome也会用到
# 用于指定图形界面显示设备的参数 对于 VNC 端口 :1 => 5901
ENV DISPLAY :${VNC_DISPLAY_NUM}
EXPOSE 5901

ENV VNC_HOME $WORK_HOME/.vnc
# ENV VNC_HOME /root/.vnc

# 配置 VNC 密码 & 启动脚本 xstartup
COPY xstartup $VNC_HOME/xstartup
RUN mkdir -p $VNC_HOME \
  && echo $VNC_PASSWD | vncpasswd -f > $VNC_HOME/passwd \
  && chmod 600 $VNC_HOME/passwd \
  # 必须确保整个目录都是 用户权限
  && chown -R $WORK_USER:$WORK_USER $WORK_HOME

# 安装 noVNC
RUN git clone https://github.com/novnc/noVNC.git
COPY novnc.service /etc/systemd/system/novnc.service
RUN systemctl enable novnc
EXPOSE 6081

# 安装 Chrome
RUN apt-get update && apt-get install -y \
  # 用于处理 GPG 签名，验证 Chrome 安装包来源
  gnupg \
  # 允许 APT 使用 HTTPS 下载仓库（Chrome 的 deb 源是 HTTPS 的）
  apt-transport-https \
  # 用于验证 HTTPS 证书
  ca-certificates \
  && eval $CLEAN_CMD
# 添加 Google Chrome 的官方 GPG key 和仓库源
RUN curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
  && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get remove -y firefox && apt-get update && apt-get install -y google-chrome-stable \
  && eval $CLEAN_CMD
# 禁用欢迎页
# --no-first-run 跳过欢迎页
# --no-default-browser-check 跳过“是否设置为默认浏览器”的提示
# 处理 Chrome 崩溃
# --disable-gpu 强制 Chrome 不使用 GPU，改为软件渲染，常用于没有 GPU 或虚拟机环境。
# --disable-dev-shm-usage 在 Docker 或某些容器环境中，/dev/shm 空间太小（默认只有 64MB），会导致 Chrome 崩溃，此参数会让 Chrome 使用普通的临时文件代替。
# 修改 图标启动 默认 1920,1080
RUN sed -i 's/^Exec=\/usr\/bin\/google-chrome-stable %U/Exec=\/usr\/bin\/google-chrome-stable --no-first-run --no-default-browser-check --disable-gpu --disable-dev-shm-usage --window-size=1920,1080 %U/' /usr/share/applications/google-chrome.desktop
# 禁用 chrome 打开后 上方 设置默认浏览器提示
RUN mkdir -p $WORK_HOME/.config/google-chrome/Default/ \
  && echo "{\"browser\":{\"default_browser_infobar_last_declined\":\"13393862784810938\"}}" > $WORK_HOME/.config/google-chrome/Default/Preferences \
  && chown -R $WORK_USER:$WORK_USER $WORK_HOME

# 安装 uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
# uv python install 镜像
# ENV UV_PYTHON_INSTALL_MIRROR https://mirror.nju.edu.cn/github-release/indygreg/python-build-standalone/
# uv add 私有源
ENV UV_DEFAULT_INDEX https://pypi.tuna.tsinghua.edu.cn/simple
# share https://docs.astral.sh/uv/reference/environment/#uv_python_install_dir
ENV UV_PYTHON_INSTALL_DIR /usr/local/share/uv
ENV PATH $PATH:/usr/local/bin
# 主要是移动 bin
RUN mv $HOME/.local/bin/* /usr/local/bin \
  # root 用户 用 PATH
  && sed -i '/. "$HOME\/.local\/bin\/env"/d' ~/.bashrc \
  # 确保 uv
  && source /usr/local/bin/env \
  && uv -V \
  && uv python install 3.11

# npm 私有源
ENV NPM_REGISTRY_URL https://registry.npmmirror.com/
# 设置 npm 私有源（nrm 不会修改 yarn 的源 手动修改）
ENV SET_NPM_REGISTRY_URL_CMD "npm config set registry $NPM_REGISTRY_URL && yarn config set registry $NPM_REGISTRY_URL && pnpm config set registry $NPM_REGISTRY_URL"

# 安装 nvm 还是会装到 ~/.nvm
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
# 指定公共的安装目录
ENV NVM_HOME /usr/local/.nvm
RUN mv ~/.nvm $NVM_HOME \
  # root 用户
  && sed -i 's/$HOME\/.nvm/$NVM_HOME/g' ~/.bashrc \
  # nvm 并写入work用户
  && echo 'export NVM_DIR="$NVM_HOME"' >> $WORK_HOME/.bashrc \
  && echo '[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm' >> $WORK_HOME/.bashrc \
  && echo '[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion' >> $WORK_HOME/.bashrc
# nvm install 镜像
ENV NVM_NODEJS_ORG_MIRROR https://npmmirror.com/mirrors/node
# 确保 nvm
ENV SET_NVM_CMD 'export NVM_DIR="$NVM_HOME"; [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"; [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"'
RUN eval $SET_NVM_CMD \
  && echo "nvm version $(nvm -v)" \
  && nvm install v22.14.0 && npm i yarn pnpm pm2 -g --registry "$NPM_REGISTRY_URL" && eval $SET_NPM_REGISTRY_URL_CMD \
  && nvm alias default v22.14.0

# Dockerfile 中的 ENV 只会影响容器主进程及其派生的子进程，不会自动传播到 GUI 登录的用户 shell 中。要让 GUI 用户也看到这些变量，你需要手动将它们写入 .bashrc、.profile 或 /etc/environment。
RUN echo "NVM_HOME=${NVM_HOME}" >> /etc/environment \
  && echo "SET_NVM_CMD=${SET_NVM_CMD}" >> /etc/environment \
  && echo "SET_NPM_REGISTRY_URL_CMD=${SET_NPM_REGISTRY_URL_CMD}" >> /etc/environment \
  && echo "UV_DEFAULT_INDEX=${UV_DEFAULT_INDEX}" >> /etc/environment \
  && echo "UV_PYTHON_INSTALL_DIR=${UV_PYTHON_INSTALL_DIR}" >> /etc/environment

# work用户 设置私有源
# - 即 --login 表示模拟一个完整的登录过程，会加载该用户的环境变量（如 .bashrc, .profile 等）
RUN su - $WORK_USER -c 'eval $SET_NVM_CMD && eval $SET_NPM_REGISTRY_URL_CMD'

# 安装 Cherry-Studio
# [安装 FUSE 参考](https://github.com/AppImage/AppImageKit/wiki/FUSE)
ENV CHERRY_STUDIO_NAME Cherry-Studio-1.3.12-x86_64.AppImage
COPY ./$CHERRY_STUDIO_NAME /opt/$CHERRY_STUDIO_NAME
RUN chmod +x /opt/$CHERRY_STUDIO_NAME \
  && cd /opt \
  && ./$CHERRY_STUDIO_NAME --appimage-extract \
  && mv squashfs-root/ cherrystudio/ \
  && sed -i 's|^Exec=AppRun|Exec=env APPDIR=/opt/cherrystudio /opt/cherrystudio/AppRun|' /opt/cherrystudio/cherrystudio.desktop \
  && sed -i 's|^Icon=cherrystudio|Icon=/opt/cherrystudio/usr/share/icons/hicolor/1024x1024/apps/cherrystudio.png|' /opt/cherrystudio/cherrystudio.desktop \
  && chmod -R 755 /opt/cherrystudio \
  && ln -s /opt/cherrystudio/cherrystudio.desktop /usr/share/applications/cherrystudio.desktop \
  && rm -rf $CHERRY_STUDIO_NAME
# 获取 CherryStudioData.zip
# cd /home/$WORK_USER/.config/
# zip -r CherryStudioData.zip ./CherryStudio/
# docker cp 8c995618e7f1:/home/work/.config/CherryStudioData.zip ./CherryStudioData.zip
# 设置 设置默认 密匙/提示词/主题 等 for https://github.com/CherryHQ/cherry-studio/issues/7637
COPY ./CherryStudioData.zip /home/$WORK_USER/.config/CherryStudioData.zip
RUN cd /home/$WORK_USER/.config \
  && unzip -o ./CherryStudioData.zip \
  && rm -rf ./CherryStudioData.zip \
  # Cherry-Studio uv 使用现有
  && mkdir -p /home/$WORK_USER/.cherrystudio/bin \
  && ln -sf /usr/local/bin/uv /home/$WORK_USER/.cherrystudio/bin/uv \
  && ln -sf /usr/local/bin/uvx /home/$WORK_USER/.cherrystudio/bin/uvx \
  && chown -R $WORK_USER:$WORK_USER /home/work/

# && apt-get update \
# # 它提供了管理 PPA（个人包档案）仓库的功能  确保 add-apt-repository 可用
# && apt-get install -y software-properties-common \
# libfuse2t64 \
# && add-apt-repository universe -y
# # 命令行启动
# APPDIR=/opt/cherrystudio && ./$CHERRY_STUDIO_NAME --appimage-extract-and-run --no-sandbox

# 刷新图标 /usr/share/applications/*.desktop
# sudo update-desktop-database /usr/share/applications
# sudo gtk-update-icon-cache /usr/share/icons/hicolor
# mac fn+F2+command 输入 r 回车 重启 GNOME Shell

# 安装飞书
COPY ./Feishu-linux_x64-7.36.11.deb /app/Feishu-linux_x64-7.36.11.deb
# RUN dpkg -i /app/Feishu-linux_x64-7.36.11.deb \
#   # 用于列出硬件信息的 Linux 工具。某些应用程序（比如飞书）可能会调用它来获取硬件信息，例如网卡、CPU、内存等
#   # 飞书 需要
#   # && apt-get install -y lshw \
#   # 自动修复依赖
#   && apt-get install -f
# 命令行启动
# bytedance-feishu-stable --no-sandbox

# mcp server pyautogui
COPY ./*.tar.gz /app/
RUN mkdir -p /app/pyautogui-extend \
  && eval $SET_NVM_CMD \
  && source /usr/local/bin/env \
  && cd /app \
  && tar -zxvf $(ls -t /app/*.tar.gz | head -n 1) -C /app/pyautogui-extend \
  && rm -rf $(ls -t /app/*.tar.gz | head -n 1) \
  && cd /app/pyautogui-extend \
  && pnpm i

# 给所有用户开 应用 目录权限
RUN chown -R root:root /app && chmod -R 777 /app && eval $CLEAN_CMD

# TODO
# - 体验类
# 偶现 闪动问题
# 选择 Language 没有选项 输入不了中文
# 20.02 首次进入提示 Screen Lock disabled Screen Locking requires the GNOME display manager.
# 声音 如何打通
# [Ubuntu Linux Gnome 桌面美化](https://www.bilibili.com/opus/1064247184626548793)

# 启动
# docker run -itd --tmpfs /run --tmpfs /run/lock --tmpfs /tmp --cgroupns=host --cap-add SYS_BOOT --cap-add SYS_ADMIN -v /sys/fs/cgroup:/sys/fs/cgroup -p 5901:5901 -p 6081:6081 -m 2g --cpus 2 ubuntu-gnome-vnc-nvm-uv:2025-07-01_19-44-41
# # 挂载 /run 为内存文件系统（tmpfs），提高性能并避免写入磁盘
# --tmpfs /run
# # 挂载 /run/lock 为内存文件系统（避免锁文件写入磁盘）
# --tmpfs /run/lock
# # 挂载 /tmp 为内存文件系统（临时文件不持久化） --tmpfs /tmp:exec 里可以执行程序，方便运行 AppImage 等
# --tmpfs /tmp
# # 将宿主机的 /sys/fs/cgroup 挂载到容器内 允许容器使用 systemd 管理进程（必需参数）
# -v /sys/fs/cgroup:/sys/fs/cgroup
# # 使用宿主机的 cgroup 命名空间 允许容器内的 systemd 正常管理进程（必需参数）
# --cgroupns=host
# # 添加 SYS_BOOT 权限 允许容器执行与系统启动相关的操作（如重启服务）
# --cap-add SYS_BOOT
# # 添加 SYS_ADMIN 权限 允许容器执行高级系统管理操作（如挂载文件系统、管理设备）
# --cap-add SYS_ADMIN
# 最多使用 ​​2GB 内存
# -m 2g
# 最多使用 ​​2 个 CPU 核心​​
# --cpus 2