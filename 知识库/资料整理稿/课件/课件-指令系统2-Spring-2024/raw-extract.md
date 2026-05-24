# 计算机组成与结构

# 一指令系统2

李瑞 教授

蒋志平 副教授

计算机科学与技术学院

# 温故 一关于指令系统

- 虚拟存储系统有哪些功能？  
- 虚拟存储的工作原理？  
- 简述段式虚拟存储转换的原理和优缺点  
- 简述页式虚拟存储转换的原理和优缺点  
- 简述有哪些优化虚拟存储性能的方法？  
- CPU执行指令的4个步骤是?   
- 指令的格式是什么?

# 本节学习要点

- 指令格式  
- 可执行程序的结构  
- 对Emu8086做简单使用介绍  
- CPU是如何定位程序的？(寄存器)  
- CPU是如何定位程序中的代码或数据的？（寻址方式）

# 指令格式

# 指令格式

![](images/83b49faaf5a899fe8f4c413694cd500379cea122a218d58aef8d29511a767b6c.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    A["高级语言"] --> B["auto area() --> float { return a * b; }}    B --> C[编译"]
    C --> D["汇编语言"]
    D --> E["Load r1, a<br>Load r2, b<br>MUL r1, r2<br>RET"]
    E --> F["直译"]
    F --> G["机器代码"]
    G --> H["00010101000001110<br>1010100001011101<br>1010101011..."]
```
</details>

MUL r1, r2被转译为

这是瞎编的\~

“011101010100001011”

这一条指令包含以下4条信息：

- MUL指令的编号  
- MUL指令能支持两个操作数  
- 操作数1指向r1寄存器  
- 操作数2指向r2寄存器

# 指令格式

■ 指令 = 操作码Opcode + 操作数

Operand (0\~N)

■ 操作数，也叫地址码

地址码的内容可以是：地址、数值

地址码的目标可以是:

源/目的操作数，结果，下一条指令

地址（顺序/跳转）

例如，某定长指令格式

<table><tr><td>操作码4位</td><td>操作数8位</td><td>操作数8位</td></tr></table>

20位

# 指令格式

# ■ 常用的地址码数目：

- 三地址: ADD Y, A, B ; Y=A+B  
- 双地址：ADD Y, A ; Y=Y+A  
- 单地址: ADD C ; AC=AC+C  
- 零地址

# 指令格式

例如：计算一个典型的算术表达式：

$$
x = \frac {a \times b + c - d}{e + f}
$$

用三地址指令编写的程序如下:

MUL X, A, B ;X←(A)×(B)

ADD X, X, C ;X←(X) + (C)

SUB X, X, D ; 分子的计算结果在x中

ADD Y, E, F ;计算分母,存入Y

DIV X, X, Y ; 最后结果在x单元中

# 指令格式

$$
x = \frac {a \times b + c - d}{e + f}
$$

# 用普通二地址指令编写的程序：

MOVE X, A ;复制临时变量到X中

MUL X, B

ADD X, C

SUB X, D ;X中存放分子运算结果

MOVE Y, E ;复制临时变量到Y中

ADD Y, F ;Y中存放分母运算结果

DIV X, Y ;最后结果在x单元中

# 指令格式

$$
x = \frac {a \times b + c - d}{e + f}
$$

# 用多寄存器结构的二地址指令编写程序：

MOVE R1, A ;操作数a取到寄存器R1中

MUL R1, B

ADD R1, C

SUB R1, D ;R1中存放分子运算结果

MOVE R2, E

ADD R2, F ;R2中存放分母运算结果

DIV R1, R2 ;最后结果在R1中

MOVE X, R1 ;最后结果存入X中

# 指令格式

$$
x = \frac {a \times b + c - d}{e + f}
$$

# 用一地址指令编写的程序：

LOAD E ; 先计算分母,  
;取一个操作数到累加器中  
ADD F ;分母运算结果在累加器中  
STORE X ;保存分母运算结果到x中  
LOAD A ;开始计算分子  
MUL B   
ADD C   
SUB D ;累加器中是分子运算结果  
DIV X ;最后运算结果在累加器中  
STORE X ;保存最后运算结果到x中

# 指令格式

# 用0地址指令编写程序：

PUSH A ;操作数a压入堆栈

PUSH B ;操作数b压入堆栈

MUL ; 栈顶两数相乘 , 结果压回堆顶

PUSH C

ADD

PUSH D

SUB ; 栈顶是分子运算的结果

PUSH E

PUSH F

ADD

DIV ; 栈顶是最后运算的结果

POP X ;保存最后运算结果

$$
x = \frac {a \times b + c - d}{e + f}
$$

$$
a b ^ {*} c + d - e f + /
$$

# 指令格式

不同地址个数指令的特点及适用场合

<table><tr><td>地址数目</td><td>程序的长度</td><td>程序存储量</td><td>程序执行速度</td><td>适用场合</td></tr><tr><td>三地址</td><td>最短</td><td>最大</td><td>一般</td><td>向量,矩阵运算为主</td></tr><tr><td>二地址</td><td>较短</td><td>很大</td><td>很低</td><td>一般不宜采用</td></tr><tr><td>一地址</td><td>较长</td><td>较大</td><td>较快</td><td>连续运算,硬件结构简单</td></tr><tr><td>零地址</td><td>最长</td><td>最小</td><td>最低</td><td>嵌套,递归,变量较多</td></tr></table>

# 指令格式

# 关于地址码个数结论:

■ 对于一般商用处理机，采用多寄存器结构的二地址指令是最理想的。  
■ 如果强调硬件结构简单，并且以连续运算（如求累加和等）为主，宜采用一地址结构。  
■ 对于以向量、矩阵运算为主的处理机，最好采用三地址结构。  
■ 部分RISC处理机也采用三地址指令。  
■ 对于解决递归问题为主的处理机，宜采用零地址结构。编程容易、节省程序存储量。

# 指令编码

# 指令编码

- 指令操作码(Op code)编码方式:  
- 编码的考量因素  
- 编码方法

- 定长编码  
- 不定长编码

- 霍夫曼Huffman Coding   
- 扩展操作码

# 指令编码

构成一条指令的二进制的位数称为指令长度，一般都是字节的整数倍。

■内存大小与组织  
■CPU数据总线宽度  
■CPU内部寄存器的数量  
■寻址方式  
■指令数量

# 指令编码

# 定长指令编码:

\- 所有指令的编码Opcode长度相同!

\- 不管几操作数的指令，opcode都一样长！

\- 显然，会有指令bit浪费，或指令容量受限

![](images/7211ec27ccbc9f5a13a0e11109d9ecdf4714d0c375aab09427203d2838b4e2a4.jpg)

<details>
<summary>other</summary>

| OPCODE Field | Value |
| ------------ | ----- |
| r_c          | 32 bits |
| r_a          | 32 bits |
| r_b          | 32 bits |
| unused       | 32 bits |
</details>

# 指令编码

# Huffman指令编码:

\- 让高频指令的opcode更短！（不care操作数长度！）

# 指令编码

例：假设一台模型计算机共有7种不同的操作码，已知各种操作码在程序中出现的概率如下表，利用固定长度编码法进行操作码编码。

<table><tr><td>指令</td><td> $I_1$ </td><td> $I_2$ </td><td> $I_3$ </td><td> $I_4$ </td><td> $I_5$ </td><td> $I_6$ </td><td> $I_7$ </td></tr><tr><td>概率</td><td>0.45</td><td>0.30</td><td>0.15</td><td>0.05</td><td>0.03</td><td>0.01</td><td>0.01</td></tr></table>

解：由于N=7 因此，指令操作码固定长度为

$$
[ \mathrm{lbN} ] = [ \mathrm{lb7} ] = 3
$$

编码结果:

<table><tr><td>指令序号</td><td>概率</td><td>编码</td><td>操作码长度</td></tr><tr><td> $I_1$ </td><td>0.45</td><td>000</td><td>3位</td></tr><tr><td> $I_2$ </td><td>0.30</td><td>001</td><td>3位</td></tr><tr><td> $I_3$ </td><td>0.15</td><td>010</td><td>3位</td></tr><tr><td> $I_4$ </td><td>0.05</td><td>011</td><td>3位</td></tr><tr><td> $I_5$ </td><td>0.03</td><td>100</td><td>3位</td></tr><tr><td> $I_6$ </td><td>0.01</td><td>101</td><td>3位</td></tr><tr><td> $I_7$ </td><td>0.01</td><td>110</td><td>3位</td></tr></table>

# 指令编码

例：利用Huffman 编码法进行操作码编码。

<table><tr><td>指令</td><td> $I_1$ </td><td> $I_2$ </td><td> $I_3$ </td><td> $I_4$ </td><td> $I_5$ </td><td> $I_6$ </td><td> $I_7$ </td></tr><tr><td>概率</td><td>0.45</td><td>0.30</td><td>0.15</td><td>0.05</td><td>0.03</td><td>0.01</td><td>0.01</td></tr></table>

![](images/75bb6cb2f1987c56db3032af2bd526c560ed833d7949d1209515a66d85483b79.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    I1["0.45"] --> A["0.55"]
    I2["0.30"] --> A["0.55"]
    I3["0.15"] --> A["0.55"]
    I4["0.05"] --> A["0.55"]
    I5["0.03"] --> A["0.55"]
    I6["0.01"] --> A["0.55"]
    I7["0.01"] --> A["0.55"]
    A["0.25"] -->|0| B["1.00"]
    A["0.25"] -->|1| C["1.00"]
    A["0.25"] -->|0| D["1.00"]
    A["0.25"] -->|0| E["1.00"]
    A["0.25"] -->|1| F["1.00"]
    G["I1"] --> A
    H["I2"] --> A
    I3 --> A
    I4 --> A
    I5 --> A
    I6 -->|0| J["0.02"]
    J["0.02"] -->|1| K["1.00"]
    I7 -->|1| L["1.00"]
```
</details>

Huffman编码树生成过程

# 指令编码

编码结果:

<table><tr><td>指令序号</td><td>概率</td><td>Huffman编码法</td><td>操作码长度</td></tr><tr><td> $I_1$ </td><td>0.45</td><td>0</td><td>1位</td></tr><tr><td> $I_2$ </td><td>0.30</td><td>10</td><td>2位</td></tr><tr><td> $I_3$ </td><td>0.15</td><td>110</td><td>3位</td></tr><tr><td> $I_4$ </td><td>0.05</td><td>1110</td><td>4位</td></tr><tr><td> $I_5$ </td><td>0.03</td><td>11110</td><td>5位</td></tr><tr><td> $I_6$ </td><td>0.01</td><td>111110</td><td>6位</td></tr><tr><td> $I_7$ </td><td>0.01</td><td>111111</td><td>6位</td></tr></table>

采用 Huffman 编码法的操作码平均长度:

$$
\begin{array}{l} 0. 4 5 \times 1 + 0. 3 0 \times 2 + 0. 1 5 \times 3 + 0. 0 5 \times 4 + 0. 0 3 \times 5 + 0. 0 1 \times 6 + 0. 0 1 \times 6 \\ = 1. 9 7 (\text {位}) \end{array}
$$

# 指令编码

# Huffman操作码的主要缺点：

1) 操作码长度很不规整，硬件译码困难   
2) 与地址码共同组成固定长的指令比较困难

