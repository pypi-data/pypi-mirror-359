<!-- markdownlint-disable MD033 MD041 -->
<p align="center">
  <h1 align="center">textdraw</h1>
</p>
<p align="center">
    <img alt="GitHub Release" src="https://img.shields.io/github/v/release/denehoffman/textdraw?style=for-the-badge&logo=github"></a>
  <a href="https://github.com/denehoffman/textdraw/commits/main/" alt="Latest Commits">
    <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/denehoffman/textdraw?style=for-the-badge&logo=github"></a>
  <a href="LICENSE-APACHE" alt="License">
    <img alt="GitHub License" src="https://img.shields.io/github/license/denehoffman/textdraw?style=for-the-badge"></a>
  <a href="https://pypi.org/project/textdraw/" alt="View project on PyPI">
  <img alt="PyPI - Version" src="https://img.shields.io/pypi/v/textdraw?style=for-the-badge&logo=python&logoColor=yellow&labelColor=blue"></a>
</p>

`textdraw` is a Python library for drawing styled Unicode boxes and diagrams. Paths between points
can be generated via an A* path-finding algorithm, and text objects can be
composed to create complex layouts.

<!--toc:start-->
- [Features](#features)
- [Installation](#installation)
- [Examples](#examples)
  - [Boxed Hello World](#boxed-hello-world)
  - [Connecting boxes](#connecting-boxes)
  - [Multiple connected boxes](#multiple-connected-boxes)
  - [A Complex Example](#a-complex-example)
- [Future Plans](#future-plans)
- [Contributing](#contributing)
<!--toc:end-->

## Features

- Unicode box-drawing with `light`, `heavy`, and `double` borders
- Automatic path-finding powered by Rust backend
- Flexible padding and justification for text boxes
- Support for cleanly merging path intersections

## Installation

```shell
pip install textdraw
```

Or with `uv`:

```shell
uv pip install textdraw
```

## Examples

### Boxed Hello World

```python
from textdraw import Box, render


box = Box('Hello, world', style='italic', border_style='bold blue', line_style='double', padding=(1, 2, 1, 2))
print(render(box))
```

<p align="center">
  <img
    width="300"
    src="media/hello-world.png"
    alt="Boxed Hello World result"
  />
</p>

### Connecting boxes

```python
from textdraw import Box, Pixel, TextPath, render, Point


a = Box('A', (-20, 10), border_style='green', padding=(0, 1, 0, 1))
b = Box('B', (0, 0), border_style='red', padding=(0, 1, 0, 1))
print(a.bbox)
start_node = Pixel('', a.bbox.bottom_right + Point(1, 0), style='red')
end_node = Pixel('◼', b.bbox.top_left - Point(1, 0), style='green')
path = TextPath(
    a.bbox.bottom_right + Point(1, -1),
    b.bbox.top_left - Point(2, 0),
    style='dimmed',
    start_direction='up',
    end_direction='right',
    bend_penalty=20,
)
print(render(a, b, start_node, end_node, path))
```

<p align="center">
  <img
    width="300"
    src="media/connected-boxes.png"
    alt="Connecting boxes result"
  />
</p>

### Multiple connected boxes

```python
from textdraw import Box, TextPath, render


boxes = {
    'A': (0, 0),
    'B': (30, 0),
    'C': (0, -8),
    'D': (30, -8),
    'E': (15, -4),
    'F': (15, -12),
}
objs = []
coords = {}
for label, (x, y) in boxes.items():
    box = Box(label, (x, y), border_style='bold white', style='bold', line_style='heavy', padding=(0, 1, 0, 1))
    objs.append(box)
    coords[label] = box.bbox.center

paths = [
    ('A', 'B', 'red'),
    ('A', 'C', 'green'),
    ('B', 'D', 'blue'),
    ('C', 'D', 'magenta'),
    ('A', 'E', 'yellow'),
    ('F', 'E', 'cyan'),
    ('E', 'D', 'bright_blue'),
]

for start, end, color in paths:
    path = TextPath(coords[start], coords[end], style=color, bend_penalty=0, line_style='heavy')
    objs.append(path)

print(render(*reversed(objs))) # reversed to put boxes on top of paths
```

<p align="center">
  <img
    width="300"
    src="media/multiple-connected-boxes.png"
    alt="Multiple connecting boxes result"
  />
</p>

### A Complex Example

```python
from textdraw import BoundingBox, Box, Pixel, PixelGroup, Point, TextPath, duplicate_shifted, multipath, render


class LetterBox:
    def __init__(self, letter: str, x: int, y: int):
        self.box = Box(letter, (x, y), padding=(0, 1, 0, 1))
        self.c_right = self.box.bbox.center_right + Point(1, 0)
        self.c_left = self.box.bbox.center_left - Point(1, 0)
        self.c_top = self.box.bbox.top_center + Point(0, 1)
        self.c_bottom = self.box.bbox.bottom_center - Point(0, 1)
        barrier = Pixel('⎚', style='blinkfast red', weight=None)
        self.barriers = PixelGroup(
            [
                barrier.duplicate(self.c_left - Point(0, 1)),
                barrier.duplicate(self.c_left + Point(0, 1)),
                barrier.duplicate(self.c_right - Point(0, 1)),
                barrier.duplicate(self.c_right + Point(0, 1)),
                barrier.duplicate(self.c_bottom - Point(1, 0)),
                barrier.duplicate(self.c_bottom + Point(1, 0)),
                barrier.duplicate(self.c_top - Point(1, 0)),
                barrier.duplicate(self.c_top + Point(1, 0)),
            ]
        )

a = LetterBox('a', 0, 0)
b = LetterBox('b', 20, -8)
c = LetterBox('c', 3, -10)
bbox = BoundingBox.wrap(a.box, b.box, c.box)
bbox.top += 7
bbox.bottom -= 7
bbox.left -= 7
bbox.right += 7

all_barriers = [a.barriers, b.barriers, c.barriers, a.box, b.box, c.box]
paths = []
paths.append(
    TextPath(
        a.c_right,
        b.c_top,
        style='dimmed',
        weight=20,
        bend_penalty=20,
        environment=paths,
        barriers=all_barriers,
        bbox=bbox,
    )
)
paths.append(
    TextPath(
        a.c_bottom,
        b.c_left,
        style='green',
        weight=20,
        bend_penalty=20,
        environment=paths,
        barriers=all_barriers,
        bbox=bbox,
    )
)

paths.append(
    TextPath(
        a.c_left,
        c.c_top,
        style='blue',
        weight=20,
        bend_penalty=20,
        environment=paths,
        barriers=all_barriers,
        bbox=bbox,
    )
)

paths.append(
    TextPath(
        b.c_bottom,
        c.c_left,
        style='red',
        line_style='double',
        weight=20,
        bend_penalty=20,
        environment=paths,
        barriers=all_barriers,
        bbox=bbox,
    )
)
shared_paths = multipath(
    [c.c_bottom, b.c_left, a.c_top],
    [a.c_right, c.c_right, b.c_right],
    style='yellow',
    line_style='heavy',
    bend_penalty=20,
    environment=paths,
    barriers=all_barriers,
    bbox=bbox,
    optimize=True,
)
objs = [a.box, b.box, c.box, *paths, *shared_paths]
bbox = BoundingBox.wrap(*objs)
objs_shifted = duplicate_shifted(
    [*objs, a.barriers, b.barriers, c.barriers],
    Point(bbox.width + 3, 0),
)
print(render(*objs, *objs_shifted))
```

<p align="center">
  <img
    width="300"
    src="media/letter-box.png"
    alt="letterbox result"
  />
</p>

## Future Plans

This project was mostly a tool I wanted to create for a graph-drawing project.
However, there are some features that would be beneficial:

- Combination characters like `╤` to combine different path styles or connect
  paths with boxes directly (the latter can be done but only manually)
- A convention to use for placing arrowheads at the ends of `TextPath`s.
  Currently, this can be done manually with `Pixel`s and the `arrow` function.

## Contributing

I'm open to any contributions. Please create an issue and/or pull request,
I'll try to respond quickly.
