import os
from PIL import Image
import math
from math import cos, pi, pow, radians
import urllib.request
import numpy as np
import time


# class GoogleMapsLayers:
#   ROADMAP = "v"
#   TERRAIN = "p"
#   ALTERED_ROADMAP = "r"
#   SATELLITE = "s"
#   TERRAIN_ONLY = "t"
#   HYBRID = "y"

class SatelliteImg:

  def __init__(self, lat, lng, zoom = 19, layer = 's'):
    self.latitude = float(lat)
    self.longitude = float(lng)
    self.zoom = zoom
    self.layer = layer

  def get_img_file(self):

      # tiles
      tile_size = 256 # in pixels
      num_tiles = 1 << self.zoom    # => 2^zoom number of tiles

      point_x = int((tile_size / 2 + self.longitude * tile_size / 360.0) * num_tiles // tile_size)
      sin_y = math.sin(self.latitude * (math.pi / 180.0))
      # get y equivalent of the latitude
      point_y = int(((tile_size / 2) + 0.5 * math.log((1 + sin_y) / (1 - sin_y)) * -(tile_size / (2 * math.pi))) * num_tiles // tile_size)
      # start x and y for the top left tile coordinates
      start_x = point_x
      start_y = point_y

      # sets the number of tiles composing the image:
      tile_width = 3
      tile_height = 3

      # getting the pixel width and height for the entire tile composed image
      width = tile_size * tile_width
      height = tile_size * tile_width

      # creating a new blank image with the desired pixel dimensions.  will be used to store the final image
      map_img = Image.new('RGB', (width, height))
      offset_x = -1
      offset_y = 0
      start_x = start_x + offset_x
      start_y = start_y + offset_y
      
      for x in range(0, tile_width):
          for y in range(0, tile_height):

              # creating google image request url:
              url = f'https://mt1.google.com/vt/lyrs={self.layer}&x={start_x + x}&y={start_y + y}&z={self.zoom}'
              # tile image file name:
              current_tile = f'{str(x)}-{str(y)}'

              # the tile image data is store into current_tile after url request
              try:
                urllib.request.urlretrieve(url, current_tile)
              except Exception as e:
                print(e)
              # open that newly received image tile
              im = Image.open(current_tile)

              # paste that tile in its correct slot
              map_img.paste(im, (x * 256, y * 256))
              os.remove(current_tile)

      img_array = np.array(map_img)
      map_img.close()
    
      return img_array

def get_new_lat_lng(zoom, lat, lng, x_px_offset, y_px_offset):

  # Convert a pixel displacement at a given zoom level into a meter displacement:
  meters_per_px = 156543.03392 * cos(lat * pi / 180) / pow(2, zoom)
  x_m_offset = -x_px_offset * meters_per_px  #  Needs to be generalized.
  y_m_offset = y_px_offset * meters_per_px

  # convert meter displacement into lat, lng displacement:
  # Earth’s radius, sphere
  R = 6378137

  # Coordinate offsets in radians
  d_lat = x_m_offset / R
  d_lng = y_m_offset / (R * cos(pi * lat / 180))

  # OffsetPosition, decimal degrees
  lat_offset = d_lat * 180 / pi
  lng_offset = d_lng * 180 / pi 

  new_lat = lat + lat_offset
  new_lng = lng + lng_offset

  return new_lat, new_lng