# 解决方法之一：指令操作码的扩展技术

# 指令编码

# 扩展指令编码：

- 让操作数多的指令opcode更短，  
- 操作数少的指令opcode最长

# 指令编码

原则：短码不能是长码的前缀。

![](images/2b3554fffb2479932fba319982ebe7513775c7750fff08adc5828dfe1195211c.jpg)

<details>
<summary>tree</summary>

| 编码方法 | 编号 | 数值 |
| -------- | ---- | ---- |
| 15-15-15 编码方法 | 0000 | 0000 |
| 15-15-15 编码方法 | 0001 | 0001 |
| 15-15-15 编码方法 | ...... | ... |
| 15-15-15 编码方法 | 1110 | 1110 |
| 8-64-512 编码方法 | 8    | 8    |
| 8-64-512 编码方法 | 0000 | 0000 |
| 8-64-512 编码方法 | 0001 | 0001 |
| 8-64-512 编码方法 | ...... | ... |
| 8-64-512 编码方法 | 0111 | 0111 |
| 8-64-512 编码方法 | 1000 | 1000 |
| 8-64-512 编码方法 | 0000 | 0000 |
| 8-64-512 编码方法 | 1000 | 1000 |
| 8-64-512 编码方法 | 0001 | 0001 |
| 8-64-512 编码方法 | ...... | ... |
| 8-64-512 编码方法 | 1111 | 1111 |
| 8-64-512 编码方法 | 0111 | 0111 |
| 8-64-512 编码方法 | 1000 | 1000 |
| 8-64-512 编码方法 | 0000 | 0000 |
| 8-64-512 编码方法 | 1111 | 1111 |
| 8-64-512 编码方法 | 0111 | 0111 |
| 8-64-512 编码方法 | 512 | 512 |
| 8-64-512 编码方法 | ...... | ... |
| 8-64-512 编码方法 | 1111 | 1111 |
| 8-64-512 编码方法 | 1111 | 0111 |
| 8-64-512 编码方法 | 25   | 25   |
</details>

# 指令编码

■ 短的操作码与多种地址码配合  
■ 长的操作码与简单地址码组合  
■ 指令长度一般设计为总线宽度的整数倍  
■ 指令的长度为最小可寻址单位的整数倍   
■ 影响寻址位的因素：

- 寻址方式的个数  
- 操作数数目  
- 寄存器数目  
- 地址范围

\- 地址可寻址最小单元

# 指令编码

例：假设某型号的计算机共有14条指令，各条指令的使用频

率分别为：0.01、0.15、0.12、0.03、0.02、0.04、0.02、

0.04、0.01、0.13、0.15、0.14、0.11、0.03。

