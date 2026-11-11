型bAc中A的后面，这样，在 $I _ { 7 }$ 中当面临输入符为c时才能归约。根据项目集的构造原则有：

若[A→α·Bβ]∈项目集I，则[B→·γ]也 $\in I ( B {  } \gamma$ 为一产生式）。

由此不妨考虑把FIRST $( \beta )$ 作为用产生式B→γ归约的搜索符，称为向前搜索符，作为归约时查看的符号集合，用以代替SLR(1)分析中的FOLLOW集，把此搜索符号的集合也放在相应项目的后面，这种处理方法即LR(1)方法。

## 6.4.1 LR(1)项目集族的构造

以 $S ^ { \prime } \to \bullet S$ ，#属于初始项目集中，把#作为向前搜索符，表示活前缀为γ(若γ是有关S产生式的某一右部)要归约成S时，必须面临输入符为#才行。对初始项目 $S ^ { \prime } \to \bullet S$ ，#求闭包后，再用转换函数逐步求出整个文法的LR(1)项目集族。具体构造步骤如下：

(1）构造LR(1)项目集的闭包函数。

①假定I是一个项目集，I的任何项目都属于CLOSURE(I)。

②若有项目 $A \to _ { \alpha } \cdot \ B \beta , _ { \alpha }$ 属于 CLOSURE(I)，B→γ是文法中的产生式， $\beta \in V ^ { \ast }$ $b \in F I R S T ( \beta \alpha )$ ,则 $B  \cdot \gamma , b$ 也属于CLOSURE(I)。

③重复②，直到CLOSURE(I)不再增大为止。

（2）构造转换函数。

LR(1)转换函数的构造与LR(0)的相似：

$$
\operatorname { G O } ( I , X ) { = } \operatorname { C L O S U R E } ( J )
$$

其中I是LR(1)的项目集，X是文法符号，

$$
J = \{ \{ \pm \{ \pi \} \} \{ \not \} \xi \mathtt { H } [ \sum \alpha \_ X \ \bullet \ \beta , a ] \sharp \xi \} \mathbb { H } \boxed { A \to \alpha \ \bullet \ X \beta , a } \in I \}
$$

对文法 $G ^ { \prime }$ 的LR(1)项目集族的构造仍以 $[ S ^ { \prime }  \cdot S$ ，#为初态集的初始项目，然后对其求闭包和转换函数，直到项目集不再增大为止。

也就是对状态I经过符号X后转向状态J,求出J的核后，对核求闭包即为CLOSURE(J)。

现在可以对上面例子中不能用SLR(1)方法解决 $I _ { 5 } , I _ { 7 }$ 中移进-归约冲突的文法构造它的LR(1)项目集规范族如下：

$$
\begin{array} { r l r } { I _ { 0 1 } } & { S ^ { - }  S , ~ \forall , ~ } & { I _ { 1 2 } : S ^ { - } = A \Delta \cdot ~ d , ~ \neq } \\ & { } & { S  ~ + \alpha A d , ~ \neq } \\ & { S  ~ + \alpha A c , ~ \neq } \\ & { S  ~ + \beta A c , ~ \neq } & { A  e . ~ \mathcal { A } ~ \neq } \\ & { S  ~ + \alpha c , ~ \neq } \\ & { S  ~ + \beta c d , ~ \neq } & { I _ { 0 1 } S ^ { - } = b A \cdot c , ~ \neq } \\ & { } & { A  ~ \ast e \cdot S  e . ~ \mathcal { A } ~ \neq } \\ & { I _ { 1 2 } ~ S ^ { + }  S \cdot e . ~ \neq ~ \frac { 1 } { \mathcal { A } } ~ \neq } \\ & { I _ { 2 1 } ~ S ^ { - } \alpha ~ + \mathcal { A } d , ~ \neq } & { I _ { 3 1 } ~ S  e . ~ \partial A d \cdot ~ \neq ~ \mathcal { A } } \\ & { } & { S  e . ~ \neq ~ c . ~ \neq } \\ & { A  ~ \ast e . ~ \neq ~ \frac { 1 } { \mathcal { A } } ~ } & { I _ { 3 1 } ~ S ^ { - } = b A c \cdot ~ \neq ~ \mathcal { A } } \\ & { } & { I _ { 1 2 } ~ S ^ { - } = b \cdot ~ \partial A c , ~ \neq ~ \mathcal { A } ~ \neq } \\ & { S  b \cdot e d , ~ \neq } \\ & { A  ~ \ast e . ~ \quad } \end{array}
$$

这样LR(1)方法构造的项目集规范族在项目集 $I _ { 5 }$ 和 $I _ { 7 }$ 中的移进-归约冲突便可解决。

由于归约项目的搜索符集合与移进项目的待移进符号不相交，所以在 $I _ { 5 }$ 中，当面临输入符为d时归约，为c时移进；而在 $I _ { 7 }$ 中，则当面临输入符为c时归约，为d时移进，冲突已全部可以解决，因此该文法为LR(1)文法。

## 6.4.2LR(1)分析表的构造

由于一个LR(1)项目可以看成由两个部分组成，一部分和LR(0)项目相同，称为心，另一部分为向前搜索符集合，因而LR(1)分析表的构造与LR(0)分析表的构造在形式上基本相同，只是归约项目的归约动作取决于该归约项目的向前搜索符集，即只有当面临的输入符属于向前搜索符的集合，才做归约动作，其他情况均出错。具体构造过程如下：

若已构造出某文法的LR(1)项目集族C:

$$
C = \{ I _ { 0 } , I _ { 1 } , \cdots , I _ { n } \}
$$

其中 $I _ { k }$ 的k为分析器的状态，则动作(ACTION)表和状态转换(GOTO)表构造方法如下：(1)若项目 $[ A \to \alpha \cdot a \beta , b ]$ 属于 $I _ { k }$ ，且 $G \mathrm { O } ( I _ { k } , \boldsymbol { a } ) = I _ { j }$ ，其中 $a \in V _ { \mathrm { T } }$ ,则置 $\mathrm { A C T I O N } [ k , \alpha ] =$ $S _ { j \mathrm { ~ o ~ } } S _ { j }$ 的含义是把输入符号a和状态j分别移入文法符号栈和状态栈。

(2) 若项目 $[ A \to \alpha \cdot , \alpha ]$ 属于 $I _ { k }$ ，则置 $\mathrm { A C T I O N } [ k , a ] = r _ { j }$ 。其中， $a \in V _ { \mathrm { T } } , r _ { j }$ 的含义为把当前栈顶符号串 $\alpha$ 归约为A（即用产生式 $A \to \alpha$ 归约），j为在文法中产生式 $A \to \alpha$ 的编号。

(3) 若项目 $[ S ^ { \prime } {  } S ^ { \mathrm { ~ \bullet ~ } }$ ，#]属于 $I _ { k }$ ,则置 $\mathrm { A C T I O N } [ k , \mp ] = \mathrm { a c c }$ ，表示“接受”。

(4) 若 $\operatorname { G O } ( I _ { k } , A ) = I _ { j }$ ，其中 $A \in V _ { \mathrm { N } }$ ,则置 ${ \mathrm { G O T O } } [ k , A ] = j$ ，表示转入j状态，置当前文法符号栈顶为A，状态栈顶为 $j$ 0

(5）凡不能用规则(1)～(4)填入分析表中的元素，均置报错标志。在本书中用空白表示。

根据上述规则，对上面例子中文法的LR(1)项目集族构造其相应的LR(1)分析表，如表6.10所示。

表6.10 LR(1)分析表
<table><tr><td rowspan="2">状态</td><td colspan="6">ACTION</td><td colspan="2">GOTO</td></tr><tr><td> $a$ </td><td> $^ { b }$ </td><td> $c$ </td><td> $d$ </td><td> $e$ </td><td>#</td><td>S</td><td> $A$ </td></tr><tr><td>0</td><td> $S _ { 2 }$ </td><td> $S _ { 3 }$ </td><td></td><td></td><td></td><td></td><td>1</td><td></td></tr><tr><td>1</td><td></td><td></td><td></td><td></td><td></td><td>acc</td><td></td><td></td></tr><tr><td>2</td><td></td><td></td><td></td><td></td><td> $S _ { 5 }$ </td><td></td><td></td><td>4</td></tr><tr><td>3</td><td></td><td></td><td></td><td></td><td> $S _ { 7 }$ </td><td></td><td></td><td>6</td></tr><tr><td>4</td><td></td><td></td><td></td><td> $S _ { 8 }$ </td><td></td><td></td><td></td><td></td></tr><tr><td>5</td><td></td><td></td><td> $S _ { 9 }$ </td><td> $r _ { 5 }$ </td><td></td><td></td><td></td><td></td></tr><tr><td>6</td><td></td><td></td><td> $S _ { 1 0 }$ </td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>7</td><td></td><td></td><td> $r _ { 5 }$ </td><td> $S _ { 1 1 }$ </td><td></td><td></td><td></td><td></td></tr><tr><td>8</td><td></td><td></td><td></td><td></td><td></td><td> $r _ { 1 }$ </td><td></td><td></td></tr><tr><td>9</td><td></td><td></td><td></td><td></td><td></td><td> $r _ { 3 }$ </td><td></td><td></td></tr><tr><td>10</td><td></td><td></td><td></td><td></td><td></td><td> $r _ { 2 }$ </td><td></td><td></td></tr><tr><td>11</td><td></td><td></td><td></td><td></td><td></td><td> $r _ { 4 }$ </td><td></td><td></td></tr></table>

由表6.10可以看出，对LR(1)的归约项目不存在任何无效归约。但在多数情况下，同一个文法的LR(1)项目集的个数比LR(0)项目集的个数多，甚至可能多好几倍。这是由于同一个LR(0)项目集的搜索符集合不同，多个搜索符集合则对应着多个LR(1)项目集。这可以看成是LR(1)项目集的构造使某些同心集进行了分裂，因而项目集的个数增多了。下面举例说明这一概念。

若文法 $G ^ { \prime }$ 为

(0) $S ^ { \prime } {  } S$

(1) $S {  } B B$

(2) $B {  } a B$

(3) $B {  } b$

它的LR(1)项目集族和转换函数如图6.12所示，LR(1)分析表如表6.11所示。

![](images/c1ee5cf49cd887620267c733ff3b23fbbb46c42de2531d114db5c196922cc562.jpg)  
图6.12LR(1)项目集和转换函数

表 6.11 LR(1)分析表
<table><tr><td rowspan="2">状态</td><td colspan="3">ACTION</td><td colspan="2">GOTO</td></tr><tr><td> $a$ </td><td> $^ { b }$ </td><td>#</td><td> $S$ </td><td>B</td></tr><tr><td>0</td><td> $S _ { 3 }$ </td><td> $S _ { 4 }$ </td><td></td><td>1</td><td>2</td></tr><tr><td>1</td><td></td><td></td><td>acc</td><td></td><td></td></tr><tr><td>2</td><td> $S _ { 6 }$ </td><td> $S _ { 7 }$ </td><td></td><td></td><td>5</td></tr><tr><td>3</td><td> $S _ { 3 }$ </td><td> $S _ { 4 }$ </td><td></td><td></td><td>8</td></tr><tr><td>4</td><td> $r _ { 3 }$ </td><td> $r _ { 3 }$ </td><td></td><td></td><td></td></tr><tr><td>5</td><td></td><td></td><td> $r _ { 1 }$ </td><td></td><td></td></tr><tr><td>6</td><td> $S _ { 6 }$ </td><td> $S _ { 7 }$ </td><td></td><td></td><td>9</td></tr><tr><td>7</td><td></td><td></td><td> $r _ { 3 }$ </td><td></td><td></td></tr><tr><td>8</td><td> $r _ { 2 }$ </td><td> $r _ { 2 }$ </td><td></td><td></td><td></td></tr><tr><td>9</td><td></td><td></td><td> $r _ { 2 }$ </td><td></td><td></td></tr></table>

只要仔细分析该文法的每个LR(1)项目集的项目，不难发现，即使不考查搜索符，它的任何项目集中都没有动作冲突，因此实际上这个文法是LR(0)文法，读者可以自己构造它的LR(0)项目集，可以得知它的LR(0)分析器只含7个状态，而现在LR(1)分析器却含有10个状态，其中 $I _ { 3 }$ 和 $I _ { 6 } , I _ { 4 }$ 和 $I _ { 7 } , I _ { 8 }$ 和 $I _ { 9 }$ 分别为同心集。

如果一个文法的LR(1)分析表不含多重入口(即任何一个LR(1)项目集中无移进-归约冲突或归约-归约冲突)，则称该文法为LR(1)文法，所构造的相应分析表称为LR(1)分析表，使用LR(1)分析表的分析器称为LR(1)分析器或称规范的LR分析器。一个文法是LR(0)文法，就一定也是SLR(1)文法，也是LR(1)文法，反之则不一定成立。

## 6.5 LALR(1)分析

LR(1)分析表的构造对搜索符的计算方法比较确切，对文法放宽了要求，也就是适应的文法类广，可以解决SLR(1)方法解决不了的问题，但是，由于它的构造对某些同心集的分裂可能使状态数目引起剧烈的增长，从而导致存储容量的急剧增加，因此使应用受到一定的限制。为了克服LR(1)的这种缺点，可以采用对LR(1)项目集规范族合并同心集的方法，若合并同心集后不产生新的冲突，则为LALR(1)项目集，它的状态个数与LR(0)、SLR(1)的相同。

例如，分析图6.12中的项目集，可发现如下同心集：

$$
\begin{array} { c c } { { I _ { 3 } : B {  } a \cdot B , a / b } } & { { \qquad I _ { 6 } : B {  } a \cdot B , \# } } \\ { { } } & { { } } \\ { { B {  } \bullet a B , a / b } } & { { } } \\ { { } } & { { } } \\ { { B {  } \bullet b , a / b } } & { { } } \\ { { } } & { { } } \\ { { I _ { 4 } : B {  } b \bullet , a / b } } & { { \qquad I _ { 7 } : B {  } b \bullet , \# } } \\ { { } } & { { } } \\ { { I _ { 8 } : B {  } a B \bullet , a / b } } & { { \qquad I _ { 9 } : B {  } a B \bullet , \# } } \end{array}
$$

即 $I _ { 3 }$ 和 $I _ { 6 } , I _ { 4 }$ 和 $I _ { 7 } , I _ { 8 }$ 和 $I _ { 9 }$ 分别为同心集，将同心集合并后为

$$
\begin{array} { c } { { I _ { 3 } , I _ { 6 } : B {  } a \cdot B , a / b / \mp } } \\ { { \ } } \\ { { B {  } \bullet a B , a / b / \mp } } \\ { { \ } } \\ { { B {  } \bullet b , a / b / \mp } } \\ { { \ } } \\ { { I _ { 4 } , I _ { 7 } : B {  } b \bullet , a / b / \mp } } \\ { { \ } } \\ { { I _ { 8 } , I _ { 9 } : B {  } a B \bullet , a / b / \mp } } \end{array}
$$

同心集合并后仍不包含冲突，因此该文法满足LALR(1)要求。

合并同心集有几个问题需要说明。

（1）同心集是指心相同的项目集合并在一起，因此同心集合并后心仍相同，只是超前搜索符集合为各同心集超前搜索符集合的和集。

(2)同心集经转换函数所达的项目集仍为同心集。因为相同的心经转换函数所达的心仍相同，即仍属同心集，所以合并同心集后转换函数也自动合并。如例中I3和I6为同心集， $I _ { 3 }$ $I _ { 6 }$ 它们的转换函数分别为

$$
\begin{array} { r } { I _ { 3 } \left\{ \mathrm { G O } ( I _ { 3 } , a ) = I _ { 3 } \right. } \\ { \left. \mathrm { G O } ( I _ { 3 } , b ) = I _ { 4 } \right. } \\ { \left. \mathrm { G O } ( I _ { 3 } , B ) = I _ { 8 } \right. } \\ { I _ { 6 } \left\{ \mathrm { G O } ( I _ { 6 } , a ) = I _ { 6 } \right. } \\ { \left. \mathrm { G O } ( I _ { 6 } , b ) = I _ { 7 } \right. } \\ { \left. \mathrm { G O } ( I _ { 6 } , B ) = I _ { 9 } \right. } \end{array}
$$

而 $I _ { 3 }$ 和 $I _ { 6 } , I _ { 4 }$ 和 $I _ { 7 } , I _ { 8 }$ 和 $I _ { 9 }$ 分别为同心集。

(3)若文法是LR(1)文法，合并同心集后，若有冲突也只可能是归约-归约冲突，而不可能产生移进-归约冲突，不妨假设某LR(1)文法的项目集 $I _ { k }$ 与 $I _ { j }$ 为同心集，其中：

$I _ { k }$ 为： $[ A \to \alpha \cdot , u _ { 1 } ]$

$$
[ B \to \beta \cdot \alpha \gamma , b ]
$$

$I _ { j }$ 为： $\left[ A \to \alpha \cdot , u _ { 2 } \right]$

$$
[ B \to \beta \circ \alpha \gamma , c ]
$$

其中 $u _ { 1 } , u _ { 2 }$ 分别为超前搜索符集合。因为假设文法是LR(1)的，所以不可能有移进-归约冲突，也就是在 $I _ { k }$ 中有 $\{ u _ { 1 } \} \cap \{ a \} = \emptyset$ ,在 $I _ { j }$ 中有 $\{ u _ { 2 } \} \cap \{ a \} = \emptyset$ ，显然合并同心集后 $( \left\{ \begin{array} { l } { u _ { 1 } } \end{array} \right\} \bigcup$ $\{ u _ { 2 } \} ) \cap \{ a \} = \emptyset$ 0

（4）合并同心集后对某些错误发现的时间会产生推迟现象，但错误的出现位置仍是准确的。这意味着LALR(1)分析表比LR(1)分析表对同一输入串的分析可能会有多余归约。这个问题将在后面用例子来说明。

现在介绍构造文法的LALR(1)分析表，对于一个文法是否为LALR(1)文法，通常所采用的方法是：构造它的LR(1)项目集族，若不含任何冲突，则合并同心集；若仍不产生归约-归约冲突，则该文法便是LALR(1)文法，就可以根据合并同心集后的项目集族构造该文法的LALR(1)分析表。其构造步骤如下：

(1）构造文法 G的LR(1)项目集族， $C = \{ I _ { 0 } , I _ { 1 } , \cdots , I _ { n } \}$

（2）合并所有的同心集，使C变为 $C ^ { \prime } { = } \{ J _ { \circ } , J _ { 1 } , \cdots , J _ { m } \}$ ，便是LALR(1)的项目集。

(3) 据 $C ^ { \prime }$ 构造动作(ACTION)表，其方法与LR(1)分析表的构造相同。

① 若 $[ A \to _ { \alpha } \bullet \alpha \beta , b ] \in J _ { k }$ ，且 $G ( \boldsymbol { \mathbf { \mathit { J } } } _ { k } , \boldsymbol { \mathbf { \mathit { a } } } ) = \boldsymbol { \mathbf { \mathit { J } } } _ { j }$ ,其中 $a \in V _ { \mathrm { T } }$ ,则置 $\mathrm { A C T I O N } [ k , a ] = { \bf s } _ { j }$ ,其含义是把输入符号a和状态j分别移入文法符号栈和状态栈。

②若项目 $[ A \to \alpha \cdot , \alpha ]$ 属于 $J _ { \textit { k } }$ ,则置 $\mathrm { A C T I O N } [ k , a ] = \mathbf { r } _ { j }$ ,其中 $a \in V _ { \mathrm { T } } , \mathrm { r } _ { j }$ 的含义是 $A \to \alpha$ 是文法的第 $j$ 个产生式，此时把栈顶符号串α归约为A。

③若项目 $[ S ^ { \prime } {  } S \ \cdot$ ，#属于 $J _ { \textit { k } }$ ,则置 $\mathrm { A C T I O N } [ k , \neq ] = \mathrm { a c c }$ ，表示分析成功、接受。

④GOTO表的构造。对于不是同心集的项目集，转换函数的构造与LR(1)的相同，对同心集项目，由于合并同心集后，新集的转换函数也为同心集，因此，假定 $I _ { i _ { 1 } } I _ { i _ { 2 } } , \cdots , I _ { i _ { n } }$ 是同心集，合并后的新集为 $J _ { \textit { k } }$ ，转换函数 $\operatorname { G O } ( I _ { i _ { \cdot } } , X ) , \operatorname { G O } ( I _ { i _ { \cdot } } , X ) , \cdots , \operatorname { G O } ( I _ { i _ { \cdot } } , X )$ 也为同心集，将其合并后记作 $\boldsymbol { J } _ { \ i }$ ，因此，有 $G \mathrm { O } ( J _ { k } , X ) = J _ { i }$ ，所以当X为非终结符时， $\mathrm { G O } ( J _ { k } , X ) = J _ { i }$ ,则置${ \mathrm { G O T O } } [ k , X ] = i$ ，表示在k状态下遇非终结符X时，把X和i分别移到文法符号栈和状态栈；当X为终结符时和 ACTION表重合。

⑤分析表中凡不能用①～④填入信息的均填出错标志。

用上述步骤就可以构造前面的文法的LALR(1)分析表如下： $I _ { 3 }$ 和 $I _ { 6 }$ 合并后用 $I _ { 3 , 6 }$ 表示， $I _ { 4 }$ 和 $I _ { 7 }$ 合并后用 $I _ { 4 , 7 }$ 表示， $I _ { 8 }$ 和 $I _ { 9 }$ 合并后用 ${ \cal I } _ { 8 . 9 }$ 表示。对文法合并同心集后的LALR(1)分析表如表6.12所示。

由于合并同心集后，在新的集合中不含归约-归约冲突，所以该文法是LALR(1)文法。能用LALR(1)分析表进行语法分析的分析器称为LALR(1)分析器。

现在举例说明由于合并同心集可能对某些错误发现的时间产生推迟现象。

上面所给文法识别的句子集合是正规式 $\boldsymbol { a } ^ { * } \boldsymbol { b } \boldsymbol { a } ^ { * } \boldsymbol { b }$ ，也就是该文法可推出的句子必须含有两个b且以b为结尾。因而输入串若为 $a b$ #，显然不是这个文法能推出的句子。但用LR(1)

表6.12合并同心集后的LALR(1)分析表
<table><tr><td rowspan="2">状态</td><td colspan="3">ACTION</td><td colspan="2">GOTO</td></tr><tr><td> $a$ </td><td> $b$ </td><td>#</td><td>S</td><td>B</td></tr><tr><td>0</td><td> $S _ { 3 , 6 }$ </td><td> $S _ { 4 , 7 }$ </td><td></td><td>1</td><td>2</td></tr><tr><td>1</td><td></td><td></td><td>acc</td><td></td><td></td></tr><tr><td>2</td><td> $S _ { 3 , 6 }$ </td><td> $S _ { 4 , 7 }$ </td><td></td><td></td><td>5</td></tr><tr><td>3,6</td><td> $S _ { 3 , 6 }$ </td><td> $S _ { 4 , 7 }$ </td><td></td><td></td><td>8,9</td></tr><tr><td>4,7</td><td> $r _ { 3 }$ </td><td> $r _ { 3 }$ </td><td> $r _ { 3 }$ </td><td></td><td></td></tr><tr><td>5</td><td></td><td></td><td> $r _ { 1 }$ </td><td></td><td></td></tr><tr><td>8,9</td><td> $r _ { 2 }$ </td><td> $r _ { 2 }$ </td><td> $r _ { 2 }$ </td><td></td><td></td></tr></table>

分析表分析和用LALR(1)分析表分析时发现错误的时间不同，现将分析步骤分别写出如下。

用表6.11所示的LR(1)分析表分析输入串 $a b$ #的过程如表6.13所示。

表 6.13 对输入串 ab #用 LR(1)分析的过程
<table><tr><td>步骤</td><td>状态栈</td><td>符号栈</td><td>输入串</td><td>ACTION</td><td>GOTO</td></tr><tr><td>1</td><td>0</td><td>#</td><td> $a b \neq$ </td><td> $S _ { 3 }$ </td><td></td></tr><tr><td>2</td><td>03</td><td>a</td><td> $b \sharp$ </td><td> $S _ { 4 }$ </td><td></td></tr><tr><td>3</td><td>034</td><td>#  $a b$ </td><td>#</td><td>出错</td><td></td></tr></table>

在LR(1)项目集规范族中，当分析进入状态 $I _ { 4 }$ 时，b后只能出现a或b而不能出现#，因而出错。

而用表6.12的LALR(1)分析表分析同样的输入串 $a b$ #，分析过程如表6.14所示。

表6.14对输入串ab#用LALR(1)分析的过程
<table><tr><td>步骤</td><td>状态栈</td><td>符号栈</td><td>输入串</td><td>ACTION</td><td>GOTO</td></tr><tr><td>1</td><td>0</td><td>#</td><td> $a b$  #</td><td> $S _ { 3 , 6 }$ </td><td></td></tr><tr><td>2</td><td>0(3,6)</td><td>#a</td><td>6#</td><td> $S _ { 4 , 7 }$ </td><td></td></tr><tr><td>3</td><td>0(3,6)(4,7)</td><td>ab</td><td>#</td><td> $r _ { 3 }$ </td><td>(8,9)</td></tr><tr><td>4</td><td>0(3,6)(8,9)</td><td> $\sharp _ { \alpha B }$ </td><td>#</td><td> $r _ { 2 }$ </td><td>2</td></tr><tr><td>5</td><td>02</td><td>#B</td><td>#</td><td>出错</td><td></td></tr></table>

在LR(1)分析中 $I _ { 4 }$ 的向前搜索符只有{a，b}，而由于 $I _ { 4 }$ の $I _ { 7 }$ 为同心集，合并同心集后搜索符的集合变为{a，b，#}，所以集合扩大了，因而用LALR(1)分析表发现错误的时间也就推迟了。表6.14对ab#的分析进行了两步多余归约，但是发现错误的位置还是确切的。

为了说明LR(1)分析法强于LALR(1)分析法，而LALR(1)分析法强于SLR(1)分析法，现分别举例如下。

若有文法 $G _ { 1 } ( S ^ { \prime } )$ 的产生式如下：

(0) $S ^ { \prime } {  } S$

(1) $S {  } L { = } R$

(2) $S {  } R$

(3) L→ \* R

(4) L→i

(5) R→L

该文法的LR(0)项目集规范族为

$$
\begin{array} { r l r l } { \lambda _ { 1 , 1 } S ^ { \cdots } \cdots S } & { } & & { I _ { s , 1 } \ L ^ { \gamma \gamma } + \lambda _ { 1 } } \\ & { S + \ldots \ L - R } & { , } & & { I _ { s , 1 } S + \ldots \ L - R } \\ & { S + \ldots \ R } & { } & & { R + \ldots \ L } \\ & { L ^ { \gamma \gamma } + \ldots \ R } & { } & & { L ^ { \gamma \gamma } + \ldots \ R } \\ & { L ^ { \gamma \gamma } + \ldots \ R } & { } & & { L ^ { \gamma \gamma } } \\ & { L ^ { \gamma \gamma } + \ldots \ L } & { } & & { } \\ & { L ^ { \gamma \gamma } + \ldots \ L } & { } & & { \ldots \ R } \\ & { I _ { s , 1 } S ^ { \gamma \gamma } } & { } & & { I _ { s , 1 } + R } \\ & { I _ { s , 1 } S ^ { \gamma \gamma } } & { } & & { } \\ & { R + \ldots \ L } & { } & { } & & { I _ { s , 1 } S ^ { \gamma \gamma } + R } \end{array} .
$$

不难发现，在项目集 $I _ { 2 }$ 中存在移进项目S→L·=R和归约项目R→L·。因此该文法不是LR(0)文法。再考察是否能用SLR(1)方法解决，这就要看R的后跟符集合中是否包含=，由文法的产生式规则可求出 $\mathrm { F O L L O W } ( R ) = \{ \# , = \}$ ，所以 $\mathrm { F O L L O W } ( R ) \cap \{ = \} =$ $\{ = , \# \} \cap \{ = \} \neq \emptyset$ ，因而在 $I _ { 2 }$ 中存在的移进-归约冲突不能用SLR(1)方法解决，说明该文法不是SLR(1)文法，因此，进一步构造它的LR(1)项目集规范族，以判定是否是LR(1)文法或LALR(1)文法。

上述文法的LR(1)项目集族及转换函数如图6.13所示。

![](images/6e077dec16c9797a97fff5daded2edde5877bec05c9292e544cb81bc26f09664.jpg)  
图6.13 LR(1)项目集及转换函数

分析所有这些项目集，可以发现每个项目集中都不含移进-归约冲突或归约-归约冲突。在项目集 $I _ { 2 }$ 中，因归约项目[R→L·，#的搜索符为#，即当前输入符为#时才用产生式R→L归约，而移进项目[S→L·=R，#的移进符号为=，所以移进-归约冲突由LR(1)方法得到了解决，也说明了LR(1)分析法的功能比SLR(1)分析法的功能要强，同时也可以发现下列同心集，即 $I _ { 4 }$ 和 $I _ { 1 1 } , I _ { 5 }$ 和 $I _ { 1 2 } , I _ { 7 }$ 和 $I _ { 1 3 } , I _ { 8 }$ 和 $I _ { 1 0 }$ ，它们两两之间除了搜索符不同外，心是相同的，因此可以将这些同心集合并，合并同心集后的项目集分别如下。

$I _ { 4 }$ 和 $I _ { 1 1 }$ 为

$$
\begin{array} { r l } { \{ L  < R , = / \neq } & { } \\ { R  < L , = / \neq } & { } \\ { L  < i , = / \neq } & { } \\ { L  < k , - / \neq } & { } \\ { L  < R , - / \neq } & { } \\ { L \bar { \nu } \nabla i I _ { 1 2 } \breve { M } , } & { } \\ { \{ L  + i , \ = / \neq } & { } \\ { I _ { \tau } \Re i I _ { 1 3 } \breve { M } } & { } \\ { \{ L  \neq R , \ = / \neq } & { } \\ { \{ L  \neq } & { } \\ { \{ R  \neq L , \ = / \neq } \  & { } \end{array}
$$

进一步考察这些合并同心集后的项目集，发现它们仍不含归约-归约冲突，因此可判定该文法是LALR(1)文法，也是LR(1)文法，但不是LR(0)和 SLR(1)文法。

相应的LALR(1)分析表如表6.15所示。

表 6.15 LALR(1)分析表
<table><tr><td rowspan="2">状态</td><td colspan="4">ACTION</td><td colspan="3">GOTO</td></tr><tr><td>=</td><td> $\star$ </td><td>i</td><td>#</td><td>S</td><td>L</td><td>R</td></tr><tr><td>0 1</td><td> $S _ { 6 }$ </td><td> $S _ { 4 }$ </td><td> $S _ { 5 }$ </td><td> $\operatorname { a c c }$ </td><td>1</td><td>2</td><td>3</td></tr><tr><td>2 3</td><td></td><td></td><td></td><td> $r _ { 5 }$   $r _ { 2 }$ </td><td></td><td></td><td></td></tr><tr><td>4</td><td></td><td> $S _ { 4 }$ </td><td> $S _ { 5 }$ </td><td></td><td></td><td>8</td><td>7</td></tr><tr><td>5</td><td> $r _ { 4 }$ </td><td></td><td> $S _ { 5 }$ </td><td> $r _ { 4 }$ </td><td></td><td></td><td></td></tr><tr><td>6</td><td> $r _ { 3 }$ </td><td> $S _ { 4 }$ </td><td></td><td></td><td></td><td>8</td><td>9</td></tr><tr><td>7</td><td></td><td></td><td></td><td> $r _ { 3 }$ </td><td></td><td></td><td></td></tr><tr><td>8</td><td> $r _ { 5 }$ </td><td></td><td></td><td> $r _ { 5 }$ </td><td></td><td></td><td></td></tr><tr><td>9</td><td></td><td></td><td></td><td> $r _ { 1 }$ </td><td></td><td></td><td></td></tr></table>

下面再给出文法 $G _ { 2 } ( S ^ { \prime } )$ 是LR(1)文法而不是LALR(1)文法的例子 $, G _ { 2 } ( S ^ { \prime } )$ 的产生式如下：

(0) $S ^ { \prime } {  } S$

(1) $S {  } a A d$

(2) $S {  } b B d$

(3) $S {  } a B e$

$$
S {  } b A e
$$

$$
\begin{array} { l } { { ( 5 ) ~ A  c } } \\ { { ( 6 ) ~ B  c } } \end{array}
$$

我们可以直接构造它的LR(1)项目集如下：

$$
\begin{array} { r l } { I _ { \mathrm { c } } : S ^ { - \alpha } \star S , \neq } & { \quad L _ { 1 } \quad S ^ { - \alpha } \star A \star \mathcal { A } , \ \neq \ \# } \\ & { \quad S \bullet \bullet \bullet \alpha A \mathcal { A } , \ \quad L _ { 1 } \quad S \bullet \bullet \alpha B \bullet \ \star \ \mathcal { A } , \ \ \bullet \bullet \bullet } \\ & { \quad S \bullet \bullet \ b B \mathcal { L } , \ \ \neq \ } & { \quad L _ { 1 } \ \ A \bullet \cdots \ \bullet \ \mathcal { A } , \ \ \mathcal { A } } \\ & { \quad S \bullet \bullet \alpha B \mathcal { L } , \ \neq \ } & { \quad B \bullet \cdots \ \mathcal { A } , \ \ } \\ & { \quad S \bullet \bullet \alpha B \mathcal { L } , \ \neq \ } & { \quad L _ { 1 } \ \otimes S \bullet \mathcal { L } , \ \neq \ } \\ & { \quad L _ { 1 } \ \otimes S \bullet B \mathcal { L } , \ \neq \ } & { \quad L _ { 1 } \ \otimes S \ b B \mathcal { L } , \ \neq \ } \\ & { \quad L _ { 1 } \ \otimes S \bullet \alpha \bullet A \mathcal { A } , \ \neq \ } & { \quad L _ { 1 } \ \ \Lambda \bullet \Lambda \circ S \bullet \ \mathcal { A } , \ \ \bullet \bullet } \\ & { \quad S \bullet \alpha \bullet A \mathcal { B } , \ \ \neq \ } & { \quad L _ { 1 } \ \ \Lambda \bullet \Lambda \circ S \bullet \ \cdots \ \mathcal { A } } \\ & { \quad S \bullet \alpha \bullet B \mathcal { L } , \ \ \neq \ } & { \quad B \bullet \cdots \ \mathcal { A } , \ \ \bullet } \\ & { \quad A \bullet \bullet \cdot c \mathcal { A } } & { \quad \quad L _ { 1 } \ \wedge S \bullet S \bullet A d \mathcal { L } , \ \neq \ } \\ & { \quad B \bullet \ast \mathcal { A } , \ \neq \ } & { \quad L _ { 1 } \wedge S \bullet \alpha B \mathcal { L } , \ \neq \ } \\ & { \quad S \bullet \alpha \bullet \ b B \mathcal { L } , \ \neq \ } & { \quad L _ { 1 } \wedge S \bullet \alpha \ b B d \mathcal { L } , \ \neq \ } \\ & { \quad R \bullet \mathcal { A } \bullet \alpha \bullet \ b B d , \ \neq \ } &  \quad L _  \end{array}
$$

检查每个项目集I可知，在任一项目集中都不含移进-归约冲突或归约-归约冲突，因此文法是LR(1)的，进一步查看项目集可发现， $I _ { 6 }$ 和 $I _ { 9 }$ 是同心集：

$$
\begin{array} { r l r } { I _ { 6 } : A \to c \bullet \ , d \ } & { { } \qquad } & { I _ { 9 } : A \to c \bullet \ , e } \\ { B \to c \bullet \ , e } & { { } \qquad } & { B \to c \bullet \ , d } \end{array}
$$

若合并后则变为

$$
\begin{array} { r } { I _ { 6 , 9 } : A {  } c \bullet , d / e } \\ { B {  } c \bullet , e / d } \end{array}
$$

这样就出现了新的归约-归约冲突，因为不管当前符号是d或e，既可用产生式A→c归约，也可用产生式B→c归约，因而可判定该文法不是LALR(1)文法，当然也不可能是SLR(1)和LR(0)文法。

## 6.6 二义性文法在 LR分析中的应用

我们已经知道任何一个二义性文法绝不是LR类文法，也不是一个算符优先文法或LL(k)文法，任何一个二义性文法不存在与其相应的确定的语法分析器，但是对某些二义性文法，可以人为地给出优先性和结合性的规定，从而可以构造出比相应非二义性文法更优越的LR分析器。

例如，算术表达式的二义性文法为

$$
\begin{array} { r } { E  E + E \mid E \times E \mid ( E ) \mid i } \end{array}
$$

相应的非二义性文法可为

$$
\begin{array} { l } { E {  } E { + } T { \mid } T } \\ { T {  } T { \star } F { \mid } F } \\ { F {  } ( E ) { \mid } i } \end{array}
$$

现在构造算术表达式二义性文法的LR(0)项目集，用状态转换矩阵表示，如表6.16所示。

表6.16 算术表达式二义性文法的LR(0)项目集及状态转换矩阵
<table><tr><td rowspan=1 colspan=1>当前符号状态</td><td rowspan=1 colspan=1>十</td><td rowspan=1 colspan=1>*</td><td rowspan=1 colspan=1>C</td><td rowspan=1 colspan=1>)</td><td rowspan=1 colspan=1>i</td><td rowspan=1 colspan=1>#</td><td rowspan=1 colspan=1> $E$ </td></tr><tr><td rowspan=1 colspan=1> $I _ { 0 } :$  $E ^ { \prime } \to \bullet E$  $E  \cdot \ E + E$  $E \to \bullet E \times E$  $E \to \bullet \ ( \ E )$  $E \to * \ i$ </td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1> $I _ { z } : \mathbf { \partial }$  $E {  } ( ~ \cdot ~ E )$  $E  \circ E + E$  $E {  } \circ E \ast E$  $E \to \bullet \ ( E )$  $E \to * \ i$ </td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1> $I _ { 3 } :$  $E  i \cdot$ </td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1> $I _ { 1 } :$  $E ^ { \prime } {  } E ^ { \prime } $  $E {  } E \cdot + E$  $E {  } E \cdot * E$ </td></tr><tr><td rowspan=1 colspan=1> $I _ { 1 } :$ </td><td rowspan=1 colspan=1> $I _ { 4 } :$  $E {  } E { + \cdot } E$  $E  \cdot \ E + E$  $E {  } \cdot \ : E \times E$  $E \to \bullet \ ( \boldsymbol { E } )$  $E \to \cdot \ i$ </td><td rowspan=1 colspan=1> $I _ { 5 } : $  $E {  } E * \cdot E$  $E  \cdot \ E + E$  $E {  } \bullet E \ast E$  $E \to \bullet \ ( \boldsymbol { E } )$  $E \to \cdot \ i$ </td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1> $a c c$ </td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1> $I _ { 2 } :$ </td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1> $I _ { z } :$ </td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1> $I _ { 3 } :$ </td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1> $I _ { 6 } :$  $E {  } ( E ^ { \mathbf { \gamma } } { \cdot } \mathbf { \gamma } )$  $E {  } E \cdot + E$  $E {  } E \cdot * E$ </td></tr><tr><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1> $I _ { 2 } :$ </td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1> $I _ { 3 } :$ </td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1> $I _ { 7 } :$  $E {  } E { \not + } E \ .$  $E {  } E \cdot + E$  $E {  } E \cdot * E$ </td></tr><tr><td rowspan=1 colspan=1> $I _ { 5 } : $ </td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1> $I _ { z } :$ </td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1> $I _ { 3 } :$ </td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1> $I _ { 8 } \ ;$  $E {  } E * E ^ { \ } * E ^ { \ } * E ^ { \ }$  $E {  } E \cdot + E$  $E {  } E \cdot * E$ </td></tr><tr><td rowspan=1 colspan=1> $I _ { 6 } :$ </td><td rowspan=1 colspan=1> $I _ { 4 } :$ </td><td rowspan=1 colspan=1> $I _ { 5 } : \quad$ </td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1> $I _ { 9 } :$ 一 $E \mathrm {  } ( E ) \cdot$ </td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1> $I _ { 7 } :$ </td><td rowspan=1 colspan=1> $I _ { 4 } :$ </td><td rowspan=1 colspan=1> $I _ { 5 } : $ </td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1> $I _ { 8 } :$ </td><td rowspan=1 colspan=1> $I _ { 4 } :$ </td><td rowspan=1 colspan=1> $I _ { \mathrm { { 5 } } } : \begin{array} { r l } \end{array}$ </td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1> $I _ { 9 } , :$ </td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td></tr></table>

在表6.16中可以看出，状态 $I _ { 1 } , I _ { 7 }$ 和 $I _ { 8 }$ 中存在移进-归约冲突，现在逐个分析它们的冲突如何解决。

在 $I _ { 1 }$ 中，归约项目 $E ^ { \prime } {  } E$ ·实际上为接受项目。由于 $\mathrm { F O L L O W } ( E ^ { \prime } ) = \{ \# \}$ ，也就是只有遇到句子的结束标志#才能接受，因而与移进项目的移进符号+、\*不会冲突，所以可用SLR(1)方法解决，即遇当前输入符为#时则接受，遇+或\*时则移进。

在 $I _ { 7 }$ 和 $I _ { 8 }$ 中，由于归约项目 $[ E {  } E { + } E \bullet ] { \not { \star } } \mathbb { H } [ E {  } E \ast E \bullet ]$ 的左部都为非终结符E，而$\mathrm { F O L L O W } ( E ) = \{ \\\neq , + , \ast , ) \}$ ，而移进项目均有+和\*，也就存在

$$
\mathrm { F O L L O W } ( E ) \cap \{ + , * \} \neq \emptyset
$$

因而 $I _ { 7 }$ 和 $I _ { 8 }$ 中的冲突不能用SLR(1)的方法解决，有兴趣的读者也可证明该二义性文法用

LR(k)方法仍不能解决此冲突。

然而，用优先关系和结合性可以解决这类冲突，假如仍规定\*优先级高于十，且它们都服从左结合，那么在 $I _ { 7 }$ 中，由于\*≥十，所以遇\*移进，又因+服从左结合，所以遇+则用E→E+E归约。在 $I _ { 8 }$ 中，由 $\ast > + \mathbb { E } \ast$ 服从左结合，因此不论遇到十、\*或#都应归约，该二义性文法的LR分析表如表6.17所示。

表6.17 对表达式二义性文法的LR 分析表
<table><tr><td rowspan="2">状态</td><td colspan="6">ACTION</td><td>GOTO</td></tr><tr><td>十</td><td>*</td><td>一</td><td>)</td><td> $i$ </td><td>#</td><td>E</td></tr><tr><td>0 1</td><td> $S _ { 4 }$ </td><td> $S _ { 5 }$ </td><td> $S _ { 2 }$ </td><td></td><td> $S _ { 3 }$ </td><td>acc</td><td>1</td></tr><tr><td>2</td><td></td><td></td><td> $S _ { 2 }$ </td><td></td><td> $S _ { 3 }$ </td><td></td><td>6</td></tr><tr><td>3</td><td> $r _ { 4 }$ </td><td> $r _ { 4 }$ </td><td></td><td> $r _ { 4 }$ </td><td></td><td> $r _ { 4 }$ </td><td></td></tr><tr><td>4</td><td></td><td></td><td> $S _ { 2 }$ </td><td></td><td> $S _ { 3 }$ </td><td></td><td>7</td></tr><tr><td>5</td><td></td><td></td><td> $S _ { 2 }$ </td><td></td><td> $S _ { 3 }$ </td><td></td><td>8</td></tr><tr><td>6</td><td> $S _ { 4 }$ </td><td> $S _ { 5 }$ </td><td></td><td> $S _ { 9 }$ </td><td></td><td></td><td></td></tr><tr><td>7</td><td> $r _ { 1 }$ </td><td> $S _ { 5 }$ </td><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td><td> $r _ { 1 }$ </td><td></td><td> $r _ { 1 }$ </td><td></td></tr><tr><td>8</td><td> $r _ { 2 }$ </td><td> $r _ { 2 }$ </td><td></td><td> $r _ { 2 }$ </td><td></td><td> $r _ { 2 }$ </td><td></td></tr><tr><td>9</td><td> $r _ { 3 }$ </td><td> $r _ { 3 }$ </td><td></td><td> $r _ { 3 }$ </td><td></td><td> $r _ { 3 }$ </td><td></td></tr></table>

使用表6.17对表达式的输入串 $i + i \ast i$ #进行分析的过程如表6.18所示。

表6.18用二义性文法的分析表对输入串i十i\*i#的分析过程
<table><tr><td rowspan=1 colspan=1>步骤</td><td rowspan=1 colspan=1>状态栈</td><td rowspan=1 colspan=1>符号栈</td><td rowspan=1 colspan=1>输入串</td><td rowspan=1 colspan=1>ACTION</td><td rowspan=1 colspan=2>GOTO</td></tr><tr><td rowspan=1 colspan=1>(1)</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>#</td><td rowspan=1 colspan=1> $i + i \ast i \neq$ </td><td rowspan=3 colspan=1> $S _ { 3 }$  $r _ { 4 }$  $S _ { 4 }$ </td><td rowspan=14 colspan=2>17871</td></tr><tr><td rowspan=1 colspan=1>(2)</td><td rowspan=1 colspan=1>03</td><td rowspan=1 colspan=1>#i</td><td rowspan=1 colspan=1>+i*i#</td></tr><tr><td rowspan=3 colspan=1>(3)(4)</td><td rowspan=1 colspan=1>01</td><td rowspan=1 colspan=1>#E</td><td rowspan=1 colspan=1>+i*i#</td></tr><tr><td rowspan=2 colspan=1>014</td><td rowspan=2 colspan=1>#E+</td><td rowspan=2 colspan=1>i*i#</td><td rowspan=2 colspan=1> $S _ { 3 }$ </td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1></td></tr><tr><td rowspan=2 colspan=1>(5)</td><td rowspan=2 colspan=1>0143</td><td rowspan=2 colspan=1>#E+i</td><td rowspan=2 colspan=1>*i#</td><td rowspan=2 colspan=1> $r _ { 4 }$ </td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1></td></tr><tr><td rowspan=2 colspan=1>(6)</td><td rowspan=2 colspan=1>0147</td><td rowspan=2 colspan=1>#E+E</td><td rowspan=2 colspan=1>*i#</td><td rowspan=2 colspan=1> $S _ { 5 }$ </td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>(7)</td><td rowspan=1 colspan=1>01475</td><td rowspan=1 colspan=1>#E+E*</td><td rowspan=1 colspan=1>i#</td><td rowspan=1 colspan=1> $S _ { 3 }$ </td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>(8)</td><td rowspan=1 colspan=1>014753</td><td rowspan=1 colspan=1>#E+E* i</td><td rowspan=1 colspan=1>#</td><td rowspan=1 colspan=1> $r _ { 4 }$ </td></tr><tr><td rowspan=1 colspan=1>(9)</td><td rowspan=1 colspan=1>014758</td><td rowspan=1 colspan=1>#E+E*E</td><td rowspan=1 colspan=1>#</td><td rowspan=1 colspan=1> $r _ { 2 }$ </td></tr><tr><td rowspan=1 colspan=1>(10)</td><td rowspan=1 colspan=1>0147</td><td rowspan=1 colspan=1>#E+E</td><td rowspan=1 colspan=1>#</td><td rowspan=2 colspan=1> $r _ { 1 }$ acc</td></tr><tr><td rowspan=1 colspan=1>(11)</td><td rowspan=1 colspan=1>01</td><td rowspan=1 colspan=1>#E</td><td rowspan=1 colspan=1>#</td></tr></table>

不难发现，对二义性文法规定了优先关系和结合性后的LR分析速度比相应的非二义性文法的LR分析速度要快一些，对输入串i+i\*i#的分析，用表6.17比用表6.8(见6.3节)分析少3步，其分析过程见表6.18和表6.9。对于其他的二义性文法也可用类似的方法处理，可能构造出无冲突的LR分析表。

## 练 习

## 1. 已知文法

A→aAd|aAb|ε

判断该文法是否是SLR(1)文法，若是，请构造相应分析表，并对输入串ab#给出分析过程。

2. 若有定义二进制数的文法如下：

S→L.L|L   
L→LB|B   
B→0|1

（1）试为该文法构造LR分析表，并说明属哪类LR分析表。

（2）给出输入串101.110的分析过程。

3. 考虑文法   
S→AS|b   
A→SA|a

(1）列出这个文法的所有LR(0)项目。

(2)按(1)列出的项目构造识别这个文法活前缀的NFA，把这个NFA确定化为DFA，说明这个DFA的所有状态全体构成这个文法的LR(0)规范族。

(3)这个文法是SLR(1)的吗？若是，构造出它的SLR分析表。

(4)这个文法是LALR(1)或LR(1)的吗?

4. 下面是一个描述Σ={a,b}上的正规式的LALR(1)文法(实际上也是 SLR(1)文法），只不过用+代替|。

```csv
E→E+T|T
T→TF|F
F→F*|(E)|a|b
```

构造这个文法的LALR(1)项目集和分析表。

5. 一个类 ALGOL 的文法如下：

<Program〉→〈Block〉   
<Program〉→<Compound Statement〉   
<Block〉→〈Block head>;〈Compound Tail>   
<Block head>→begin d   
<Block head>→〈Block head>;d   
<Compound Tail>→S end   
<Compound Tail>→S;〈Compound Tail>   
<Compound Statement〉→begin〈Compound Tail>

试构造其LR(O)分析表。

6. 文法G=({U,T,S},{a,b,c,d,e},P,S),其中P 为

S→UTa|Tb

T→S|Sc|d U→US|e

(1)判断G是LR(0)、SLR(1)、LALR(1)还是LR(1)的，说明理由。

（2）构造相应的分析表。

7. 证明下面文法不是 LR(0)而是 SLR(1)。S→AA→Ab|bBa$B {  } a A c \mid a \mid a A b$

8. 证明文法(其中\$相当于#)S→A\$A→BaBb|DbDaB→εD→ε

是LR(1)而不是 SLR(1)的。

9. 证明下面文法是LR(1)而不是LALR(1)的。$S \to A \alpha \mid b A e \mid B e \mid b B a$ A→dB→d

10.判断下列6个文法是否为LR类文法，若是，请说明是LR(0)、SLR(1)、LALR(1)或LR(1)的哪一种，并构造相应的分析表；若不是，请说明理由。

(1) $\begin{array} { l } { S {  } A B } \\ { A {  } a B a \mid \varepsilon } \\ { B {  } b A b \mid \varepsilon } \end{array}$

(2) $\begin{array} { l } { S {  } D ; B | B } \\ { D {  } d | \varepsilon } \\ { B {  } B ; a | a | \varepsilon } \end{array}$

(3) S→aAd|eBd|aBr|eAr A→a B→a

(4) $\begin{array} { l } { { A  A b B a \mid B } } \\ { { \mid B  a \mid \varepsilon } } \end{array}$

11. 设文法 G[S]为  
S→AS|ε  
A→aA|b

(1)证明G[S]是LR(1)文法。

(2)构造它的LR(1)分析表。

(3）给出输入符号串abab#的分析过程。

12. 证明任何 SLR(1)文法都是LR(1)文法。

13. 证明任何SLR(1)文法都是LALR(1)文法。

14. 一个文法若是 SLR(1)文法，那么它的 SLR(1)和 LALR(1)识别活前缀的 DFA的状态数目相同，但LALR(1)对一些错误的发现可能比SLR(1)要早。请说明理由。

15.已知文法为：

S→a|∧|(T)

$$
T {  } T , S | S
$$

(1)构造它的LR(0)、LALR(1)和LR(1)分析表。

(2)给出对输入符号串(a#和(a,a#的分析过程。

（3）说明（1)中3种分析表发现错误的时刻和输入串的出错位置有何区别。

16. 给定文法：

S→do S or S|do S|S;S|act

（1）构造识别该文法活前缀的DFA。

(2)该文法是LR(0)的吗？是SLR(1)的吗？说明理由。

（3）若对一些终结符的优先级以及算符的结合规则规定如下：

① or 优先性大于 do。

②；服从左结合。

③;优先性大于 do。

④；优先性大于 $\underline { { \boldsymbol { \mathrm { ~ o r } } } }$ 8

请构造该文法的LR分析表。

17. 已知某文法 G[S]的LALR(1)分析表如表6.19 所示。

表6.19 对表达式二义性文法的LR 分析表
<table><tr><td rowspan=2 colspan=1>状态</td><td rowspan=1 colspan=5>ACTION</td><td rowspan=1 colspan=1>GOTO</td></tr><tr><td rowspan=1 colspan=1> $a$ </td><td rowspan=1 colspan=1>t</td><td rowspan=1 colspan=1>g</td><td rowspan=1 colspan=1> $c$ </td><td rowspan=1 colspan=1>#</td><td rowspan=1 colspan=1>S</td></tr><tr><td rowspan=7 colspan=1>012345678910111213141516</td><td rowspan=1 colspan=1> $S _ { 1 1 }$  $S _ { 1 1 }$ </td><td rowspan=3 colspan=1> $S _ { 8 }$  $S _ { 8 }$ </td><td rowspan=7 colspan=1> $S _ { 3 }$  $r _ { 1 }$  $S _ { 9 }$  $S _ { 1 3 }$  $r _ { 4 }$  $r _ { 2 }$  $r _ { 3 }$ </td><td rowspan=4 colspan=1> $S _ { 4 }$  $S _ { 2 }$  $S _ { 4 }$  $S _ { 7 }$  $r _ { 1 }$  $S _ { 1 0 }$  $S _ { 4 }$ </td><td rowspan=7 colspan=1>acc $r _ { 1 }$  $r _ { 4 }$  $r _ { 2 }$  $r _ { 3 }$ </td><td rowspan=7 colspan=1>116141215</td></tr><tr><td rowspan=1 colspan=1> $S _ { 5 }$ </td></tr><tr><td rowspan=2 colspan=1> $S _ { 6 }$  $S _ { 1 1 }$ </td></tr><tr><td rowspan=2 colspan=1> $S _ { 8 }$  $S _ { 8 }$ </td></tr><tr><td rowspan=2 colspan=1> $S _ { 1 1 }$  $S _ { 1 1 }$ </td><td rowspan=3 colspan=1> $S _ { 4 }$  $S _ { 2 }$  $S _ { 4 }$  $S _ { 2 }$  $S _ { 2 }$  $S _ { 2 }$ </td></tr><tr><td rowspan=2 colspan=1> $S _ { 8 }$ </td></tr><tr><td rowspan=1 colspan=1></td></tr></table>

并且已知各规则右边语法符号的个数以及左边的非终结符如下：

<table><tr><td rowspan=1 colspan=1>规则编号</td><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>2</td><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>4</td></tr><tr><td rowspan=1 colspan=1>右部长度</td><td rowspan=1 colspan=1>4</td><td rowspan=1 colspan=1>4</td><td rowspan=1 colspan=1>4</td><td rowspan=1 colspan=1>4</td></tr><tr><td rowspan=1 colspan=1>左部符号</td><td rowspan=1 colspan=1>S</td><td rowspan=1 colspan=1>S</td><td rowspan=1 colspan=1>S</td><td rowspan=1 colspan=1>S</td></tr></table>

写出使用上述LALR(1)分析器分析下面的串的过程(只需写出前10步，列出所有可能的 $r _ { i } , s _ { j }$ 序列，注意先后次序）：

$$
a c a a c c g t g c c a a c g a t g c c a a . . .
$$

18. 给定如下文法 G[S]:

S →if S else S

$$
S \to { \underline { { \mathrm { i f } } } } \ S
$$

$$
S  a
$$

为文法 G[S]增加产生式 $S ^ { \prime } {  } S$ ，得到增广文法 $G ^ { \prime } [ S ]$ ，下图是相应的LR(0)项目集和识别活前缀的 DFA(i表示if,e 表示else):

![](images/8c85b2b9d12afc2d592861f777b2376fc92dbd5d273a0b0e592f515d7e58c63b.jpg)

(1）指出该DFA中的全部冲突状态及其冲突类型，以说明文法G[S]不是LR(0)文法。

(2)文法 G[S]也不是 SLR(1)文法。为什么？

(3)给出文法G[S]的LR(1)项目集和相应的DFA。

(4)指出(3)中 DFA的全部冲突状态，以说明文法G[S]也不是LR(1)文法。

(5）若规定 else优先匹配左边靠近它的未匹配的if，则可以解决上述两个DFA中的状态冲突。试给出文法G[S]在规定这一规则情况下的SLR(1)分析表和LR(1)分析表。

(6)对于文法G[S]中正确的句子，基于(5)中两个分析表均可以成功进行LR分析。然而，对于不属于文法G[S]中的句子，两种分析过程发现错误的速度不同，即发现错误时所经过的移进-归约总步数有差异。试给出一个长度不超过10的句子(即所包含的终结符个数不超过10），使得两种分析过程发现错误的速度不同。哪一个更快？对于你给的例子，两种分析过程分别到达哪个状态时会发现错误？

## 第7章 语法制导的语义计算

对于词法和语法正确的源程序，编译程序就可以对它进行语义分析。在语义分析阶段，首先是收集或计算源程序的上下文相关信息，并将这些信息分配到相应的程序单元记录下来。在这一过程中，若发现程序存在静态一致性或完整性方面的问题，则报告静态语义错误：若不存在静态一致性或完整性方面的问题，则称该程序通过了静态语义检查。语义分析过程中与静态语义检查相关的部分称为静态语义分析。对于已通过静态语义检查的程序，编译程序可将其翻译到后续的中间表示形式，即中间代码生成。中间代码生成的过程体现了如何在更低的级别诠释程序的动态语义。关于静态语义分析和中间代码生成，可参阅第8章内容。

在编译程序的实现中，一种经典的方法是由语法分析程序的分析过程来主导语义分析以及翻译的过程，本书将其称为语法制导的语义计算。在编译方面的许多书籍中也称其为语法制导的翻译。对于特定的翻译遍，比如第8章的静态语义分析与中间代码生成，则可以相应地称其为语法制导的静态语义分析和语法制导的中间代码生成。

为描述完成什么样的语义计算，需要在语法定义的基础上建立适当的语义计算模型。如果语法定义采用上下文无关文法，则建立这种语义计算模型的基本途径是对上下文无关文法进行扩展，为文法符号附加语义信息，并针对产生式设计适当的语义动作，以便告诉分析引擎在语法分析过程中可以执行的语义动作。

本章介绍两种重要的语义计算模型：属性文法和翻译模式。属性文法是一种基本的语义计算模型，适用于对一般原理的理解；而翻译模式是面向实现的语义计算模型，有助于理解语法制导的语义计算程序的自动构造方法(比如yacc工具的工作原理)。

本章的最后简要介绍了语法分析/语义计算程序的构造工具yacc，使读者初步了解yacc工具的使用，同时加深对基本原理的理解。

## 7.1 基于属性文法的语义计算

## 7.1.1 属性文法

## 7.1.1.1 基本概念和术语

属性文法的理论体系较为复杂，由于本书仅将其作为描述语义计算的工具，所以不从理论研究的视角出发，而是从实际应用的角度对其进行非形式化的介绍。首先通过例子来引入与属性文法相关的基本概念和术语。

考虑{a，b，c}上的语言 $L = \{ a ^ { n } b ^ { n } c ^ { n } | n \geq 1 \}$ 。可以证明[20]：L不是任何上下文无关文法的语言。设有如下文法G[S]：

$$
S {  } A B C
$$

易知，这一文法的语言 $L ( G ) = L ( a ^ { + } b ^ { + } c ^ { + } )$ ,这里 $a ^ { + } = a \alpha ^ { * } , b ^ { + }$ 和 $c ^ { + }$ 类似。显然有 $L \subseteq$ L(G)。

如果对G[S]附加某种限定条件，使其只产生满足这一限定条件的字符串，则可能接受语言L。这一想法可以通过属性文法来实现。

在文法 $G \ [ S ]$ 基础上，为文法符号关联有特定意义的属性，并为产生式关联相应的语义动作或条件谓词，称之为属性文法，并称文法G[S]是这一属性文法的基础文法。以下是基于G[S]的一个属性文法：

S→ABC {(A. num=B. num) and (B. num=C. num)}   
A→A1a {A.num :=A1.num+1}   
A→a {A. num :=1}   
$\begin{array} { r l r } { B { \to } B _ { 1 } b } & { { } \quad } & { \{ B , \mathrm { n u m } : = B _ { 1 } . \mathrm { n u m } + 1 \} } \end{array}$   
B→b {B. num :=1}   
$C \mathrm {  } C _ { 1 } c$ {C. num :=C1. num+1}   
C→c {C. num :=1}

文法符号的属性可用来刻画与该文法符号关联的任何特定意义的信息，如值、名字串、类型、偏移地址、代码片段等。设文法符号X关联一个属性a，我们用X.a来表示对这个属性的访问。例如，在上述属性文法中，A.num表示对文法符号A所关联属性num的访问。

这里要注意的是，为了明确指出一个属性值对应于当前产生式中哪个位置的文法符号，在书写同一个文法符号时，会用到文法符号的下标形式。例如，在以上属性文法的第二条产生式中，A和 $A _ { 1 }$ 分别表示出现于不同位置的文法符号A。对于同一个属性num，它们相应的属性值分别用 A. num和 $A _ { 1 }$ . num来访问。

在属性文法中，每个产生式 $A  \alpha$ 都关联一个语义计算规则的集合，如上面例子中花括号内的部分。每个语义计算规则或者是一个语义动作，或者是一个条件谓词。本书中，将语义动作的一般形式表示为

$$
b : = f ( c _ { 1 } , c _ { 2 } , \cdots , c _ { k } )
$$

其中 $, b , \ c _ { 1 } \ , \ c _ { 2 } \ , \cdots , \ c _ { k }$ 对应产生式中某些文法符号的属性。f是用于描述如何计算属性值的函数，或称为语义函数。

语义动作也可以只包含一个语义函数，形如

$$
f ( c _ { 1 } , \ c _ { 2 } , \cdots , \ c _ { k } )
$$

另外，形如 $X , a : = Y , b$ 的语义动作称为复写规则。后面将会看到，复写规则对于语义计算程序的构造有独特的作用。

在具体应用中，语义函数可以通过实际的代码片段来实现，但一般不要有副作用，否则会使语义计算复杂化。

上面例子中的 $( A , \mathrm { n u m } = B , \mathrm { n u m } ) \mathrm { a n d } ( B , \mathrm { n u m } = C , \mathrm { n u m } )$ 是一个条件谓词，表示由当前属性的取值所决定的一个限定条件。

对于给定的属性文法，在基于语法分析过程进行语义计算时，使用某个产生式完成一步

分析时将执行相应的语义动作，但其前提是必须满足相应的条件谓词。

通过以上解释或后续内容的学习，不难理解，上述属性文法可以接受的语言是 $L =$ $\{ a ^ { n } b ^ { n } c ^ { n } | n \geq 1 \}$ 。

由于在目前较实用的语法制导的语义计算程序构造工具中很少有相应的支持，所以本书不讨论包含条件谓词的属性文法。在实际应用中，可以采取提示信息或其他方式达到同样的语义计算效果。

例7.1 对于语言 $L = \{ a ^ { n } b ^ { n } c ^ { n } | n { \geq } 1 \}$ ，可以设计如下属性文法作为语义计算模型：

```asp
S→ABC {if(A. num=B.num) and (B. num=C.num)
then print("Accepted!")
else print("Refused!")}
A→A₁a {A. num :=A1. num+1}
A→a {A. num :=1}
B→B₁b {B. num := B1. num+1}
B→b {B. num :=1}
C→C1c {C. num :=C1. num+1}
C→c {C. num :=1}
```

对于该属性文法，若输入串属于L，则语义计算结果会执行print("Accepted!")，否则将会执行print（"Refused!")。当然，如果输入串不属于正规式 $a a ^ { * } b b ^ { * } c c ^ { * }$ 所表示的串，那么就会报告语法错误。

## 7.1.1.2 综合属性和继承属性

对关联于产生式 $A \to \alpha$ 的语义动作 $b : = f ( c _ { 1 } , \ c _ { 2 } , \cdots , \ c _ { k } )$ ，如果b是A的某个属性，则称b是A的一个综合属性。从分析树的角度来看，由于计算综合属性是对父结点的属性赋值，所以是自底向上传递信息。

对关联于产生式 $A  \alpha$ 的语义动作 $b : = f ( c _ { 1 } , c _ { 2 } , \cdots , c _ { k } )$ ，如果b是产生式右部某个文法符号X的某个属性，则称b是文法符号X的一个继承属性。从分析树的角度来看，由于计算继承属性是对子结点的属性赋值，所以是自顶向下传递信息。

在例7.1的属性文法例子中，文法符号A、B和C的属性num都是综合属性。图7.1(a)是针对输入串aaabbbccc的一棵分析树。对此分析树进行自底向上(后序)遍历，并执行关联于相应产生式的语义动作，得到针对该输入串的一个语义计算过程，如图7.1(b)所示。

再看一个含有继承属性的属性文法。

例 7.2 对于语言 $L = \{ a ^ { n } b ^ { n } c ^ { n } | n \geq 1 \}$ ，还可以设计一个含有继承属性的属性文法作为语义计算模型(开始符号为 S):

S→ABC {B. in\_num :=A. num; C. in\_num :=A. num;   
if (B.num=0 and(C.num=0))   
then print("Accepted!")   
else print("Refused!")}   
A→A1 a{A.num :=A1. num+1}   
A→a {A. num :=1}

![](images/bb41e8db58c46475f4ce5c0aac20dc1767f24f309df2a1ab39017816581c2235.jpg)  
图7.1 综合属性的计算：自底向上传递信息

$$
\begin{array} { r l r l } & { B \to B _ { 1 } \ : b } & & { \{ B _ { 1 } : \mathrm { i n } _ { - } \mathrm { n u m } : = B , \mathrm { i n } _ { - } \mathrm { n u m } ; B , \mathrm { n u m } : = B _ { 1 } , \mathrm { n u m } - 1 \} } \\ & { B \to b } & & { \{ B , \mathrm { n u m } : = B , \mathrm { i n } _ { - } \mathrm { n u m } - 1 \} } \\ & { C \to C _ { 1 } \ : c } & & { \{ C _ { 1 } , \mathrm { i n } _ { - } \mathrm { n u m } : = C , \mathrm { i n } _ { - } \mathrm { n u m } ; C _ { \star } \mathrm { n u m } : = C _ { 1 } . \mathrm { n u m } - 1 \} } \\ & { C \to c } & & { \{ C _ { \star } \mathrm { n u m } : = C _ { \star } \mathrm { i n } _ { - } \mathrm { n u m } - 1 \} } \end{array}
$$

这个属性文法既包含综合属性，又包含继承属性。其中，A.num,B.num和C.num是综合属性，而 B. in\_num 和 C. in\_num 是继承属性。

同例7.1,对于该属性文法，当输入串属于L,则语义计算结果会执行print("Accepted!")，否则将会执行print("Refused!")。如果输入串不属于正规式 $a a ^ { * } b b ^ { * } c c ^ { * }$ 所表示的串，那么就会报告语法错误。

在图7.1(a)的分析树基础上，对于综合属性值进行自底向上计算，而对于继承属性值进行自顶向下计算，得到输入串aaabbbccc的一个语义计算过程，如图7.2所示。

![](images/3a77cd8b7db67850c70a939ae0679524dce16712d7f06e73dcbad73642cb8912.jpg)  
图7.2 继承属性的计算：自顶向下传递信息

下面看一个更复杂的例子。

例7.3 以下属性文法可用于将二进制无符号小数转化为十进制小数(开始符号为N):

$$
\begin{array} { r l r l } & { N  S _ { 1 } , S _ { 2 } } & & { \{ N , v : = S _ { 1 } . \ : v + S _ { 2 } . \ : v ; \ : S _ { 1 } . \ : f : = 1 ; \ : S _ { 2 } . \ : f : = 2 ^ { - S _ { 2 } . \ : l } \} } \\ & { S  S _ { 1 } B } & & { \{ S _ { 1 } , f : = 2 S , f ; \ : B , f : = S , f ; \ : S , v : = S _ { 1 } , v + B , v ; \ : S , l : = S _ { 1 } . \ : l + 1 \} } \\ & { S  B } & & { \{ S , l : = 1 ; \ : S , v : = B . \ : v ; \ : B . \ : f : = S , f \} } \\ & { B  0 } & & { \{ B , v : = 0 \} } \\ & { B  1 } & & { \{ B , v : = B . \ : f \} } \end{array}
$$

其中，各个属性具有如下含义：

•符号N的综合属性v表示十进制小数形式的转化结果。

· 符号S的综合属性v表示二进制整数或定点小数(小数点之后的二进制数)对应的十进制数值。

• 符号 S的综合属性l表示二进制整数或定点小数的0、1串长度。

· 符号S的继承属性f表示S推导的0、1串中最末一位为1时应该对应的十进制数值。从属性文法的第一行中的 $S _ { 1 } . \ f : = 1$ 和第二行中的 $S _ { 1 } . \ f : = 2 S . \ f$ 可知：小数点前第一位数为1时，对应的十进制数值为 $2 ^ { 0 } = 1$ ；小数点前第二位数为1时，对应的十进制数值为 $2 ^ { 1 } = 2$ ；小数点前第三位数为1时，对应的十进制数值为 $2 ^ { 2 } = 4$ ，等等。从属性文法的第一行中的 $S _ { 2 } \cdot f : = 2 ^ { - S _ { 2 } \cdot l }$ 和第二行中的 $S _ { 1 } . \ f : = 2 S . \ f$ 可知：小数点后第一位数为1时，对应的十进制数值为 $2 ^ { - 1 } = 0 . 5$ ；小数点后第二位数为1时，对应的十进制数值为 $2 ^ { - 2 } = 0 , 2 5$ ；小数点后第三位数为1时，对应的十进制数值为 $2 ^ { - 3 } = 0 . 1 2 5$ ，等等。

· 符号B的综合属性v表示二进制数的当前一位数字(0或1)对应的十进制数值。

· 符号B的继承属性f表示二进制数的当前一位数字是1时应该对应的十进制数值。含义类似于符号S的继承属性f。

基于该属性文法进行语义计算的过程比起前面两个例子要复杂一些，各个属性之间有比较复杂的依赖关系。在7.1.2节里，将以这一属性文法为例来介绍一种通用的方法—遍历分析树进行语义计算。

## 7.1.2 遍历分析树进行语义计算

基于属性文法，通过遍历分析树进行语义计算可以采取下列步骤：

（1）构造输入串的语法分析树。

（2）构造依赖图。

(3）若该依赖图是无圈的，则按此无圈图的一种拓扑排序对分析树进行遍历，从而计算所有的属性值。若依赖图含有圈，则这一步骤失效。

这里，依赖图是一个有向图，用来描述分析树中的属性与属性之间的相互依赖关系。图7.3描述了构造依赖图的一般过程。

for 分析树中每一个结点 n do  
for 结点 n所用产生式的语义动作中涉及的每一个属性a do  
为a在依赖图中建立一个结点；  
for 结点 n所用产生式中每个形如 $f ( c _ { 1 } , c _ { 2 } , \cdots , c _ { k } )$ 的语义动作 do  
为该规则在依赖图中也建立一个结点(称为虚结点)；  
for 分析树中每一个结点 n do  
for 结点 n所用产生式对应的每个语义动作 $b : = f ( c _ { 1 } , c _ { 2 } , \cdots , c _ { k } )$ do  
(可以只是 $f ( c _ { 1 } , c _ { 2 } , \cdots , c _ { k } )$ ，此时结点b为一个虚结点)  
for i :=1 to k do  
从结点ci到结点b构造一条有向边  
图7.3 构造依赖图的一般过程

例7.4对于例7.3的属性文法，考虑针对输入串10.01的语义计算过程。首先，基于输入串10.01的分析树，根据图7.3描述的方法构造依赖图。为分析树中所有结点的每个属性建立一个依赖图中的结点，并给定一个标记序号。结果，该依赖图共有21个结点，分别
