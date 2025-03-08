import Metashape


def run_m_thinning():
    chunk = Metashape.app.document.chunk
    step = Metashape.app.getInt("Specify the selection step:", 2)
    index = 1
    for camera in chunk.cameras:
        if not (index % step):
            camera.selected = True
        else:
            camera.selected = False
        index += 1


Metashape.app.addMenuItem("🛠 GIS scripts/M thinning [m_thinning.py]", run_m_thinning)
