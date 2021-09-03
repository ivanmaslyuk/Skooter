def hex_to_rgb(hex_code):
    if not (hex_code.startswith('#') and len(hex_code) == 7):
        raise Exception(f'Got unexpected color value {hex_code}. Only hex color values are supported.')

    color_hex = hex_code.strip('#')
    r = int(color_hex[0:2], base=16)
    g = int(color_hex[2:4], base=16)
    b = int(color_hex[4:6], base=16)
    return r, g, b
