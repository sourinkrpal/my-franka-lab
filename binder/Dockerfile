FROM intel4coro/base-notebook:20.04-noetic

# --- Prevent interactive prompts during package installation --- #
USER root
ENV DEBIAN_FRONTEND=noninteractive

# --- Give NB_USER sudo permission --- #
RUN apt update && apt install -y sudo && \
    echo "jovyan ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/jovyan && \
    chmod 0440 /etc/sudoers.d/jovyan

# --- Install basic tools --- #
USER root
RUN  apt update -qq && apt install -y -qq \
        software-properties-common \
        gnupg2 \
        curl \
        wget \
        vim \
        git \
        byobu \
        tmux \
        net-tools\
        ca-certificates \
        apt-transport-https \
        build-essential \
        locales \
        lsb-release

# --- Install VNC server and XFCE desktop environment --- #
USER root
RUN apt-get -y -qq update \
 && apt-get -y -qq install \
        dbus-x11 \
        xfce4 \
        xfce4-panel \
        xfce4-session \
        xfce4-settings \
        xorg \
        gnome-shell \
        gnome-session \
        gnome-terminal \
        xubuntu-icon-theme \
        fonts-dejavu \
    # Disable the automatic screenlock since the account password is unknown
 && apt-get -y -qq remove xfce4-screensaver \
 && mkdir -p /opt/install \
 && chown -R $NB_UID:$NB_GID $HOME /opt/install \
 && rm -rf /var/lib/apt/lists/*

# Install a VNC server (TurboVNC)
ENV PATH=/opt/TurboVNC/bin:$PATH
RUN echo "Installing TurboVNC"; \
    # Install instructions from https://turbovnc.org/Downloads/YUM
    wget -q -O- https://packagecloud.io/dcommander/turbovnc/gpgkey | \
    gpg --dearmor >/etc/apt/trusted.gpg.d/TurboVNC.gpg; \
    wget -O /etc/apt/sources.list.d/TurboVNC.list https://raw.githubusercontent.com/TurboVNC/repo/main/TurboVNC.list; \
    apt-get -y -qq update; \
    DEBIAN_FRONTEND=noninteractive apt-get -y -qq install \
        -o Dpkg::Options::="--force-confdef" \
        -o Dpkg::Options::="--force-confold" \
        turbovnc \
    ; \
    rm -rf /var/lib/apt/lists/*; \
    rm -f /etc/apt/sources.list.d/TurboVNC.list

# Install VNC jupyterlab extension (use conda to avoid mamba ABI issues)
USER ${NB_USER}
RUN conda install -y websockify
ENV DISPLAY=:1

###############################################################
# --- Install MuJoCo 2.1 + mujoco-py (patched, non-interactive) --- #
###############################################################
USER root

# System dependencies for mujoco-py (non-interactive and force dpkg config choices)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      -o Dpkg::Options::="--force-confdef" \
      -o Dpkg::Options::="--force-confold" \
      patchelf \
      libgl1 \
      mesa-utils \
      libosmesa6-dev \
      libglew-dev \
      libglfw3 \
      libglfw3-dev \
    && rm -rf /var/lib/apt/lists/*

# Download and install MuJoCo 2.1.0 (no license needed)
ENV MUJOCO_VERSION=2.1.0
ENV MUJOCO_DIR=/home/${NB_USER}/.mujoco/mujoco-${MUJOCO_VERSION}

RUN mkdir -p /home/${NB_USER}/.mujoco && \
    wget -q https://mujoco.org/download/mujoco210-linux-x86_64.tar.gz -O /tmp/mujoco.tar.gz && \
    tar -xzf /tmp/mujoco.tar.gz -C /home/${NB_USER}/.mujoco && \
    mv /home/${NB_USER}/.mujoco/mujoco210 ${MUJOCO_DIR} && \
    rm /tmp/mujoco.tar.gz && \
    chown -R ${NB_USER}:users /home/${NB_USER}/.mujoco

ENV LD_LIBRARY_PATH=${MUJOCO_DIR}/bin:${LD_LIBRARY_PATH}

# Install mujoco-py as NB_USER (must be after MuJoCo runtime is in place)
USER ${NB_USER}
ENV MUJOCO_PY_MUJOCO_PATH=${MUJOCO_DIR}
RUN pip install --upgrade pip && \
    pip install "mujoco-py<2.2,>=2.1" && \
    pip install PyOpenGL PyOpenGL_accelerate

###############################################################
# --- End of MuJoCo block --- #
###############################################################

# --- Install ROS2 --- #
USER root
ENV ROS_DISTRO=jazzy
ARG ROS_PKG=desktop
ENV ROS_PATH=/opt/ros/${ROS_DISTRO}
ENV ROS_ROOT=${ROS_PATH}/share/ros
ENV ROS_WS=${HOME}/ros2_ws

# Set locale
RUN locale-gen en_US en_US.UTF-8 && \
    update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
ENV LANG=en_US.UTF-8

USER root
RUN add-apt-repository universe
RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | tee /etc/apt/sources.list.d/ros2.list > /dev/null

# Robust apt update / upgrade / install for ROS2 block (non-interactive, repair broken packages)
USER root
ENV DEBIAN_FRONTEND=noninteractive
RUN set -eux; \
    apt-get update; \
    apt-get -y --fix-broken install || true; \
    dpkg --configure -a || true; \
    apt-get -y upgrade -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold"; \
    apt-get install -y --no-install-recommends \
      -o Dpkg::Options::="--force-confdef" \
      -o Dpkg::Options::="--force-confold" \
      ros-dev-tools \
      ros-${ROS_DISTRO}-${ROS_PKG}; \
    apt-get -y --fix-broken install || true; \
    dpkg --configure -a || true; \
    apt-get clean; \
    rm -rf /var/lib/apt/lists/*

# Save ROS setup for NB user
RUN echo "source ${ROS_PATH}/setup.bash" >> /home/${NB_USER}/.bashrc

# --- Install python packages --- #
USER ${NB_USER}
RUN pip install --upgrade \
        jupyterlab \
        ipywidgets \
        jupyter-resource-usage \
        jupyter-server-proxy \
        jupyterlab-git \
        jupyter-remote-desktop-proxy\
        jupyter_offlinenotebook \
        Pillow \
        rosdep \
        sidecar \
        lark \
        catkin_tools \
        colcon-common-extensions \
        PyQt5 \
        PySide2 \
        matplotlib \
        opencv-python \
    && pip cache purge

# setuptools version of ROS jazzy
RUN pip install setuptools==68.1.2

# --- Install VSCode server --- #
USER ${NB_USER}
RUN conda install -y conda-forge::code-server
RUN echo 'alias code="$(which code-server)"' >> ~/.bashrc
RUN code-server --install-extension ms-python.python \
  && code-server --install-extension ms-toolsai.jupyter
RUN pip install git+https://github.com/yxzhan/jupyter-code-server.git
ENV CODE_WORKING_DIRECTORY=${HOME}

# --- Copy notebooks --- #
USER ${NB_USER}
WORKDIR ${HOME}/work
COPY --chown=${NB_USER}:users ./ ${HOME}/work

# --- Entrypoint --- #
COPY --chown=${NB_USER}:users binder/entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]
CMD [ "start-notebook.sh" ]

# Apply a patch layer. 
# For unknown reason, the "topic_based_ros2_control" package was removed from the rosdep. 
USER root
RUN apt install -y ros-jazzy-topic-based-ros2-control
USER ${NB_USER}

