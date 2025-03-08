import Metashape


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

