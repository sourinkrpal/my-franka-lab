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

# -------------------------
# Multiverse build & setup
# -------------------------
ARG MULTIVERSE_DIR=/home/Multiverse/multiverse
ARG BUILD_DIR=$MULTIVERSE_DIR/build
ARG MULTIVERSE_REPO=https://github.com/MultiverseAI/multiverse.git

USER root

# install build & python dev dependencies needed by Multiverse
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
      git cmake build-essential python3-venv python3-dev python3-pip \
      virtualenv virtualenvwrapper swig pkg-config \
      libeigen3-dev libboost-all-dev libpython3-dev \
      libssl-dev libglu1-mesa-dev libgl1-mesa-dev libx11-dev \
      libavcodec-dev libavformat-dev libswscale-dev \
      && rm -rf /var/lib/apt/lists/*

# Create Multiverse working directories and clone source (or COPY your local source)
RUN mkdir -p /home/Multiverse && \
    git clone --depth 1 ${MULTIVERSE_REPO} ${MULTIVERSE_DIR} || true && \
    chown -R ${NB_USER}:users /home/Multiverse

# Install virtualenvwrapper (system-wide) and create a 'multiverse' virtualenv
# Use the notebook user to create and own the virtualenv so packages are installed to the NB_USER home
USER ${NB_USER}
ENV WORKON_HOME=/home/${NB_USER}/.virtualenvs
ENV VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
RUN python3 -m pip install --upgrade pip setuptools wheel virtualenv virtualenvwrapper && \
    mkdir -p $WORKON_HOME && \
    # initialize virtualenvwrapper env startup
    mkdir -p /home/${NB_USER}/.local/bin && \
    (echo "export WORKON_HOME=$WORKON_HOME" >> /home/${NB_USER}/.bashrc) && \
    (echo "export VIRTUALENVWRAPPER_PYTHON=$VIRTUALENVWRAPPER_PYTHON" >> /home/${NB_USER}/.bashrc) && \
    (echo "source /usr/local/bin/virtualenvwrapper.sh" >> /home/${NB_USER}/.bashrc) || true

# create virtualenv and install python deps into it, using virtualenvwrapper
# we use bash -lc to source virtualenvwrapper and run workon in the same shell
RUN /bin/bash -lc "source /usr/local/bin/virtualenvwrapper.sh && mkvirtualenv --system-site-packages multiverse" && \
    /bin/bash -lc "source /usr/local/bin/virtualenvwrapper.sh && workon multiverse && \
        pip install --no-cache-dir psutil==5.9.2 pyside6 pyopengl pyside6-wheel cython \
            owlready2 markupsafe==2.0.1 jinja2 pybind11 urdf_parser_py mujoco==3.2.7 \
            mujoco-mjx==3.2.7 scipy panel"

# Build Multiverse from source: create build dir, configure and build.
# We intentionally do two cmake configs in the example (modules off then on) as in your example.
RUN /bin/bash -lc "source /usr/local/bin/virtualenvwrapper.sh && workon multiverse && \
        cd $MULTIVERSE_DIR && mkdir -p $BUILD_DIR && \
        cmake -S $MULTIVERSE_DIR -B $BUILD_DIR -DCMAKE_INSTALL_PREFIX:PATH=$MULTIVERSE_DIR \
          -DMULTIVERSE_CLIENT_LIBRARY_TYPE=STATIC -DSTDLIB=libstdc++ \
          -DBUILD_SRC=ON -DBUILD_MODULES=OFF -DBUILD_CONNECTORS=OFF -DBUILD_KNOWLEDGE=OFF -DBUILD_PARSER=OFF -DBUILD_TESTS=OFF && \
        cmake -S $MULTIVERSE_DIR -B $BUILD_DIR -DCMAKE_INSTALL_PREFIX:PATH=$MULTIVERSE_DIR \
          -DMULTIVERSE_CLIENT_LIBRARY_TYPE=STATIC -DSTDLIB=libstdc++ \
          -DBUILD_MODULES=ON -DBUILD_CONNECTORS=ON -DBUILD_KNOWLEDGE=OFF -DBUILD_PARSER=OFF -DBUILD_TESTS=OFF && \
        make -C $BUILD_DIR -j$(nproc) && cmake --install $BUILD_DIR"

# ensure NB_USER owns installed Multiverse files
USER root
RUN chown -R ${NB_USER}:users /home/Multiverse || true

# export PYTHONPATH and auto-activate multiverse virtualenv on shell login
USER ${NB_USER}
RUN echo "export PYTHONPATH=\$PYTHONPATH:$MULTIVERSE_DIR/lib/dist-packages" >> /home/${NB_USER}/.bashrc && \
    echo "source /usr/local/bin/virtualenvwrapper.sh && workon multiverse" >> /home/${NB_USER}/.bashrc

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
# Copy notebooks & set entrypoint
# ------------------------------------------------------------
WORKDIR ${HOME}/work
COPY --chown=${NB_USER}:users ./ ${HOME}/work

COPY --chown=${NB_USER}:users binder/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["start-notebook.sh"]
