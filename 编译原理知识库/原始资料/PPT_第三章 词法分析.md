## 第三章 词法分析

记号 (token)

源程序

词法分析器

取下一个记号

语法分析器

符号表

## 本章内容

词法分析器：把构成源程序的字符流翻译成记号流，还完成和用户接口的一些任务

围绕词法分析器的自动生成展开

介绍正规式、状态转换图和有限自动机概念

## 词法分析的任务：

从左至右逐个字符地扫描源程序，产生一个个的单词符号，把作为字符串的源程序改造成为单词符号串的中间程序。

词法分析器/扫描器：执行词法分析的程序。

词法分析器的功能：输入源程序，输出单词符号。

单词符号：一个程序语言的基本语法符号。分为以下 5 种。

确定

关键字：由程序语言定义的具有固定意义的标识符。也可称为保留字或基本字。例如：Pascal 中的 begin ，endif 等。它是确定的。

不限

2、标识符：用来表示各种名字，如变量名、数组名、过程名等。它是不限的。

β、常数：常数的类型一般有整型、实型、布尔型、文字型等。它是不限的。

、运算符：如+-、\*、／等。它是确定的。

5界符：如逗号、分号、括号、/\*，\*/等。它是确定的。

单词符号的表示形式：词法分析器所输出的单词符号常常表示成二元式（单词种别，单词自身的值）。

单词种别可以用以下形式表示：

1、一类单词统一用一个整数值代表其属性。例如：1代表关键字，2代表标识符等。

2、每一个单词一个类别。例如：1 代表 BEGIN，2 代表 END 等。单词自身的值可以表示成：常量的二进制表示；常量、变量等在符号表种的地址码，等等。

注意：一个语言的单词符号如何分种，分几种，怎样编码，是一个技术问题。标识符一般同归为一种。常数则宜按类型（整、实、布尔）分。。运算符可采用一符一种，但也可把具有一关键字可以将其全体视为一种也可一字一种定共性的视为一种。界符则一般采用一符一种。如何进行分种主要取决于处理上的方便。

若是一符一种分种，单词自身值就不需要了。否则，要查符号表。

例 3-1 ：151 － FORTRAN 编译程序的词法分析器在扫描输入串

IF (5·EQ·M) GOTO 100 后，它输出的单词符号串是：

逻辑IF (34，\_)

左括号 (2，\_)

整常数 （20， ‘5’的二进制表示)

等号（6，\_）

