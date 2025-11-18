# -----------------------------------------------------------------------------
# Merged Dockerfile: intel4coro base + TurboVNC/XFCE + ROS Jazzy + Multiverse
# -----------------------------------------------------------------------------
FROM intel4coro/jupyter-ros2:jazzy-py3.12

# ------------------------------------------------------------
# Basic env and safety
# ------------------------------------------------------------
USER root
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=en_US.UTF-8

# Ensure NB_USER is set (most jupyter/base images define it; fallback to jovyan)
ARG NB_USER=jovyan
ENV NB_USER=${NB_USER}
ENV NB_UID=1000
ENV HOME=/home/${NB_USER}
ENV PATH=/opt/TurboVNC/bin:${PATH}
ENV DISPLAY=:1

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# ------------------------------------------------------------
# Core system packages (one apt layer)
# ------------------------------------------------------------
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
      sudo locales gnupg2 curl wget vim git byobu tmux net-tools ca-certificates \
      apt-transport-https build-essential lsb-release software-properties-common \
      dirmngr rsync wget unzip ca-certificates \
      # multimedia / video dev libs (ffmpeg)
      libavcodec-dev libavformat-dev libswscale-dev \
      # linear algebra / C++ dev
      libeigen3-dev libboost-all-dev pkg-config cmake swig \
      # python dev
      python3-venv python3-dev python3-pip python3-setuptools python3-wheel \
      # Qt / GUI dev (for PySide6 / pyside wheels)
      qtbase5-dev qtdeclarative5-dev libqt5svg5-dev libqt5webkit5-dev \
      libxcb1-dev libx11-dev libxext-dev libxi-dev libxrandr-dev libxinerama-dev libxcursor-dev \
      # GL / offscreen rendering / mesa
      libglu1-mesa-dev libgl1-mesa-dev libosmesa6 libosmesa6-dev libglew-dev libglfw3 libglfw3-dev \
      # extra build helpers
      patchelf && \
    locale-gen en_US.UTF-8 && \
    echo "${NB_USER} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${NB_USER} && \
    chmod 0440 /etc/sudoers.d/${NB_USER} && \
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

# TurboVNC repository (use trusted keyring pattern)
RUN wget -q -O- https://packagecloud.io/dcommander/turbovnc/gpgkey | \
        gpg --dearmor >/etc/apt/trusted.gpg.d/TurboVNC.gpg && \
    wget -q -O /etc/apt/sources.list.d/TurboVNC.list \
        https://raw.githubusercontent.com/TurboVNC/repo/main/TurboVNC.list && \
    apt-get update -qq && \
    apt-get install -y --no-install-recommends turbovnc && \
    rm -f /etc/apt/sources.list.d/TurboVNC.list && \
    rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# ROS 2 Jazzy (keep your existing setup)
# ------------------------------------------------------------
ENV ROS_DISTRO=jazzy
ENV ROS_PKG=desktop
ENV ROS_PATH=/opt/ros/jazzy

RUN add-apt-repository -y universe && \
    curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
        -o /usr/share/keyrings/ros-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
        http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" \
        > /etc/apt/sources.list.d/ros2.list && \
    apt-get update -qq && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ros-dev-tools ros-${ROS_DISTRO}-${ROS_PKG} && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN echo "source ${ROS_PATH}/setup.bash" >> /home/${NB_USER}/.bashrc && \
    rosdep init || true && rosdep update || true && rosdep fix-permissions || true

# Optional ros package (don't fail build if not present)
RUN DEBIAN_FRONTEND=noninteractive apt-get update -qq && \
    apt-get install -y --no-install-recommends ros-jazzy-topic-based-ros2-control || true && \
    rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# NodeJS (for jupyterlab extensions)
# ------------------------------------------------------------
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# Multiverse: build & install (using python venv, robust deps)
# Place this before switching to NB_USER for pip/conda installs
# ------------------------------------------------------------
ARG MULTIVERSE_DIR=/home/Multiverse/multiverse
ARG BUILD_DIR=$MULTIVERSE_DIR/build
ARG MULTIVERSE_REPO=https://github.com/MultiverseAI/multiverse.git

# Prepare Multiverse parent dir, clone source (or change to COPY if you have local source)
RUN mkdir -p /home/Multiverse && \
    chown -R ${NB_USER}:users /home/Multiverse

USER ${NB_USER}
ENV VENV_DIR=/home/${NB_USER}/.venvs/multiverse
RUN python3 -m venv --system-site-packages $VENV_DIR && \
    $VENV_DIR/bin/python -m pip install --upgrade pip setuptools wheel

# Clone multiverse as the notebook user (keeps ownership neat)
RUN git clone --depth 1 ${MULTIVERSE_REPO} ${MULTIVERSE_DIR} || true && \
    chown -R ${NB_USER}:users ${MULTIVERSE_DIR}

