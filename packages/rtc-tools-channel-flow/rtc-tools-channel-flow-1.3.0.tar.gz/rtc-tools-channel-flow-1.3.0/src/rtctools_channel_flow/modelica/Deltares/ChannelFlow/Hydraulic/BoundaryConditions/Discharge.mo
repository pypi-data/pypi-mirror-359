within Deltares.ChannelFlow.Hydraulic.BoundaryConditions;

model Discharge "Defines a discharge"
  /*
  Note: The default medium is FreshWater.
  To use a different medium, decalre the choice in your model file, for example
  replaceable package MyMedium = Deltares.ChannelFlow.Media.SalineWater;
  Pass this as an argument to the Discharge block (redeclare package medium=MyMedium)
  */
  extends Deltares.ChannelFlow.Internal.HQOnePort;
  function smooth_switch = Deltares.ChannelFlow.Internal.Functions.SmoothSwitch;
  input Modelica.Units.SI.VolumeFlowRate Q;
  input Modelica.Units.SI.MassFlowRate M[medium.n_substances];
  parameter Boolean upwind = true; // If true and there is outlfow from the system (into the discharge boudnary) then the concentration of the connected element is used.
equation
  HQ.Q + Q = 0;
  if upwind then
    // We don't use SmoothSwitch here, as we assume Q to be a constant input.
    if Q > 0 then
      HQ.M = -M;
    else
      HQ.M = -Q * HQ.C;
    end if;
  else
    HQ.M = -M;
  end if;
  annotation(Icon(coordinateSystem(extent = {{-100, -100}, {100, 100}}, preserveAspectRatio = true, initialScale = 0.1, grid = {10, 10}), graphics = {Polygon(visible = true, fillColor = {255, 0, 255}, fillPattern = FillPattern.Solid, points = {{0, -40}, {50, 40}, {-50, 40}})}));
end Discharge;
