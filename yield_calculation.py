import photovoltaic as pv
from photovoltaic.core import arccosd, arcsind, cosd, sind

class YieldEstimation:

    def __init__(
        self, 
        module_azimuth, 
        module_elevation, 
        module_area, 
        rated_power, 
        maximum_power_point_current, 
        system_voltage, 
        module_efficiency, 
        nrel_data,
        gmt_offset,
        latitude,
        longitude) -> None:

        self.module_azimuth = module_azimuth
        self.module_elevation = module_elevation
        self.module_area = module_area
        self.rated_power = rated_power
        self.maximum_power_point_current = maximum_power_point_current
        self.system_voltage = system_voltage
        self.module_efficiency = module_efficiency
        self.nrel_data = nrel_data
        self.gmt_offset = int(gmt_offset)
        self.latitude = float(latitude)
        self.longitude = float(longitude)
    
    def get_total_yearly_power(self):
        print(self.nrel_data.head())
        # Calculate the elevation and azimuth of the sun for every hour of the year
        self.nrel_data['elevations'], self.nrel_data['azimuths'] = pv.sun.sun_position(
            dayNo = self.nrel_data['Day'], 
            latitude = self.latitude, 
            longitude = self.longitude, 
            GMTOffset = self.gmt_offset,
            H = self.nrel_data['Hour'],
            M = 0
            )
        
        # Compare the sun position to the module angle to calculate the fraction of direct irradiance
        self.nrel_data['fraction_normal_to_module'] = pv.sun.module_direct(
            self.nrel_data['azimuths'], 
            self.nrel_data['elevations'],
            self.module_azimuth, 
            self.module_elevation
            )
        
        # calculate the direct normal irradiance on the module:
        self.nrel_data['DNI_module'] = self.nrel_data['DNI'] * self.nrel_data['fraction_normal_to_module']

        # diffuse horizontal irradiance calculation:
        self.nrel_data['diffuse_module'] = self.nrel_data['DHI'] * (180 - self.module_elevation) / 180

        # Total module irradiance in W/m^2
        self.nrel_data['total_module'] = self.nrel_data['diffuse_module'] + self.nrel_data['DNI_module']

        self.nrel_data['PV_Array_Ah'] = self.nrel_data['total_module'] * self.maximum_power_point_current / 1000

        P_yearly = self.module_area * self.rated_power * self.nrel_data['total_module'].sum() / 1e3

        return P_yearly


    