试给出定长、只能有两种码长的扩展操作码的两种编码方案，

并计算各种方案的平均码长。

【解】

<table><tr><td>指令</td><td> $I_1$ </td><td> $I_2$ </td><td> $I_3$ </td><td> $I_4$ </td><td> $I_5$ </td><td> $I_6$ </td><td> $I_7$ </td></tr><tr><td>概率</td><td>0.15</td><td>0.15</td><td>0.14</td><td>0.13</td><td>0.12</td><td>0.11</td><td>0.04</td></tr><tr><td>指令</td><td> $I_8$ </td><td> $I_9$ </td><td> $I_{10}$ </td><td> $I_{11}$ </td><td> $I_{12}$ </td><td> $I_{13}$ </td><td> $I_{14}$ </td></tr><tr><td>概率</td><td>0.04</td><td>0.03</td><td>0.03</td><td>0.02</td><td>0.02</td><td>0.01</td><td>0.01</td></tr></table>

# 指令编码

定长编码：

<table><tr><td>指令</td><td> $I_1$ </td><td> $I_2$ </td><td> $I_3$ </td><td> $I_4$ </td><td> $I_5$ </td><td> $I_6$ </td><td> $I_7$ </td></tr><tr><td>概率</td><td>0.15</td><td>0.15</td><td>0.14</td><td>0.13</td><td>0.12</td><td>0.11</td><td>0.04</td></tr><tr><td>扩展编码</td><td>0000</td><td>0001</td><td>0010</td><td>0011</td><td>0100</td><td>0101</td><td>0110</td></tr><tr><td>码长</td><td>4</td><td>4</td><td>4</td><td>4</td><td>4</td><td>4</td><td>4</td></tr><tr><td>指令</td><td> $I_8$ </td><td> $I_9$ </td><td> $I_{10}$ </td><td> $I_{11}$ </td><td> $I_{12}$ </td><td> $I_{13}$ </td><td> $I_{14}$ </td></tr><tr><td>概率</td><td>0.04</td><td>0.03</td><td>0.03</td><td>0.02</td><td>0.02</td><td>0.01</td><td>0.01</td></tr><tr><td>扩展编码</td><td>0111</td><td>1000</td><td>1001</td><td>1010</td><td>1011</td><td>1100</td><td>1101</td></tr><tr><td>码长</td><td>4</td><td>4</td><td>4</td><td>4</td><td>4</td><td>4</td><td>4</td></tr></table>

其操作码的平均码长: $\mathrm{H} = 4$ (位)。

# 指令编码

两种码长的扩展操作码：（方法一）

<table><tr><td>指令</td><td> $I_1$ </td><td> $I_2$ </td><td> $I_3$ </td><td> $I_4$ </td><td> $I_5$ </td><td> $I_6$ </td><td> $I_7$ </td></tr><tr><td>概率</td><td>0.15</td><td>0.15</td><td>0.14</td><td>0.13</td><td>0.12</td><td>0.11</td><td>0.04</td></tr><tr><td>扩展编码</td><td>000</td><td>001</td><td>010</td><td>011</td><td>100</td><td>101</td><td>110</td></tr><tr><td>码长</td><td>3</td><td>3</td><td>3</td><td>3</td><td>3</td><td>3</td><td>3</td></tr><tr><td>指令</td><td> $I_8$ </td><td> $I_9$ </td><td> $I_{10}$ </td><td> $I_{11}$ </td><td> $I_{12}$ </td><td> $I_{13}$ </td><td> $I_{14}$ </td></tr><tr><td>概率</td><td>0.04</td><td>0.03</td><td>0.03</td><td>0.02</td><td>0.02</td><td>0.01</td><td>0.01</td></tr><tr><td>扩展编码</td><td>111000</td><td>111001</td><td>111010</td><td>111011</td><td>111100</td><td>111101</td><td>111110</td></tr><tr><td>码长</td><td>6</td><td>6</td><td>6</td><td>6</td><td>6</td><td>6</td><td>6</td></tr></table>

其操作码平均码长为： $\mathbf{H} = \sum_{i=1}^{n} p_i l_i$

$$
\mathrm{H} = (0. 1 5 + 0. 1 5 + 0. 1 4 + 0. 1 3 + 0. 1 2 + 0. 1 1 + 0. 0 4) \times 3 +
$$

$$
(0. 0 4 + 0. 0 3 + 0. 0 3 + 0. 0 2 + 0. 0 2 + 0. 0 1 + 0. 0 1) \times 6
$$

$$
= 0. 8 4 \times 3 + 0. 1 6 \times 6 = 3. 4 8 (\text {位})
$$

# 指令编码

大概率

<table><tr><td>指令</td><td> $I_1$ </td><td> $I_2$ </td><td> $I_3$ </td><td> $I_4$ </td><td> $I_5$ </td><td> $I_6$ </td><td> $I_7$ </td></tr><tr><td>概率</td><td>0.15</td><td>0.15</td><td>0.14</td><td>0.13</td><td>0.12</td><td>0.11</td><td>0.04</td></tr><tr><td>扩展编码</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>码长</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>指令</td><td> $I_8$ </td><td> $I_9$ </td><td> $I_{10}$ </td><td> $I_{11}$ </td><td> $I_{12}$ </td><td> $I_{13}$ </td><td> $I_{14}$ </td></tr><tr><td>概率</td><td>0.04</td><td>0.03</td><td>0.03</td><td>0.02</td><td>0.02</td><td>0.01</td><td>0.01</td></tr><tr><td>扩展编码</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>码长</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr></table>

小概率

# 指令编码

大概率

两种码长的扩展操作码：（方法二）

<table><tr><td>指令</td><td> $I_1$ </td><td> $I_2$ </td><td> $I_3$ </td><td> $I_4$ </td><td> $I_5$ </td><td> $I_6$ </td><td> $I_7$ </td></tr><tr><td>概率</td><td>0.15</td><td>0.15</td><td>0.14</td><td>0.13</td><td>0.12</td><td>0.11</td><td>0.04</td></tr><tr><td>扩展编</td><td>000</td><td>001</td><td>010</td><td>011</td><td>100</td><td>101</td><td>11000</td></tr><tr><td>码长</td><td>3</td><td>3</td><td>3</td><td>3</td><td>3</td><td>3</td><td>5</td></tr><tr><td>指令</td><td> $I_8$ </td><td> $I_9$ </td><td> $I_{10}$ </td><td> $I_{11}$ </td><td> $I_{12}$ </td><td> $I_{13}$ </td><td> $I_{14}$ </td></tr><tr><td>概率</td><td>0.04</td><td>0.03</td><td>0.03</td><td>0.02</td><td>0.02</td><td>0.01</td><td>0.01</td></tr><tr><td>扩展编</td><td>11001</td><td>11010</td><td>11011</td><td>11100</td><td>11101</td><td>11110</td><td>11111</td></tr><tr><td>码长</td><td>5</td><td>5</td><td>5</td><td>5</td><td>5</td><td>5</td><td>5</td></tr></table>

