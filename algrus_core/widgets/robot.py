import time
import uuid

from IPython.display import display, update_display, HTML

class RobotWidget:
    def __init__(self, size=10, publish=None):
        # size оставлен для совместимости; width/height задают реальные
        # размеры поля и могут отличаться для прямоугольной карты.
        self.size = size
        self.width = size
        self.height = size
        self.pos_x = 0
        self.pos_y = 0
        self.direction = 0  # 0=вверх, 1=вправо, 2=вниз, 3=влево
        self.painted = set()
        self.walls = set()
        # Клетка-выход (символ «2» в карте), если задана.
        self.exit = None
        self.step_delay = 0.3
        self._display_id = None
        # publish — функция ядра, отправляющая display_data в iopub.
        # Нужна потому, что AlgrusKernel наследуется от kernelbase.Kernel,
        # где IPython.display.display() не инициализирован и возвращает None.
        self._publish = publish


    def _render_html(self):
        # Цвета
        bg = "#fafafa"
        grid = "#e0e0e0"
        wall_color = "#555"
        paint_color = "#ffe066"
        robot_color = "#e03131"

        cell = 40
        canvas_width = self.width * cell
        canvas_height = self.height * cell

        # Генерируем SVG (проще, чем Canvas, и работает везде)
        svg = f'<svg width="{canvas_width}" height="{canvas_height}" style="background:{bg}; border:1px solid #ccc;">'

        # Сетка
        for x in range(self.width + 1):
            svg += f'<line x1="{x*cell}" y1="0" x2="{x*cell}" y2="{canvas_height}" stroke="{grid}"/>'
        for y in range(self.height + 1):
            svg += f'<line x1="0" y1="{y*cell}" x2="{canvas_width}" y2="{y*cell}" stroke="{grid}"/>'

        # Стены
        for (x, y) in self.walls:
            svg += f'<rect x="{x*cell}" y="{y*cell}" width="{cell}" height="{cell}" fill="{wall_color}"/>'

        # Закрашенные клетки
        for (x, y) in self.painted:
            svg += f'<rect x="{x*cell+2}" y="{y*cell+2}" width="{cell-4}" height="{cell-4}" fill="{paint_color}"/>'

        # Выход из лабиринта
        if self.exit is not None:
            ex, ey = self.exit
            svg += (
                f'<rect x="{ex*cell+6}" y="{ey*cell+6}" '
                f'width="{cell-12}" height="{cell-12}" fill="#2f9e44"/>'
                f'<text x="{ex*cell+cell//2}" y="{ey*cell+cell//2}" '
                f'font-family="sans-serif" font-size="18" fill="white" '
                f'text-anchor="middle" dominant-baseline="central">В</text>'
            )

        # Робот (треугольник)
        cx = self.pos_x * cell + cell // 2
        cy = self.pos_y * cell + cell // 2
        r = cell // 3

        if self.direction == 0:    # вверх
            pts = f"{cx},{cy-r} {cx-r},{cy+r} {cx+r},{cy+r}"
        elif self.direction == 1:  # вправо
            pts = f"{cx+r},{cy} {cx-r},{cy-r} {cx-r},{cy+r}"
        elif self.direction == 2:  # вниз
            pts = f"{cx},{cy+r} {cx-r},{cy-r} {cx+r},{cy-r}"
        else:                      # влево
            pts = f"{cx-r},{cy} {cx+r},{cy-r} {cx+r},{cy+r}"

        svg += f'<polygon points="{pts}" fill="{robot_color}"/>'
        svg += '</svg>'
        return svg

    def show(self):
        html = self._render_html()

        # В ядре Jupyter отправляем сообщения напрямую через iopub.
        # Первое сообщение — display_data (создаёт вывод), все следующие —
        # update_display_data (только обновляют его, не добавляя копий).
        if self._publish is not None:
            if self._display_id is None:
                self._display_id = uuid.uuid4().hex
                msg_type = 'display_data'
            else:
                msg_type = 'update_display_data'
            self._publish(msg_type, {
                'data': {'text/html': html},
                'metadata': {},
                'transient': {'display_id': self._display_id},
            })
            return

        # Запасной вариант: обычный IPython с запущенным shell.
        if self._display_id:
            update_display(HTML(html), display_id=self._display_id)
        else:
            handle = display(HTML(html), display_id=True)
            if handle is not None:
                self._display_id = handle.display_id

    def reset_view(self):
        """Начинает новый вывод робота в текущей ячейке."""
        self._display_id = None


    def _update(self):
        """Перерисовывает виджет."""
        self.show()
        time.sleep(self.step_delay)

    def _cell_free(self, x, y):
        """Свободна ли клетка (вне поля считается стеной)."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        return (x, y) not in self.walls

    def _wall_ahead(self):
        dx, dy = [(0,-1), (1,0), (0,1), (-1,0)][self.direction]
        return not self._cell_free(self.pos_x + dx, self.pos_y + dy)

    # --- Датчики робота ---
    def впереди_свободно(self):
        dx, dy = [(0,-1), (1,0), (0,1), (-1,0)][self.direction]
        return self._cell_free(self.pos_x + dx, self.pos_y + dy)

    def справа_свободно(self):
        dx, dy = [(0,-1), (1,0), (0,1), (-1,0)][(self.direction + 1) % 4]
        return self._cell_free(self.pos_x + dx, self.pos_y + dy)

    def слева_свободно(self):
        dx, dy = [(0,-1), (1,0), (0,1), (-1,0)][(self.direction - 1) % 4]
        return self._cell_free(self.pos_x + dx, self.pos_y + dy)

    def на_выходе(self):
        return self.exit is not None and (self.pos_x, self.pos_y) == self.exit

    # --- Команды Робота ---
    def сброс(self):
        self.pos_x = 0
        self.pos_y = 0
        self.direction = 0
        self.painted.clear()
        self._update()
    def вперед(self):
        if self._wall_ahead():
            raise RuntimeError("Робот упёрся в стену")
        dx, dy = [(0,-1), (1,0), (0,1), (-1,0)][self.direction]
        self.pos_x += dx
        self.pos_y += dy
        self._update()

    def влево(self):
        self.direction = (self.direction - 1) % 4
        self._update()

    def вправо(self):
        self.direction = (self.direction + 1) % 4
        self._update()

    def закрасить(self):
        self.painted.add((self.pos_x, self.pos_y))
        self._update()

    def задать_карту(self, *карты):
        """Задаёт стены из строк: 1 — стена, 0 — свободно, 2 — выход.

        Первая строка — y=0, символ с индексом x — координата (x, y).
        """
        self.walls.clear()
        self.exit = None

        for y, row in enumerate(карты):
            for x, char in enumerate(row):
                if char == '1':
                    self.walls.add((x, y))
                elif char == '2':
                    # «2» — свободная клетка, отмеченная как выход.
                    self.exit = (x, y)

        # Поле принимает размеры карты (может быть прямоугольным).
        if карты:
            self.height = len(карты)
            self.width = max(len(row) for row in карты)
            self.size = max(self.width, self.height)

        self._update()

    def залить(self):
        """Закрашивает всю свободную область вокруг робота (без рекурсии)."""
        start = (self.pos_x, self.pos_y)
        if start in self.walls:
            return

        stack = [start]
        seen = set()

        while stack:
            x, y = stack.pop()
            if (x, y) in seen or (x, y) in self.walls:
                continue
            if not (0 <= x < self.width and 0 <= y < self.height):
                continue

            seen.add((x, y))
            self.painted.add((x, y))
            stack.append((x + 1, y))
            stack.append((x - 1, y))
            stack.append((x, y + 1))
            stack.append((x, y - 1))

        self._update()

    def найти_выход(self):
        """Ведёт робота к отмеченному выходу по кратчайшему пути (BFS)."""
        from collections import deque

        if self.exit is None:
            raise RuntimeError(
                'Выход не задан: отметьте клетку выхода цифрой 2 в карте'
            )

        start = (self.pos_x, self.pos_y)
        if start == self.exit:
            return

        directions = ((0, -1), (1, 0), (0, 1), (-1, 0))
        queue = deque([start])
        parent = {start: None}

        while queue:
            x, y = queue.popleft()
            if (x, y) == self.exit:
                break
            for dx, dy in directions:
                neighbour = (x + dx, y + dy)
                if neighbour not in parent and self._cell_free(*neighbour):
                    parent[neighbour] = (x, y)
                    queue.append(neighbour)

        if self.exit not in parent:
            raise RuntimeError('Выход недостижим из текущей клетки')

        path = []
        cell = self.exit
        while cell is not None:
            path.append(cell)
            cell = parent[cell]
        path.reverse()

        # Идём по найденному пути, разворачивая робота в нужную сторону.
        for nx, ny in path[1:]:
            dx, dy = nx - self.pos_x, ny - self.pos_y
            self.direction = directions.index((dx, dy))
            self.pos_x, self.pos_y = nx, ny
            self._update()

    def стена_впереди(self):
        return self._wall_ahead()

    def клетка_закрашена(self):
        return (self.pos_x, self.pos_y) in self.painted
