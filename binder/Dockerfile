FROM quay.io/jupyter/minimal-notebook:python-3.12

# --- Prevent interactive apt prompts --- #
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

# Install a VNC server (TurboVNC) - non-interactive dpkg options to avoid prompts
ENV PATH=/opt/TurboVNC/bin:$PATH
RUN echo "Installing TurboVNC"; \
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
    rm -f /etc/apt/sources.list.d/TurboVNC.list;

# Install VNC jupyterlab extension (use conda to avoid mamba ABI issues)
USER ${NB_USER}
RUN conda install -y websockify
ENV DISPLAY=:1

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

# perform ROS apt operations robustly (non-interactive, repair broken packages if needed)
RUN set -eux; \
    apt-get update; \
    apt-get -y --fix-broken install || true; \
    dpkg --configure -a || true; \
    DEBIAN_FRONTEND=noninteractive apt-get -y upgrade -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold"; \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      -o Dpkg::Options::="--force-confdef" \
      -o Dpkg::Options::="--force-confold" \
      ros-dev-tools \
      ros-${ROS_DISTRO}-${ROS_PKG}; \
    apt-get -y --fix-broken install || true; \
    dpkg --configure -a || true; \
    apt-get clean; rm -rf /var/lib/apt/lists/*

# Save ROS setup for NB user
RUN echo "source ${ROS_PATH}/setup.bash" >> /home/${NB_USER}/.bashrc
RUN rosdep init || true
RUN rosdep update || true
RUN rosdep fix-permissions || true

# --- Install python packages --- #
USER ${NB_USER}
RUN pip install --upgrade \
        jupyterlab \
        ipywidgets \
        jupyter-resource-usage \
        jupyter-server-proxy \
        jupyterlab-git \
        jupyter-remote-desktop-proxy \
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
        mujoco \
    && pip cache purge

# setuptools version of ROS jazzy
RUN pip install setuptools==68.1.2

# --- Install VSCode server --- #
USER ${NB_USER}
RUN conda install -y -c conda-forge code-server
RUN echo 'alias code="$(which code-server)"' >> ~/.bashrc
# Installing extensions at build time is brittle; install from the Desktop terminal if needed:
# code-server --install-extension ms-python.python
# code-server --install-extension ms-toolsai.jupyter

RUN pip install git+https://github.com/yxzhan/jupyter-code-server.git
ENV CODE_WORKING_DIRECTORY=${HOME}

# --- Install PyBullet --- #
USER ${NB_USER}
RUN pip install --no-cache-dir pybullet panda-gym[pybullet] gymnasium pillow matplotlib

# ---- Install system libs required by modern mujoco (OpenGL/OSMesa etc) ----
USER root
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      libosmesa6 libosmesa6-dev libgl1 mesa-utils \
      libglew-dev libglfw3 libglfw3-dev patchelf \
      && rm -rf /var/lib/apt/lists/*

# ---- Install the Python mujoco binding and example repo ----
# install under the notebook user so pip packages live in user environment
USER ${NB_USER}
RUN pip install --no-cache-dir mujoco && \
    # optional: clone the menagerie (small) so demos are available in the image
    git clone --depth 1 https://github.com/google-deepmind/mujoco_menagerie.git ${HOME}/mujoco_menagerie || true

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
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" ros-jazzy-topic-based-ros2-control || true
USER ${NB_USER}
