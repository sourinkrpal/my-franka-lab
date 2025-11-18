FROM intel4coro/jupyter-ros2:jazzy-py3.12

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 \
    ROS_DISTRO=jazzy \
    ROS_PKG=desktop \
    ROS_PATH=/opt/ros/jazzy \
    PATH=/opt/TurboVNC/bin:${PATH} \
    DISPLAY=:1 \
    CODE_WORKING_DIRECTORY=/home/jovyan

USER root

# ------------------------------------------------------------
# Basic packages
# ------------------------------------------------------------
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
      sudo locales software-properties-common gnupg2 curl wget \
      vim git byobu tmux net-tools ca-certificates apt-transport-https \
      build-essential lsb-release wget gnupg-agent && \
    echo "jovyan ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/jovyan && \
    chmod 0440 /etc/sudoers.d/jovyan && \
    locale-gen en_US.UTF-8 && \
    rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# XFCE desktop + TurboVNC
# ------------------------------------------------------------
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
      dbus-x11 xfce4 xfce4-session xfce4-settings xfce4-panel \
      xorg xubuntu-icon-theme fonts-dejavu && \
    apt-get remove -y --purge xfce4-screensaver || true && \
    rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://packagecloud.io/dcommander/turbovnc/gpgkey | gpg --dearmor \
      > /usr/share/keyrings/turbovnc-archive-keyring.gpg && \
    curl -fsSL https://raw.githubusercontent.com/TurboVNC/repo/main/TurboVNC.list \
      -o /etc/apt/sources.list.d/TurboVNC.list && \
    sed -i "s|deb |deb [signed-by=/usr/share/keyrings/turbovnc-archive-keyring.gpg] |g" /etc/apt/sources.list.d/TurboVNC.list && \
    apt-get update -qq && apt-get install -y --no-install-recommends turbovnc && \
    rm -f /etc/apt/sources.list.d/TurboVNC.list && rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# ROS 2 Jazzy
# ------------------------------------------------------------
RUN add-apt-repository -y universe && \
    curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
      -o /usr/share/keyrings/ros-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
      http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" \
      > /etc/apt/sources.list.d/ros2.list && \
    apt-get update -qq && \
    apt-get install -y --no-install-recommends ros-dev-tools ros-${ROS_DISTRO}-${ROS_PKG} && \
    rm -rf /var/lib/apt/lists/*

RUN echo "source ${ROS_PATH}/setup.bash" >> /home/${NB_USER}/.bashrc && \
    rosdep init || true && rosdep update || true && rosdep fix-permissions || true

RUN apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      ros-jazzy-topic-based-ros2-control || true && \
    rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# System libs for GL / MuJoCo / PyBullet
# ------------------------------------------------------------
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
      libosmesa6 libosmesa6-dev libgl1 mesa-utils \
      libglew-dev libglfw3 libglfw3-dev patchelf && \
    rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# Python & Jupyter extensions
# ------------------------------------------------------------
USER ${NB_USER}

RUN conda install -y -c conda-forge websockify code-server && \
    conda clean -afy && \
    python -m pip install --upgrade pip setuptools==68.1.2 && \
    python -m pip install --no-cache-dir \
        jupyterlab ipywidgets jupyter-resource-usage \
        jupyter-server-proxy jupyterlab-git jupyter-remote-desktop-proxy \
        jupyter_offlinenotebook Pillow rosdep sidecar lark catkin_tools \
        colcon-common-extensions PyQt5 PySide2 matplotlib opencv-python \
        mujoco pybullet panda-gym[pybullet] gymnasium && \
    python -m pip install --no-cache-dir git+https://github.com/yxzhan/jupyter-code-server.git && \
    python -m pip cache purge || true && \
    echo 'alias code="$(which code-server)"' >> ~/.bashrc

# ------------------------------------------------------------
# MuJoCo menagerie
# ------------------------------------------------------------
RUN git clone --depth 1 https://github.com/google-deepmind/mujoco_menagerie.git \
      ${HOME}/work/notebooks/mujoco_menagerie || true

# ------------------------------------------------------------
# Copy notebooks & entrypoint
# ------------------------------------------------------------
WORKDIR ${HOME}/work
COPY --chown=${NB_USER}:users ./ ${HOME}/work
COPY --chown=${NB_USER}:users binder/entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["start-notebook.sh"]
