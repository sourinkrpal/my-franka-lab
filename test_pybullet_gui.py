import pybullet as p
import pybullet_data
import time

print("Connecting to GUI...")
cid = p.connect(p.GUI)
if cid < 0:
    raise RuntimeError("Could not start PyBullet GUI. Make sure VNC Desktop is open.")

# Optional: PyBullet built-in data path
p.setAdditionalSearchPath(pybullet_data.getDataPath())

# Basic physics setup
p.resetSimulation()
p.setGravity(0, 0, -9.81)

# Load a plane from built-in pybullet_data (this file ALWAYS exists)
print("Loading plane...")
p.loadURDF("plane.urdf")

# Create simple shapes (no URDFs needed)
print("Creating demo objects...")
col_box = p.createCollisionShape(p.GEOM_BOX, halfExtents=[0.1, 0.1, 0.1])
col_sphere = p.createCollisionShape(p.GEOM_SPHERE, radius=0.15)

# Create two bodies
p.createMultiBody(baseCollisionShapeIndex=col_box, basePosition=[0, 0, 0.5])
p.createMultiBody(baseCollisionShapeIndex=col_sphere, basePosition=[0.3, 0, 0.6])

print("Running simulation...")
for _ in range(1200):  # ~5 seconds
    p.stepSimulation()
    time.sleep(1.0 / 240.0)

p.disconnect()
print("Done.")
