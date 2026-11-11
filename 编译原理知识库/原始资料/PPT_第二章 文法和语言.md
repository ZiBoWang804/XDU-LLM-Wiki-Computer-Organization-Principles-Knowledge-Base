## 程序语言的语法描述与分析

## 目的：

语言的语法结构的形式描述

从形式描述中，研究语法分析器的构造(算符优先分析法和递归子程序分析法)

## 第二章 文法和语言本章内容

## •引言

\- 语言和文法的直观概念

-符号和符号串的相关概念

## 文法与语言

\- 文法和语言的形式定义

文法的分类

\- 上下文无关文法

语法树与二义性

句型的分析

文法的改造

## 一、引言

定义或表示语言的方法：

当一个语言有有限个句子时，可采用枚举法

如：语言只有两个句子，则可表示为：

L={ I am a teacher , You are student}

X 大多数语言都是无穷的，可用下列方法描述

1. 制定有限条规则，用来产生所需要描述的语言中的所有句子

2. 建立一种装置(自动机)

## 例：

<句子>=><主语短语><动词短语=>...

< 句子>::=< 主语短语>< 动词短语V

< 主语短语>::=the<名词>

<动词短语>::=<动词><宾语短语V

<宾语短语>::=<冠词><名词>

<名词>::=monkey|banana

<动词 >::=ate|has

<冠词>::=the|a

## 一、引言

## ·文法（grammar)

问题：如何描述语言

定义：文法是描述语言的语法结构的形式规则（即语法规则）

目的： 解决语言的有穷说明问题，包含对语法的描述，但却不表达任何语义

## 几个概念：

1. 字母表 组成语言的基本符号。英语字母表：26个字母

2. 符号串 字母表中的符号组成的任何有穷序列。abce

3. 符号串的长度 符号串中包含的符号个数。 $| \mathsf { a b c } | = 3 \cdot | \mathsf { e } |$

空符号串不包含任何符号的符号串。 $| \xi | = 0$

5. 符号串的前缀买符号串的后缀（尾) 从符号串的尾或头去除若干个符号。

符号串的真前缀（真后缀)

6. 符号串的子串

不能等于他本身。

7. 符号串的连接 符号串中连续的若干个符号。

8. 符号串的方幂

符号串的次幂运算。 $\scriptstyle \mathbf { x } = \mathbf { a } \ z = \mathbf { a } \mathbf { a } \mathbf { a } \ldots \mathbf { a } = \mathbf { a } ^ { n }$

## 几个概念：

9. 符号串集合 基于字母表上的所有符号串集合。

10.符号串集合的和、积 $A = \{ 0 , 1 \} , \mathrm { ~ B = \{ a , b \} ~ }$

11.符号串集合的方幂符号串集合的次幂运算。

12. 符号串集合的闭包 $\begin{array} { l } { \Delta { = } \{ 0 , 1 \} } \\ { \cup _ { \mathsf { A } ^ { \mathsf { n } } } } \end{array}$ ，则 $\scriptstyle \mathsf { A } ^ { \star } = \mathsf { A } ^ { 0 } \mathsf { U } \mathsf { A } ^ { 1 } \mathsf { U } \mathsf { A } ^ { 2 }$

$$
\mathsf { A } ^ { + } = \mathsf { A } ^ { 1 } \mathsf { U } \mathsf { A } ^ { 2 } . . . \mathsf { U } \mathsf { A } ^ { \mathsf { n } }
$$

规则 重写规则、产生式或生成式。

是形如 ${ \mathfrak { a } } _ {  } { \mathfrak { \beta } }$ 或 ${ \mathfrak { A } } { \overset { \vartriangle } { = } } { \mathfrak { s } } = { \mathfrak { B } }$ 的 $( \texttt { a } , \texttt { \beta } )$ 有序对，其中 α 是某字母表 Ⅴ的的正闭包 ${ \mathsf { V } } ^ { + }$ 的一个符号，β是 $\ b { \mathsf { V } } ^ { \star }$ 的一个符号。

α称为规则的左部，β称为规则的右部。

→和：=含义相同，读作“生成”

## 二、文法与语言

1、一个文法 G 是一个四元式 $( \mathsf { V } _ { \mathsf { N } } , \mathsf { V } _ { \mathsf { T } } , \mathsf { P } , \mathsf { S } \ )$ ，其中：

${ \sf V } _ { \sf N } :$ 是非空有限集，它的每个元素是非终结符号；

$$
\mathsf { V } _ { \mathsf { r } } \cap \mathsf { V } _ { \mathsf { N } } { = } \Phi ;
$$

$$
\mathsf { V } _ { \mathsf { T } } \cup \mathsf { V } _ { \mathsf { N } } { = } \mathsf { V } ;
$$

$v _ { T } :$ 是非空有限集，它的每个元素是终结符号；

