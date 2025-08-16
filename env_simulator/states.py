import re

class States:
    def __init__(self, pit, wumpus, is_random=False):
        self.actions = []
        self.pits = [pit]
        self.wumpuses = [wumpus]
        if is_random:
            self.knowledge = ['']
        else:
            self.knowledge = []

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
        def kb_to_grid_string(kb, N):
            #  "$" = Safe, "!" = Deadly, "-" = unknown
            grid = ["-"] * (N * N)
            
            for s in kb:
                match = re.match(r"Safe\((\d+),\s*(\d+)\)", s)
                if match:
                    i, j = int(match.group(1)), int(match.group(2))
                    grid[i * N + j] = "$"
                    continue
                match = re.match(r"Deadly\((\d+),\s*(\d+)\)", s)
                if match:
                    i, j = int(match.group(1)), int(match.group(2))
                    grid[i * N + j] = "!"
            
            return "".join(grid)
        i, j = agent.position
        self.actions.append(i, j, agent.direction, result)
        self.pits.append(pit)
        self.wumpuses.append(wumpus)
        if knowledge is None:
            self.knowledge.append['']
        else:
            self.knowledge.append[kb_to_grid_string(knowledge)]