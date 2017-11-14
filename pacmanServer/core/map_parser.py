import xml.etree.ElementTree
import os.path


class SVGMapParser:
    def __init__(self, file: str):
        if not os.path.isfile(file):
            raise OSError('Map file does not exist')

        it = xml.etree.ElementTree.iterparse(file)
        for _, el in it:
            if '}' in el.tag:
                el.tag = el.tag.split('}', 1)[1]  # strip all namespaces
        self._root = it.root

    def get_dimensions(self):
        screen_width = int(self._root.attrib['width'].rstrip('.px'))
        screen_height = int(self._root.attrib['height'].rstrip('.px'))
        return screen_width, screen_height

    def get_blocks(self):
        for child in self._root.findall('rect'):
            x = int(child.attrib['x'])
            y = int(child.attrib['y'])
            width = int(child.attrib['width'])
            height = int(child.attrib['height'])
            if 'transform' in child.attrib:
                rotate = child.attrib['transform']
                angle = int(rotate[rotate.find("(") + 1:rotate.find(")")])
            else:
                angle = 0
            h = child.attrib['fill'].lstrip('#')
            color = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
            yield (x, y, width, height, angle, color)