Ρ：产生式集合（有限），每个产生式形式是

$\{ \mathbf { \boldsymbol { a } } { \to } \beta | \in \mathcal { ( V } _ { \intercal } \mathbf { \boldsymbol { \mathsf { u V } } } _ { \intercal } ) ^ { \ast }$ 且至少包含一个非终结符，$B \in ( V , \cup V _ { N } ) ^ { \ast } \} ;$

$\mathsf { S } : \mathsf { S } { \in } \mathsf { V } _ { \mathsf { N } }$ ，称为开始符或识别符，至少要出现在一条规则的左部；

## 例1、 考虑下面的算术表达式的文法及语言

$V _ { N } :$ 表达式、运算符

$$
V _ { \tau } : \ \mathrm { ~ i d ~ } + \ - \ \star \ / \ \uparrow \ ( )
$$

得到文法G1(E):

表达式->表达式运算符表达式

表达式 ->(表达式)

$$
E  \mathsf { E A E } | ( \mathsf { E } ) | \ - \ \mathsf { E }
$$

表达式 -> id

运算符

$$
A \to + \mid - \mid { ^ { \star } \mid } / { \mid \uparrow }
$$

$$
E > \mathrm { i d } + \mathrm { i d }
$$

s：表达式

$$
\mathsf { E } \to \mathsf { i d } ^ { \star } ( \mathsf { i d } + \mathsf { i d } )
$$

由此可见，文法 G1(E) 所定义的语言是上述算术表达式，

如： $\mathrm { i d } + \mathrm { i d } \quad , \quad \mathrm { i d } ^ { \ast } ( \mathrm { i d } + \mathrm { i d } )$ 等

它表达了简单算术表达式由id 用A 连接起来

该文法的： ${ \sf V } _ { \sf N }$ 是出现P的左部所有符号集合

V是P的所有符号

$$
\therefore v _ { \mathrm { { r } } } = \mathsf { V } \backslash \mathsf { V } _ { \mathrm { { N } } }
$$

S是该文法所定义的句子名字

∴写出了Ρ，就能找出其它三元素

## 2、从此可见

终结符：是用以组成语言中的串的基本符号，与程序语言中“单词”是同义语；

如：表达式 id+(id)\*( - id)中，+\*、/、↑、id均为终结符

非终结符：是标记某种串的集合的特定符号与“语法变量”、“语法范畴”是同义词；

如：表达式、运算符都表示一个串的集合

开始符号：一个 ${ \sf V } _ { \sf N }$ ，标记感兴趣的语法范畴。其它非终结符用以定义其它的串集，这有助于定义该语言，也有助于为它处理的语言提供一个分层的结构；

✓该语法范畴叫“句子”，在程序语言中叫“程序”

✓语言的句子是由一串 ${ \tt V } _ { \tt N }$ 定义，到最后才是一串 ${ \sf V } _ { \sf T }$

产生式：规定由终结符和别的语法范畴组成一个新的语法范畴的办法；

结构：非终结符 ->一串非终结符和终结符

如： $\mathbf A = > \mathbf a$

$$
\begin{array} { c c c } { \textsf { A } } & { \textsf { > } } & { \ q } \\ { \downarrow } & { \ } & { \downarrow } \end{array}
$$

左部符号

右部候选式

$$
{ \sf V } _ { \sf N }
$$

$$
\scriptstyle \mathbf { a } = \mathbf { X } _ { 1 } \mathbf { X } _ { 2 } \ldots \mathbf { X } _ { n } \ \cdot \mathbf { \mu } \mathbf { X } _ { i } \in \mathbf { V }
$$

## 3、习惯记号

$\mathsf { V } _ { \mathsf { N } } \cdot$ 大写字母 $A \cdot B \cdot C \cdot S$ 等

${ \sf V } _ { \sf T } \mathrm { \large : }$ 小写字母，0\~9，+、－等运算符，

标点，分界符，黑体字母串idif

$x \cdot \forall \cdot 7 :$ 文法符号，或 ${ \sf V } _ { \sf N }$ 或 $\mathsf { v } _ { \mathsf { T } } -$

个符号

$\begin{array} { r l } { \textbf { U } \cdot \textbf { V } , \quad \textbf { W } . . . \textbf { Z } : \quad \big \textbf { V } _ { \intercal } } & { { } } \end{array}$ 中串

