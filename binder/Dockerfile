# -----------------------------------------------------------------------------
# Base image
# -----------------------------------------------------------------------------
FROM jupyter/minimal-notebook:ubuntu-20.04

# --- Define Environment Variables--- #
# ARG ROS_PKG=ros-base
ARG ROS_PKG=desktop-full
LABEL version="ROS-noetic-${ROS_PKG}"
ENV ROS_DISTRO=noetic
ENV ROS_PATH=/opt/ros/${ROS_DISTRO}
ENV ROS_ROOT=${ROS_PATH}/share/ros
ENV ROS_WS=/home/${NB_USER}/workspace/ros

# Avoid interactive prompts during apt installs
ENV DEBIAN_FRONTEND=noninteractive

# -----------------------------------------------------------------------------
# System packages (single combined layer)
# -----------------------------------------------------------------------------
USER root
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
      git vim curl tmux wget gnupg2 net-tools ca-certificates \
      apt-transport-https build-essential lsb-release \
      xfce4 xfce4-panel xfce4-session xfce4-settings xorg \
      xubuntu-icon-theme xvfb dbus-x11 libqt5x11extras5 \
      # lightweight desktop + VNC prerequisites (drop gnome if not needed) \
      && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# -----------------------------------------------------------------------------
# TurboVNC (VNC server)
# -----------------------------------------------------------------------------
ENV PATH=/opt/TurboVNC/bin:$PATH
RUN echo "Installing TurboVNC"; \
    wget -q -O- https://packagecloud.io/dcommander/turbovnc/gpgkey | \
      gpg --dearmor >/etc/apt/trusted.gpg.d/TurboVNC.gpg; \
    wget -O /etc/apt/sources.list.d/TurboVNC.list https://raw.githubusercontent.com/TurboVNC/repo/main/TurboVNC.list; \
    apt-get -y -qq update; \
    apt-get -y -qq install turbovnc; \
    rm -rf /var/lib/apt/lists/*

USER $NB_USER
RUN conda install -y websockify
ENV DISPLAY=:1

# -----------------------------------------------------------------------------
# Oh-my-bash and user shell setup
# -----------------------------------------------------------------------------
USER ${NB_USER}
RUN bash -c "$(curl -fsSL https://raw.githubusercontent.com/ohmybash/oh-my-bash/master/tools/install.sh)" --unattended
# Copy your bashrc (must exist in build context). This file should be owned by NB_USER.
COPY --chown=${NB_USER}:users ./bashrc.sh /home/${NB_USER}/.bashrc

# Update nodejs for Jupyter extensions
RUN mamba install -y -q "nodejs>=22"

# -----------------------------------------------------------------------------
# MuJoCo install (REQUIRES APPROVED BINARIES & KEY)
# -----------------------------------------------------------------------------
# NOTE: Do NOT commit mjkey.txt or MuJoCo archives into a public repo.
# Recommended: use BuildKit secret for mjkey (keeps it out of image history).
ARG MUJOCO_VERSION=mujoco210
ENV MUJOCO_DIR=/root/.mujoco/${MUJOCO_VERSION}
ENV LD_LIBRARY_PATH="${MUJOCO_DIR}/bin:${LD_LIBRARY_PATH}"
ENV MUJOCO_PY_MUJOCO_PATH=${MUJOCO_DIR}

USER root
RUN mkdir -p /root/.mujoco

# If you want to include a local archive during local builds, uncomment the COPY lines below
# and *do not commit* the files to git. Add them to .dockerignore.
# COPY mujoco210.tar.gz /tmp/mujoco210.tar.gz
# COPY mjkey.txt /root/.mujoco/mjkey.txt

# Use BuildKit secret for mjkey (recommended). This RUN requires BuildKit:
#   DOCKER_BUILDKIT=1 docker build --secret id=mjkey,src=./mjkey.txt -t myimage:mujocto .
# If a local /tmp/mujoco210.tar.gz exists (from COPY), it will be unpacked.
# --- Binder-safe MuJoCo unpack (no BuildKit secrets) ---
# If you want MuJoCo in Binder builds, you MUST have the archive and key in the repo (not recommended for public repos).
# This block will unpack /tmp/mujoco210.tar.gz if present in the build context
# and will use /root/.mujoco/mjkey.txt if it was provided by platform admins (or if you added it).
RUN if [ -f /tmp/mujoco210.tar.gz ]; then \
      mkdir -p /root/.mujoco && \
      tar -xzf /tmp/mujoco210.tar.gz -C /root/.mujoco && \
      rm -f /tmp/mujoco210.tar.gz ; \
    fi && \
    # If a mjkey file was copied into the image (not recommended to commit), ensure correct perms:
    if [ -f /root/.mujoco/mjkey.txt ]; then \
      chmod 600 /root/.mujoco/mjkey.txt ; \
    fi && \
    chown -R root:root /root/.mujoco || true && chmod -R a+rX /root/.mujoco || true


# Install mujoco Python bindings (will fail if incompatible with native libs)
# Remove/comment this line if you prefer to install mujoco only when binaries are present.
RUN /opt/conda/bin/pip install --no-cache-dir mujoco

# If your code depends on legacy mujoco-py, uncomment and use only with matching binaries:
# RUN /opt/conda/bin/pip install --no-cache-dir "mujoco-py==2.1.2.14"

# -----------------------------------------------------------------------------
# ROS Noetic: apt repo and installation
# -----------------------------------------------------------------------------
# Use modern apt key handling (signed-by)
RUN curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | gpg --dearmor > /usr/share/keyrings/ros-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" \
      > /etc/apt/sources.list.d/ros-latest.list

RUN apt-get update -y && \
    apt-get dist-upgrade -y && \
    apt-get install -y --no-install-recommends \
      ros-${ROS_DISTRO}-${ROS_PKG} \
      ros-${ROS_DISTRO}-tf2-tools && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Source ROS setup for both root and NB_USER shells
RUN echo "source ${ROS_PATH}/setup.bash" >> /root/.bashrc
RUN echo "source ${ROS_PATH}/setup.bash" >> /home/${NB_USER}/.bashrc

# -----------------------------------------------------------------------------
# Python packages (install as root via conda's pip for stability)
# -----------------------------------------------------------------------------
USER root
SHELL ["conda", "run", "-n", "base", "/bin/bash", "-c"]
RUN /opt/conda/bin/pip install --no-cache-dir \
    autobahn \
    catkin-tools \
    cbor2 \
    cryptography==38.0.4 \
    empy==3.3.4 \
    gnupg \
    ipywidgets \
    "jupyterlab~=4.0.0" \
    sidecar \
    jupyter-resource-usage \
    jupyter-offlinenotebook \
    jupyter-server-proxy \
    jupyter-remote-desktop-proxy \
    jupyter-archive \
    jupyterlab_execute_time \
    jupyterlab-language-pack-de-DE \
    service_identity \
    pymongo \
    Pillow \
    pycryptodomex \
    pyyaml==5.3.1 \
    rosdep \
    rosinstall \
    rosinstall-generator \
    rosdistro \
    simplejpeg \
    twisted \
    vcstool \
    wstool \
    pybullet \
&& /opt/conda/bin/pip cache purge

# -----------------------------------------------------------------------------
# JupyterLab custom extensions
# -----------------------------------------------------------------------------
RUN /opt/conda/bin/pip install \
  https://raw.githubusercontent.com/yxzhan/jupyterlab-rviz/master/dist/jupyterlab_rviz-0.3.2.tar.gz \
  https://raw.githubusercontent.com/yxzhan/extension-examples/main/cell-toolbar/dist/jupyterlab_examples_cell_toolbar-0.1.4.tar.gz

# -----------------------------------------------------------------------------
# code-server (VS Code server)
# -----------------------------------------------------------------------------
USER ${NB_USER}
RUN mamba install -y code-server
RUN echo 'alias code="$(which code-server)"' >> /home/${NB_USER}/.bashrc
# install some extensions for code-server
RUN code-server --install-extension ms-python.python \
  && code-server --install-extension ms-toolsai.jupyter

# jupyter-code-server bridge
USER root
RUN /opt/conda/bin/pip install -U tornado
USER ${NB_USER}
RUN /opt/conda/bin/pip install git+https://github.com/yxzhan/jupyter-code-server.git

# -----------------------------------------------------------------------------
# Create a ROS workspace with Robot Web Tools (rvizweb)
# -----------------------------------------------------------------------------
USER ${NB_USER}
RUN mkdir -p ${ROS_WS}/src
WORKDIR ${ROS_WS}

USER root
RUN rosdep init || true

USER ${NB_USER}
RUN catkin init && \
    cd src && \
    wstool init && \
    wstool merge https://raw.githubusercontent.com/yxzhan/rvizweb/master/.rosinstall && \
    wstool update && \
    catkin config --extend ${ROS_PATH}

USER root
RUN apt-get update -y && \
    rosdep update --include-eol-distros && \
    rosdep install -y --ignore-src --from-paths ./ -r && \
    rosdep fix-permissions || true

USER ${NB_USER}
RUN catkin build
RUN echo "source ${ROS_WS}/devel/setup.bash" >> /home/${NB_USER}/.bashrc

USER ${NB_USER}
WORKDIR /home/${NB_USER}

# -----------------------------------------------------------------------------
# Copy JupyterLab UI settings and webapps config
# -----------------------------------------------------------------------------
COPY --chown=${NB_USER}:users ./jupyter-settings.json /opt/conda/share/jupyter/lab/settings/overrides.json
COPY --chown=${NB_USER}:users webapps.json ${ROS_WS}/src/rvizweb/webapps/app.json

# -----------------------------------------------------------------------------
# Entrypoint and default command
# -----------------------------------------------------------------------------
COPY --chown=${NB_USER}:users entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]
CMD [ "start-notebook.sh" ]

