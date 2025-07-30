within Deltares.ChannelFlow.Internal;

partial class Reservoir
// a base class for any reservoir lake: 1) volumes and flows only or 2) volumes, flows and water levels
// no equations for the water balance specified. 
// turbine flow is the portion of the reservoir release that is guided through the power hose.
// spill flow accounts for flow throgh bottom outlet and flow through the spillway
  import SI = Modelica.Units.SI;
  // Inputs
  input SI.VolumeFlowRate Q_turbine;
  input SI.VolumeFlowRate Q_spill;
  // States
  SI.Volume V(min = 0, nominal = 1e6);
equation
  annotation(Icon(coordinateSystem( initialScale = 0.1, grid = {10, 10}), graphics = {Polygon(fillColor = {0, 255, 255}, fillPattern = FillPattern.Solid, points = {{40, 50}, {-45, 0}, {40, -50}, {40, 50}, {40, 50}}), Text(origin = {0, -80}, extent = {{-70, 20}, {70, -20}}, textString = "%name", fontName = "MS Shell Dlg 2")}));
end Reservoir;