$a \cdot \{ 3 \cdot \forall :$ 文法符号串 $\in ( \mathsf { V } _ { \intercal } \mathsf { U } \mathsf { V } _ { \mathsf { N } } ) ^ { \star }$

S: 开始符号，第一个产生式中出现

->: 生成/定义为（元语言符号）

或（元语言符号）

## 问题：表达式语言无穷，如何定义？

●有穷条产生式，产生无穷集，要求产生式必须递归

定义算术表达式，用了两条浓缩的产生式，一般定义一个语言的产生式是很复杂的

对递归的算术表达式的产生式，进行反复推导产生 表达式语言

## 4、推导与语言

问题：用文法如何定义一个语言？

思路：从S出发，反复使用P，对非终结符替换展开，最后得到全由终结符串组成的一个串

涉及到：替换->推导->句型->句子->语言

①直接推导：是两个字符串之间的一种关系R

如：（αAβ）R（αyβ），它表示：

若 $A \to \mathsf { v e P } \ , \quad \mathsf { a } \ \cdot \ \mathsf { \beta } \in \mathsf { V } ^ { \star }$

则R 就是直接推导，R 记为

即： $\mathbf { a A \beta } \Rightarrow \mathbf { a y \beta }$

②推导：如两个串 ${ \harpoonright _ { 0 } } \cdot \ v u _ { \mathfrak n }$ ，存在一个串序列

$$
\mathbf { U } _ { 0 } \Rightarrow \mathbf { U } _ { 1 } \Rightarrow \ldots \Rightarrow \mathbf { U } _ { n }
$$

则 $\mathbf { u } _ { 0 } \mathbb { R } _ { 1 } \ \mathbf { u } _ { \mathrm { n } } \ \cdot \ \mathbb { R } _ { 1 }$ 记 司 米

${ \bf u } _ { 0 } \stackrel { + } { \longrightarrow } { \bf u } _ { \mathrm { n } } :$ 表示从 ${ \bf u } _ { 0 }$ 出发，经一步或若干步，可推导出 $\mathbf { u } _ { \mathfrak { n } }$

$\mathbf { u } _ { 0 } \overset { * } {  } \mathbf { u } _ { \mathfrak { n } }$ ：表示从 ${ \bf u } _ { 0 }$ 出发，经0步或若干步，可推导出 $\mathbf { u } _ { \mathfrak { n } }$

## ③怎样由推导引出语言？

✓只需在推导中加一些限制

即对： ${ \bf u } _ { 0 } \stackrel { + } {  } { \bf u } _ { \mathrm { n } }$ 或 $\mathbf { u } _ { 0 }$ un

·如令 ${ \bf u } _ { 0 }$ 为S，即推导要从开始符号开始，那么：

$\mathbf { S } \stackrel { * } { \Rightarrow } \alpha \quad \mathbf { \Omega } ^ { } \cdot \mathbf { \Omega } \mathrm { a } \in \mathbf { V } ^ { \star }$ ，称α为G的句型

·如再要求 $\mathsf { a } \in \mathsf { V } _ { \tau } { } ^ { \star }$ ，则α为G的句子

文法G 所产生的句子的全体是一个语言，记为L(G)$\mathsf { L } ( \mathsf { G } ) = \{ \mathbf { a } \mid \mathsf { S } \ \stackrel { + } { \to } \mathbf { a } \ \& \ \mathbf { a } \in \mathsf { V } _ { \mathsf { T } } { } ^ { * } \ \}$

## 说明

①由文法G 定义语言L 是依赖一种运算，关 \*

$\ b { \mathsf { V } } ^ { \star }$ 中有许多的串，仅有那些(S,u)(S,v)存关系的uν才有可能成为语言中的句子。

②αβ、γ是句型，表示(S，α)(S，β)， 米的关系，但它的构成不全为 ${ \sf V } _ { \sf T }$ 的字符。

③G 的句型集，是指存在 $s ^ { \pm }$ α 关系的所有 α，该 集的子集是L(G)

④V\*⊃句型集⊃L(G)

例：G[E]： E→E+T|TT→T\*F|FF→(E)|a

句子：用符号 a，+，\*，（和）构成的算术表达式

$$
( \textsf { a } + \textsf { a } ) ^ { \star } \mathsf { a }
$$

## 练习：

## 对于文法 G[S]：

S→1A|0B|ε

$$
\mathbf { A } \to \mathbf { 0 } \mathbf { S } \mid \mathbf { 1 } \mathbf { A } \mathbf { A }
$$

$$
\mathbf { B } \to \mathbf { 1 5 } | \mathbf { 0 } \mathbf { B } \mathbf { B }
$$

(1) 请写出三个关于 G[S] 的句子;

(2) 符号串 11A0S 是否为 G [S] 的句型?试证明你的结论。

## 主要知识点回顾

文法

推导

句型

句子

语言

符号串集合∑\*和Σ+有什么区别？

## 练习

1.G[S]:

$$
V _ { \parallel } = \{ S \}
$$

$$
V _ { \gamma } { = } \{ 0 , 1 \}
$$

$$
P = \{ S \{ \substack { \{ S \{ S \{ 1 \} \} }  \quad S \{ > 0 \{ 1 \}   \}
$$

则 $L ( \mathbf { G } ) = ?$

## 文法的等价

若L $\begin{array} { r l } { ( \mathbf { \Delta G } _ { 1 } ) } & { { } = \mathbf { L } \quad ( \mathbf { \Delta G } _ { 2 } ) } \end{array}$ 则称文法 $\mathbf { G } _ { 1 }$ 和 $\mathbf { G } _ { 2 }$ 是等价的。

如文法 ${ \bf G } _ { 1 } [ \ A ] : \ \mathsf { A } \to 0 \mathsf { R }$ 与 $\mathsf { G } _ { 2 } [ \mathsf { S } ] : \mathsf { S } \to 0 \mathsf { S } \uparrow$ A→01 S→01 R→A1 是否等价呢?

## 例 2 根据文法 G:

$$
E  E + E \mid E ^ { \star } E \mid ( \textsf { E } ) \mid \mid
$$

最左推导是指，任何一步 α=>β都是对α中的最左非终结符进行替换的

最右推导是指，任何一步α=>β都是对α中的最右非终结符进行替换的

注意：从一个句型到另一个句型的推导过程并不唯一，但通常只考虑最左推导和最右推导。

1：文法G 所描述的语言是 的集合。

A 文法G 词汇表V中所有符号组成的符号串

B 文法G 词汇表V的闭包 V\*中的所有符号串

C 由文法的开始符号推导出的所有符号串

D由文法的识别符推导出的所有终结符号串

2：已知语言 $L = \{ \mathbf { a } ^ { \mathsf { n } } \mathbf { b } \mathbf { b } ^ { \mathsf { n } } | \mathbf { n } { > } = 1 \}$ ，则下述文法中，文法可以产生语言L。

A Z→aZb|aAb|b A→aAb|b

B Z→aAb A→b

C Z→AbB A→aA|a B→bB|b

D Z→aAb A→aAb|b

## 练习

```perl
2. 文法 $\mathsf { G } = \mathsf { \Gamma } ( \mathsf { V } _ { \mathsf { N } } , \mathsf { V } _ { \mathsf { T } } , \mathsf { P } , \mathsf { S } )$ ，其中
$V _ { N } = \{ 1 , \mathsf { D } , \mathsf { L } \}$
V={0，1，2，3，4，5，6，7，8，9,
$\mathsf { a } , \mathsf { b } , \mathsf { c } , \mathsf { d } , \ldots , \mathsf { Z } \}$
P={I->L|IL|ID L->a|b|c...|z D->0|1|2|...|9}
则L(G)=
```

## 1、文法的描述应达到要求：

形式上严格、准确；

易于理解；

具有较强的描述能力；

有利于句子的分析和翻译，构造语法分析器

## 2、文法分类：分为四类（012、3型文法），对应四类语言；

与程序语言语法有关的是上下文无关文法

## 文法的类型

通过对产生式施加不同的限制，Chomsky 将文法分为四种类型：

0型文法：对任一产生式 $a  \beta$ ，都有 $\alpha \in ( \mathsf { V } _ { \mathsf { N } } \mathsf { U } \mathsf { V } _ { \top } ) ^ { + }$ $\mathsf { \beta } \in ( \mathsf { V } _ { \mathsf { N } } \mathsf { u } \mathsf { V } _ { \top } ) ^ { * }$

1 型文法：对任一产生式 $a  \beta$ ，都有 $| \beta | \geq | \alpha |$ ，仅仅$S \to \varepsilon$ 除外

2 型文法：对任一产生式 $a  \beta$ ，都有 $\alpha { \in } V _ { \nu }$ $\beta { \in } ( \mathsf { V } _ { \mathsf { N } } \mathsf { U } \mathsf { V } _ { \top } ) ^ { * }$

3 型文法：任一产生式 $a  \beta$ 的形式都为 A→aB 或 A→a，其中 $\pmb { \Delta } \in \mathbb { V } _ { \mathbb { N } }$ 9 $\mathsf { B } \in \mathsf { V } _ { \mathsf { N } }$ 9 $\mathsf { a t } \mathsf { V } _ { \mathsf { T } }$

## 文法的类型

例：1型（上下文有关）文法

文法 G[S]: S→CD Ab→bA

$$
\mathbf { C } {  } \mathbf { a } \mathbf { C } \mathbf { A }
$$

$$
\mathtt { B a \to a B }
$$

$$
\mathsf { C } \to \mathsf { b } \mathsf { C } \mathsf { B }
$$

$$
\mathbb { B } \mathbb { b }  \mathbb { b } \mathbb { B }
$$

$$
\mathbb { A D } \to \supseteq \mathbb { D }
$$

$$
\mathbb { C } \to \varepsilon
$$

$$
\mathsf { B D } \to \mathsf { b D }
$$

$$
\mathsf { D } \to \varepsilon
$$

$$
\mathbb { A } \mathbb { a } \to \mathbb { b } \mathbb { D }
$$

## 文法的类型

## 例：2型（上下文无关）文法

文法 G[S]： S→ABA→BS|0B→SA|1

## 3型文法

G[S]:

$$
\mid  \mid
$$

$$
\mathsf { T } \to \mathsf { T }
$$

A→0A|1B|0S

$$
{ \mathsf { T } } \to { \mathsf { d } } { \mathsf { T } }
$$

B→1B|1|0

$$
\mathbb { T }  \mathbb { }
$$

$$
\mathsf T \to \mathbb d
$$

## 文法的类型

四种文法之间的逐级“包含”关系

![](images/097dde67e287a71b4c7492c8b02943cd8b392fcc4e85b52a4618ddca51f5ea1c.jpg)

## 文法和语言

0型文法产生的语言称为0型语言

1型文法或上下文有关文法（CSG）产生的语言称为1型语言或上下文有关语言（CSL）

2型文法或上下文无关文法（CFG）产生的语言称为2型语言或上下文无关语言（CFL）

3型文法或正则（正规）文法（RG）产生的语言称为3型语言正则（正规）语言（RL）

## 文法和语言

四种文法之间的关系是将产生式做进一步限制而定义的。

存在0型语言，不是上下文有关（1型）语言

存在1 型语言，不是上下文无关（2 型）语言

存在2型语言，不是正规（3 型）语言

## 根据形式语言理论，文法和识别系统间有这样的关系

0型文法（短语结构文法）的能力相当于图灵机，可以表征任何递归可枚举集，而且任何0型语言都是递归可枚举的

1型文法（上下文有关文法）：产生式的形式为 $ { \mathbf { a } } _ { 1 }  { \mathsf { A } }  { \mathbf { a } } _ { 2 } \to  { \mathbf { a } } _ { 1 }  { \mathsf { B } }  { \mathbf { a } } _ { 2 }$ 即只有A出现在 ${ \mathfrak { a } } _ { 1 }$ 和 ${ \mathfrak { a } } _ { 2 }$ 的上下文中时，才允许β取代A。其识别系统是线性界限自动机。

任何能用图灵机描述的计算都能机械实现，任何能在现代计算机上实现的计算都能用图灵机描述

## 带

磁头

有限控制器

2型文法（上下文无关文法CFG）：产生式的形式为A→β，β取代A时与A的上下文无关。其识别系统是不确定的下推自动机。

3型文法（正规文法RG）：产生的语言是有穷自动机（FA）所接受的集合

## 练习：

以下文法描述的语言是什么？属于那类文法?

G[S]: S->Aa A->bA|a

G[S]: S->aSBC|abC CB->BC bB->bb bC->bc cC->cc

## 3、上下文无关文法的特点：

它所定义的语法范畴（或语法单位）是完全独立于这种范畴可能出现的环境的

## 说明

上下文无关文法只能描述一部分语言，但已足够描述现今的程序设计语言

自然语言要用其他的文法来描述

## 三、语法树与二义性

## 1、语法树

目的：为了理解句子的语法，得到句子如何从开始符号推导得到，因此引入“图”

定义：句型推导的图形表示，它与替换顺序的选取无关

作用：明显的形成文法所暗含的句子分层语法结构，为语法分析提供一些新的途径

树的内节点：非终结符A标记若A->α，则该产生式的一棵子树为

![](images/862a89ed782406ff9e1a73aeab11377d3626208b787af4201c675fca47d822c5.jpg)

树的叶：非终结符终结符，对应一个句型

●语法树为语法分析提供一些新的途径

## ●在语法树中找出文法中的概念

·内结点A

$$
{ \sf V } _ { \sf N }
$$

·叶

文法符号

·子树

直接推导

·根结点

S

·任一次全剪

句型

叶 $\exists \in \mathsf { V } _ { \mathsf { T } }$ 时，将叶子顺序排列 句子

E ->EAE|( E )| — E |

例3E」 —（id + id）的语法树id

最左推导： $\begin{array} { r l } { \Xi ^ { \Rightarrow } } & { { } = \mathsf { E } ^ { \Rightarrow } \quad - ( \mathsf { E } ) \mathsf { F } \quad - ( \mathsf { E } _ { - } ^ { \mathsf { A }  + }  - \vert + \vert / \vert \uparrow \vert  } \end{array}$ $( \ " { \bf d } + \ " { \bf d } )$   
最右推导： $\begin{array} { r l r l r l } { \Xi \to } & { { } = \mathsf { E } \Rightarrow } & { - \left( \mathsf { \ E } \right) \mathsf { \Sigma } \vdash } & { { } \left( \mathsf { E } + \mathsf { E } \right) } & { - \left( \mathsf { E } + \mathsf { E } \right) } & { { } \lnot \left( \mathsf { E } + \mathsf { i } \mathrm { c } \mathsf { i } \right) } & { \lnot \left( \mathsf { E } + \mathsf { i } \right) } \end{array}$ $( \mathbb { i } \mathbb { d } \mathbb { + } \mathbb { i } \mathbb { d } )$

语法树

![](images/9db0b4e390d1f0683afc4afcb8428a39da3dd2c02bddca9dec9a6dff3be99cfe.jpg)

## 由此可见，

·每一中间过程，句型很容易获得

·树忽略了符号的替换顺序的不同，不同推导过程得到相同的语法树

·有的语法，对于同一句子、应用不同规则进行推导得到不同的语法树

例 4 根据文法 G[E]:E-> E+E|E\*E|(E)li对句子 id + id \* id 进行推导

## ①文法G

$$
E  E { + } E \mid E ^ { { \star } E } \mid ( \textsf { E } ) \mid \mid
$$

②推导1

$$
\begin{array} { r l } & { \mathsf { E } \Rightarrow \mathsf { E } \dag \mathsf { E } \Rightarrow \mathsf { i d } \dag \mathsf { E } \Rightarrow \mathsf { i d } \dag \mathsf { E } \Rightarrow \mathsf { i d } \dag \mathsf { E } ^ { \ast } \mathsf { E } \Rightarrow \mathsf { i d } \dag \mathsf { i d } ^ { \ast } \mathsf { E } \dag \mathsf { E } \Rightarrow \mathsf { i d } \dag \mathsf { i d } ^ { \ast } \mathsf { E } \dag \mathsf { E } } \\ & { \Rightarrow \mathsf { i d } \dag \mathsf { i d } \dag \mathsf { i d } } \end{array}
$$

③推导2

$$
{ \begin{array} { r l } & { \mathsf { E } \Rightarrow \mathsf { E } ^ { * } \mathsf { E } = > \mathsf { E } + \mathsf { E } ^ { * } \mathsf { E } = > \mathsf { i d } + \mathsf { E } ^ { * } \mathsf { E } \Rightarrow \mathsf { i d } + \mathsf { i d } + \mathsf { i d } ^ { * } \mathsf { E } } \\ & { } \\ & { \Rightarrow \mid \mathsf { d } + \mathsf { i d } ^ { * } \mathsf { i d } } \end{array} }
$$

②与③两种推导对应两棵不同的语法树，如下所示：

![](images/6dddb683b8e0e8db983af6423e9136fe22cf47421e0ccd81a178acadfa3c1d33.jpg)

推导1的语法树

$$
\begin{array} { r l } & { \mathsf { E } = > \mathsf { E } + \mathsf { E } = > \mathsf { i d } + \mathsf { E } } \\ & { \quad = > \mathsf { i d } + \mathsf { E } ^ { \star } \mathsf { E } \Rightarrow \mathsf { i d } + \mathsf { i d } ^ { \star } \mathsf { E } } \\ & { \quad = > \mathsf { i d } + \mathsf { i d } ^ { \star } \mathsf { i d } } \end{array}
$$

![](images/b6164ca9cbb3449cbe56f0db2958d8ae677776e2c4468eec5c078e3e0c55f6f6.jpg)  
推导2的语法树

$$
\begin{array} { r l } & { \mathsf { E } = > \mathsf { E } ^ { \star } \mathsf { E } = > \mathsf { E } + \mathsf { E } ^ { \star } \mathsf { E } } \\ & { \quad = > \mathsf { i d } + \mathsf { E } ^ { \star } \mathsf { E } = > \mathsf { i d } + \mathsf { i d } ^ { \star } \mathsf { E } } \\ & { \quad = > \mathsf { i d } + \mathsf { i d } ^ { \star } \mathsf { i d } } \end{array}
$$

## 2、二义性问题

## ·定义：

文法G 的某一句子有两棵不同的树，则G 为二义的。

●处理二义性对语法分析不便，因此希望：

1）判定二义否

2）控制充分条件，消除二义性

## ●解决办法：尽量去掉二义性

①如对上例，可以通过阐明运算符的优先性和结合性来解除文法的二义性

②通过重写一个文法，把结合性和优先规则结 合进文法本身中去

注意到， $\angle 1 ( G ) = \angle ( G ^ { \prime } ) , G = \angle G ^ { \prime }$

## ●语言的二义性问题与文法的二义性问题

①如L找到一个文法是无二义的，则L是无二义的；

②如未找到一个文法是无二义的，则也不能断定它二义，但先天二义也存在；

③ 文法的二义性是不可判定的。

(因为文法的二义性由句子的语法树决定，不可能对无穷句子来判别)

最后，作为描述程序语言的上下文无关文法，我们限制：

① G 不含下面的产生式

P->P

②每一 $\mathsf { P } \in \mathsf { V } _ { \mathsf { N } }$ 必须都有用处，即$\exists s \equiv { \mathrm { a p } } _ { \mathsf { B } }$ ，Ρ在句型中出现$\exists \ v { v } \in \mathsf { V } _ { \tau } ^ { \star } , \mathsf { P } \stackrel { \star } {  } ,$ ，即对P不存在不终结的回路

## 练习1

已知文法G为：

$$
\mathsf { S } \mathrm { - } \mathsf { > } \mathsf { i } \mathsf { S } \mathsf { e } \mathsf { S }
$$

$$
S - > i S
$$

$V _ { N } = \{ \quad \}$ Vτ={ 1

$$
S - > i
$$

2）给出句子iiiei的最左推导最右推导语法树

3）证明文法是二义性的。

4）是几型文法？

$$
1 7 V _ { A } = \{ \ s \}
$$

$$
V _ { 1 } = \{ \dot { V } , e \}
$$

$2 ) S  S e S \Rightarrow \because S e S \Rightarrow \downarrow \downarrow \downarrow e S \Rightarrow \downarrow \downarrow \downarrow e S \Rightarrow \downarrow \downarrow \downarrow e V \downarrow$ (最左推导) $S = \because S e S \Rightarrow \vdots S e \downarrow \Rightarrow \vdots \ddots S e \dot { \times } \Rightarrow \ddot { m } \dot { \times } e \dot { V }$ (最右推导)

![](images/e02662da4f7a95f76a5aa56dd8cc1292a434ad3a64406a9939ab384cb544f6ab.jpg)

3）：对于句子e有两棵不同的语法树4）是二型

![](images/f4d3e534c9f507da795477e460bbeb23c2d30cbb0b2b3efbc0de272810bea162.jpg)

![](images/8f7843eb63fccdf5ba4a9c457ae40483849e9ed436ec1bfc4d67a0e6e6295f01.jpg)

∴该文法具有二义性.

## 四、句型的分析

## 1. 句型的分析

指构造一种算法，用以判断所给的符号串是否为某一文法的句型或句子。是一个过程。

其中，将算法称为分析算法，完成句型分析的程序称为分析程序或识别程序。

在编译程序中，词法分析阶段和语法分析阶段都存在句型分析。

## 2. 分析算法分为：

## 自上而下的分析方法

从文法的开始符号出发，以给定的符号串为目标，试图推导出此符号串。

## 自下向上的分析方法

从给定的符号串出发，反复用文法中有关产生式的左部去替换当前符号串中相应的子串，以期最后将其规约为文法的开始符号。

## 两种方法反映了两种语法树的构造过程。

自上而下方法是从文法符号开始，将它做为语法树的根，向下逐步建立语法树，使语法树的结果正好是输入符号串

自下而上方法则是从输入符号串开始，以它做为语法树的结果，自底向上地构造语法树

## 句型分析的有关问题

1）在自上而下的分析方法中如何选择使用哪个产生式进行推导？假定要被代换的最左非终结符号是 B，且有n条规则：B→A1|A2|..|An，那么如何确定用哪个右部去替代B？

2）在自下而上的分析方法中如何识别可归约的串？在分析程序工作的每一步，都是从当前串中选择一个子串，将它归约到某个非终结符号，该子串称为“可归约串

## 3 句型分析的有关问题

短语：令G是一个文法，S是文法的开始符号，若αβδ是文法G的一个句型，如果有S α且Aβ则称β是句型αβ6相对于非终结符A的短语直接短语：如果有Aβ，则称β是句型$\alpha \beta \delta$ 相对于规则A一>β的直接短语

句柄：一个句型的最左直接短语称为该句型的句柄。

## 例i\*i+i

例：i\*i+i的短语、直接短语和句柄

![](images/7357be1c35d7803178f16955db8aa61b9ac3165bba76da7357c25c321e6e4aaf.jpg)

G[E] : E→E+T|T T→T\*F|F F→(E)|i   
句型：i\*i+i

![](images/a34f22f17be8d2f24f6bf09596d8c7ff6a34c92b44169dd1f81c7b021d2c1df6.jpg)

短语 $\mathbf { i } _ { 1 } ^ { \circ } \cdot \mathbf { \ l } _ { 2 } ^ { \circ } \mathbf { \ l } _ { 3 } ^ { \circ } \textrm {  { ~ \overline { { ~ \theta ~ } ~ } } } \mathbf { I } _ { 1 } ^ { \circ \circ } \textbf { I } _ { 2 }$ ${ \underline { { \hat { \bf l } } } } _ { \underline { { \hat { \bf l } } } }$ 3 C

直接短语： ${ \bf { \bar { l } } } _ { 1 } \quad \bf { 9 } \quad { \bf { \bar { l } } } _ { 2 } \quad \bf { 9 } \quad { \bf { \bar { l } } } _ { 3 }$ 句柄： $\mathbf { \widetilde { I } _ { 1 } }$

## 练习2

已知文法 G 为：

S->aAcB|Bd

A->AaB|c

B->bScA|b

写出句型 aAaBcbbdcc 的语法树，并指出相应的短语直接短语句柄

## 一、一士以S为核

B为根1 a, 1 C 1 B 1 S为核 A为核 接短语：AaB， 句柄：AaBC 11iA a B： 11 11 1 b，c11 一 1 111 (1 11 短语：AaB，b，c1 1 一 1!1 111 111 根 1 aAaBcbbdcc一  
1 11 二 1 bd,bbdcc一  
1—T

## 化简文法文法实用中的一些说明

文法中不含有有害规则和多余规则

有害规则：形如U→U的产生式。会引起文法的二义性

多余规则：指文法中任何句子的推导都不会用到的规则

文法中不含有不可到达和不可终止的非终结符

1）文法中某些非终结符不在任何规则的右部出现该非终结符称为不可到达。

2）文法中某些非终结符，由它不能推出终结符号串，该非终结符称为不可终止。

对于文法 G[S]，为了保证任一非终结符 A 在句子推导中出现，必须满足如下两个条件：

1. A 必须在某句型中出现  
即有 $S = > { \alpha } A \beta$ ，其中α，β属于 $\mathsf { V } ^ { \star }$ 2. 必须能够从 A 推出终结符号串t来即 $\mathbf { A } = > \mathbf { t }$ ，其中 $\mathbf { t } \in \mathbf { V } _ { \mathrm { T } } { } ^ { * }$

## 已知语言构造出描述其的文法

已知字母表 ${ \sf T } = \{ { \sf a } , { \sf b } \}$

(L(G)={ξ}

$\mathsf { L } ( \mathsf { G } ) \mathop { = } \{ \mathsf { a } , \mathsf { b } $

$L ( \mathbf { G } ) = \{ \ a ^ { n } \mid n > = 1 \}$

$L ( G ) = \{ \left. \exists ^ { n } \mathbf { b } ^ { n } \right| n > = 0 \}$

$$
\scriptstyle \lfloor ( \mathsf { G } ) = \{ \mathsf { a } ^ { \mathsf { n } } \mathsf { b } ^ { \mathsf { m } } | \mathsf { n } , \mathsf { m } > = 0 \}
$$

## 已知语言构造出描述其的文法

已知字母表 ${ \sf T } = \{ { \sf a } , { \sf b } \}$

(L(G)={ aⁿbⁿci| n>=1,i>=0}

$L ( G ) = \{ \left. \mathsf { a } ^ { \mathsf { m } } \mathsf { b } ^ { \mathsf { n } } \mathsf { a } ^ { \mathsf { n } } \mathsf { b } ^ { \mathsf { m } } \right| \mathsf { n } , \mathsf { m } > = 1 \}$

L(G)={ abⁿabⁿ-1 | n>=1 }

88 $\mathsf { L } ( \mathsf { G } ) { = } \{ \mathsf { W c W R } \mid \mathsf { W } \mathsf { \{ c ( a \mid b ) ^ { \ast } , W ^ { \mathsf { R } } } $ 是W的反置}

## [本章小结]

## 考察本章知识点最典型的题目是

1.已知文法G[A]，写出它定义的语言描述

如：G[A]: A→0B|1C B→1|1A|0BB C→00A1CC

答案：G[A]定义的语言由01符号串组成，串中0和1 的个数相同.

2. 给出语言描述，构造文法

如：构造一文法，其定义的语言是由算符+，\*，(,)和运算对象a构成的算术表达式的集合

答案 1: G[E] E→E+T|T T→T\*F |F F→(E)|a   
答案2:G[E]E→E+E|E\*E|(E)|a

1. 以下文法描述的语言是什么？属于几型文法?

1）文法G[S]：S→bSc|bc

2）文法 G[S]：S->BC B->bCc|bc C->dC|c

3）文法G[S]：S->fBC B->bB|b C->c

2. 根据语言写出文法。

1） $L ( G ) = \{ 6 ^ { \cap } \mathbb { C } ^ { \mathsf { m } } { \mathsf { d } } ^ { 2 \mathsf { m } } | \cap , \mathsf { m } > = 0 \}$

2）L(G)={b²ⁿcn|n>=1}

3） $\mathsf { L } ( \mathsf { G } ) { = } \{ \mathsf { b c } ^ { \mathsf { n } } \mathsf { b } | \mathsf { n } { > } { = } 0 \}$

3. 已知文法G 为：

S->W W->U|WjU U->G|U+G G->)W\*1(

1）给出终结符集和非终结符集。

2）给出句型G+Gj(的最左推导和语法树

3）给出该句型的短语、直接短语和句柄

4）该文法是几型文法？给出该句型的素短语和最左素短语
