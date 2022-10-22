#判断矩阵中是否存在某条路径
public class myPath {
    public static int num=0;
    public static void main(String[] args) {
        char [][] matrix=new char[3][4];
        char ch1[] = { 'a', 'b', 'c', 'd' };
        char ch2[] = { 'b', 'c', 'd', 'a' };
        char ch3[] = { 'c', 'd', 'a', 'b' };
        matrix[0]=ch1;
        matrix[1]=ch2;
        matrix[2]=ch3;
        char str[]={'a','b','c','d'};
        boolean yn=hasPath(matrix,str);
        System.out.println(yn);
        System.out.println(num);

    }
    public static boolean hasPath(char[][] matrix,char []str){
        if (matrix==null||str==null){
            return false;
        }
        int rows=matrix.length;
        int cols=matrix[0].length;
        //初始化所有节点为没有访问过。
        boolean [][]visited=new  boolean[rows][cols];
        for (int i=0;i<rows;i++){
            for (int j=0;j<cols;j++){
                visited[i][j]=false;
            }
        }
        //初始化路线长度为0
        int pathlength=0;
        for (int i=0;i<rows;i++){
            for (int j=0;j<cols;j++){
                if (blpath(matrix,str,visited,i,j,pathlength)){
                    return true;
                }
            }
        }


        return false;
    }
    //回溯法找路径
    public static  boolean blpath(char [][]matrix ,char []str ,boolean[][] visited,int i,int j,int pathlenth){

        int rows=matrix.length;
        int cols=matrix[0].length;
        if (pathlenth==str.length){
                num++;
            return true;
        }
        boolean haspath=false;
        //判断当前节点是否存在，是否被访问过
        if (i>=0&&i<rows&&j>=0&&j<cols&&matrix[i][j]==str[pathlenth] && visited[i][j] == false){
            visited[i][j]=true;
            pathlenth++;
            //System.out.println(pathlenth);
            //找到第一个节点
            //递归查找这个节点的周围4个节点是否有下一个str的值
            haspath=blpath(matrix,str,visited,i+1,j,pathlenth)|
                    blpath(matrix,str,visited,i-1,j,pathlenth)|
                    blpath(matrix,str,visited,i,j+1,pathlenth)|
                    blpath(matrix,str,visited,i,j-1,pathlenth);
            //查找失败，str的下标回退一位，并且此节点做root不存在路径
            if (!haspath){
                pathlenth--;
                visited[i][j]=false;
            }

        }
        return haspath;
    }


}