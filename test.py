url = f'https://mt1.google.com/vt/lyrs={self.layer}&x={start_x + x}&y={start_y + y}&z={self.zoom}'

# tile image file name:
current_tile = f'{str(x)}-{str(y)}'

# the tile image data is store into current_tile after url request
print('one')
urllib.request.urlretrieve(url, current_tile)