# Install Python deps into the venv (use conservative stable pins where shown)
RUN $VENV_DIR/bin/pip install --no-cache-dir \
        psutil==5.9.2 pyside6 pyopengl pyside6-wheel cython \
        owlready2 markupsafe==2.0.1 jinja2 pybind11 urdf_parser_py \
        mujoco==3.2.7 mujoco-mjx==3.2.7 scipy panel || true

# Build Multiverse using the venv (activate in same shell)
RUN /bin/bash -lc "source $VENV_DIR/bin/activate && \
        mkdir -p $BUILD_DIR && \
        cmake -S $MULTIVERSE_DIR -B $BUILD_DIR -DCMAKE_INSTALL_PREFIX:PATH=$MULTIVERSE_DIR \
          -DMULTIVERSE_CLIENT_LIBRARY_TYPE=STATIC -DSTDLIB=libstdc++ \
          -DBUILD_SRC=ON -DBUILD_MODULES=OFF -DBUILD_CONNECTORS=OFF -DBUILD_KNOWLEDGE=OFF -DBUILD_PARSER=OFF -DBUILD_TESTS=OFF && \
        cmake -S $MULTIVERSE_DIR -B $BUILD_DIR -DCMAKE_INSTALL_PREFIX:PATH=$MULTIVERSE_DIR \
          -DMULTIVERSE_CLIENT_LIBRARY_TYPE=STATIC -DSTDLIB=libstdc++ \
          -DBUILD_MODULES=ON -DBUILD_CONNECTORS=ON -DBUILD_KNOWLEDGE=OFF -DBUILD_PARSER=OFF -DBUILD_TESTS=OFF && \
        make -C $BUILD_DIR -j$(nproc) && cmake --install $BUILD_DIR"

# Ensure ownership is correct and add PYTHONPATH / venv activation
USER root
RUN chown -R ${NB_USER}:users /home/Multiverse || true

USER ${NB_USER}
RUN mkdir -p /home/${NB_USER}/.venvs && \
    echo "export VIRTUAL_ENV=$VENV_DIR" >> /home/${NB_USER}/.bashrc && \
    echo "export PATH=\$VIRTUAL_ENV/bin:\$PATH" >> /home/${NB_USER}/.bashrc && \
    echo "export PYTHONPATH=\$PYTHONPATH:${MULTIVERSE_DIR}/lib/dist-packages" >> /home/${NB_USER}/.bashrc && \
    # make sure venv activation is effective in spawned shells
    echo "source \$VIRTUAL_ENV/bin/activate >/dev/null 2>&1 || true" >> /home/${NB_USER}/.bashrc

# ------------------------------------------------------------
# Python & Jupyter extensions (user)
# ------------------------------------------------------------
USER ${NB_USER}
# conda may be available in base image; using conda for some installs keeps compatibility
RUN conda install -y -q websockify code-server -c conda-forge && \
    python -m pip install --upgrade pip setuptools==68.1.2 && \
    python -m pip install --no-cache-dir \
        jupyterlab ipywidgets jupyter-resource-usage jupyter-server-proxy \
        jupyterlab-git jupyter-remote-desktop-proxy jupyter_offlinenotebook \
        Pillow rosdep sidecar lark catkin_tools colcon-common-extensions \
        PyQt5 PySide2 matplotlib opencv-python mujoco pybullet panda-gym[pybullet] gymnasium && \
    python -m pip cache purge || true

# code-server alias and jupyter-code-server extension
RUN echo 'alias code="$(which code-server)"' >> /home/${NB_USER}/.bashrc && \
    python -m pip install --no-cache-dir git+https://github.com/yxzhan/jupyter-code-server.git || true

ENV CODE_WORKING_DIRECTORY=${HOME}

# clone example repo (non-fatal)
RUN git clone --depth 1 https://github.com/google-deepmind/mujoco_menagerie.git \
        ${HOME}/work/notebooks/mujoco_menagerie || true

# ------------------------------------------------------------
# System libs for PyBullet / MuJoCo / graphics (root)
# ------------------------------------------------------------
USER root
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
        libosmesa6 libosmesa6-dev libgl1 mesa-utils \
        libglew-dev libglfw3 libglfw3-dev patchelf && \
    rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# Copy notebooks & entrypoint, set permissions
# ------------------------------------------------------------
USER ${NB_USER}
WORKDIR ${HOME}/work
COPY --chown=${NB_USER}:users ./ ${HOME}/work
COPY --chown=${NB_USER}:users binder/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# optional: keep jupyter lab overrides if you have them
COPY --chown=${NB_USER}:users binder/jupyter-settings.json /usr/local/share/jupyter/lab/settings/overrides.json || true

# Final ownership safety
USER root
RUN chown -R ${NB_USER}:users /home/${NB_USER} || true
USER ${NB_USER}

ENTRYPOINT ["/entrypoint.sh"]
CMD ["start-notebook.sh"]
