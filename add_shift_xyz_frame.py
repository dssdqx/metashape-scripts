import Metashape

# Checking compatibility
compatible_major_version = "2.0"
found_major_version = ".".join(Metashape.app.version.split('.')[:2])
if found_major_version != compatible_major_version:
    raise Exception("Incompatible Metashape version: {} != {}".format(
        found_major_version, compatible_major_version))


def add_altitude():
    """
    Adds user-defined altitude for camera instances in the Reference pane
    """

    doc = Metashape.app.document
    if not len(doc.chunks):
        raise Exception("No chunks!")

    dX = Metashape.app.getFloat("Shift Х (coordinate system units):", 0)
    dY = Metashape.app.getFloat("Shift Y (coordinate system units):", 0)
    dZ = Metashape.app.getFloat("Shift Z (coordinate system units):", 0)
    
    print("Script started...")
    chunk = doc.chunk

    for camera in chunk.cameras:
        if camera.reference.location:
            coord = camera.reference.location
            camera.reference.location = Metashape.Vector(
                [coord.x + dX, coord.y + dY, coord.z + dZ])


label = "🛠 GIS scripts/XYZ Shift [add_shift_xyz_frame.py]"
Metashape.app.addMenuItem(label, add_altitude)
print("To execute this script press {}".format(label))
