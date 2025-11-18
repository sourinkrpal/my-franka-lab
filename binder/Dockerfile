# -----------------------------------------------------------------------------
# Merged Dockerfile: intel4coro base + TurboVNC/XFCE + ROS Jazzy + Multiverse
# -----------------------------------------------------------------------------
FROM intel4coro/jupyter-ros2:jazzy-py3.12

USER root
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=en_US.UTF-8

# Notebook user (fallback to jovyan)
ARG NB_USER=jovyan
ENV NB_USER=${NB_USER}
ENV NB_UID=1000
ENV HOME=/home/${NB_USER}
ENV PATH=/opt/TurboVNC/bin:${PATH}
ENV DISPLAY=:1

# Multiverse dirs (export as env for later runtime)
ENV MULTIVERSE_DIR=/home/Multiverse/multiverse
ENV MULTIVERSE_BUILD_DIR=${MULTIVERSE_DIR}/build

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# ------------------------------------------------------------
# Core system packages (one apt layer)
# ------------------------------------------------------------
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
      sudo locales gnupg2 curl wget vim git byobu tmux net-tools ca-certificates \
      apt-transport-https build-essential lsb-release software-properties-common \
      dirmngr rsync unzip \
      libavcodec-dev libavformat-dev libswscale-dev \
      libeigen3-dev libboost-all-dev pkg-config cmake swig \
      python3-venv python3-dev python3-pip python3-setuptools python3-wheel \
      qtbase5-dev qtdeclarative5-dev libqt5svg5-dev libqt5webkit5-dev \
      libxcb1-dev libx11-dev libxext-dev libxi-dev libxrandr-dev libxinerama-dev libxcursor-dev \
      libglu1-mesa-dev libgl1-mesa-dev libosmesa6 libosmesa6-dev libglew-dev libglfw3 libglfw3-dev \
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

# TurboVNC repo (trusted keyring)
RUN wget -q -O- https://packagecloud.io/dcommander/turbovnc/gpgkey | \
        gpg --dearmor >/etc/apt/trusted.gpg.d/TurboVNC.gpg && \
    wget -q -O /etc/apt/sources.list.d/TurboVNC.list \
        https://raw.githubusercontent.com/TurboVNC/repo/main/TurboVNC.list && \
    apt-get update -qq && \
    apt-get install -y --no-install-recommends turbovnc && \
    rm -f /etc/apt/sources.list.d/TurboVNC.list && \
    rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# ROS 2 Jazzy
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

# Optional ROS package (non-fatal)
RUN DEBIAN_FRONTEND=noninteractive apt-get update -qq && \
    apt-get install -y --no-install-recommends ros-jazzy-topic-based-ros2-control || true && \
    rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# Node.js for JupyterLab extensions
# ------------------------------------------------------------
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# Prepare Multiverse parent dir (root) and files (download tarball)
# ------------------------------------------------------------
RUN mkdir -p /home/Multiverse && chown -R ${NB_USER}:users /home/Multiverse

# Use an archive fetch rather than git clone to avoid credential or git config issues
ARG MULTIVERSE_REPO_TARBALL=https://github.com/MultiverseAI/multiverse/archive/refs/heads/main.tar.gz
USER root
RUN curl -fsSL "${MULTIVERSE_REPO_TARBALL}" | tar -xzf - -C /home/Multiverse --strip-components=1 && \
    chown -R ${NB_USER}:users /home/Multiverse && \
    ls -la /home/Multiverse | sed -n '1,40p'

# ------------------------------------------------------------
# Create venv and install Python dependencies (as NB_USER)
# ------------------------------------------------------------
USER ${NB_USER}
ENV VENV_DIR=/home/${NB_USER}/.venvs/multiverse
RUN mkdir -p /home/${NB_USER}/.venvs && \
    python3 -m venv --system-site-packages $VENV_DIR && \
    $VENV_DIR/bin/python -m pip install --upgrade pip setuptools wheel