其操作码平均码长为： $\mathbf{H} = \sum_{i=1}^{n} p_i l_i$

$$
\begin{array}{l} \mathbf {H} = (0. 1 5 + 0. 1 5 + 0. 1 4 + 0. 1 3 + 0. 1 2 + 0. 1 1) \times 3 + \\ (0. 0 4 + 0. 0 4 + 0. 0 3 + 0. 0 3 + 0. 0 2 + 0. 0 2 + 0. 0 1 + 0. 0 1) \times 5 \\ = 0. 8 \times 3 + 0. 2 \times 5 = 3. 4 (\text {位}) \\ \end{array}
$$

小概率

# 指令格式

8086 / 8088指令编码由1～6个字节组成，它包括操作码（第一字节）、寻址方式（第二字节）和操作数（第三到第六字节）三部分组成p

opcode

opcode

Mod字节

opcode

Mod字节

Data/disp

opcode

Mod字节

Data/disp(低)

Data/disp(高)

opcode

Mod字节

disp(低)

disp(高)

Data

opcode

Mod字节

disp(低)

disp(高)

Data(低)

Data(高)

操作码部分

寻址方式部分

操作数部分

# 可执行程序的两个结构

# 可执行程序的两个结构

\- 一个最简单的C代码: 其实一点也不简单...

```txt
int main() {
    printf("Hello world!\n");
} 
```

# 可执行程序的两个结构

\- 一个最简单的C代码： 其实一点也不简单...

![](images/2b029d25a98a9fa319aac9b750e548117b394b192926c75aaa2819316ca35de6.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    A["如何定义为程序的入口?"] --> B{int main() { printf("Hello world!\n"); }} 
    B --> C["调用libc库中的printf函数"]
    C --> D{如何调用这个函数？链接它！}
    D --> E["动态链接？通过OS找到libc"]
    E --> F{这是一个常量，存哪？}
    F --> G["数据和代码可以流水帐一样堆起来么？No!}<br>    D --> H[静态链接，把libc的printf及其依赖都打包进来"]
    H --> I{如何调用printf方法？}
    I --> J{可执行程序中上怎么存另一块代码？}
    J --> K["可执行程序是有结构的"]
```
</details>

# 可执行程序的两个结构

\- 一个最简单的C代码:

```txt
int main() {
    printf("Hello world!\n");
} 
```

经历2个步骤变成可执行程序：

- 编译（把自己的程序逻辑变为机器代码）  
- 链接（链接其它库的函数调用）

\- 可执行程序的静态结构（ELF为例）

- ELF Header   
- Sections

- CODE   
• DATA   
• BSS   
- RODATA   
- HEAP   
- STACK   
● ....

• Section Header Table

# 可执行程序的两个结构

# - 可执行程序的静态结构（ELF为例）

- ELF Header   
- Sections

- CODE/TEXT   
• DATA   
• BSS   
- HEAP   
- STACK   
●
...

• Section Header Table

![](images/a5b9b774ddf060a41d234f7b65739b83800d440e1ede74688ca277b8bbacfc10.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    A["ARM ASSEMBLY"] --> B["mov r2, #13 MSG_LEN"]
    A --> C["add r1, pc, #20 msg(pc-relative)"]
    A --> D["mov r0, #1 STOUT_FILENO"]
    A --> E["mov r7, #4 SC_WRITE"]
    A --> F["svc 0 system call"]
    G["EQUIVALENT C CODE"] --> H["write(STDOUT_FILENO, &quot;Hello world!\n&quot;, len(&quot;Hello world!\n&quot;));"]
    I["mov r0, #1 return code"] --> J["mov r7, #1 SC_EXIT"]
    I --> K["svc 0 system call"]
    L["exit(1);"] --> M
```
</details>

# STRINGS

"Hello World!\n", 0

# 可执行程序的两个结构

\- 可执行程序的静态结构（ELF为例）

- ELF Header   
- Sections

- CODE/TEXT   
• DATA   
• BSS   
- HEAP   
- STACK   
●
...

• Section Header Table

地址高位  
![](images/2bd2498f204001a740445100f37dfe728e34de05ec3a9412a80683281338d316.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    A["stack"] --> B["栈(未展开)"]
    C["heap"] --> D["堆(未展开)"]
    E["uninitialized data"] --> F["bss"]
    G["initialized data"] --> H["data"]
    I["text"] --> J["Code/Text段，存程序代码"]
```
</details>

地址低位

# 地址高位

<table><tr><td>stack</td></tr><tr><td>↓</td></tr><tr><td>↑</td></tr><tr><td>heap</td></tr><tr><td>uninitialized data</td></tr><tr><td>bss</td></tr><tr><td>initialized data</td></tr><tr><td>data</td></tr><tr><td>text</td></tr></table>

# 地址低位

# 可执行程序的两个结构

\- 可执行程序的动态结构—进程!

\- 程序映射到4GB虚拟内存空间

\- 每个线程有自己的Stack/Heap

\- 虚拟地址被OS映射到实际物理地址

![](images/b67a2e081e0c70c4fc8d37adb45ec361f52149e2c5a4e53ae69980e8ea233e30.jpg)

<details>
<summary>text_image</summary>

程序映射到4GB虚拟内存空间
每个线程有自己的Stack/Heap
虚拟地址被OS映射到实际物理地址
</details>

<table><tr><td></td><td>code</td><td>plt</td><td>data</td><td>got</td><td>bss</td><td></td><td>heap</td><td></td><td>shared memory</td><td></td><td>shared libraries</td><td></td><td>stack</td></tr></table>

# 可执行程序的内存结构

# - 关于Stack/Heap

![](images/84e52cb0bdb85261200b0bbfd5aadb9ea7932d04812d743f1f6a4bf9a2399a8b.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    A["Writeable; not executable"] --> B["Stack"]
    B --> C["Dynamic Data (Heap)"]
    C --> D["Static Data"]
    D --> E["Literals"]
    E --> F["Read-only; not executable"]
    F --> G["Instructions"]
    
    style A fill:#f9f,stroke:#333
    style B fill:#ff9,stroke:#333
    style C fill:#ffcc,stroke:#333
    style D fill:#cfc,stroke:#333
    style E fill:#cfc,stroke:#333
    style F fill:#cfc,stroke:#333
    style G fill:#cfc,stroke:#333
    
    note1["Managed 'automatically' (by compiler)"]
    note2["Managed by programmer"]
    note3["Initialized when process starts"]
    note4["Initialized when process starts"]
    note5["Initialized when process starts"]
```
</details>

![](images/c19bc21e6ef4df33a9d13ddac93d6e88a12d774e201fc0e6e0f092b03c23cb76.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    A["stack"] --> B["static"]
    C["heap"] --> D["box 1"]
    C --> E["box 2"]
    C --> F["box 3"]
    style A fill:#fff,stroke:#000
    style B fill:#fff,stroke:#000
    style C fill:#fff,stroke:#000
    style D fill:#fff,stroke:#000
    style E fill:#fff,stroke:#000
    style F fill:#fff,stroke:#000
```
</details>

# 可执行程序的内存结构

- 关于Stack/Heap  
![](images/4493afe2d752d375bbcfe370b899eda43a307288148c72589ca2ffbf91683579.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    A["stack"] --> B["heap"]
    B --> C["low address"]
    C --> D["text"]
    D --> E["initialized data"]
    E --> F["uninitialized data(bss)"]
    F --> G["high address"]
```
</details>

一个典型的Java程序内存模型  
![](images/b43d4a729493f6dda26b738f5ed62d1285178995929fbaebefc98df4faabe3aa.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    A["Stack"] --> B["String["] args =]
    A --> C["Employee e1 ="]
    A --> D["Employee e2 ="]
    A --> E["Employee e3 ="]
    
    F["Heap"] --> G["String["] args =]
    F --> H["String["] char[] value =]
    F --> I["String["] char[] value =]
    F --> J["String["] char[] value =]
    F --> K["String["] char[] value =]
    F --> L["String["] char[] value =]
    
    M["Heap"] --> N["String["] args =]
    M --> O["Employee name ="]
    M --> P["ssn ="]
    M --> Q["emailAddress ="]
    M --> R["yearOfBirth = 0"]
    
    S["Heap"] --> T["String["] args =]
    S --> U["String["] char[] value =]
    S --> V["String["] char[] value =]
    S --> W["String["] char[] value =]
    
    X["Heap"] --> Y[", 'J', 'h', 'o', 'n'"]
    X --> Z[", '5', '5', '5', '-', '1', '2', '-', '3', '4', '5'"]
    X --> AA[", 'j', 'o', 'h', 'n', '@', 'c'...y', 'c', 'o', 'm'"]
    X --> AB[", 'T', 'o', 'm'"]
    X --> AC[", '4', '5', '6', '-', '7', '8', '-', '9', '0', '1'"]
