import cairo
import collections
import math
import pango
import pangocairo

from PIL import Image

FONT_NAME = 'Aharoni'
RUNOUT = 50
TEXT_PADDING = 30
THUMBNAIL_SIZE = (1280, 720)

BoxSpec = collections.namedtuple(
    'BoxSpec', ['x', 'y', 'width', 'height', 'angle', 'fg_color', 'bg_color'])

TITLE_BOX = BoxSpec(22, 480, 1200, 116, -2.0, '000000', 'c56000')
SUBTITLE_BOX = BoxSpec(148, 570, None, 100, 2.5, 'e3e3e3', 'c58800')

def _parse_color(color_str):
  args = [iter(color_str)] * 2
  return tuple([float(int(''.join(c), base=16)) / 255. for c in zip(*args)])

def _surface_for_bg_image(bg_image_file):
  bg_img = Image.open(bg_image_file)
  img = bg_img.resize(THUMBNAIL_SIZE, Image.LANCZOS)
  data = bytearray(img.tobytes('raw', 'BGRA', 0, 1))
  return cairo.ImageSurface.create_for_data(
      data, cairo.FORMAT_ARGB32, *THUMBNAIL_SIZE)

def _layout_text(pc, text, height):
  layout = pc.create_layout()
  layout.set_font_description(pango.FontDescription(FONT_NAME))
  layout.set_text(text)

  extents = layout.get_line(0).get_extents()[1]
  layout_width = pango.units_to_double(extents[2])
  layout_height = pango.units_to_double(pango.ASCENT(extents))
  scale_ratio = float(height) / layout_height
  return layout, scale_ratio, scale_ratio * layout_width

def _draw_box(spec, text, c):
  # Text layout
  pc = pangocairo.CairoContext(c)
  text_layout, scale_ratio, text_width = _layout_text(
      pc, text, spec.height - 2 * TEXT_PADDING)

  # Global transform
  c.save()
  c.translate(spec.x, spec.y)
  c.rotate(spec.angle * math.pi / 180.)

  # Background
  if spec.width:
    width = spec.width
  else:
    width = text_width + 2 * TEXT_PADDING + RUNOUT
  c.set_source_rgb(*_parse_color(spec.bg_color))
  c.rectangle(0, 0, width, spec.height)
  c.fill()

  # Foreground
  c.translate(TEXT_PADDING, TEXT_PADDING)
  c.scale(scale_ratio, scale_ratio)
  c.set_source_rgb(*_parse_color(spec.fg_color))
  pc.show_layout(text_layout)
  c.restore()

def _draw_overlay(surface, title, subtitle):
  c = cairo.Context(surface)
  _draw_box(SUBTITLE_BOX, subtitle, c)
  _draw_box(TITLE_BOX, title, c)

def generate_thumbnail(bg_image_file, title, subtitle, out_file):
  surface = _surface_for_bg_image(bg_image_file)
  _draw_overlay(surface, title, subtitle)
  surface.write_to_png(out_file)

def generate_mask(out_file):
  surface = cairo.SVGSurface(out_file, *THUMBNAIL_SIZE)
  c = cairo.Context(surface)
  c.set_source_rgba(0, 0, 0, 0.5)
  c.rectangle(0, 0, *THUMBNAIL_SIZE)
  c.fill()
  _draw_overlay(surface, 'Title', 'Subtitle')
  surface.finish()
