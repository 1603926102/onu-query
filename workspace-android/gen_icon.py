import sys
import os

# Generate icon using pure Python (no PIL needed)
# Create a simple 512x512 PNG icon with a network/wifi signal design

def create_png_chunk(chunk_type, data):
    """Create a PNG chunk"""
    import struct, zlib
    chunk_len = struct.pack('>I', len(data))
    chunk_crc = struct.pack('>I', zlib.crc32(chunk_type + data) & 0xffffffff)
    return chunk_len + chunk_type + data + chunk_crc

def create_icon():
    size = 512
    channels = 4  # RGBA
    
    # Create image data (RGBA)
    img = [[0, 0, 0, 0] for _ in range(size * size)]
    
    def set_pixel(x, y, r, g, b, a=255):
        if 0 <= x < size and 0 <= y < size:
            img[y * size + x] = [r, g, b, a]
    
    def fill_circle(cx, cy, r, r_c, g_c, b_c):
        for y in range(max(0, cy - r), min(size, cy + r + 1)):
            for x in range(max(0, cx - r), min(size, cx + r + 1)):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r ** 2:
                    set_pixel(x, y, r_c, g_c, b_c, 255)
    
    def fill_rect(x1, y1, x2, y2, r_c, g_c, b_c):
        for y in range(max(0, y1), min(size, y2)):
            for x in range(max(0, x1), min(size, x2)):
                set_pixel(x, y, r_c, g_c, b_c, 255)
    
    # Background - rounded square (blue gradient)
    cx, cy = size // 2, size // 2
    radius = size // 2 - 8
    
    # Blue background gradient (top to bottom)
    for y in range(size):
        for x in range(size):
            if (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2:
                # Gradient from #1976D2 to #0D47A1
                ratio = y / size
                r = int(25 + ratio * (13 - 25))
                g = int(118 + ratio * (71 - 118))
                b = int(210 + ratio * (161 - 210))
                set_pixel(x, y, r, g, b, 255)
    
    # Draw WiFi/signal icon (white arcs)
    # Center dot
    fill_circle(cx, cy + 60, 18, 255, 255, 255)
    
    # Arc 1 (inner)
    r1 = 80
    for angle in range(-60, 61):
        import math
        rad = math.radians(angle)
        x = int(cx + r1 * math.sin(rad))
        y = int(cy + 60 - r1 * math.cos(rad))
        fill_circle(x, y, 18, 255, 255, 255)
    
    # Arc 2 (middle)
    r2 = 140
    for angle in range(-55, 56):
        import math
        rad = math.radians(angle)
        x = int(cx + r2 * math.sin(rad))
        y = int(cy + 60 - r2 * math.cos(rad))
        fill_circle(x, y, 18, 255, 255, 255)
    
    # Arc 3 (outer)
    r3 = 200
    for angle in range(-50, 51):
        import math
        rad = math.radians(angle)
        x = int(cx + r3 * math.sin(rad))
        y = int(cy + 60 - r3 * math.cos(rad))
        fill_circle(x, y, 18, 255, 255, 255)
    
    # Serialize to raw bytes
    raw = b''
    for y in range(size):
        raw += b'\x00'  # filter type
        for x in range(size):
            r, g, b, a = img[y * size + x]
            raw += bytes([r, g, b, a])
    
    # PNG signature
    signature = b'\x89PNG\r\n\x1a\n'
    
    # IHDR chunk
    import struct, zlib
    ihdr_data = struct.pack('>IIBBBBB', size, size, 8, 6, 0, 0, 0)
    ihdr = create_png_chunk(b'IHDR', ihdr_data)
    
    # IDAT chunk
    compressed = zlib.compress(raw, 9)
    idat = create_png_chunk(b'IDAT', compressed)
    
    # IEND chunk
    iend = create_png_chunk(b'IEND', b'')
    
    return signature + ihdr + idat + iend

# Generate icons
png_data = create_icon()
out_path = os.path.join(os.path.dirname(sys.argv[0]), 'icon.png')
with open(out_path, 'wb') as f:
    f.write(png_data)
print(f"Icon created: {out_path} ({len(png_data)} bytes)")
