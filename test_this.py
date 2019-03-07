import vtk  # noqua: F401
import vtkzbhps


def test_instantiation():
    cpt = vtkzbhps.vtkCPTDistanceField2D()
    assert cpt.GetDomain() == (0.0, 0.0, 0.0, 0.0)
    pw = vtkzbhps.vtkProsthesisWidget()
    assert pw.GetEnabled() == 0