标识符 (26，M')

右括号 (16，\_)

GOTO (30，\_)

标号 （19，100'的二进制表示）

IF 为关键字，种别编码34，('为界符，种别编码2，采用一符一种的编码方式。  
常数类型，种别编码20，单词等号为运算符，种别编码6，M 为标识符，种别编码 26，  
单词自身值为M'  
')'为界符，种别编码16，采GOTO为关键字，种别编码30100为标号，种别编码19，单词内部的值用100的二进制表示。

例 3-2 ： 下述 C++ 代码段： while ( i >= j ) i - - ;经词法分析器处理以后，它将被转换为如下的单词符号串

(while , \_)  
((，\_)  
(id ，指向i的符号表指针)  
(>=，\_)  
( id ，指向 j 的符号表指针  
（）， \_)  
( id ，指向i的符号表指针  
(--,\_)  
(；，\_)

## 词法错误

词法分析器对源程序采取非常局部的观点

例：难以发现下面的错误

$$
\mathsf { f i } \left( \mathsf { a } = \mathsf { f } \left( \mathsf { x } \right) \right) \ldots
$$

在实数是“数字串.数字串”格式下，可以发现下面的错误

123.x

紧急方式的错误恢复删掉当前若干个字符，直至能读出正确的记号

错误修补 进行增、删、替换和交换字符的尝试

## 词法分析与语法分析的关系

1、把词法分析从语

中脱离出来的优点：

使编译程序的结构更加

外存

析和条理化。

·词法分析和语法分析

scanner简

语法

源程

号单同法分析可以使用正则文法自动构造词

·有利于提高

分析

析的

scanner

源程序

·可以改善词 的细节，甚至于一个语法分析配几个 scanner，把不同的输入变成一种内部表示。

2、把词法分析作 scannè 为子程孝分析scanner  
·scanner 当作一遍。

·把 scanner 当作子程序canner 作为一遍

词法分村

的设计

设计前提：

输入

预处理部分

scanner

立的牙程序

预处理

输入缓冲区

法分析器的任务为输出单词符号。

子程序

扫描缓冲区 止理

·必要性：编辑性字符如空白符、回车符等，除了出现在文字和扫描器市双 以外，在别处出现都没有意义。 扫

单词符号

扫描器

功能✨則除无用字符。

语法分析器

·实现：预处理子程序。

图 2.1 词法分析器

## 扫描缓冲区的结构：

缓冲区大小：120 个字符。

采用两个指示器：起点指示器、搜索指示器。

两个互补区。

![](images/7df5e45310ee73ae2da1978ea4db915eb857a1a9b1ee03ba4a283bb23b19d07e.jpg)

## 单词符号的识别——超前搜索

单词符号识别的简单方法：超前搜索

关键字识别：

例如：在标准 FORTRAN 中

$$
1 ~ \cdot ~ \mathsf { D O } 9 9 \mathsf { K } = 1 , 1 0
$$

$$
2 \ \cdot \ \mathrm { I F } ( 5 . \mathsf { E Q } . \mathsf { M } ) \mathrm { I } = 1 0
$$

$$
3 ~ { \cdot } ~ \mathsf { D O } 9 9 \mathsf { K } = 1 . 1 0
$$

$$
4 \cdot \operatorname { I F } ( 5 ) = 5 5
$$

其中的DOIF为关键字

其中的DOIF为标识符的一部分

## 标识符的识别

多数语言的标识符是字母开头的“字母/数字”串，而且在程序中标识符的出现后都跟着算符或界符。因此不难识别。

## 常数的识别

对于某些语言的常数的识别也需要使用超前搜索。算符和界符的识别

对于诸如 C++ 语言中的 “+ +” 66 ，这种复合成的算符，需要超前搜索。

## 词法分析-识别单词，校正拼写错误

描述工具：正规文法正规式

识别工具：有限自动机

单词(正规集)

## 正规表达式与有正规式与正

运算符的优先顺序：先“\*”，次"“最后“”

正规

$\sum ^ { * }$ 的子集U，Ⅴ：

积

2、

$$
\mathsf { U V } = \{ \alpha \beta | \alpha \in \mathsf { U } \ \& \ \beta \in \mathsf { V } \}
$$

3、

n 次积

$$
\mathsf { V } = \mathsf { V W } _ { \cdots } \mathsf { V }
$$

$$
V ^ { 0 } = \{ \varepsilon \}
$$

V的闭包

$$
\lor ^ { * } \ = \lor 0 \ \cup \ \lor 1 \ \cup \ \lor 2 \ \cup \ . . .
$$

V的正则闭包

$$
\mathsf { V } ^ { + } = \mathsf { V } \mathsf { V } ^ { \star }
$$

算得

到的表达式，每一个正规式都对应一个字符串集合，叫做正规集。

“\*”读做“闭 包 99

例 3-3：令Σ= {A，B，0，1}，则：

正规式

正规集

(A|B)(A|B|0|1)\*∑上“标识符”的全体若两个正规式表示相同的正规集，则认为二者等价，记为U=V。例如：$b ( \mathsf { a b } ) ^ { \star } { = } ( \mathsf { b a } ) ^ { \star } \mathsf { b }$

(0|1)(0|1)\* 大

∑上“数”的全体

(a|b)\*=(a\*b\*)\*

例 3-4：令∑= {a，b}，下面是∑上的正规式和相应的正规集：

正规式 正规集

ba\* ∑上所有的以b为首，并且后跟任 意多个 a 的字，{b, ba,baa,baaa,…….}

a(a|b)\* ∑上所有的以a为首的字

$( \mathsf { a } | \mathsf { b } ) ^ { \star } ( \mathsf { a } \mathsf { a } | \mathsf { b } \mathsf { b } ) ( \mathsf { a } | \mathsf { b } ) ^ { \star }$ ∑上所有含有两个连续的 a 或者 b的字令U、Ⅴ和W均为正规式，显而易见，下列关系普遍成立：

$1 \cdot \mathsf { U } | \mathsf { V } = \mathsf { V } | \mathsf { U }$ (交换律)

$2 \setminus \mathsf { U } \left| \left( \mathsf { V } \left| \mathsf { W } \right. \right) = \left( \mathsf { U } \left| \mathsf { V } \right. \right) \right| \mathsf { W }$ (结合律)；

$3 \cdot \mathsf { U } ( \mathsf { W } \mathsf { M } ) = ( \mathsf { U } \mathsf { V } ) \mathsf { W }$ (结合律);

$4 \setminus \mathsf { U } ( \mathsf { V } | \mathsf { W } ) = \mathsf { U } \mathsf { V } | \mathsf { U } \mathsf { W }$ (分配律)

## 练习

## 标识符类单词

“由字母和数字组成，但第一个字符必须是字母”

设字母 $a { = } \{ \mathbf { a } | \mathbf { b } | \mathbf { c } _ { \cdots } | z \}$ $\scriptstyle \mathsf { n } = \{ 0 | 1 | 2 , \ldots | 9 \}$

正规式

$$
r { = } \mathsf { a } ( \mathsf { a } \mid \mathsf { n } ) ^ { \star }
$$

出 正规文法

$$
\begin{array} { c } { { \mathsf { G } : S \to \mathsf { a A } | \mathsf { a } } } \\ { { \mathsf { A } \to \mathsf { a A } | \mathsf { n A } | \mathsf { a } | \mathsf { n } } } \end{array}
$$

## 练习

## 十进制整型常量

“由 0-9 数字组成”

正规式 $\mathbf { \partial } = ( 1 \mid \ldots \mid 9 ) ( 0 \mid \ldots \mid 9 ) ^ { * } \mid 0$

正规文法=

## 正规式和正规文法的等价性

正规式转正规文法

正规文法转正规式

正规集

## 两者之间的转换方法见书46-47页

## 正规式 ${ \sf R } = \sf { a } ( \sf { a } | \sf { d } ) ^ { \star }$ 转换为等价正规文法

令S是文法的开始符号，首先形成 $S \to \alpha ( \alpha | d ) ^ { * }$ ,然后形成 $S {  } a A$ 和 $A \to ( a | d ) ^ { * }$ ,再变换形成

$$
S {  } a A A {  } ( a | d ) B
$$

$$
A { \xrightarrow { } } e \quad B \to ( a | d ) B
$$

$$
B {  } \varepsilon
$$

进而变换为全部符合正规文法产生式的形式：

$$
S  a A B  a B
$$

$$
A  \alpha B B  d B
$$

$$
A {  } d B \quad B {  } { \varepsilon }
$$

$$
A {  } \varepsilon
$$

表3.1 正规文法到正规式的转换规则
<table><tr><td></td><td>文法产生式</td><td>正规式</td></tr><tr><td>规则1</td><td> $A  x B$   $B {  } y$ </td><td> $A = x y$ </td></tr><tr><td>规则2</td><td> $A {  } x A | _ { \textrm { y } }$ </td><td> $A = x ^ { * } \ y$ </td></tr><tr><td>规则3</td><td> $A  x$   $A  y$ </td><td> $A = x \mid y$ </td></tr></table>

## 练习

文法 G[S]:

$$
\mathsf { A } \mathrm { - } \mathsf { > a } \mathsf { A }
$$

$$
\mathsf { A } \mathrm { - } \mathsf { > } \mathsf { d } \mathsf { A }
$$

$$
A = \tt { > } a
$$

$$
A = > 0
$$

转换为等价的正规式

首先有

$$
S { = } a A | a
$$

$$
A = \left( a A \vert d A \right) \vert \left( a \vert d \right)
$$

再将A的正规式变换为 $A = ( a \mid d ) A \mid ( a \mid d )$ ，又变换为 $A { = } ( a | d ) ^ { * } ( a | d )$ ，再将A右端代入S 的正规式得

$$
S = a ( a \mid d ) ^ { * } ( a \mid d ) | a
$$

再利用正规式的代数变换可依次得到

$$
\begin{array} { l } { { S = a \left( a \left| d \right. \right) \cdot \left( a \left| d \right. \right) \left| \varepsilon \right. } } \\ { { S = a \left( a \left| d \right. \right) \cdot } } \end{array}
$$

即 $a \left( a \left| d \right. \right) ^ { * }$ 为所求。

## 状态转换图

转换图：是一张有限方向图。在状态转换图中，结点代表状态，用圆圈表示。状态之间用箭弧连接。箭弧上的标记（字符）代表在射出结状态下可能出现的输入字符或字符类。

状态转换图的功能：用于识别一定的字符串。

初态：一张转换图的启动条件，至少有一个，用圆圈表示。

终态：一张转换图的结束条件，至少有一个，用双圈表示。

\*：表示多读进了一个字符。

（c）识别整数的转换  
![](images/fb32b9bcfe0e3d94f1753f39802b1337fca4f1a347b9e1c232c9eb62c1dbce2b.jpg)

例 3-5：简单的状态转换图示例：

![](images/e99e195b7d0fbe7d95e47f817d3168b0b3769d1ce1cd20f1888187a81d26eeb1.jpg)

![](images/2fb4ebfd129964d61f4479ccff07c1ed7fb0e59f89d6d73af60adf3e233bfb81.jpg)  
图

例 3-6：识别 FORTRAN 实型常数的转换图：

例如下列实型常数可以被以下转换图识别：

![](images/320187ded49ae7860ac2fdca3e9bca523f5c40c52d587ea2be9ea007f1fc9053.jpg)  
图3.2 状态转换图

例3-7：综合实例—一做出识别下表所示的小语言的单词符号的状态转换图
<table><tr><td rowspan=1 colspan=1>单词符号</td><td rowspan=1 colspan=1>种别编码</td><td rowspan=1 colspan=1>助忆符</td><td rowspan=1 colspan=1>内码值</td></tr><tr><td rowspan=1 colspan=1>DIM</td><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>$DIM</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>IF</td><td rowspan=1 colspan=1>2</td><td rowspan=1 colspan=1>$IF</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>DO</td><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>$ DO</td><td rowspan=1 colspan=1>一</td></tr><tr><td rowspan=1 colspan=1>STOP</td><td rowspan=1 colspan=1>4</td><td rowspan=1 colspan=1>$ STOP</td><td rowspan=1 colspan=1>一</td></tr><tr><td rowspan=1 colspan=1>END</td><td rowspan=1 colspan=1>5</td><td rowspan=1 colspan=1>$ END</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>标识符</td><td rowspan=1 colspan=1>6</td><td rowspan=1 colspan=1>$ID</td><td rowspan=1 colspan=1>1</td></tr><tr><td rowspan=1 colspan=1>常数 (整)</td><td rowspan=1 colspan=1>7</td><td rowspan=1 colspan=1>$INT</td><td rowspan=1 colspan=1>内部字符串</td></tr><tr><td rowspan=1 colspan=1>三</td><td rowspan=1 colspan=1>8</td><td rowspan=1 colspan=1>$ ASSIGN</td><td rowspan=1 colspan=1>标准二进制形式</td></tr><tr><td rowspan=1 colspan=1>十</td><td rowspan=1 colspan=1>9</td><td rowspan=1 colspan=1>$ PLUS</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>大</td><td rowspan=1 colspan=1>10</td><td rowspan=1 colspan=1>$ STAR</td><td rowspan=1 colspan=1>一</td></tr><tr><td rowspan=1 colspan=1>**</td><td rowspan=1 colspan=1>11</td><td rowspan=1 colspan=1>$ POWER</td><td rowspan=1 colspan=1>欢</td></tr><tr><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>12</td><td rowspan=1 colspan=1>$ COMMA</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>(</td><td rowspan=1 colspan=1>13</td><td rowspan=1 colspan=1>$ LPAR</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>14</td><td rowspan=1 colspan=1>$ RPAR</td><td rowspan=1 colspan=1></td></tr></table>

右图即为对上页所示的简单语言进行词法分析的状态转换图。

## 字母或数字

![](images/897bc492f954c50ac753c8c408da894471218684c34df22fbfb85e76f8474713.jpg)

## 状态转换图的实现

1、CHAR 字符变量，存放最新读进的源程序字符。

2TOKEN 字符数组，存放构成单词的字符串。

3GETCHAR 过程，将下一输入字符读入 CHAR，搜索指示器前移一个字符。

4GETBC 过程，检查CHAR 中的字符是否为空白。若是，则调用GETCHAR

直至 CHAR 中进入一个非空白字符。

5CONCAT 过程，把CHAR 中的字符连接到 TOKEN 之后。

6LETTER 布尔函数过程，它们分别判断CHAR 中的字符是数字或是字母DIGIT 从而给出真假值TRUEFALSE。

7RESERVE 整型函数过程，用 TOKEN 中的字符串查保留字表，若是一个保留

字则给予编码，否则回送0值（假定0不是保留字的编码）。

以上函数和子程序过程都不难编制，使用它们能够方便的构造状态转换图的对应程序。一般，我们可以让每一个状态结对应一个程序段。

例如：我们可以让不含回路的分叉结，对应一个CASE 语句，或者是一组 IF...THEN...ELSE 语句。具体见后面实例。

终态结一般对应一个 RETURN(C,VAL)语句。其中 C 为单词种别编码；VAL 是字符数组的 TOKEN ，或者是一个整数值，或者无定义。具体见后面实例。

为了把状态转换图转化成程程序，它要做的工作如下：

GETCHAR是过程，将下一输入字符读入CHAR，搜索指示器前移一个字符。

第一步：从输入缓中取一个字符。为此，我们使用函数GCHAR，每次调用它，推进先行指针，送回一个字符。

第二步：确定在本状态下，哪一条箭弧是用刚刚来的输入字符标识的。如果找到，控制就转到该弧所指向的状态；若找不到，那么寻找该单词的企图就失败了。

失败：先行指针必须重新回到开始指针处，并用另一状态图来搜索另一单词。如果所有的状态转换图都试过之后，还没有匹配的，就表明这是一个词法错误，此时，调用错误校正程序。

![](images/38d432c9119b812d175d30b9b98515395238a85593e238d004709a415d9ec175.jpg)

例3一8：以下CASE语态图：

statei： GETCHAR；读取下—个输入字符：CASE CHAR O // 判断 $\mathsf { C H A R }$ 是什么

END ;

字符变量，存放最新读进的源程序字符。

过程，将下一输入字符读入CHAR，搜索指示器前移一个字符。

![](images/d48767f9121d4c690eb522842a29a666f493ea1638d90b98d3b76e3b45cae159.jpg)

## 例3-9：示例- -如何把状态结对应于一段程序：

字母或数字

字母

![](images/8a27ba80417c5f3ea874d9e60aff2f7399be54781fa33f4cda3280efef5934dd.jpg)

其他

DELIMITER(C) 是过程，只要碰到标识符后的分界符，它返回TRUE。分界符一般为：空格、算术、逻辑符号，括号、

对于如上的状态转换图，状态1的代码如下所。

state 1 : ${ \bf C } : = { \bf G E T C H A R }$

if LETTER( C) or DIGIT(C)

then goto state 1

else if DELIMITER(C)

then goto state 2

else FAIL()

![](images/dbbb6a0ed9dccff6528aeee582d001cdf488fc62053fae90e10a7b9623cce604.jpg)

例 3 －10：以下程序段对应的布尔函数过程，它们分别判断 CHAR 中的字符是数字或是字母，从而给出真假值TRUEFALSE。

![](images/d824892846e65aebf33b751a1b7ab31cab833dc14ba1d852140f37fd8ecb21e9.jpg)

![](images/36096eea88e996008ba84ed462d2a004b05324ba2dc39efdb9f4d69982d7fe3c.jpg)

```sql
例 3 － 11：以下程序段对应的状态图
0'... '9' ： BEGIN
WHILE DIGIT DO
BEGIN CONCAT ; GETC
RETRACT ;
RETURN($INT,DTB) ;
END ;
```

## 正规式：(012..19)(01|2.19)\*

RETURN 语句，对应终态结，其中 \$INT 为种别编码，DTB 为一个把十进制转换到二进制的转换函数。它把 TOKEN 中的数字译成标准二进制码，并以此为函数值返回。

## 有限自动机（FA）确定有限自动机（DFA）

一个确定有限自动机（DFA）M是一个五元式：

$\begin{array} { r } { \mathsf { \textbf { M } } = \left( \mathsf { S } , \mathsf { \sum } , \mathsf { m o v e } , \mathsf { S } _ { 0 } , \mathsf { F } \right) } \end{array}$ ，其中

1、S是一个有限集，它的每个元素称为一个状态

2、Σ是一个有穷字母表，它的每个元素称为一个输入字符

3move是一个从S×∑至S的单值部分映射。 $\delta ( \mathsf { s } , \mathsf { a } ) = \mathsf { s } ^ { \prime }$ 意味着：当现行状态为、输入字符为a时，将转换到下一状态 $\bullet ^ { \prime }$ 。我们称 $\bullet ^ { \prime }$ 为s的一个后继状态。

4 $\mathsf { s } _ { \mathsf { o } } { \mathsf { \in } } { \mathsf { s } }$ 是唯一的初态

5、F气是一个终态集（可空）。

显然，一个 DFA 可用一个矩阵表示，该矩阵的行表示状态，列表示输入字符，矩阵元素表示 $\delta ( \mathsf { s } , \mathsf { a } )$ 的值。这个矩阵称为状态转换矩阵。

$$
\mathbb { M } = ( \{ 0 , 1 , 2 , 3 \} , \{ \mathsf { a } , \mathsf { b } \} , \delta , \{ 3 \} )
$$

其中δ为：

例2-12：有DFA  
相应的状态转换矩阵如下表：
<table><tr><td rowspan=1 colspan=1>状态</td><td rowspan=1 colspan=1>a</td><td rowspan=1 colspan=1>b</td></tr><tr><td rowspan=1 colspan=1></td><td rowspan=2 colspan=1>I</td><td rowspan=2 colspan=1>2</td></tr><tr><td rowspan=1 colspan=1>U</td></tr><tr><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>&#x27;3</td><td rowspan=1 colspan=1>2</td></tr><tr><td rowspan=1 colspan=1>2</td><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>3</td></tr><tr><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>3</td></tr></table>

一个DFA也可用一张（确定的）状态转换图来表示。假定DFA Μ 含有 m 个状态和 n 个输入字符，那么，这个状态转换图含有 m 个状态结点，每个结点顶多有 n 条箭弧射出和别的结点相连接，整张图含有一个初态结点和若干个（可以为0）终态结点

如下表所示的状态转换矩阵对应的状态转换图如右图：

<table><tr><td rowspan=1 colspan=1>状态</td><td rowspan=1 colspan=1>a</td><td rowspan=1 colspan=1>B</td></tr><tr><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>2</td></tr><tr><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>2</td></tr><tr><td rowspan=1 colspan=1>2</td><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>3</td></tr><tr><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>3</td></tr></table>

![](images/09cc590a5e746e6ed45e55f77ea15027b06adc195c784816bdef2cc5e51f75d2.jpg)  
图 3.5 状态转换图

上图所示的状态转换图的S、Σ及∑\*如下：

$$
S = \{ 0 , 1 , 2 , 3 \}
$$

$$
S = \{ a , b \}
$$

$\sum ^ { + } \{ { \bf a } \mid 0$ 为ε，或者 α 为 ab 的任意组合}

![](images/ad2d768f9776ece327b915cf323378b23981082b19af68f6a51f1dbbffe50e74.jpg)

从初态0到终态3有同理：从初态0到终态3还有如图所示的通路，箭弧上到标记符连接起来的字 bba属于∑\*，所以右图所示的 DFA 可以识别字bba。

加上可选的小数部分，数字常量的正则表达式 number = signedNat(“.”nat)？对应的 DFA 如下图：

$$
\bf { 0 . 1 9 1 t = 1 0 . 9 }
$$

$$
\boldsymbol { \mathrm { n a t } } = \boldsymbol { \mathrm { d i g } } \boldsymbol { \mathrm { i t } } ^ { + }
$$

signedNat = ( +|- )? nat

$$
\mathsf { n u m b e r } = \mathsf { \underline { { s } } i g n e d N a l t } ( ^ { u } ,
$$

digit

nat 对应的 DFA 如下图

signedNat 对应的 DFA 如下图

digit

接受与正则式 ab+| ab\*| b\* 相同的语言的 DFA 如下所示：

![](images/9a881d313d1134ecac7ee69f0061ee04ea5861f8b5b4c51313794768afea5b95.jpg)

例 3-14：串中只有一个 b 被如下所示的 DFA 接受：

![](images/ec29004f1ada13f2f54e0f8d88137d26d946a9b88a9601f0c58f24552cc46134.jpg)

注意二者之间的区别

例 3-15：包含最多一个 b 的串被如下所示的 DFA 接受：

![](images/cafa64a1ab16144c5ed9102c40996c70236e2ae5ea7c824a2f31b815f1ac0b5c.jpg)

定理：如果一个 DFA M 的输入字母表为Σ，则我们也称Μ 是Σ上的一个 DFA。可以证明：∑上的一个字宗Ⅴ ∑\*是正规的，当且仅当存在Σ上的 DFA Μ，使得 Ⅴ=L(M)。

DFA 的确定性表现在映射δ： S×∑→s 是一个单值函数。即：对于任何状态 s∈S 和输入符号 a∈∑，δ(s,a) 唯一确定了一个状态。

从转换图角度，我们也可以得到答案。

如果允许是一个多值函数，我们就得到下一节要讲到的非确定自动机的概念。

## 非确定有限自动机 （NFA）

一个非确定有限自动机（NFA） M 是一个五元式：

$\begin{array} { r } { \mathsf { M } \ = \ ( \mathsf { S } , \mathsf { \sum } , \mathsf { m o v e } , \mathsf { S } _ { 0 } , \mathsf { F } ) } \end{array}$ ，其中

1S是一个有限集，它的每个元素称为一个状态

2、Σ是一个有穷字母表，它的每个元素称为一个输入字符

3、 $\mathsf { m o v e }$ 是一个从 $S \times \Sigma ^ { \star }$ 至S的子集的映射，即δ： $S \times \sum ^ { \ast } \to 2 ^ { s }$

4 $S _ { \vartheta }$ 写是一个非空初态集

5、 $F ^ { \sum } \overline { { \overline { { \mathbf { \mu } } } } }$ 是一个终态集（可空）。

个含有 m 个状态和 n 个输入字符的 NFA 可用一张如下的状态转换图来表示：该图含有 m 个状态结点，每个结点可以射出若干条弧与别的结点相连接，每条弧用Σ\*中的一个字（可以是不同的字，也可以是空字）做标记，整张图至少含有一个初态结点和若干个（可以为0）终态结点。某些结点既可以是初态结点也可以是终态结点。

![](images/7b671ef1809faef89aa261a5c3c3010b146d142a897d99142721c2e9203c7d4d.jpg)

![](images/9a0863a0fcc6bdc87c590de02878518c29a66a3ef1b55751440ee7f6df63d393.jpg)

下图所示的状态转换图的S、Σ及Σ\*如下：

$$
S = \{ 0 , 1 , 2 , 3 , 4 , 5 , 6 \}
$$

$$
\sum = \{ a , b \}
$$

∑\*= {α| α为 ε，或者 α 为 a b 的任意组合 }

从初态x到终态y的连接通路弧上，有如下标记字： 记字：εεaaεε，去除ε，为aa，所以字aa可为NFA NFA接受。

对于Σ\*中的任何一个字α，若从某一初态结点到某一的通路，且这条通路上的标记字依序连接成的ε）等于α，则称α  
可以为 NFA M 识别。

![](images/f60c0262d8ebe882cf2e6b244b1677650fe513e4e6f170f089af8aa24a44c35e.jpg)

接受ab

接受 $\widehat { \mathbf { q } } \mathbf { b } ^ { \mathrm { ~ + ~ } }$

接受 $\widehat { \mathbf { a } } \mathbf { b } ^ { \star }$

接受 ${ \bf { b } } ^ { \star }$

![](images/d45b31aa9ce4f252e67e148f320023a53ebcdaa3df1e8a88ef1408501e92683a.jpg)

由此，我们可以看出这个NFA接受与正则式 ab+|ab\*| b相同的语言！

例 3-16：上图所示的 NFA 的以下两个转换序列都可以接受串 abb：

$$
\begin{array} { l } { { -  1 \longrightarrow 2 \stackrel { b } {  } 2 \stackrel { b } {  } 4 \stackrel { \varepsilon } { \longrightarrow } 2 \stackrel { b } {  } 4 } } \\ { { -  1 \stackrel { a } { \longrightarrow }  3 \stackrel { \varepsilon } { \longrightarrow } 4 \stackrel { \varepsilon } { \longrightarrow } 2 \stackrel { b } {  } 4 \stackrel { \varepsilon } { \longrightarrow } 2 \stackrel { b } {  } 4 \stackrel { \varepsilon } { \longrightarrow } 2 \stackrel { b } {  } 4 } } \end{array}
$$

## 练习：考虑以下 NFA 通过怎样的转换接受串 acab：

![](images/3513e1d485cd2aa4d3c35d8ba93367ba902469521f81a84bb660009a6e16a158.jpg)

## NFA转换为等价的DFACLOSURE(I)的定义

DFA 是 NFA 的特例，可以采用子集法将 NFA 确定

化

假定Ι 是 NFA Μ 的状态集的一个子集，我们定义ε\_CLOSURE(I)为：

1、若s∈I，则 $\mathsf { S } { \in } \varepsilon \_ { \mathsf { C L O S U R E } ( \mathbb { I } ) }$

2、若s∈I，那么从s出发经过任意条ε弧而能到达的任何状态s'都属于ε\_CLOSURE(I)。

状态集ε\_CLOSURE(I)称为的ε\_闭包。

## Move运算

假定Ι是NFA Μ的状态集的子集， $\tt a \in \tt S$ ，定义

$$
\scriptstyle \mathbf { J } = \mathbf { m o v e } ( \mathbf { I } )
$$

其中，J是那些可从中的某一状态结点出发经过一条a弧而

到达的状态结点的全体。

## 子集算法

1 表的初始化构造

2 处理表的一行

3 重复处理

如果某一行的第一列的状态子集已经确定，例如记为${ \mathbb I } ,$ 那么，求出这一行的第二个和第三个子集 $\mathbb { I } _ { \mathfrak { a } }$ 和 $\mathbb { I } _ { \mathrm { b } }$ 看它们是否已在表的第一列出现将未出现的填入到后面空行的第一列。

## Ja为 {5,3}

例 3-17：考虑下图所示NFA的确定化  
![](images/5bc9be1af9c26c0a5f3f54e2005e5ad1fbedb655980e5a5f066efa1f189c5a97.jpg)

<table><tr><td rowspan=1 colspan=1>I</td><td rowspan=1 colspan=1>Ia</td><td rowspan=1 colspan=1>Ib</td></tr><tr><td rowspan=1 colspan=1>{X,5,1}</td><td rowspan=1 colspan=1>{5,3,1}</td><td rowspan=1 colspan=1>{5,4,1}</td></tr><tr><td rowspan=1 colspan=1>{5,3,1}</td><td rowspan=1 colspan=1>{5,3,1,2,6,Y}</td><td rowspan=1 colspan=1>{5,4,1}</td></tr><tr><td rowspan=1 colspan=1>{5,4,1}</td><td rowspan=1 colspan=1>{5,3,1}</td><td rowspan=1 colspan=1>{5,4,1,2,6,Y}</td></tr><tr><td rowspan=1 colspan=1>{5,3,1,2,6,Y}</td><td rowspan=1 colspan=1>{5,3,1,2,6,Y}</td><td rowspan=1 colspan=1>{5,4,1,6,Y}</td></tr><tr><td rowspan=1 colspan=1>{5,4,1,6,Y}</td><td rowspan=1 colspan=1>{5,3,1,6,Y}</td><td rowspan=1 colspan=1>{5,4,1,2,6,Y}</td></tr><tr><td rowspan=1 colspan=1>{5,4,1,2,6,Y}</td><td rowspan=1 colspan=1>{5,3,1,6,Y}</td><td rowspan=1 colspan=1>{5,4,1,2,6,Y}</td></tr><tr><td rowspan=1 colspan=1>{5,3,1,6,Y}</td><td rowspan=1 colspan=1>{5,3,1,2,6,Y}</td><td rowspan=1 colspan=1>{5,4,1,6,Y}</td></tr></table>

ε\_CLOSURE(J)为{5,3，1}（根据ε\_闭包的定义)

=ε\_CLOSRE{X}勺{X,5,1}从状态出发经过一条根据此方法依次求出左边表中的状态转换矩阵即可。E\_CLUSURU)-{,3,1}。从而Ia={5,3,1}。

对右下图表中的所有子集重新命名，得到左图中的状态转换矩阵形成如下状态转换矩阵，从而得到相应的DFA。如图所示：

根据重命名的状态填写表格

<table><tr><td rowspan=1 colspan=3></td></tr><tr><td rowspan=1 colspan=1>S</td><td rowspan=1 colspan=1></td><td></td></tr><tr><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>2</td></tr><tr><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>2</td></tr><tr><td rowspan=1 colspan=1>2</td><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>5</td></tr><tr><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>4</td></tr><tr><td rowspan=1 colspan=1>4</td><td rowspan=1 colspan=1>6</td><td rowspan=1 colspan=1>5</td></tr><tr><td rowspan=1 colspan=1>5</td><td rowspan=1 colspan=1>6</td><td rowspan=1 colspan=1>5</td></tr><tr><td rowspan=1 colspan=1>6</td><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>4</td></tr></table>

![](images/d2a3de39b68c08e2fe9686d12b60bb2a7cb3fa23851a890b4bda467a85f12db8.jpg)

例 3-18：考虑下图所示 NFA 的确定化：  
![](images/bace18d82d797d651acb711730a043f7d5c36e66b5c5c3a21ab3cfdd777bca88.jpg)

## NFA→DFA 转换方法小结

设 DFA M={S,Σ,D,S0,St}，NFA N={K,Σ,f,K0,Kt}

(1) S由上述的C组成

(2) Μ 和 N 的输入字母表是相同的，即Σ

(3) 转换函数D是这样定义的： 当ε-closure(move[S1,S2,..,Sj],a))=[R1,R2,...,.Ri]; 则定义 D([S1,S2,..,Sj],a) =ε-closure(move[S1,S2,..,Sj],a)) =[R1,R2,..,Ri]

(4) S0=ε--closure(K0) 为 M 的开始状态;

(5) St={[Sj,Sk....,Se],其中 [Sj,Sk,...,Se]∈S 且 {Sj,SKk,...,Se}∩Kt≠∅}

## 确定有限自动机的化简

一个确定有限自动机M 的化简是指：

寻找一个状态数比 M 少的 DFA M’，使得 $\mathsf { L } ( \mathsf { M } ) { \mathop { = } } \mathsf { L } ( \mathsf { M } ^ { \prime } )$ o

一个 DFA M 的状态最少化过程旨在将 M 的状态集分割成些不相交的子集，使得任何不同的两个子集中的状态都是可区别的，而同一子集中的任何两个状态都是等价的。最后，在每个子集中选出一个代表，同时消去其它等价状态。

例 3-19：考虑下图所示 DFA 的化简：

划分的组为：{3,4,5,6},{1}, {0},{2} 2}

至此，整个划分有4组：  
{3,4,5,6},{1},{0},{2}。每个组都不可再划分。最后令状态3代表{34，5，6}  
，把原来到达4、5、6状态得弧都导入3，并删除4、5、6，这样就得到了下图一一化简以后的DFA :

![](images/26aee8622286f726fc1488ea57851e9b8fca6d18e6fdbc554010b98e2f182221.jpg)

## 正规式与有限自动机的等价性

关于正规式和有限自动机的等价性，有以下结论：

1、对于任何有限自动机 M，都存在一个正规式 r，使得 $\lfloor ( \boldsymbol { \mathsf { r } } ) = \lfloor ( \boldsymbol { \mathsf { G } } )$ O

2、对于任何正规式 r，都存在一个有限自动机 M，使得$\mathsf { L } ( \mathsf { M } ) = \mathsf { L } ( \mathsf { r } )$ O

替换规则：用于证明结论：对于任何有限自动机M都存在一个正规式r，使得 $\mathsf { L } ( \mathsf { r } ) = \mathsf { L } ( \mathsf { G } )$

① $\textcircled { 1 } \textcircled { 2 } \textcircled { 1 } \textcircled { 3 }$

![](images/1f7148b285529bb6d22e7c3554e0ef30ba1f61dbe83e6a4b297bd1cfec87fbd3.jpg)

![](images/5118d08dfaad72a814ce9f8fb7728403325440f98842419763fbe14e4f2fd331.jpg)

代之以

代之以

代之以

① $\textcircled{2}$

① V\_1IV{2 2

1 $V _ { 1 } V _ { 2 } ^ { \star } V _ { 3 }$ 2

a,b

NFA 转换为正规式：

![](images/bf9d27f306bceabf5e6ecb21215ecb9fbdf8bb53bbb787e012aa31ddf36fcfc4.jpg)

a,b

$$
( a | b ) ^ { * } ( a a | b b ) ( a | b ) ^ { * }
$$

![](images/ae15ac6b00ce63d2e511f90e44ae67500844ab3bf2d086f050577caa7bf805e3.jpg)  
a,b

代之以

![](images/3e6bf87a00f688100b7cfa7bc2272fb0dd81270391efa3f810664b232e695a62.jpg)

![](images/2144ea39b6ff1b55c9b89201bf054b0711c75169326c0854f8bb111fe9f4d662.jpg)

代之以

![](images/242f789e4e8bda9288039a9b1fabe72e45bac6139797279157773d97cf295b70.jpg)

![](images/0b68d8e4a62f6fd67480bb95797b8554e4d9c768462bbf65a75badd3cd6df04a.jpg)

代之以

![](images/9ad4e1dfca4f137cf5353b0949032e692e4eb963e63b1edcac1db72d6861db82.jpg)

正规式： $\mathsf { r } \mathrm { = } \mathsf { a } ( \mathsf { a } | 0 ) ^ { \star }$ 转换为 ${ \tt N F A }$

![](images/7eb0c32bb2c48b5023c7060e9f4f444e3f0477a4041a177a0bcd8d95474b39a6.jpg)

## 练习：

1、将下列非确定有限自动机 NFA 转换为确定有限自动机 DFA，并构造一个正则文法，使得它的句子正是该自动机接受的字符串。

![](images/b00316c9477dce8e2a8ce18ac3d72905ed124ade4833be5c8cbb1afd0e1eb5a3.jpg)

a  
![](images/e3f3a72f8fb51693d387a48a8d45867903b1a8f3440bae4daf837df39c780267.jpg)  
a,b

## 本章要点

词法分析器的作用和接口，用高级语言编写词法分析器等内容

掌握下面涉及的一些概念，它们之间转换的技巧、方法或算法

非形式描述的语言↔正规式

☑ 正规式 → NFA

非形式描述的语言↔ NFA

NFA → DFA

☑ DFA → 最简 DFA

非形式描述的语言↔DFA（或最简DFA)

## 例题1

叙述下面的正规式描述的语言，并画出接受  
该语言的最简DFA 的状态转换图(1101)\* 0\*

描述的语言是，所有不含子串001的0和1的串

![](images/2180c8a1f56a06fa97074aed8c63baf917d9465506f9b191e28cec4602fe8856.jpg)

刚读过的不是0 连续读过一个0

连续读过不少于两个0

## 例题 页2

![](images/1b240bd6a486815931805b6a398f3951ed943524f3f540a9a3c2fae4a5d991ac.jpg)

## 例题 3

写出语言“所有相邻数字都不相同的非空数字串”的正规定义

123031357106798035790123

$$
\begin{array} { l } { { a n s w e r  ( 0 \mid n o \_ { 0 } \ 0 \ ) \ ( n o \_ { \_ { - } } \ 0 \ ) * \ ( n o \_ { \_ { - } } \ 0 \ ) \mid \ } } \\ { { n o \ } { \stackrel { O } {  } } ( { \bf 1 } \mid n o \_ { - } \ 0 \_ { \bf 1 } \ ) \ ( n o \_ { - } \ 0 \_ { \bf 1 } \ 1 \ ) * \ ( n o \_ { - } \ 0 \ - 1 \ \mid \ \varepsilon \ ) \mid } \\ { { \bar { n } o \ } { \stackrel { O } {  } } ( { \bf \frac { 1 } { \varepsilon } } { \mid \varepsilon  } { \stackrel {  } { \Theta } } ) } \\ { { n o \ } { \stackrel { O - } {  } } ( { \bf \frac { 1 } { \varepsilon } } { \mid \varepsilon  } ) } \end{array}
$$

将这些正规定义逆序排列就是答案

## 例题4

下面C语言编译器编译下面的函数时，报告   
parse error before ‘else'   
long gcd(p,q)   
long p,q;   
if (p%q == 0)   
/\* then part \*|   
return q 此处遗漏分号   
else   
I\* else part \*|   
return gcd(q, p%q);

## 例题4

现在少了第一个注释的结束符号后，反而不   
报错了   
long gcd(p,q)   
long p,q; if (p%q == 0) I\* then part return q else I\* else part \*| return gcd(q, p%q);
