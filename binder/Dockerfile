FROM intel4coro/jupyter-ros2:jazzy-py3.12

USER root
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=en_US.UTF-8

# ------------------------------------------------------------
# Basic system setup
# ------------------------------------------------------------
RUN apt update -qq && \
    apt install -y -qq sudo locales software-properties-common gnupg2 curl wget \
        vim git byobu tmux net-tools ca-certificates apt-transport-https \
        build-essential lsb-release && \
    echo "jovyan ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/jovyan && \
    chmod 0440 /etc/sudoers.d/jovyan && \
    locale-gen en_US.UTF-8

# ------------------------------------------------------------
# XFCE desktop + TurboVNC
# ------------------------------------------------------------
RUN apt update -qq && \
    apt install -y -qq dbus-x11 xfce4 xfce4-session xfce4-settings xfce4-panel \
        xorg xubuntu-icon-theme fonts-dejavu && \
    apt remove -y xfce4-screensaver && \
    rm -rf /var/lib/apt/lists/*

# TurboVNC repository
RUN wget -q -O- https://packagecloud.io/dcommander/turbovnc/gpgkey | \
        gpg --dearmor >/etc/apt/trusted.gpg.d/TurboVNC.gpg && \
    wget -q -O /etc/apt/sources.list.d/TurboVNC.list \
        https://raw.githubusercontent.com/TurboVNC/repo/main/TurboVNC.list && \
    apt update -qq && \
    apt install -y -qq turbovnc && \
    rm /etc/apt/sources.list.d/TurboVNC.list && \
    rm -rf /var/lib/apt/lists/*

ENV PATH=/opt/TurboVNC/bin:${PATH}
ENV DISPLAY=:1

# ------------------------------------------------------------
# ROS 2 Jazzy
# ------------------------------------------------------------
ENV ROS_DISTRO=jazzy \
    ROS_PKG=desktop \
    ROS_PATH=/opt/ros/jazzy

RUN add-apt-repository -y universe && \
    curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
        -o /usr/share/keyrings/ros-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
        http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" \
        > /etc/apt/sources.list.d/ros2.list

RUN apt update && \
    DEBIAN_FRONTEND=noninteractive apt install -y --no-install-recommends \
        ros-dev-tools ros-${ROS_DISTRO}-${ROS_PKG} && \
    apt clean && rm -rf /var/lib/apt/lists/*

RUN echo "source ${ROS_PATH}/setup.bash" >> /home/${NB_USER}/.bashrc && \
    rosdep init || true && rosdep update || true && rosdep fix-permissions || true

# Patch: topic_based_ros2_control
RUN DEBIAN_FRONTEND=noninteractive apt install -y ros-jazzy-topic-based-ros2-control || true

# ------------------------------------------------------------
# Python & Jupyter extensions
# ------------------------------------------------------------
USER ${NB_USER}

RUN conda install -y websockify && \
    pip install --upgrade jupyterlab ipywidgets jupyter-resource-usage \
        jupyter-server-proxy jupyterlab-git jupyter-remote-desktop-proxy \
        jupyter_offlinenotebook Pillow rosdep sidecar lark catkin_tools \
        colcon-common-extensions PyQt5 PySide2 matplotlib opencv-python \
        mujoco && \
    pip install setuptools==68.1.2 && \
    pip cache purge

# ------------------------------------------------------------
# VS Code Server
# ------------------------------------------------------------
RUN conda install -y -c conda-forge code-server && \
    echo 'alias code="$(which code-server)"' >> ~/.bashrc && \
    pip install git+https://github.com/yxzhan/jupyter-code-server.git

ENV CODE_WORKING_DIRECTORY=${HOME}

# ------------------------------------------------------------
# PyBullet + MuJoCo support
# ------------------------------------------------------------
RUN pip install --no-cache-dir pybullet panda-gym[pybullet] gymnasium

USER root
RUN apt update && apt install -y --no-install-recommends \
        libosmesa6 libosmesa6-dev libgl1 mesa-utils \
        libglew-dev libglfw3 libglfw3-dev patchelf && \
    rm -rf /var/lib/apt/lists/*

USER ${NB_USER}
RUN git clone --depth 1 https://github.com/google-deepmind/mujoco_menagerie.git \
        ${HOME}/work/notebooks/mujoco_menagerie || true

# ------------------------------------------------------------
# MuJoCo for Multiverse (required!)
# ------------------------------------------------------------
USER ${NB_USER}
ENV MUJOCO_VERSION=3.1.2
ENV MUJOCO_DIR=${HOME}/.mujoco/mujoco-${MUJOCO_VERSION}

RUN mkdir -p ${HOME}/.mujoco && \
    wget -q https://github.com/google-deepmind/mujoco/releases/download/${MUJOCO_VERSION}/mujoco-${MUJOCO_VERSION}-linux-x86_64.tar.gz && \
    tar -xf mujoco-${MUJOCO_VERSION}-linux-x86_64.tar.gz -C ${HOME}/.mujoco && \
    rm mujoco-${MUJOCO_VERSION}-linux-x86_64.tar.gz

ENV LD_LIBRARY_PATH=${MUJOCO_DIR}/lib:${LD_LIBRARY_PATH}

# ------------------------------------------------------------
# Required
# ------------------------------------------------------------
USER root
RUN apt update && apt install -y --no-install-recommends \
    ros-jazzy-ros2-control \
    ros-jazzy-ros2-controllers \
    ros-jazzy-controller-manager \
    ros-jazzy-control-msgs && \
    rm -rf /var/lib/apt/lists/*
USER ${NB_USER}

# ------------------------------------------------------------
# Multiverse installation
# ------------------------------------------------------------
USER ${NB_USER}
ENV MV_ROOT=${HOME}/Multiverse
ENV MULTIVERSE_REPO=https://github.com/Multiverse-Framework/Multiverse
ENV MULTIVERSE_BRANCH=main

RUN set -ex && \
    mkdir -p ${MV_ROOT} && \
    cd ${HOME} && \
    git clone --recurse-submodules --depth 1 --branch ${MULTIVERSE_BRANCH} ${MULTIVERSE_REPO} ${MV_ROOT} || \
      (cd ${MV_ROOT} && git submodule update --init --recursive) && \
    cd ${MV_ROOT} && \
    if [ -f "./Multiverse-Launch/requirements.txt" ]; then \
      pip install --no-cache-dir -r ./Multiverse-Launch/requirements.txt; fi && \
    if [ -f "./Multiverse-Utilities/requirements.txt" ]; then \
      pip install --no-cache-dir -r ./Multiverse-Utilities/requirements.txt; fi && \
    if [ -f "./Multiverse-Launch/src/multiverse_connectors/multiverse_simulators_connector/src/mujoco_connector/requirements.txt" ]; then \
      pip install --no-cache-dir -r ./Multiverse-Launch/src/multiverse_connectors/multiverse_simulators_connector/src/mujoco_connector/requirements.txt || true; fi && \
    if [ -d "./Multiverse-Launch/src/multiverse_connectors/multiverse_ros_connector/ros_ws/multiverse_ws2" ]; then \
      cd ./Multiverse-Launch/src/multiverse_connectors/multiverse_ros_connector/ros_ws/multiverse_ws2 && \
      colcon build --symlink-install || true; \
      cd ${MV_ROOT}; \
    fi

# ------------------------------------------------------------
# Copy notebooks & set entrypoint
# ------------------------------------------------------------
WORKDIR ${HOME}/work
COPY --chown=${NB_USER}:users ./ ${HOME}/work

COPY --chown=${NB_USER}:users binder/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["start-notebook.sh"]