# install python deps into the venv (prefer binaries to reduce build time where possible)
RUN $VENV_DIR/bin/pip install --no-cache-dir --prefer-binary \
        psutil==5.9.2 pyside6 pyopengl pyside6-wheel cython \
        owlready2 markupsafe==2.0.1 jinja2 pybind11 urdf_parser_py \
        mujoco==3.2.7 mujoco-mjx==3.2.7 scipy panel || true

# ------------------------------------------------------------
# Build Multiverse from source using venv (single shell activation)
# ------------------------------------------------------------
RUN /bin/bash -lc "source $VENV_DIR/bin/activate && \
        mkdir -p ${MULTIVERSE_BUILD_DIR} && \
        cmake -S ${MULTIVERSE_DIR} -B ${MULTIVERSE_BUILD_DIR} -DCMAKE_INSTALL_PREFIX:PATH=${MULTIVERSE_DIR} \
          -DMULTIVERSE_CLIENT_LIBRARY_TYPE=STATIC -DSTDLIB=libstdc++ \
          -DBUILD_SRC=ON -DBUILD_MODULES=OFF -DBUILD_CONNECTORS=OFF -DBUILD_KNOWLEDGE=OFF -DBUILD_PARSER=OFF -DBUILD_TESTS=OFF && \
        cmake -S ${MULTIVERSE_DIR} -B ${MULTIVERSE_BUILD_DIR} -DCMAKE_INSTALL_PREFIX:PATH=${MULTIVERSE_DIR} \
          -DMULTIVERSE_CLIENT_LIBRARY_TYPE=STATIC -DSTDLIB=libstdc++ \
          -DBUILD_MODULES=ON -DBUILD_CONNECTORS=ON -DBUILD_KNOWLEDGE=OFF -DBUILD_PARSER=OFF -DBUILD_TESTS=OFF && \
        make -C ${MULTIVERSE_BUILD_DIR} -j$(nproc) && cmake --install ${MULTIVERSE_BUILD_DIR}"

# ensure NB_USER owns Multiverse files
USER root
RUN chown -R ${NB_USER}:users /home/Multiverse || true

# auto-activate the venv and expose PYTHONPATH to notebooks/terminals
USER ${NB_USER}
RUN echo "export VIRTUAL_ENV=${VENV_DIR}" >> /home/${NB_USER}/.bashrc && \
    echo "export PATH=\$VIRTUAL_ENV/bin:\$PATH" >> /home/${NB_USER}/.bashrc && \
    echo "export PYTHONPATH=\$PYTHONPATH:${MULTIVERSE_DIR}/lib/dist-packages" >> /home/${NB_USER}/.bashrc && \
    echo "source \$VIRTUAL_ENV/bin/activate >/dev/null 2>&1 || true" >> /home/${NB_USER}/.bashrc

# ------------------------------------------------------------
# Python & Jupyter extensions (user)
# ------------------------------------------------------------
USER ${NB_USER}
RUN conda install -y -q websockify code-server -c conda-forge && \
    python -m pip install --upgrade pip setuptools==68.1.2 && \
    python -m pip install --no-cache-dir \
        jupyterlab ipywidgets jupyter-resource-usage jupyter-server-proxy \
        jupyterlab-git jupyter-remote-desktop-proxy jupyter_offlinenotebook \
        Pillow rosdep sidecar lark catkin_tools colcon-common-extensions \
        PyQt5 PySide2 matplotlib opencv-python mujoco pybullet panda-gym[pybullet] gymnasium && \
    python -m pip cache purge || true

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

COPY --chown=${NB_USER}:users binder/jupyter-settings.json /usr/local/share/jupyter/lab/settings/overrides.json || true

USER root
RUN chown -R ${NB_USER}:users /home/${NB_USER} || true
USER ${NB_USER}

ENTRYPOINT ["/entrypoint.sh"]
CMD ["start-notebook.sh"]