```
</details>

# 可执行程序的内存结构

- 关于Stack/Heap  
- 高性能的Heap分配器可以尽量避免碎片，显著提升性能...  
- 当然对Java来说，GC的影响更大...

- Default Allocator
list<int> b;
// same as:
list<int, allocator<int>> b;   
- Custom Allocator
  #include "MyAlloc.h"
  list<int, MyAlloc<int>> c;

![](images/8f6c899a9417e68d0f8d4f1ebd46d048aff7cde6b6744af22ea4818924ba4a67.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    A["Stack"] --> B["Free Memory"]
    B --> C["Heap"]
    C --> D["Static Data"]
```
</details>

![](images/ed9fae6f35ebe09193ed8440decb825a27f5dccac2389bc1dafa1ad6c379a9ce.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    A["Stack"] --> B["Free Memory"]
    B --> C["Heap"]
    C --> D["Static Data"]
```
</details>

So, 这和指令系统有什么关系?

CPU，是如何定位程序的？

# CPU的内部寄存器

# 8086 CPU的内部寄存器

![](images/cfe225ed06a37bc55cc7e372af57739c5e97515145c072f0f7d7ea22dc559160.jpg)

command-line arguments and environment variables

# 存器

行时的

阶段，

址等

<table><tr><td>AH</td><td>AL</td></tr><tr><td>BH</td><td>BL</td></tr><tr><td>CH</td><td>CL</td></tr><tr><td>DH</td><td>DL</td></tr></table>

<table><tr><td>SP</td></tr><tr><td>BP</td></tr><tr><td>SI</td></tr><tr><td>DI</td></tr></table>

AX
BX
CX
DX

数据寄存器

堆栈指针
基数指针
源变址
目的变址

指针寄存器
指针寄存器

通用寄存器

![](images/7f388e8ad906c0e2b7ab50c659a9f559987d4250572654906e5a2cf2fa7a3c98.jpg)

initialized to zero by exec

read from program file by exec

器

<table><tr><td colspan="2">IP</td></tr><tr><td>PSWH</td><td>PSWL</td></tr></table>

<table><tr><td>CS</td></tr><tr><td>DS</td></tr><tr><td>SS</td></tr><tr><td>ES</td></tr></table>

指令指针
状态标志

} 控制寄存器

代码段
数据段
堆栈段
附加段

段寄存器

\- 数据寄存器

# CPU的内部寄存器

![](images/7100a816a53646d8799ed2054efe723dee5b3c2014052e25af4410e54c0bb16e.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    A["low address"] --> B["text"]
    B --> C["initialized data"]
    B --> D["uninitialized data(bss)"]
    B --> E["heap"]
    E --> F["stack"]
    F --> G["high address"]
    style A fill:#f9f,stroke:#333
    style B fill:#ccf,stroke:#333
    style C fill:#cfc,stroke:#333
    style D fill:#fcc,stroke:#333
    style E fill:#cff,stroke:#333
    style F fill:#ffc,stroke:#333
    style G fill:#fcf,stroke:#333
    style_H["SI/DI/BX 3种"] --> I["Orange line"]
    H --> J["Red line"]
    H --> K["Blue line"]
    H --> L["Blue line"]
    H --> M["Blue line"]
    H --> N["Blue line"]
    H --> O["Blue line"]
```
</details>

<table><tr><td>AH</td><td>AL</td></tr><tr><td>BH</td><td>BL</td></tr><tr><td>CH</td><td>CL</td></tr><tr><td>DH</td><td>DL</td></tr></table>

<table><tr><td>SP</td></tr><tr><td>BP</td></tr><tr><td>SI</td></tr><tr><td>DI</td></tr></table>

<table><tr><td colspan="2">IP</td></tr><tr><td>PSWH</td><td>PSWL</td></tr></table>

<table><tr><td>CS</td></tr><tr><td>DS</td></tr><tr><td>SS</td></tr><tr><td>ES</td></tr></table>

AX
BX
CX
DX

堆栈指针
基数指针
源变址
目的变址

指令指针状态标志

代码段
数据段
堆栈段
附加段

# CPU的内部寄存器

物理地址=段寄存器×16 + 偏移地址  
![](images/f65985ee74000bbca2b91213a5317a359a33b04f48984830bb38677d0966897c.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    A["IP"] --> B["代码段"]
    C["CS"] --> B
    D["SP"] --> E["堆栈段"]
    F["SS"] --> E
    G["BX"] --> H["数据段"]
    I["DS"] --> J["存贮器"]
```
</details>

Then, How ???   
![](images/e0319bd28cae38d28962b65d3db26158cec8290a7b6bba8073629d1d457a892d.jpg)

<details>
<summary>text_image</summary>

20位
CS
DS
SS
ES
段寄存器
4位
16位
偏移量
+
物理地址
A₀~A₁₉
</details>

<table><tr><td>AH</td><td>AL</td></tr><tr><td>BH</td><td>BL</td></tr><tr><td>CH</td><td>CL</td></tr><tr><td>DH</td><td>DL</td></tr></table>

AX
BX
CX
DX

数据寄存器

<table><tr><td>SP</td></tr><tr><td>BP</td></tr><tr><td>SI</td></tr><tr><td>DI</td></tr></table>

堆栈指针
基数指针
源变址
目的变址

指针寄存器
指针寄存器

<table><tr><td colspan="2">IP</td></tr><tr><td>PSWH</td><td>PSWL</td></tr></table>

指令指针状态标志

}控制寄存器

<table><tr><td>CS</td></tr><tr><td>DS</td></tr><tr><td>SS</td></tr><tr><td>ES</td></tr></table>

代码段
数据段
堆栈段
附加段

段寄存器

# CPU的内部寄存器

\- 数据寄存器:

- 4个16位长，AX, BX, CX, DX   
- 或8个8位，AH, AL, ...

\- 指针寄存器: SP 和 BP

- BP是基址指针寄存器，通常用于存放基地址，以使8088的寻址更加灵活；  
- SP是堆栈指针寄存器，由它和堆栈段寄存器一起来确定堆栈内数据在内存中的位置；

<table><tr><td>AH</td><td>AL</td></tr><tr><td>BH</td><td>BL</td></tr><tr><td>CH</td><td>CL</td></tr><tr><td>DH</td><td>DL</td></tr></table>

AX
BX
CX
DX

![](images/0af5f2cdf214ed67c5d1ebd1da14d49070433fa6112ec8542065ef2fa2f5583c.jpg)

<table><tr><td>SP</td></tr><tr><td>BP</td></tr><tr><td>SI</td></tr><tr><td>DI</td></tr></table>

堆栈指针
基数指针
源变址
目的变址
指令指针
状态标志

<table><tr><td colspan="2">IP</td></tr><tr><td>PSWH</td><td>PSWL</td></tr></table>

代码段
数据段
堆栈段
附加段

<table><tr><td>CS</td></tr><tr><td>DS</td></tr><tr><td>SS</td></tr><tr><td>ES</td></tr></table>

# CPU的内部寄存器

\- 变址寄存器: SI/DI:

\- Source/Destination Index, 源/目的变址，用于变址寻址；

<table><tr><td>AH</td><td>AL</td></tr><tr><td>BH</td><td>BL</td></tr><tr><td>CH</td><td>CL</td></tr><tr><td>DH</td><td>DL</td></tr></table>

AX
BX
CX
DX

![](images/90cf7e55d3fa392a21fec5c3e5f245ff47c283768bc465f78e4e2edafe83faa1.jpg)

<table><tr><td>SP</td></tr><tr><td>BP</td></tr><tr><td>SI</td></tr><tr><td>DI</td></tr></table>

堆栈指针
基数指针
源变址
目的变址

<table><tr><td colspan="2">IP</td></tr><tr><td>PSWH</td><td>PSWL</td></tr></table>

指令指针状态标志

<table><tr><td>CS</td></tr><tr><td>DS</td></tr><tr><td>SS</td></tr><tr><td>ES</td></tr></table>

代码段
数据段
堆栈段
附加段

# CPU的内部寄存器

# - 控制寄存器: PSW

# - Process State Word处理机状态字

15 0

<table><tr><td></td><td></td><td></td><td></td><td>O</td><td>D</td><td>I</td><td>T</td><td>S</td><td>Z</td><td></td><td>A</td><td></td><td>P</td><td></td><td>C</td></tr></table>

C —进位标志位

A —半加标志位

S —符号标志位

I —中断允许标志位

O — 溢出标志位

P —奇偶标志位

Z — 零标志位

T —陷阱标志位(单步标志位)

D —方向标志位

<table><tr><td>AH</td><td>AL</td></tr><tr><td>BH</td><td>BL</td></tr><tr><td>CH</td><td>CL</td></tr><tr><td>DH</td><td>DL</td></tr></table>

AX
BX
CX
DX

![](images/911d0e765c30dff47a6243aaa2b6a39b2873a519c8be7ca677125e80c32734f4.jpg)

<table><tr><td>SP</td></tr><tr><td>BP</td></tr><tr><td>SI</td></tr><tr><td>DI</td></tr></table>

堆栈指针
基数指针
源变址
目的变址

<table><tr><td colspan="2">IP</td></tr><tr><td>PSWH</td><td>PSWL</td></tr></table>

指令指针状态标志

<table><tr><td>CS</td></tr><tr><td>DS</td></tr><tr><td>SS</td></tr><tr><td>ES</td></tr></table>

代码段
数据段
堆栈段
附加段

# CPU的内部寄存器

\- 那么，2023年的处理呢？

• AMD64 / x86-64

<table><tr><td>64-bit register</td><td>Lower 32 bits</td><td>Lower 16 bits</td><td>Lower 8 bits</td></tr><tr><td>rax</td><td>eax</td><td>ax</td><td>al</td></tr><tr><td>rbx</td><td>ebx</td><td>bx</td><td>bl</td></tr><tr><td>rcx</td><td>ecx</td><td>cx</td><td>cl</td></tr><tr><td>rdx</td><td>edx</td><td>dx</td><td>dl</td></tr><tr><td>rsi</td><td>esi</td><td>si</td><td>sil</td></tr><tr><td>rdi</td><td>edi</td><td>di</td><td>dil</td></tr><tr><td>rbp</td><td>ebp</td><td>bp</td><td>bpl</td></tr><tr><td>rsp</td><td>esp</td><td>sp</td><td>spl</td></tr><tr><td>r8</td><td>r8d</td><td>r8w</td><td>r8b</td></tr><tr><td>r9</td><td>r9d</td><td>r9w</td><td>r9b</td></tr><tr><td>r10</td><td>r10d</td><td>r10w</td><td>r10b</td></tr><tr><td>r11</td><td>r11d</td><td>r11w</td><td>r11b</td></tr><tr><td>r12</td><td>r12d</td><td>r12w</td><td>r12b</td></tr><tr><td>r13</td><td>r13d</td><td>r13w</td><td>r13b</td></tr><tr><td>r14</td><td>r14d</td><td>r14w</td><td>r14b</td></tr><tr><td>r15</td><td>r15d</td><td>r15w</td><td>r15b</td></tr></table>

<table><tr><td>AH</td><td>AL</td></tr><tr><td>BH</td><td>BL</td></tr><tr><td>CH</td><td>CL</td></tr><tr><td>DH</td><td>DL</td></tr></table>

AX
BX
CX
DX

![](images/1c6ca896a3fa9383ecd6408bb197c98a804e93889366ee98d6b02f7beb0095da.jpg)

<table><tr><td>SP</td></tr><tr><td>BP</td></tr><tr><td>SI</td></tr><tr><td>DI</td></tr></table>

堆栈指针
基数指针
源变址
目的变址
指令指针
状态标志

<table><tr><td colspan="2">IP</td></tr><tr><td>PSWH</td><td>PSWL</td></tr></table>

代码段
数据段
堆栈段
附加段

<table><tr><td>CS</td></tr><tr><td>DS</td></tr><tr><td>SS</td></tr><tr><td>ES</td></tr></table>

# CPU的内部寄存器

\- 那么，2020年的处理呢？

• ARM AArch64,

Registers across CPU modes 

<table><tr><td>usr</td><td>sys</td><td>svc</td><td>abt</td><td>und</td><td>irq</td><td>fiq</td></tr><tr><td colspan="7">R0</td></tr><tr><td colspan="7">R1</td></tr><tr><td colspan="7">R2</td></tr><tr><td colspan="7">R3</td></tr><tr><td colspan="7">R4</td></tr><tr><td colspan="7">R5</td></tr><tr><td colspan="7">R6</td></tr><tr><td colspan="7">R7</td></tr><tr><td colspan="6">R8</td><td>R8_fiq</td></tr><tr><td colspan="6">R9</td><td>R9_fiq</td></tr><tr><td colspan="6">R10</td><td>R10_fiq</td></tr><tr><td colspan="6">R11</td><td>R11_fiq</td></tr><tr><td colspan="6">R12</td><td>R12_fiq</td></tr><tr><td>R13</td><td>R13_svc</td><td>R13_abt</td><td>R13_und</td><td>R13_irq</td><td>R13_fiq</td><td></td></tr><tr><td>R14</td><td>R14_svc</td><td>R14_abt</td><td>R14_und</td><td>R14_irq</td><td>R14_fiq</td><td></td></tr><tr><td colspan="7">R15</td></tr><tr><td colspan="7">CPSR</td></tr><tr><td></td><td>SPSR_svc</td><td>SPSR_abt</td><td>SPSR_und</td><td>SPSR_irq</td><td>SPSR_fiq</td><td></td></tr></table>

<table><tr><td>AH</td><td>AL</td></tr><tr><td>BH</td><td>BL</td></tr><tr><td>CH</td><td>CL</td></tr><tr><td>DH</td><td>DL</td></tr></table>

AX
BX
CX
DX

![](images/e12174e1e807da3f1820e822863ab455952217a5337ee956099c9fc37c09af94.jpg)

<table><tr><td>SP</td></tr><tr><td>BP</td></tr><tr><td>SI</td></tr><tr><td>DI</td></tr></table>

堆栈指针
基数指针
源变址
目的变址
指令指针
状态标志

<table><tr><td colspan="2">IP</td></tr><tr><td>PSWH</td><td>PSWL</td></tr></table>

代码段
数据段
堆栈段
附加段

<table><tr><td>CS</td></tr><tr><td>DS</td></tr><tr><td>SS</td></tr><tr><td>ES</td></tr></table>

# 寻址方式

运算，

需要数据，

需要取数据，

需要知道用哪种方式去取数据，

还需要知道从哪里取数据，

-- 寻址方式

Addressing Mode !

# 但在此之前，

# 必须仔细学习一个汇编指令...

# - MOV指令

格式: MOV OPRD1, OPRD2
目的 源

功能：（OPRD2）→（OPRD1）

其中：目的操作OPRD1

源操作数 OPRD2

存储器 mem

通用寄存器 r

段寄存器 SEG（除CS）

立即数 im

存储器 mem

通用寄存器 r

段寄存器 SEG（含CS）

但也有4种例外情况：

- 目的操作数不能为立即数，或 CS、IP;  
·内存单元之间不能进行数据直接传送；  
- 立即数不能直接传送到段寄存器中；  
·段寄存器之间的不能进行数据直接传送；

# Done !

# 寻址方式Addressing Mode

- Immediate 立即   
- Direct 直接  
- Register 寄存器  
- Register + Indirect 寄存器间接 (2种)   
- Register + Indexing 寄存器相对  
- Base + Displacement 基址变址 (2种)  
- Base + Displacement + Indexing 基址+变址+相对  
- Implicit 隐式

# 寻址方式 — 立即寻址

- 操作数直接包含在指令中！（跟在操作码后面）  
- 操作数是在代码段！！

例如:

MOV AL, 27H

ADD AL, 35H

MOV AX, 2000H

![](images/8ae925e3ea94e1f7071be7106e42b3b53445c22db641b47a82630ea0947bed44.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    A[":"] --> B["操作码"]
    B --> C["imL"]
    C --> D["imH"]
    D --> E["..."]
    E --> F["AH"]
    E --> G["AL"]
```
</details>

注意！！ 地址低位去AL，高位去AH !!!!

# 寻址方式 - 直接寻址

\- 操作数的段内偏移地址直接包含在指令中! （跟在

操作码后面)

\- 操作数是在数据段！！

例如:

MOV AX, [2000H ]

设DS=3000H

![](images/4ac6a6acd056b5851754fa111d7065af910cbb1f0a03e2e1096d637cd190cba6.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    A["操作数"] --> B["00H"]
    B --> C["20H"]
    C --> D["..."]
    D --> E["32000H"]
    E --> F["32001H"]
    F --> G["..."]
    G --> H["DS 3000<br>£<< 2000<br>32000"]
    H --> I["AH"]
    H --> J["AL"]
```
</details>

# 寻址方式 - 寄存器寻址

\- 操作数在某个寄存器中!

例如:

MOV DS, AX

![](images/04d2fefe65893f8d1c455ab7d0e57a1d088499e246b3840d2145b98ef229e1c3.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    A["AX"] --> B["DS"]
    B --> A
```
</details>

# 寻址方式 — 寄存器间接寻址

- 操作数的段内偏移地址放在SI/DI/BP/BX其中一  
个寄存器中!

\- 分两种情况:

- 如果是SI/DI/BX < - 搭配DS在数据段找操作数  
- 如果是BP < - 搭配SS在堆栈段找操作数

# 寻址方式 — 寄存器间接寻址

# 例如：

MOV AX, 2000H

MOV DS, AX

MOV SI, 1000H

MOV AX, [SI]

![](images/a0c4bc2321ddc868b3d75ec5b335810f63a30d80e8989c820d38aad63a98482f.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    A["21000H"] --> B["操作数"]
    B --> C["DS 2000"]
    C --> D["£<< SI 1000"]
    D --> E["21000"]
    F["21001H"] --> G["..."]
    G --> H["AH"]
    G --> I["AL"]
```
</details>

(a)

# 寻址方式 - 寄存器间接寻址

# 例如：

MOV AX, 3000H

MOV SS, AX

MOV BP, 2000H

MOV AX, [BP]

![](images/f6d7eaa7cc34bd743908caa7225b0019913c53af0782c2dca426b4b08646c24a.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    A["操作数"] --> B["32000H"]
    A --> C["32001H"]
    D["ss"] --> E["£<< BP 3000 2000 32000"]
    F["AH"] --> G["AL"]
```
</details>

(b)

# 寻址方式 - 寄存器间接寻址

■ 例:假设有指令: MOV BX,[DI], 在执行时, (DS)=1000H, (DI)=2345H, 存储单元12345H的内容是4354H。问执行指令后, BX的值是什么?  
解：

根据寄存器间接寻址方式的规则，在执行本例指令时，寄存器DI的值不是操作数，而是操作数的地址。该操作数的物理地址(Physical Address, PA)应由DS和DI的值形成，即：

$$
\mathrm{PA} = (\mathrm{DS}) ^ {*} 1 6 + \mathrm{DI} = 1 0 0 0 \mathrm{H} ^ {*} 1 6 + 2 3 4 5 \mathrm{H} = 1 2 3 4 5 \mathrm{H} 。
$$

所以，该指令的执行效果是：把从物理地址为12345H开始的一个字的值传送给BX。

# 寻址方式 - 寄存器间接寻址

■ 例:假设有指令: MOV BX,[DI], 在执行时, (DS)=1000H, (DI)=2345H, 存储单元12345H的内容是4354H。问执行指令后, BX的值是什么?  
解：

根据寄存器间接寻址方式的规则，在执行本例指令时，寄存器DI的值不是操作数，而是操作数的地址。该操作数的物理地址(Physical Address, PA)应由DS和DI的值形成，即：

$$
\mathrm{PA} = (\mathrm{DS}) ^ {*} 1 6 + \mathrm{DI} = 1 0 0 0 \mathrm{H} ^ {*} 1 6 + 2 3 4 5 \mathrm{H} = 1 2 3 4 5 \mathrm{H} 。
$$

所以，该指令的执行效果是：把从物理地址为12345H开始的一个字的值传送给BX。

![](images/17b43c011ab840000e19310f7ad84ca1e30954a9f03e0d226e89e6bcd1278562.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph LR
    A["BX 43"] --> B["DX 54"]
    B --> C["DS: 1000H + DI: 2345H"]
    C --> D["12345H"]
    D --> E["OP 10000H"]
    D --> F["OP 12345H"]
    E --> G["54H"]
    F --> H["43H"]
    G --> I["数据段"]
    H --> I
    style A fill:#f9f,stroke:#333
    style B fill:#ccf,stroke:#333
    style C fill:#cfc,stroke:#333
    style D fill:#fcc,stroke:#333
    style E fill:#cff,stroke:#333
    style F fill:#ffc,stroke:#333
    style G fill:#fcf,stroke:#333
    style H fill:#cff,stroke:#333
    style I fill:#ffc,stroke:#333
```
</details>

# 寻址方式 - 寄存器相对寻址

- 本质是寄存器间接 + 相对寻址：在寄存器间接的基础上再加上地址偏移值DISP；  
- DISP跟着操作码后面，在代码段！！！  
- 同样分两种情况:

- 如果是SI/DI/BX < - 搭配DS在数据段找操作数  
- 如果是BP < - 搭配SS在堆栈段找操作数

例: MOV AX, DISP [SI]

# 寻址方式 — 寄存器相对寻址

例：MOV AX, DISP [SI] ; DISP=1000H; DS = 3000H; SI = 2000H

![](images/fc2da65d0ef5135e725300b5b399d18e08e3333a061ae64e1677084ce890c089.jpg)

<details>
<summary>bar_stacked</summary>

| Category   | Value |
| ---------- | ----- |
| DS         | 3000  |
| £<< SI     | 2000  |
| £<< DISP   | 1000  |
|          | 33000 |
</details>

# 寻址方式 - 寄存器相对寻址

例: 假设指令: MOV BX, [SI+100H], 在执行它时, (DS)=1000H, (SI)=2345H, 内存单元12445H的内容为2715H, 问该指令执行后, BX的值是什么?

解：根据寄存器相对寻址方式的规则，在执行本例指令时，源操作数的有效地址EA为：

$$
\mathrm{EA} = (\mathrm{SI}) + 1 0 0 \mathrm{H} = 2 3 4 5 \mathrm{H} + 1 0 0 \mathrm{H} = 2 4 4 5 \mathrm{H}
$$

该操作数的物理地址应由DS和EA的值形成，即：

$$
\mathrm{PA} = (\mathrm{DS}) ^ {*} 1 6 + \mathrm{EA} = 1 0 0 0 \mathrm{H} ^ {*} 1 6 + 2 4 4 5 \mathrm{H} = 1 2 4 4 5 \mathrm{H} 。
$$

所以，该指令的执行效果是：把从物理地址为12445H开始的一个字的值传送给BX。

# 寻址方式 — 寄存器相对寻址

例: 假设指令: MOV BX, [SI+100H], 在执行它时, (DS)=1000H, (SI)=2345H, 内存单元12445H的内容为2715H, 问该指令执行后, BX的值是什么?

解：根据寄存器相对寻址方式的规则，在执行本例指令时，源操作数的有效地址EA为：

$$
\mathrm{EA} = (\mathrm{SI}) + 1 0 0 \mathrm{H} = 2 3 4 5 \mathrm{H} + 1 0 0 \mathrm{H} = 2 4 4 5 \mathrm{H}
$$

该操作数的物理地址应由DS和EA的值形成,即:

$$
\mathrm{PA} = (\mathrm{DS}) ^ {*} 1 6 + \mathrm{EA} = 1 0 0 0 \mathrm{H} ^ {*} 1 6 + 2 4 4 5 \mathrm{H} = 1 2 4 4 5 \mathrm{H} 。
$$

所以，该指令的执行效果是：把从物理地址为12445H开始的一个字的值传送给BX。

![](images/3c32fb4dc8aaac4692f4bff0fc8c4ae8a76889cd65ae823dd79dc0325c0e6e57.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    BX["BX 27 15"] -->|①| EA["EA: 2445H"]
    EA -->|②| DS["DS:1000H"]
    DS -->|③| OP["OP"]
    OP -->|④| 15H["15H"]
    15H -->|⑤| BS["BX 27 15"]
    BS -->|⑥| SI["SI: 2345H + 100H"]
    SI --> EA
    EA --> DS
    DS --> OP
    OP --> 15H
    15H --> 27H["27H"]
    style BX fill:#FFD700,stroke:#333
    style OP fill:#90EE90,stroke:#333
    style DS fill:#FFD700,stroke:#333
    style 15H fill:#FF6347,stroke:#333
    style 27H fill:#FF6347,stroke:#333
```
</details>

# 数据寻址方式 — 总结

■ 加起来！！！把右边的地址值全加起来！！！  
- BX找DS! ! ! !   
■ BP找SS！！！  
- “直接” v.s “间接”   
- “相对” v.s “变址”

<table><tr><td>源操作数</td><td>指令的变形</td><td>源操作数的寻址方式</td></tr><tr><td>只有偏移量</td><td>MOV AX, [100H]</td><td>直接寻址方式</td></tr><tr><td>只有一个寄存器</td><td>MOV AX, [BX] 或 MOV AX, [SI]</td><td>寄存器间接寻址方式</td></tr><tr><td>有一个寄存器和偏移量</td><td>MOV AX, [BX+100H] 或 MOV AX, [SI+100H]</td><td>寄存器相对寻址方式</td></tr><tr><td>有二个寄存器</td><td>MOV AX, [BX+SI]</td><td>基址加变址寻址方式</td></tr><tr><td>有二个寄存器和偏移量</td><td>MOV AX, [BX+SI+100H]</td><td>相对基址加变址寻址方式</td></tr></table>