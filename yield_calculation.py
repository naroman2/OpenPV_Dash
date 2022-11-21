import photovoltaic as pv
from photovoltaic.core import arccosd, arcsind, cosd, sind
from datetime import datetime, date, timedelta 

class YieldEstimation:

    def __init__(
        self, 
        module_azimuth, 
        module_elevation, 
        module_area, 
        rated_power, 
        maximum_power_point_current, 
        system_voltage, 
        system_losses, 
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
        self.system_losses = system_losses
        self.nrel_data = nrel_data
        self.gmt_offset = int(gmt_offset)
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.voc_module = 90
        self.jl = 8.35/243.36
    
    def get_total_yearly_power(self):
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

        P_yearly = (self.module_area * self.rated_power * self.nrel_data['total_module'].sum() / 1e6) * (1 - self.system_losses)

        print(self.nrel_data['total_module'].sum() / 1e3)
        print('number of modules', self.module_area)
        print('rated pwer', self.rated_power)
        print(self.system_losses)

        return P_yearly
    
    def get_monthly_yields(self):
        mon_yield = [0, 0, 0, 0, 0, 0, 0, 0, 0,  0,  0,  0] 
        mon_index = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        
        for mon in mon_index:
            for i in self.nrel_data.index:
                yield_month = str(self.nrel_data['Month'][i])
                if str(mon) == yield_month:
                    mon_yield[mon - 1] = mon_yield[mon - 1] + (self.module_area * self.rated_power * self.nrel_data['total_module'][i] / 1e6) * (1 - self.system_losses)
        return mon_yield


    
