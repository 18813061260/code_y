



//代码执行大致过程如下：首先在board数组中找到一个位置，使得board[i][j] == word[0]，可以作为搜索的入口。由于题目说明遍历过的元素不能重复访问，因此我们只需将遍历走过的元素替换成‘\0’(字符串中不存在的值)。然后通过上下左右搜索直到找到一个可行解即返回true，再继续进行下一元素的匹配搜索。若上下左右都没有元素与字符串字符匹配，那么就返回false，代表搜索失败。如果匹配到字符串末尾全部匹配上，则返回true，代表路径搜索成功。


class Solution {
public:
    bool exist(vector<vector<char>>& board, string word) {
        if(word.empty()||board.empty()||board[0].empty())
            return false;
        for(int i=0;i<board.size();i++)
        {
            for(int j=0;j<board[0].size();j++)
            {
                //回溯法
                if(dfs(board,word,i,j,0))
                return true;
            }
        }
        return false;
    }
private:
    bool dfs(vector<vector<char>>& board,string& word,int i,int j,int w)
    {
        //判断索引是否越界或者当前值是否匹配，如果不满足则返回false
        if(i<0||i>=board.size()||j<0||j>=board[0].size()||board[i][j]!=word[w])
            return false;
        //如果当前已经匹配到了字符串最后一位，则返回true。（-1是因为数组下标从0开始）
        if(w==word.size()-1)
            return true;

        //保留当前的值到临时变量中
        char tem=board[i][j];
        //将当前值替换成数组中不可能存在的值（目的就是为了让这个值不再被遍历）
        board[i][j]='\0';

        //遍历当前索引的左右下上的值是否与字符串下一字符匹配（递归）
        //若匹配一致则返回true，再继续进行下一字符的判断
        if(dfs(board,word,i-1,j,w+1)
         ||dfs(board,word,i+1,j,w+1)
         ||dfs(board,word,i,j-1,w+1)
         ||dfs(board,word,i,j+1,w+1))
         return true;
        else
        {
            //如果不匹配则将当前值替换为原先值，返回false
            board[i][j]=tem;
            return false;
        }
    }
};

