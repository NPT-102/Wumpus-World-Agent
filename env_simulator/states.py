import re

class States:
    def __init__(self, pit, wumpus, map, is_random=False):
        self.gold = None
        for i, row in enumerate(map):
            for j, cell in enumerate(row):
                if "G" in cell:
                    self.gold = (i, j)
                    break
            if self.gold:
                break
        self.N = len(map)
        self.actions = [(0, 0, 'N', '')]
        self.pits = [pit]
        self.wumpuses = [wumpus]
        self.knowledge = ['-'*self.N*self.N]

    def add(self, agent, result, pit, wumpus, knowledge=None):
        """
        Ghi lại trạng thái mới của trò chơi sau khi agent vừa hoàn thành 1 hành động

        Parameters
        ----------
        agent : Agent
            Đối tượng agent hiện tại, chứa thông tin vị trí và hướng nhìn.
        result : str
            Kết quả hành động vừa thực hiện. Các giá trị hợp lệ:
            - 'killed' : agent vừa giết được một Wumpus.
            - 'missed' : agent vừa bắn nhưng không trúng Wumpus.
            - 'gold'   : agent vừa nhặt được vàng.
            - 'escaped': agent vừa thoát khỏi mê cung.
            - 'die'    : agent vừa chết
            - ''       : agent vừa làm hành động không cần minh họa
        pit : list[tuple[int, int]]
            Danh sách tọa độ các hố trong bản đồ.
        wumpus : list[tuple[int, int]]
            Danh sách tọa độ các Wumpus còn sống trong bản đồ.
        knowledge : optional
            knowledge base chứa fact các ô safe và deadly.

        Returns
        -------
        None
            Hàm này chỉ ghi lại trạng thái, không trả về giá trị.
        """
        def kb_to_grid_string(kb):
            #  "$" = Safe, "!" = Deadly, "-" = unknown
            grid = ["-"] * (self.N * self.N)
            
            for s in kb:
                match = re.match(r"Safe\((\d+),\s*(\d+)\)", s)
                if match:
                    i, j = int(match.group(1)), int(match.group(2))
                    grid[i * self.N + j] = "$"
                    continue
                match = re.match(r"Deadly\((\d+),\s*(\d+)\)", s)
                if match:
                    i, j = int(match.group(1)), int(match.group(2))
                    grid[i * self.N + j] = "!"
            return "".join(grid)

        i, j = agent.position
        self.actions.append((i, j, agent.direction, result))
        self.pits.append(pit)
        self.wumpuses.append(wumpus)
        if knowledge is None:
            self.knowledge.append('-'*self.n)
        else:
            self.knowledge.append(kb_to_grid_string(knowledge.facts))