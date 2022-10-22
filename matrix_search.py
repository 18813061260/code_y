
'''
矩阵路径搜索算法
可以理解为暴力法遍历矩阵中所有字符串的可能性。
DFS通过递归，先朝一个方向搜到底，再回溯至上一个结点，沿另一个方向搜索，以此类推。
在搜索中，如果遇到这个路不可能和目标字符串匹配成功，应该立即返回。称之为不可行剪枝。
递归参数为当前元素在矩阵board中的位置i,j以及当前目标字符在word中的索引k。
如果当前索引越界或者当前矩阵元素与目标元素不同或者当前矩阵元素已经被访问过时，返回False，当字符串已经完全匹配时，返回True。当返回False时，要注意将这条不可能路径上的visited数组置为0。

'''

class Solution:
    def exist(self, board: List[List[str]], word: str) -> bool:
        row, column = len(board), len(board[0]) 
        visited = [[0 for i in range(len(board[0]))] for j in range(len(board))]
        def dfs(i,j, k):
            if not word[k:]:
                return True
            ret = False
            if  0 <= i < row and 0 <= j < column and visited[i][j]==0 and board[i][j] == word[k]:
                visited[i][j] = 1
                ret = dfs(i+1,j, k+1) or dfs(i-1, j, k+1) or dfs(i, j+1, k+1) or dfs(i, j-1, k+1)
                if ret == 0:
                    visited[i][j] = 0
            return ret

        for i in range(row):
            for j in range(column):
                if dfs(i,j, 0):
                    return True
        return False




'''
深度优先搜索： 可以理解为暴力法遍历矩阵中所有字符串可能性。DFS 通过递归，先朝一个方向搜到底，再回溯至上个节点，沿另一个方向搜索，以此类推。
剪枝： 在搜索中，遇到 这条路不可能和目标字符串匹配成功 的情况（例如：此矩阵元素和目标字符不同、此元素已被访问），则应立即返回，称之为 可行性剪枝 。

'''
class Solution:
    def exist(self, board: List[List[str]], word: str) -> bool:
        def dfs(i, j, k):
            if not 0 <= i < len(board) or not 0 <= j < len(board[0]) or board[i][j] != word[k]: return False
            if k == len(word) - 1: return True
            board[i][j] = ''
            res = dfs(i + 1, j, k + 1) or dfs(i - 1, j, k + 1) or dfs(i, j + 1, k + 1) or dfs(i, j - 1, k + 1)
            board[i][j] = word[k]
            return res

        for i in range(len(board)):
            for j in range(len(board[0])):
                if dfs(i, j, 0): return True
        return False
