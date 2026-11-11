## 第6章 LR分析

在第5章中已经讨论过，自底向上分析方法是一种移进-归约过程，当分析的栈顶符号串形成句柄或可归约串时就采取归约动作。若是限定采用规范规约，那么自底向上分析法的关键问题是在分析过程中如何确定句柄。LR分析法正是给出一种能根据当前分析栈中的符号串(通常以状态表示)和向右顺序查看输入串的 $k \left( k \geqslant 0 \right)$ 个符号就可唯一地确定分析器的动作是移进还是归约和用哪个产生式归约，因而也就能唯一地确定句柄。LR分析法的归约过程是规范推导的逆过程，所以LR分析过程是一种规范归约过程。

LR(k)分析方法是1965年Knuth[48]提出的，括号中的k表示向右查看输入串符号的个数。这种方法比起自顶向下的LL(k)分析方法和自底向上的优先分析方法对文法的限制要少得多，也就是说，对于大多数用无二义性上下文无关文法描述的语言都可以用相应的LR分析器进行识别，而且这种方法还具有分析速度快，能准确、即时地指出出错位置的特点。它的主要缺点是对于一个实用语言文法的分析器的构造工作量相当大，k愈大，构造愈复杂，实现比较困难。因此，目前许多实用的编译程序，当采用LR分析器时都是借助于美国Bell 实验室推出的 yacc 来实现的。yacc 能接受一个用BNF描述的满足 LR类中 LALR(1)的上下文无关文法并对其自动构造出LALR(1)分析器。

本章主要介绍LR分析的基本思想和当 $k \leqslant 1$ 时LR分析器的基本构造原理和方法。其中LR(0)分析器在分析过程中不需向右查看输入符号，因而它对文法的限制较大，对绝大多数高级语言的语法分析器是不能适用的；然而，它是构造其他LR类分析器的基础。当k=1时，已能满足当前绝大多数高级语言编译程序的需要。本章着重介绍LR(0)、SLR(1)、LALR(1)和LR(1)这4种分析器的构造方法，其中 SLR(1)和LALR(1)分别是LR(0)和LR(1)的一种改进。

## 6.1 LR 分析概述

一个LR分析器由3个部分组成：

（1）总控程序，也可以称为驱动程序。对所有的LR分析器，总控程序都是相同的。

(2)分析表或分析函数。不同的文法分析表将不同，同一个文法采用的LR分析器不同时，分析表也不同，分析表又可分为动作(ACTION)表和状态转换(GOTO)表两个部分，它们都可用二维数组表示。

（3）分析栈，包括文法符号栈和相应的状态栈。它们均是先进后出栈。

分析器的动作由栈顶状态和当前输入符号来决定(LR(0)分析器不需向前查看输入符号）。

LR分析器工作过程示意图如图6.1所示。

其中SP为栈指针，S[i为状态栈，X[i为文法符号栈。状态转换表内容按关系GOTO$[ S _ { i } , X ] = S _ { j }$ 确定，该关系式是指当栈顶状态为 $S _ { i }$ 遇到当前文法符号为X时应转向状态

$S _ { j }$ 。X为终结符或非终结符，状态的含义将在后面介绍。

![](images/d3498bbd574c29ae0cb7897eff42eaf5d8a4940d823f5915e142879971b5df5d.jpg)  
图 6.1 LR 分析器工作过程示意图

$\operatorname { A C T I O N } [ S _ { i } , a ]$ 规定了栈顶状态为 $S _ { i }$ 时遇到输入符号a应执行的动作。动作有4种可能：

## (1) 移进。

当 $S _ { j } = \mathrm { G O T O } [ S _ { i } , \alpha ]$ 成立，则把 $S _ { j }$ 移入到状态栈，把a移入到文法符号栈。其中i、j表示状态号。

## (2) 归约。

当在栈顶形成句柄为 $\beta$ 时，则用 $\beta$ 归约为相应的非终结符A，即当文法中有 $A  \beta$ 的产生式，而 $\beta$ 的长度为r(即 $| \beta | = r )$ ，则从状态栈和文法符号栈中自栈顶向下去掉r个符号，即栈指针SP减去 $r _ { \circ }$ 并把A移入文法符号栈内，再把满足 $S _ { j } = \mathrm { G O T O } [ S _ { i } , A ]$ 的状态移进状态栈，其中 $S _ { i }$ 为修改指针后的栈顶状态。

## (3) 接受 $\alpha c c .$

当归约到文法符号栈中只剩文法的开始符号S，并且输入符号串已结束，即当前输入符是#，则为分析成功。

## (4) 报错。

当遇到状态栈顶为某一状态下出现不该遇到的文法符号时则报错，说明输入串不是该文法能接受的句子。

LR分析器的关键部分是分析表的构造，后边将针对每种不同的LR分析器详细介绍其构造思想及方法。

## 6.2 LR(0)分析

LR(0)分析表构造的思想和方法是构造其他LR分析表的基础。在第5章例5.1中曾给出文法G[S]为：

(1) $S {  } a A c B e$

(2) $A  b$

(3) $A {  } A b$

(4) $B {  } d$

对输入串abbcde#用自底向上归约的方法进行分析，当归约到第(5)步时栈中符号串为#aAb，采用了产生式(3)进行归约而不是用产生式(2)归约，而在第(3)步归约时栈中符号串为#ab时却用产生式(2)归约，虽然在第(3)步和第(5)步归约前栈顶符号都为b，但归

约所用产生式却不同，其原因在于已分析过的部分，即在栈中的前缀不同。在LR分析中就体现为状态栈的栈顶状态不同。为了说明这个问题，先在表6.1中给出例5.1中文法G[S]的LR(0)分析表，在表6.2中给出对输入串abbcde#的分析过程。

表6.1 例5.1文法的LR(0)分析表
<table><tr><td rowspan=2 colspan=1></td><td rowspan=1 colspan=6>ACTION</td><td rowspan=1 colspan=3>GOTO</td></tr><tr><td rowspan=1 colspan=1> $a$ </td><td rowspan=1 colspan=1>C</td><td rowspan=1 colspan=1>e</td><td rowspan=1 colspan=1> $^ { b }$ </td><td rowspan=1 colspan=1> $d$ </td><td rowspan=1 colspan=1>#</td><td rowspan=1 colspan=1>S</td><td rowspan=1 colspan=1> $A$ </td><td rowspan=1 colspan=1>B</td></tr><tr><td rowspan=1 colspan=1>0123456789</td><td rowspan=1 colspan=1> $S _ { 2 }$  $r _ { 2 }$  $r _ { 3 }$  $r _ { 4 }$  $r _ { 1 }$ </td><td rowspan=1 colspan=1> $S _ { 5 }$  $r _ { 2 }$  $r _ { 3 }$  $r _ { 4 }$  $r _ { 1 }$ </td><td rowspan=1 colspan=1> $r _ { 2 }$  $r _ { 3 }$  $S _ { 9 }$  $r _ { 4 }$  $r _ { 1 }$ </td><td rowspan=1 colspan=1> $S _ { 4 }$  $S _ { 6 }$  $r _ { 2 }$  $r _ { 3 }$  $r _ { 4 }$  $r _ { 1 }$ </td><td rowspan=1 colspan=1> $r _ { 2 }$  $S _ { 8 }$  $r _ { 3 }$  $r _ { 4 }$  $r _ { 1 }$ </td><td rowspan=1 colspan=1> $a c c$  $r _ { 2 }$  $r _ { 3 }$  $r _ { 4 }$  $r _ { 1 }$ </td><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>7</td></tr></table>

表 6.2 对输入串 abbcde#的分析过程
<table><tr><td rowspan=1 colspan=1>步骤</td><td rowspan=1 colspan=1>状态栈</td><td rowspan=1 colspan=1>符号栈</td><td rowspan=1 colspan=1>输入串</td><td rowspan=1 colspan=1>ACTION</td><td rowspan=1 colspan=1>GOTO</td></tr><tr><td rowspan=1 colspan=1>(1)</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>#</td><td rowspan=1 colspan=1>abbcde#</td><td rowspan=1 colspan=1> $S _ { 2 }$ </td><td rowspan=7 colspan=1>33</td></tr><tr><td rowspan=1 colspan=1>(2)</td><td rowspan=1 colspan=1>02</td><td rowspan=1 colspan=1>#a</td><td rowspan=1 colspan=1>bbcde#</td><td rowspan=1 colspan=1> $S _ { 4 }$ </td></tr><tr><td rowspan=1 colspan=1>(3)</td><td rowspan=1 colspan=1>024</td><td rowspan=1 colspan=1>#ab</td><td rowspan=1 colspan=1>bcde#</td><td rowspan=1 colspan=1> $r _ { 2 }$ </td></tr><tr><td rowspan=1 colspan=1>(4)</td><td rowspan=1 colspan=1>023</td><td rowspan=1 colspan=1>#aA</td><td rowspan=1 colspan=1>bcde#</td><td rowspan=1 colspan=1> $S _ { 6 }$ </td></tr><tr><td rowspan=1 colspan=1>(5)</td><td rowspan=1 colspan=1>0236</td><td rowspan=1 colspan=1>#aAb</td><td rowspan=1 colspan=1>cde#</td><td rowspan=1 colspan=1> $r _ { 3 }$ </td></tr><tr><td rowspan=1 colspan=1>(6)</td><td rowspan=1 colspan=1>023</td><td rowspan=1 colspan=1>#aA</td><td rowspan=1 colspan=1>cde#</td><td rowspan=1 colspan=1> $S _ { 5 }$ </td></tr><tr><td rowspan=1 colspan=1>(7)</td><td rowspan=1 colspan=1>0235</td><td rowspan=1 colspan=1>#aAc</td><td rowspan=1 colspan=1>de#</td><td rowspan=1 colspan=1> $S _ { 8 }$ </td></tr><tr><td rowspan=1 colspan=1>(8)</td><td rowspan=1 colspan=1>02358</td><td rowspan=1 colspan=1>#aAcd</td><td rowspan=1 colspan=1>e #</td><td rowspan=1 colspan=1> $r _ { 4 }$ </td><td rowspan=4 colspan=1>71</td></tr><tr><td rowspan=1 colspan=1>(9)</td><td rowspan=1 colspan=1>02357</td><td rowspan=1 colspan=1>#aAcB</td><td rowspan=1 colspan=1>e #</td><td rowspan=1 colspan=1> $S _ { 9 }$ </td></tr><tr><td rowspan=1 colspan=1>(10)</td><td rowspan=1 colspan=1>023579</td><td rowspan=1 colspan=1>#aAcBe</td><td rowspan=1 colspan=1>#</td><td rowspan=2 colspan=1> $r _ { 1 }$  $a c c$ </td></tr><tr><td rowspan=1 colspan=1>(11)</td><td rowspan=1 colspan=1>01</td><td rowspan=1 colspan=1>#S</td><td rowspan=1 colspan=1>#</td></tr></table>

## 6.2.1 可归前缀和子前缀

为使最右推导和最左归约的关系看得更清楚，可以在推导过程中加入一些附加信息。若对例5.1文法G[S]中的每条产生式编上序号，用[i表示，并将其加在产生式的尾部，就使产生式变为

$$
S \mathrm {  } a A c B e [ 1 ]
$$

$$
A {  } b [ 2 ]
$$

$$
A  A b [ 3 ]
$$

$$
B {  } d [ 4 ]
$$

但i不属于产生式的文法符号，对输入串abbcde进行推导时把序号也带入，作最右推导，形成如下形式：

$$
\begin{array} { r l } & { S \Rightarrow \alpha A c B e [ 1 ] \Rightarrow a A c d [ 4 ] e [ 1 ] } \\ & { \Rightarrow a A b [ 3 ] c d [ 4 ] e [ 1 ] \Rightarrow a b [ 2 ] b [ 3 ] c d [ 4 ] e [ 1 ] } \end{array}
$$

输入串abbcde是该文法的句子。

它的逆过程—最左归约(规范归约)则为

$$
\begin{array} { r l r l } & { \alpha b [ 2 ] b [ 3 ] c d [ 4 ] e [ 1 ] } & & { { \mathbb H } ^ { 3 / 2 } \underline { { \texttt X } } \underline { { \texttt X } } ( 2 ) \mathbb J \exists \underline { { \mathcal E } } \underline { { \texttt Y } } } \\ & { \Leftarrow \alpha A b [ 3 ] c d [ 4 ] e [ 1 ] } & & { { \mathbb H } ^ { 3 / 2 } \underline { { \texttt X } } \underline { { \texttt X } } ( 3 ) \mathbb J \exists \underline { { \mathcal E } } \underline { { \texttt Y } } } \\ & { \Leftarrow \alpha A c d [ 4 ] e [ 1 ] } & & { { \mathbb H } ^ { 3 / 2 } \underline { { \texttt X } } \underline { { \texttt X } } ( 4 ) \mathbb J \mathbb J } \\ & { \Leftarrow \alpha A c B e [ 1 ] } & & { { \mathbb H } ^ { 3 / 2 } \underline { { \texttt X } } \underline { { \texttt X } } ( 1 ) \mathbb J \exists \underline { { \mathcal E } } \underline { { \texttt Y } } } \\ & { \Leftarrow { \cal S } } \end{array}
$$

其中⇐表示归约。从这里可以看到，对一个合法的句子而言，每次归约后得到的都是由已归约部分和输入剩余部分合起来构成文法的规范句型，而用哪个产生式继续归约仅取决于当前句型的前部，例中每次归约前句型的前部依次为

$$
\begin{array} { l } { a b [ 2 ] } \\ { a A b [ 3 ] } \\ { a A c d [ 4 ] } \\ { a A c B e [ 1 ] } \end{array}
$$

这正是在表6.2的分析过程中每次采取归约动作前符号栈中的内容，即分别对应步骤(3)、(5)、(8)、(10)时符号栈中的符号串，规范句型的这种前部称作可归前缀。

再来分析上述每个前部的前缀：

$$
\begin{array} { l } { \varepsilon , a , a b } \\ { \varepsilon , a , a A , a A b } \\ { \varepsilon , a , a A , a A c , a A c d } \\ { \varepsilon , a , a A , a A c , a A c B , a A c B e } \end{array}
$$

不难发现前缀a、aA和aAc都不只是某一个规范句型的前缀，因此把在规范句型中形成可归前缀之前包括可归前缀在内的所有前缀都称为活前缀。活前缀为一个或若干规范句型的前缀。在规范归约过程中的任何时刻，只要已分析过的部分(即在符号栈中的符号串)均为规范句型的活前缀，则表明输入串已被分析过的部分是该文法某规范句型的一个正确部分。

为了适于LR分析的进行，需对文法作扩充，在原文法G中增加产生式 $S ^ { \prime } {  } S , S$ 为原文法G的开始符号，所得的新文法称为G的拓广文法，以 $G ^ { \prime }$ 表示， $S ^ { \prime }$ 为拓广后文法 $G ^ { \prime }$ 的开始符号。易见文法 $G ^ { \prime }$ 和G等价。对文法进行拓广的目的是：对某些右部含有开始符号的文法，在归约过程中能分清是否已归约到文法的最初开始符，还是在文法右部出现的开始符号，拓广文法的开始符号 $S ^ { \prime }$ 只在左部出现，这样确保了不会混淆。

由此可以形式地定义活前缀如下。

定义6.1 若 $S ^ { ' } \Rightarrow \alpha A \omega \Rightarrow \alpha \beta \omega$ 是文法 G 的拓广文法 $G ^ { \prime }$ 中的一个规范推导，符号串 $\gamma$ 是$\alpha \beta$ 的前缀，则称γ是G的一个活前缀。也就是说γ是规范句型 $\alpha \beta \omega$ 的前缀，但它的右端不超过该句型句柄的末端。

由以上分析很容易理解，在LR分析过程中，实际上是把 $\alpha \beta$ 的前缀列出，放在符号栈中，一旦在栈中出现 $\alpha \beta$ ，即句柄已经形成，则用产生式 $A  \beta$ 进行归约。

## 6.2.2 识别活前缀的有限自动机

在LR方法实际分析过程中，并不是去直接分析文法符号栈中的符号是否形成句柄，但它带来一个启示，可以把终结符和非终结符都看成一个有限自动机的输入符号，每把一个符号进栈时看成已识别过了该符号，而状态进行转换，当识别到可归前缀时，相当于在栈中形成句柄，则认为到达了识别句柄的终态。

如果对例5.1的文法用拓广文法表示成

现对句子abbcde列出可归前缀：

构造识别其活前缀及可归前缀的有限自动机如图6.2所示。

![](images/75104b69f94c25b13e2087cbabc3ab287dc00a621039f0aed59c4e9f926c5fc3.jpg)  
图6.2 识别活前缀及可归前缀的有限自动机

每一个终态都是句柄识别态，用 $\textcircled{ i}$ 表示，仅有带\*号的状态既是句柄识别态又是句子识别态，句子识别态仅有唯一的一个。

如果加一个开始状态X并用ε弧和每个识别可归前缀的有限自动机连接，则可变为图6.3。

将图6.3确定化并重新编号后变为图6.4。

由例5.1中的文法，对输入串abibcde#可以有如下推导：

$$
\begin{array} { r l } & { S ^ { ' } \Rightarrow S } \\ & { ~ \Rightarrow a A c B e } \\ & { ~ \Rightarrow a A c d e } \\ & { ~ \Rightarrow a A c d e } \\ & { ~ \Rightarrow a A b c d e } \\ & { ~ \Rightarrow a b ^ { i } b c d e } \end{array}
$$

![](images/2923519d05e590d5754538b01f7f88c3034e25991448e9241f90ca9f266b0f58.jpg)  
图6.3 识别活前缀的不确定有限自动机

其中i为任意正整数。

由此可见该文法所描述的语言可用正规式$a b ^ { + } c d e$ 表示。

用有限自动机识别时，每当识别完句柄，则状态回退句柄串长度的状态数。例如，在图6.4中，若已识别到状态⑤，这时句柄已形成，而且句柄是Ab，则应用A→Ab归约，状态应退回到②，又因左部为A，所以相当于在状态②时又遇到A，这时应转向状态④。在状态④再遇到输入串的一个b，又转到状态⑤，重复上述过程。

![](images/85adcc8d8395f3ea242bc89ad573e3de6d4c9c6ab3ca5623955c9db1075a484f.jpg)  
图6.4 识别活前缀的确定有限自动机

然而对于一个复杂的文法，它的可归前缀并不是如此简单就能计算出来的。

## 6.2.3活前缀及可归前缀的一般计算方法

在6.2.2节中，仅根据对某些句子规范推导的逆过程直观地看出它的活前缀和可归前缀，然后构造其有限自动机，在6.2.2节的例子中用一个句子归约过程的所有活前缀和可归前缀构造出的有限自动机，刚好也是识别整个文法的活前缀及可归前缀的有限自动机，这仅是一个特殊情况。然而，对一个任给的上下文无关文法，需有确定的办法来求出它的所有活前缀和可归前缀，才能构造其识别该文法活前缀的有限自动机。下面给出其算法。

定义6.2 设 $G = ( V _ { \mathrm { N } } , V _ { \mathrm { T } } , P , S )$ 是一个上下文无关文法，对于 $A \in V _ { \mathrm { N } }$ 有

$$
\operatorname { L C } ( A ) = \{ \alpha \mid S ^ { \prime } { \xrightarrow { * } } \alpha A \omega , \alpha { \in } V ^ { * } , \omega { \in } V _ { \mathbb { T } } ^ { * } \}
$$

其中 $S ^ { \prime }$ 是 G 的拓广文法 $G ^ { \prime }$ 的开始符号。

这里LC(A)表明了在规范推导中在非终结符A左边出现的符号串的集合。有了这个集合，就可以找出不包含句柄部分在内的所有活前缀。

推论：若文法G中有产生式 $B {  } \gamma A \delta$ ,则有

$$
\operatorname { L C } ( A ) { \overset { \vartriangle } { \supseteq } } \operatorname { L C } ( B ) \cdot \{ \gamma \}
$$

因为对任一形为 $\alpha B \omega$ 的句型，必有规范推导：

$$
S ^ { ' } \hat { \vec { R } } \otimes \alpha \bar { B } \omega \Rightarrow \alpha \gamma A \delta \omega
$$

即对任一个 $\alpha \in \operatorname { L C } ( B )$ ,定有 $\alpha \gamma { \in } \operatorname { L C } ( A )$

所以 $\operatorname { L C } ( B ) \bullet \langle \gamma \rangle \subseteq \operatorname { L C } ( A )$ o

由定义6.2推论和文法的产生式可列出方程组，那么例5.1文法可有方程：

$$
\beta { \bf C } ( S ^ { \prime } ) = \{ \varepsilon \}\tag{1}
$$

$$
\boxed { \mathrm { L C } ( S ) = \mathrm { L C } ( S ^ { \prime } ) \bullet \{ \varepsilon \} = \{ \varepsilon \} }\tag{2}
$$

$$
\operatorname { L C } ( A ) = \operatorname { L C } ( S ) \bullet \{ a \} \bigcup \operatorname { L C } ( A ) \bullet \{ \varepsilon \} = \{ a \}\tag{3}
$$

$$
\lfloor \mathbf { L C } ( B ) = \mathbf { L C } ( S ) \bullet \{ a A c \} = \{ a A c \}\tag{4}
$$

实际上，前缀的集合可以用正规表达式表示，为方便起见，下面用正规式来表示前缀集合，即上述方程可表示为

$$
\begin{array} { r } { \mathrm { ~  ~ \psi ~ } ( \mathrm { L C } ( S ^ { \prime } ) = \varepsilon } \end{array}\tag{1}
$$

$$
\operatorname { L C } ( S ) = \varepsilon\tag{2}
$$

$$
\operatorname { L C } ( A ) = a\tag{3}
$$

$$
\begin{array} { r } { \boxed { \mathrm { L C } ( B ) } = a A c } \end{array}\tag{4}
$$

这里仅求出了每个非终结符在规范推导过程中用该非终结符的右部替换该非终结符之前，它的左部可能出现的串，也就是在规范归约过程中用句柄归约成该非终结符之前不包含句柄部分的串，因而只要再把句柄加入就求得了包含句柄的活前缀。对LR(0)方法来说，包含句柄的活前缀计算非常简单，只需把上面已求得的活前缀再加上产生式的右部，可用如下形式表示：

规定 LR(0)CONTEXT $( A \{  \beta  ) = \mathrm { L C } ( A ) \ \bullet \ \beta , \mathrm { L R } ( 0 ) \mathrm { C O N T E X T } ( A \{  \beta  )$ 可简写为LR(0)$\mathrm { C } ( A \to \beta )$ ，这样对例5.1文法，包含句柄的活前缀可有

$$
\begin{array} { r l } & { \mathrm { L R } ( 0 ) \mathrm { C } ( S ^ { \prime } {  } S ) = S } \\ & { \mathrm { L R } ( 0 ) \mathrm { C } ( S {  } a A c B e ) { = } a A c B e } \\ & { \mathrm { L R } ( 0 ) \mathrm { C } ( A {  } b ) { = } a b } \\ & { \mathrm { L R } ( 0 ) \mathrm { C } ( A {  } A b ) { = } a A b } \\ & { \mathrm { L R } ( 0 ) \mathrm { C } ( B {  } d ) { = } a A c d } \end{array}
$$

包含句柄的活前缀也就是可归前缀，将它们展开也就得到了所有的活前缀。

读者可以用它构造识别文法活前缀的有限自动机，不难发现其结果与图6.2相同，说明用上述算法与前面用直观方法所求得的结果一致。为了进一步说明这种计算的结果为 $V _ { \mathrm { { N } } } \bigcup V _ { \mathrm { { T } } }$ 的正规式，下面再举一例。

设文法 $G ^ { \prime }$ 为

(0) $S ^ { \prime } {  } E$ (1) $E {  } a A$ (2) $E {  } b B$ (3) $A {  } c A$ (4) $A  d$ (5) $B {  } c B$ (6) $B {  } d$

求不包含句柄在内的活前缀方程组为

$$
\scriptstyle { \left\{ \begin{array} { l l } { \mathrm { L C } ( S ^ { \prime } ) = \varepsilon } \\ { \mathrm { L C } ( E ) = \mathrm { L C } ( S ^ { \prime } ) \cdot \varepsilon = \varepsilon } \\ { \mathrm { L C } ( A ) = \mathrm { L C } ( E ) \cdot a \left| \mathrm { L C } ( A ) \cdot \varepsilon = a c ^ { * } \right. } \\ { \left. \mathrm { L C } ( B ) = \mathrm { L C } ( E ) \cdot b \right| \mathrm { L C } ( B ) \cdot \varepsilon = b c ^ { * } } \end{array} \right. }
$$

所以包含句柄的活前缀为

$$
\begin{array} { r l } & { \mathrm { L R } ( 0 ) \mathrm { C } ( S ^ { ' }  E ) = E } \\ & { \mathrm { L R } ( 0 ) \mathrm { C } ( E  a A ) = a A } \\ & { \mathrm { L R } ( 0 ) \mathrm { C } ( E  b B ) = b B } \\ & { \mathrm { L R } ( 0 ) \mathrm { C } ( A  c A ) = a c ^ { * } c A } \\ & { \mathrm { L R } ( 0 ) \mathrm { C } ( A  d ) = a c ^ { * } d } \\ & { \mathrm { L R } ( 0 ) \mathrm { C } ( B  c B ) = b c ^ { * } c B } \\ & { \mathrm { L R } ( 0 ) \mathrm { C } ( B  d ) = b c ^ { * } d } \end{array}
$$

由此可构造以文法符号为字母表的识别活前缀(包含句柄在内)的不确定有限自动机如图6.5所示。

如前所述，所有的状态都为活前缀的识别状态，有双圈 $\textcircled{ i}$ 的状态为识别句柄的状态，双圈旁边有\*号的为识别句子的状态。识别句子的状态是唯一的。对图6.5的不确定有限状态自动机可用子集法进行确定化，结果如图6.6所示。

![](images/ee1928666d03cf59b39901a2f6848d65251e3be81a9106c9f04a90120c2baed4.jpg)  
图6.5 识别可归前缀的不确定有限自动机

![](images/de1a06156381aed5d7aaaa29ce2ee0d508ef16e52dd6bddca0429ef5f338981c.jpg)  
图6.6 识别可归前缀的确定有限自动机

因此，对任何一个上下文无关文法，只要能构造出它的识别可归前缀的有限自动机，就可以构造其相应的分析表，也就是前面所介绍的状态转换表和动作表。用这种方法构造出的识别可归前缀的有限自动机从理论的角度讲是很严格的，然而，对于一个实用的高级语言的文法实现起来却是很复杂的，因此下面再介绍一种实用的方法。

## 6.2.4 LR(0)项目集规范族的构造

## 1. LR(0)项目

在文法G中每个产生式的右部适当位置添加一个圆点构成项目。

例如， $j ^ { 2 }$ 生式 $S {  } a A c B e$ 对应有6个项目。

$$
[ 0 ] \quad S \to \bullet a A c B e
$$

$$
[ 1 ] \quad S \to \alpha \bullet A c B e
$$

[2] S→aA·cBe   
[3] S→aAc· Be   
[4] S→aAcB·e   
[5] S→aAcBe·

一个产生式可对应的项目个数一般为它的右部符号长度加1。值得注意的是，对空产生式，A→ε仅有一个项目A→·。

每个项目的含义与圆点的位置有关，概括地说，圆点的左部表示分析过程的某时刻欲用该产生式归约时已识别过的句柄部分，圆点右部表示期待的后缀部分。

上例中项目的编号用[]中的数字表示，项目[0]意味着希望用S的右部归约，当前输入串中符号应为a；项目[1]表明用该产生式归约已与第一个符号a匹配过了。需分析非终结符A的右部；项目[2]表明A的右部已分析完归约成A，目前希望遇到输入串中的符号为 $c _ { \textup { c } }$ 依此类推，直到项目[5]为S的右部都已分析完毕，则句柄已形成，可以进行归约。

## 2. 构造识别活前缀的NFA

把文法的所有产生式的项目都列出，并使每个项目都作为NFA的一个状态。

$$
G ^ { \prime }
$$

$$
S ^ { \prime } {  } E
$$

$$
E {  } a A | b B
$$

$$
A \to c A | d
$$

$$
B {  } c B | d
$$

该文法的项目有   
1. $S ^ { \prime }  \cdot E$ 10. $A  d \cdot$   
2. $S ^ { \prime } {  } E ^ { \prime }$ 11. $E \mathrm {  } \cdot \delta B$   
3. $E {  } \bullet a A$ 12. E→b· B   
4. $E {  } \alpha \cdot A$ 13. E→bB·   
5. $E {  } a A ^ { \mathrm { ~ o ~ } }$ 14. B→ · cB   
6. $A  \cdot { } c A$ 15. B→c· B   
7. $A  c \cdot A$ 16. $\cal B \to c \cal B \ \cdot$   
8. $A  c A \cdot$ 17. B→ · d   
9. $A  \cdot d$ 18. $B  d \cdot$

由于 $S ^ { \prime }$ 仅在第一个产生式的左部出现，因此规定项目1为初态，其余每个状态都为活前缀的识别态，圆点在最后的项目为句柄识别态，第一个产生式的句柄识别态为句子识别态。状态之间的转换关系确定方法如下：

若i项目为： $X {  } X _ { 1 } X _ { 2 } { \cdots } X _ { i - 1 } \bullet X _ { i } { \cdots } X _ { n }$

j项目为： $X {  } X _ { 1 } X _ { 2 } { \cdots } X _ { i - 1 } X _ { i } \ { \bullet } \ X _ { i + 1 } { \cdots } X _ { n }$

i项目和 $j$ 项目出于同一个产生式，对应于NFA为状态j的圆点只落后于状态i的圆点一个符号的位置，那么从状态i到状态j连一条标记为 $X _ { i }$ 的箭弧。如果 $X _ { i }$ 为非终结符，则也会有以它为左部的有关项目及其相应的状态。例如，有项目形如

$$
\begin{array} { c c c } { { i } } & { { } } & { { X  \gamma \bullet A \delta } } \\ { { k } } & { { } } & { { A  \bullet \beta } } \end{array}
$$

则从状态i画标记为ε的箭弧到状态k，对于A的所有产生式圆点在最左边的状态都连一条从i状态到该状态的箭弧，箭弧上标记为ε。

按上面的规则，可对文法G′的所有项目对应的状态构造出识别活前缀的有限自动机 $G ^ { \prime }$ NFA，如图6.7所示。图中双圈表示句柄识别态，双圈外有\*号者为句子“接受”态。

也可以根据圆点所在的位置和圆点后是终结符还是非终结符把项目分为以下几种：

（1）移进项目，形如 $A \to _ { \alpha } \cdot \alpha \beta$ ，其中 $\alpha , \beta \in V ^ { \ast } , \alpha \in V _ { \mathrm { ~ T ~ } }$ ，即圆点后面为终结符的项目为移进项目，对应状态为移进状态。分析时把a移进符号栈。

（2）待约项目，形如 $A \to _ { \alpha } \cdot \ B \beta$ ，其中 $\alpha , \beta \in V ^ { \star } \ , B \in V _ { \mathrm { ~ N ~ } }$ ，即圆点后面为非终结符的项目称待约项目，它表明所对应的状态等待着分析完非终结符B所能推出的串归约成B，才能继续分析A的右部。

（3）归约项目，形如 $A \to \alpha \ \cdot$ ,其中 $\alpha \in V ^ { \ast }$ ，即圆点在最右端的项目，称归约项目，它表明一个产生式的右部已分析完，句柄已形成，可以归约。

（4）接受项目，形如 $S ^ { \prime } {  } \alpha ^ { \mathbf { \alpha } }$ ,其中 $\alpha \in V ^ { + } , S ^ { \prime } \to \alpha$ 为拓广文法， $S ^ { \prime }$ 为左部的产生式只有一个，因而它是归约项目的特殊情况，对应状态称为接受状态。规定 $S ^ { \prime } \to \bullet \ q$ 为初态。实际上接受项目中的α为文法的开始符号。

对于图6.7所示的识别活前缀的NFA，可以利用第3章讲过的子集法将其确定化。对确定化后的DFA，如果把每个子集中所含状态集对应的项目写在新的状态中，结果如图6.8所示。

![](images/64b6700da98e21a87da9e4f906e6d73982b0dd86b79b84aef5ed83cb8ec64e3c.jpg)  
图6.7 识别活前缀的NFA

## 3. LR(0)项目集规范族的构造

构成识别一个文法活前缀的DFA项目集(状态)的全体称为这个文法的LR(0)项目集规范族；然而，构造识别活前缀的DFA若按上面的介绍的方法，列出拓广文法的所有项目，按规定原则构造其NFA(见图6.7)，然后再确定化为DFA(见图6.8)，这样做确定化的工作量较大。分析图6.8中每个状态中项目集的构成，不难发现如下规律。

若状态中包含形如 $A  \alpha \cdot B \beta$ 的项目，则形如 $B  \cdot \gamma$ 的项目也在此状态内。例如，0状态中的项目集为

![](images/e03d95cbf9dc67cf25d4c10be21f3bbdaf583e0a6492f53e606b3b3582982bd9.jpg)  
图 6.8 识别活前缀的 DFA

$$
\{ S ^ { \prime }  \bullet , E , E  \bullet a A , E  \bullet b B \}
$$

回顾由 NFA确定化到DFA时， $E  \bullet a A$ 和 $E  \cdot \ b B$ 正是属于 $S ^ { \prime }  \cdot E$ 所在的项目集中。因而，可以用闭包函数(CLOSURE)来求DFA一个状态的项目集。

若文法G已拓广为 $G ^ { \prime }$ ，而S为文法G的开始符号，拓广后增加产生式 $S ^ { \prime } {  } S$ 。如果I是文法 $G ^ { \prime }$ 的一个项目集，定义和构造I的闭包CLOSURE(I)的步骤如下：

(1)I的项目均在CLOSURE(I)中。

(2) 若 $A \to _ { \alpha } \cdot B \beta$ 属于CLOSURE(I)，则每一形如 $B {  } \cdot \gamma$ 的项目也属于CLOSURE(I)。

(3)重复(2)直到不出现新的项目为止，即CLOSURE(I)不再扩大。

由此，可以很容易构造出初态的闭包，即 $S ^ { \prime } \to \bullet S$ 属于I，再按上述3步求其闭包。

有了初态的项目集，其他状态的项目集如何求出？回顾在构造识别活前缀的NFA时除了箭弧上标记为ε的外，其两个相邻状态对应的项目出自同一个产生式，只是圆点的位置相差1。

箭弧上的标记为前一个状态和后一个状态对应项目圆点间的符号，而识别活前缀的DFA的每个状态是一个项目集，项目集中的每个项目都不相同，每个项目圆点后的符号不一定相同，因而对每个项目圆点移动一个位置后，箭弧上的标记也不会完全相同，这样，对于不同的标记将转向不同的状态。例如，初态 $\{ S ^ { \prime }  \bullet , E  \bullet \ a A , E  \bullet \ b B \}$ ，对第一个项目，圆点右移一个位置后变为 $S ^ { \prime } {  } E ^ { \mathrm { ~ . ~ } }$ ，箭弧标记应为 $E ;$ 对第二个项目 $E ^ {  } \cdot a A$ ，圆点右移一个位置后变为 $E {  } a \cdot A$ ，箭弧标记为 $\alpha _ { i }$ 同样第三个项目圆点右移一个位置后变为 $E {  } b \cdot B$ 箭弧标记为 $b _ { \circ }$ 显然，初态发出了3个不同标记的箭弧，因而转向3个不同的状态，也就由初态派生出3个新的状态，对于每个新的状态又可以利用前面的方法，若圆点后为非终结符，则可对其求闭包，得到该状态的项目集。圆点后面为终结符或在一个产生式的最后，则不会再增加新的项目。例中新状态的项目 $E {  } a \cdot A$ ，求其闭包可得到项目集为 $\{ E {  } a \ { \cdot } \ A$ $A  \bullet \ c A , A  \bullet \ d \}$ 。同样，另一新状态的项目 $E {  } b \cdot B$ ，求其闭包得到项目集为 $\{ E {  } b ~ \cdot ~ B$ $\boldsymbol { B }  \bullet \ c \boldsymbol { B } , \boldsymbol { B }  \bullet \ d \}$ 。对于新状态仅含项目 $S ^ { \prime } {  } E$ ·的则不会再增加新的项目。这样，由初态出发，对其项目集的每个项目的圆点向右移动一个位置，用箭弧转向不同的新状态，箭弧上用移动圆点经过的符号标记。新状态的初始项目(即圆点移动后的项目)称为核。例中$E {  } a \cdot A$ 和 $E  b \cdot B$ 都为核，对核求闭包就为新状态的项目集。为把这个过程写成一般的形式，定义转换函数GO(I,X)如下：

$$
\operatorname { G O } ( I , X ) { = } \operatorname { C L O S U R E } ( J )
$$

其中，I为包含某一项目集的状态。

X为一文法符号， $X \in { V _ { \mathrm { v } } } \cup V _ { \mathrm { T } }$

J={任何形如 $A \to _ { \alpha } X ~ \cdot ~ \beta$ 的项目 $| A \to \alpha \cdot X \beta$ 属于I}

这也表明，若状态Ⅰ识别活前缀γ，则状态J识别活前缀γX。圆点不在产生式右部最左边的项目称为核，但开始状态拓广文法的第一个项目 $S ^ { \prime } \to \cdot S$ 除外。因此用GO(I,X)转换函数得到的J为转向后状态所含项目集的核。核可能是由一个或若干个项目组成。因此，可以使用闭包函数CLOSURE和转向函数GO(I,X)构造文法 $G ^ { \prime }$ 的LR(0)项目集规范族，步骤如下：

(1) 置项目 $S ^ { \prime }  \cdot S$ 为初态集的核，然后对核求闭包，CLOSURE $\{ S ^ { \prime } \mathrm {  } \cdot S \} )$ ，得到初态的项目集。

（2）对初态集或其他所构造的项目集，应用转换函数 $\operatorname { G O } ( I , X ) = \operatorname { C L O S U R E } ( J )$ 求出新状态J的项目集。

(3)重复(2)直到不出现新的项目集为止。

最后还需要说明的是，由于任何一个高级语言相应文法的产生式是有限的，每个产生式右部的文法符号个数是有限的，因此每个产生式可列出的项目也为有限的，由有限的项目组成的子集(即项目集)作为DFA的状态也是有限的，所以不论用哪种方法构造识别活前缀的有限自动机，必定会在有穷的步骤内结束。

以上介绍了构造识别文法活前缀DFA的3种方法，读者可对它们进行比较分析以加深理解。这3种方法可以粗略地概括如下。

第1种方法是根据形式定义求出活前缀的正规表达式，然后由此正规表达式构造NFA，再确定化为DFA。

第2种方法是求出文法的所有项目，按一定规则构造识别活前缀的NFA，再确定化为DFA。

第3种方法是把拓广文法的第一个项目 $\{ S ^ { \prime }  \bullet S \}$ 作为初态集的核，通过求核的闭包和转换函数，求出LR(0)项目集规范族，再由转换函数建立状态之间的连接关系，得到识别活前缀的 DFA。

显然第1种方法从理论上讲比较严格确切，第2、3种方法较为直观，从直观上的分析与理论上实现的结果吻合。3种做法虽然不同，但出发点都是把LR分析方法的归约过程看成是识别文法规范句型活前缀的过程，因为只要分析到的当前状态是活前缀的识别态，则说明已分析过的部分是该文法的某规范句型的一部分，也就说明了已分析过的部分是正确的。

进一步分析所构造的LR(0)项目集规范族的项目，可分为如下4种：

（1）移进项目。圆点后为终结符的项目，形如 $A  \alpha \cdot \alpha \beta$ ,其中 $\alpha , \beta \in V ^ { \ast } , \alpha \in V _ { \mathrm { { T } } }$ ,相应状态为移进状态。

(2)归约项目。圆点在产生式右部最后的项目，形如 $A \to \beta \ \cdot$ ,其中 $\beta \in V ^ { * }$ ,对于 $\beta { = } \varepsilon$ 的项目为 $A \to \bullet$ (对应产生式为 $A  _ { \varepsilon } )$ ，相应状态为归约状态。

（3）待约项目。圆点后为非终结符的项目，形如 $A \to _ { \alpha } \cdot { \cal B } \beta$ ，其中α $\ B \in V ^ { \ast } \ , B \in V _ { \mathrm { ~ N ~ } }$ ,这表明用产生式A的右部归约时，首先要将B的产生式右部归约为B，对A的右部才能继续进行分析。也就是期待着继续分析过程中首先能进行归约得到 $B _ { \cdot }$

（4）接受项目。当归约项目为 $S ^ { \prime } {  } S$ ·时，则表明已分析成功，即输入串为该文法的句子，相应状态为接受状态。

一个项目集中可能包含以上4种不同的项目，但是一个项目集中不能有下列情况存在：

（1）移进和归约项目同时存在，形如

$$
\begin{array} { c } { { A {  } \alpha \bullet \alpha \beta } } \\ { { { } } } \\ { { B {  } \gamma \bullet } } \end{array}
$$

这时如果面临输入符号为a,不能确定移进a还是把γ归约为B，因为LR(0)分析是不向前看符号，所以对归约的项目不管当前符号是什么都应归约。对于同时存在移进和归约项目的称移进-归约冲突。

（2）归约和归约项目同时存在，形如

$$
\begin{array} { c } { { A {  } \beta ~ { } } } \\ { { { } } } \\ { { B {  } \gamma ~ { } } } \end{array}
$$

这时不管面临什么输入符号，都不能确定归约为A还是归约为B，对同时存在两个以上归约项目的状态称归约-归约冲突。

对一个文法的LR(0)项目集规范族不存在移进-归约冲突或归约-归约冲突时，称这个文法为LR(0)文法。

## 4. LR(0)分析表的构造

LR(0)分析表是LR(0)分析器的重要组成部分，它是总控程序分析动作的依据。对于不同的文法，LR(0)分析表不同，它可以用一个二维数组表示，行标为状态号，列标为文法符号和#号。分析表的内容可由两部分组成，一部分为动作(ACTION)表，它表示当前状态下面临输入符号时应做的动作是移进、归约、接受还是出错，动作表的列标只包含终结符和#；另一部分为转换表(GOTO)，它表示在当前状态下面临文法符号时应转向的下一个状态，相当于识别活前缀的有限自动机DFA的状态转换矩阵。因此构造一个文法的LR(0)分析表时，首先构造其识别活前缀的DFA，这样可以很方便地利用DFA的项目集和状态转换函数构造它的LR(0)分析表。在实际应用中为了节省存储空间，通常把关于终结符部分的GOTO表和ACTION表重叠，也就是把当前状态下面临终结符应做的移进-归约动作和转向动作用同一数组元素表示。

LR(0)分析表的构造算法如下：

假设已构造出LR(0)项目集规范族为

$$
C = \{ I _ { 0 } , I _ { 1 } , \cdots , I _ { n } \}
$$

其中 $I _ { k }$ 为项目集的名字，k为状态名，令包含 $S ^ { \prime } \to \cdot S$ 项目的集合 $I _ { \textit { k } }$ 的下标k为分析器的初始状态。那么分析表的ACTION表和GOTO表的构造步骤如下：

(1) 若项目 $A  \alpha \cdot \alpha \beta$ 属于 $I _ { \ k }$ 且转换函数 $G \mathrm { O } \left( { { I _ { k } } , \alpha } \right) = { I _ { j } }$ ，当a为终结符时则置$\operatorname { A C T I O N } [ k , \alpha ]$ 为 $S _ { j }$ ，其动作含义为将终结符a移进符号栈，状态j进入状态栈(相当于在状态 k 时遇a转向状态j)。

(2) 若项目 $A \to \alpha ^ { \textit { - } }$ 属于 $I _ { k }$ ，则对任何终结符 $a$ 和#号置 ACTION[k,a]和 ACTI-

ON[k，#]为rj，j为在文法G′中某产生式A→α的序号。rj动作的含义是把当前文法符号 $r _ { j } , { j }$ $G ^ { \prime }$ $\boldsymbol { r } _ { j }$ 栈顶的符号串α归约为A，并将栈指针从栈顶向下移动 $\mid \alpha \mid$ 的长度，符号栈中弹出 $\mid \alpha \mid$ 个符号，非终结符A变为当前面临的符号。

(3) 若 $\operatorname { G O } ( I _ { k } , A ) = I _ { j }$ ,则置GOTO[k，A]为“j”，其中A为非终结符，表示当前状态为“k”时，遇文法符号A时状态应转向j，因此A移入文法符号栈，j移入状态栈。

(4) 若项目 $S ^ { \prime } {  } S \cdot$ 属于 $I _ { k }$ ，则置 ACTION[k，#]为 acc，表示接受。

(5）凡不能用上述方法填入的分析表的元素，均应填上报错标志。为了表的清晰，本书在表中用空白表示错误标志。

根据这种方法构造的LR(0)分析表不含多重定义时称为LR(0)分析表，能用LR(0)分析表的分析器称为LR(0)分析器，能构造LR(0)分析表的文法称为LR(0)文法。

若对文法 $G ^ { \prime }$ 的产生式编号如下：

(0) $S ^ { \prime } {  } E$ (4) $A  d$ (1) $E {  } a A$ (5) $B {  } c B$ (2) $E {  } b B$ (6) $B {  } d$ (3) $A {  } c A$

那么按上述算法构造的这个文法的LR(0)分析表如表6.3所示。

表6.3LR(0)分析表
<table><tr><td rowspan="2">状态</td><td colspan="5">ACTION</td><td colspan="3">GOTO</td></tr><tr><td> $a$ </td><td> $b$ </td><td>C</td><td> $d$ </td><td>#</td><td>E</td><td>A</td><td>B</td></tr><tr><td>0 1</td><td> $S _ { 2 }$ </td><td> $S _ { 3 }$ </td><td></td><td></td><td> $a c c$ </td><td>1</td><td></td><td></td></tr><tr><td>2 3</td><td></td><td></td><td> $S _ { 4 }$   $S _ { 5 }$ </td><td> $S _ { 1 0 }$   $S _ { 1 1 }$ </td><td></td><td></td><td>6</td><td>7</td></tr><tr><td>4</td><td></td><td></td><td> $S _ { 4 }$ </td><td> $S _ { 1 0 }$ </td><td></td><td></td><td>8</td><td></td></tr><tr><td>5</td><td></td><td></td><td> $S _ { 5 }$ </td><td> $S _ { 1 1 }$ </td><td></td><td></td><td></td><td>9</td></tr><tr><td>6</td><td> $r _ { 1 }$ </td><td> $r _ { 1 }$ </td><td> $r _ { 1 }$ </td><td> $r _ { 1 }$ </td><td> $r _ { 1 }$ </td><td></td><td></td><td></td></tr><tr><td>7</td><td> $r _ { 2 }$ </td><td> $r _ { 2 }$ </td><td> $r _ { 2 }$ </td><td> $r _ { 2 }$ </td><td> $r _ { 2 }$ </td><td></td><td></td><td></td></tr><tr><td>8</td><td> $r _ { 3 }$ </td><td> $r _ { 3 }$ </td><td> $r _ { 3 }$ </td><td> $r _ { 3 }$ </td><td> $r _ { 3 }$ </td><td></td><td></td><td></td></tr><tr><td>9</td><td> $r _ { 5 }$ </td><td> $r _ { 5 }$ </td><td> $r _ { 5 }$ </td><td> $r _ { 5 }$ </td><td> $r _ { 5 }$ </td><td></td><td></td><td></td></tr><tr><td>10</td><td> $r _ { 4 }$ </td><td> $r _ { 4 }$ </td><td> $r _ { 4 }$ </td><td> $r _ { 4 }$ </td><td> $r _ { 4 }$ </td><td></td><td></td><td></td></tr><tr><td>11</td><td> $r _ { 6 }$ </td><td> $r _ { 6 }$ </td><td> $r _ { 6 }$ </td><td> $r _ { 6 }$ </td><td> $r _ { 6 }$ </td><td></td><td></td><td></td></tr></table>

## 5. LR(0)分析器的工作过程

对一个文法构造了它的LR(0)分析表后，就可以在LR分析器的总控程序(驱动程序)控制下对输入串进行分析，即根据输入串的当前符号和分析栈的栈顶状态查找分析表应采取的动作，对状态栈和符号栈进行相应的操作，即移进、归约、接受或报错。具体说明如下：

(1) 若 $\mathrm { A C T I O N } [ S , \alpha ] = S _ { j }$ ，a为终结符，则把a移入符号栈，j移入状态栈。

(2) 若 $\mathrm { A C T I O N } [ S , \alpha ] = r _ { j }$ ，a为终结符或#号，则用第j个产生式归约，并将两个栈的指针减去k，其中k为第j个产生式右部的符号串长度，这时当前面临符号为第j个产生式

左部的非终结符，不妨设为A，归约后栈顶状态设为n，则再进行GOTO[n，A]。

(3) 若 $\mathrm { A C T I O N } [ S , a ] = \operatorname { a c c } , a$ 应为#号，则为接受，表示分析成功。

(4) 若 $G \mathrm { O T O } [ S , A ] = j , A$ 为非终结符，表明前一动作是用关于A的产生式归约的，当前面临的非终结符A应移入符号栈，j移入状态栈。对于终结符的GOTO[S，a]已和ACTION[S,a]重合。

(5）若ACTION[S,a]为空白，则转向出错处理。

现在用表6.3的LR(0)分析表给出对输入串bccd#的LR(0)分析，其状态栈、符号栈及输入串的变化过程如表6.4所示。

表 6.4 对输入串 bccd #的 LR(0)分析过程
<table><tr><td>步骤</td><td>状态栈</td><td>符号栈</td><td>输入串</td><td>ACTION</td><td>GOTO</td></tr><tr><td>(1)</td><td>0</td><td>#</td><td>bccd #</td><td> $S _ { 3 }$ </td><td></td></tr><tr><td>(2)</td><td>03</td><td>#b</td><td> $c c d \#$ </td><td> $S _ { 5 }$ </td><td></td></tr><tr><td>(3)</td><td>035</td><td>#bc</td><td>cd #</td><td> $S _ { 5 }$ </td><td></td></tr><tr><td>(4)</td><td>0355</td><td>#bcc</td><td>d#</td><td> $S _ { 1 1 }$ </td><td></td></tr><tr><td>(5)</td><td>0355(11)</td><td>#bccd</td><td>#</td><td> $r _ { 6 }$ </td><td>9</td></tr><tr><td>(6)</td><td>03559</td><td>#bccB</td><td>#</td><td> $r _ { 5 }$ </td><td>9</td></tr><tr><td>(7)</td><td>0359</td><td>#bcB</td><td>#</td><td> $r _ { 5 }$ </td><td>7</td></tr><tr><td>(8)</td><td>037</td><td>#bB</td><td>#</td><td> $r _ { 2 }$ </td><td>1</td></tr><tr><td>(9)</td><td>01</td><td>#E</td><td>#</td><td>acc</td><td></td></tr></table>

## 6.3 SLR(1)分析

由于大多数实用的程序设计语言的文法不能满足LR(0)文法的条件，本节介绍一种SLR(1)文法，其思想是基于容许LR(0)规范族中有冲突的项目集(状态)，用向前查看一个符号的办法来进行处理，以解决冲突。因为只对有冲突的状态才向前查看一个符号，以确定做哪种动作，所以称这种分析方法为简单的LR(1)分析法，用SLR(1)表示。能用这种分析法分析的文法就是SLR(1)文法。下面作具体介绍。

先看文法例：

<实型变量说明>→real<标识符表>

<标识符表 $>  <$ 标识符表>,i

<标识符表>→i

将该文法缩写并拓广后得文法 $G ^ { \prime }$ 如下：

(0) $S ^ { \prime } {  } S$

(1) $S {  } r D$

(2) $D \to D , i$

(3) $D \to i$

首先构造该文法的LR(0)项目集规范族，如表6.5所示。

表6.5 G'的LR(0)项目集规范族
<table><tr><td rowspan=1 colspan=1>状态</td><td rowspan=1 colspan=1>核集合</td><td rowspan=1 colspan=1>闭包增加项目</td><td rowspan=1 colspan=1>项目集</td></tr><tr><td rowspan=1 colspan=1> $I _ { 0 }$ </td><td rowspan=1 colspan=1> $S ^ { \prime } \to \cdot S$ </td><td rowspan=1 colspan=1> $S \to \cdot \ D$ </td><td rowspan=1 colspan=1> $\overline { { S ^ { \prime } \to \cdot \cal S } }$ S→ · rD</td></tr><tr><td rowspan=1 colspan=1> $I _ { 1 }$ </td><td rowspan=1 colspan=1> $S ^ { \prime } {  } S \cdot$ </td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>S′→S.</td></tr><tr><td rowspan=1 colspan=1> $I _ { 2 }$ </td><td rowspan=1 colspan=1> $S {  } r { \cdot } D$ </td><td rowspan=1 colspan=1>D→ · D, iD→ · i</td><td rowspan=1 colspan=1>S→r · DD→ · D, iD→ · i</td></tr><tr><td rowspan=1 colspan=1> $I _ { 3 }$ </td><td rowspan=1 colspan=1> $S \to r D \ \cdot$  $D \to D \cdot \mathbf { \mu } , i$ </td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>S→rD.D→D· ,i</td></tr><tr><td rowspan=1 colspan=1> $I _ { 4 }$ </td><td rowspan=1 colspan=1>D→i.</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>D→i.</td></tr><tr><td rowspan=1 colspan=1> $I _ { 5 }$ </td><td rowspan=1 colspan=1> $D \to D , \cdot \textit { i }$ </td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1> $D \to D , \cdot \textit { i }$ </td></tr><tr><td rowspan=1 colspan=1> $I _ { 6 }$ </td><td rowspan=1 colspan=1> $D \to D , i \ \cdot$ </td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>D→D,i.</td></tr></table>

再用GO函数构造出识别活前缀的DFA，如图6.9所示。

![](images/3615fca600aa02fd785bba39ea3fa1060855ee4e3753338782b02f1e9931c2bd.jpg)  
图 6.9 识别文法 $G ^ { \prime }$ 活前缀的 DFA

分析每个状态包含的项目集，不难发现在状态 $I _ { 3 }$ 中含有以下项目：

S→rD·为归约项目。

D→D· ,i 为移进项目。

也就是按S→rD·项目的动作认为用S→rD产生式进行归约的句柄已形成，不管当前的输入符号是什么，都应把rD归约成S。但是按D→D·，i项目，当面临输入符为“，”时，应将“，”移入符号栈，状态转向 $I _ { 5 }$ 。显然该文法不是LR(0)文法，也可在构造它的LR(0)分析表时发现这个问题，如表6.6所示。

表 6.6 实数说明文法的 LR(0)分析表
<table><tr><td rowspan="2">状态</td><td colspan="4">ACTION</td><td colspan="2">GOTO</td></tr><tr><td> $r$ </td><td>6</td><td>i</td><td>#</td><td>S</td><td>D</td></tr><tr><td>0</td><td> $S _ { 2 }$ </td><td></td><td></td><td></td><td>1</td><td></td></tr><tr><td>1</td><td></td><td></td><td></td><td> $a c c$ </td><td></td><td></td></tr><tr><td>2</td><td></td><td></td><td> $S _ { 4 }$ </td><td></td><td></td><td>3</td></tr><tr><td>3</td><td> $r _ { 1 }$ </td><td> $r _ { 1 } , S _ { 5 }$ </td><td> $r _ { 1 }$ </td><td> $r _ { 1 }$ </td><td></td><td></td></tr><tr><td>4</td><td> $r _ { 3 }$ </td><td> $r _ { 3 }$ </td><td> $r _ { 3 }$ </td><td> $r _ { 3 }$ </td><td></td><td></td></tr><tr><td>5 6</td><td> $r _ { 2 }$ </td><td> $r _ { 2 }$ </td><td> $S _ { 6 }$   $r _ { 2 }$ </td><td> $r _ { 2 }$ </td><td></td><td></td></tr></table>

在这种情况下，只需要考查当用句柄rD归约成S时，S的后跟符号集合中不包含当前所有移进项目的移进符号的集合时，则这种移进-归约冲突便可解决，例中S的后跟符集合为{#}，移进项目只有一个“，”，因而移进项目中期待移进的符号集合为{，}，这样可以在状态 $I _ { 3 }$ 中当遇“，”时做移进动作，当遇#号时做归约动作。上述LR(0)分析表做局部改动后不再存在冲突时称为SLR(1)文法，其分析表如表6.7所示。

表6.7实数说明文法的SLR(1)分析表
<table><tr><td rowspan="2">状态</td><td colspan="4">ACTION</td><td colspan="2">GOTO</td></tr><tr><td> $r$ </td><td>。</td><td>i</td><td>#</td><td>S</td><td>D</td></tr><tr><td>0</td><td> $S _ { 2 }$ </td><td></td><td></td><td></td><td>1</td><td></td></tr><tr><td>1</td><td></td><td></td><td></td><td> $a c c$ </td><td></td><td></td></tr><tr><td>2</td><td></td><td></td><td> $S _ { 4 }$ </td><td></td><td></td><td>3</td></tr><tr><td>3</td><td></td><td> $S _ { 5 }$ </td><td></td><td> $r _ { 1 }$ </td><td></td><td></td></tr><tr><td>4</td><td> $r _ { 3 }$ </td><td> $r _ { 3 }$ </td><td> $r _ { 3 }$ </td><td> $r _ { 3 }$ </td><td></td><td></td></tr><tr><td>5</td><td></td><td></td><td> $S _ { 6 }$ </td><td></td><td></td><td></td></tr><tr><td>6</td><td> $r _ { 2 }$ </td><td> $r _ { 2 }$ </td><td> $r _ { 2 }$ </td><td> $r _ { 2 }$ </td><td></td><td></td></tr></table>

假定一个LR(0)规范族中含有如下的项目集(状态)I:

$$
I = \{ X {  } _ { \alpha } \bullet b \beta , A {  } \gamma \bullet , B {  } \delta \bullet \}
$$

也就是在该项目集中含有移进-归约冲突和归约-归约冲突。其中 $\alpha , \beta , \gamma , \delta$ 为文法符号串，b为终结符。那么只要在所有含有A或B的句型中，直接跟在A或B后的可能终结符的集合即FOLLOW(A)和FOLLOW(B)互不相交，且都不包含b，也就是只要满足

$$
\mathrm { F O L L O W } ( A ) \bigcap \mathrm { F O L L O W } ( B ) = \emptyset
$$

$$
\mathrm { F O L L O W } ( A ) \bigcap \{ b \} = \emptyset
$$

$$
\mathrm { F O L L O W } ( B ) \cap \{ b \} = \emptyset
$$

那么，当在状态Ⅰ时，如果面临某输入符号为a，则动作可按以下规定决策：

(1) 若 $a = b$ ，则移进。

(2) 若 $a \in { \mathrm { F O L L O W } } ( A )$ ，则用产生式A→γ进行归约。

(3) 若 $\alpha { \in } \mathrm { F O L L O W } ( B )$ ，则用产生式B→δ进行归约。

（4）此外，报错。

通常LR(0)规范族的一个项目集I中可能含有多个移进项目和多个归约项目，可假设项目集I(状态)中有m个移进项目： $A _ { 1 } \to \alpha _ { 1 } \bullet a _ { 1 } \beta _ { 1 } , A _ { 2 } \to _ { \alpha _ { 2 } } \bullet a _ { 2 } \beta _ { 2 } , \cdots , A _ { m } \to _ { \alpha _ { m } } \bullet a _ { m } \beta _ { m }$ ;同时含有n个归约项目： $B _ { 1 } \to \gamma _ { 1 } ~ \bullet ~ , B _ { 2 } \to \gamma _ { 2 } ~ \bullet ~ , \cdots , B _ { n } \to \gamma _ { n } ~ \bullet ,$ ，只要集合 $\{ a _ { 1 } , a _ { 2 } , \cdots , a _ { m } \}$ 和$\mathrm { F O L L O W } ( B _ { 1 } ) , \mathrm { F O L L O W } ( B _ { 2 } ) , \cdots , \mathrm { F O L L O W } ( B _ { n } )$ 两两交集都为空，那么仍可用上述规则解决冲突，即考查当前输入符号以决定动作。

(1) 若 $a \in \{ a _ { 1 } , a _ { 2 } , \cdots , a _ { m } \}$ ，则移进。

(2) 若 $\alpha \in \mathrm { F O L L O W } ( B _ { i } ) , i = 1 , 2 , \cdots , n$ ,则用 $B _ { i } {  } \gamma _ { i }$ 进行归约。

（3）此外，报错。

如果对于一个文法的LR(0)项目集规范族的某些项目集或LR(0)分析表中所含有的动作冲突都能用上述方法解决，则称这个文法是SLR(1)文法，所构造的分析表为SLR(1)

分析表，使用SLR(1)分析表的分析器称为SLR(1)分析器。

例如，可以构造算术表达式文法的LR(0)项目集规范族，然后分析它是LR(0)文法还是SLR(1)文法，现将表达式文法G拓广如下：

(0) $S ^ { \prime } {  } E$

(1) $E {  } E { + } T$

(2) $E \to T$

(3) $T \to T \times F$

(4) $T \mathrm {  } F$

(5) $F {  } ( E )$

(6) $F {  } i$

该文法的LR(0)项目集规范族为

$$
\begin{array} { r l r } { \| _ { \mathrm { ~ L ~ P ~ } } \| _ { 2 } ^ { \infty } = - \frac { \mu } { \tau } \exp } & { \quad \mathrm { ~ L _ { 1 } ~ P - \mu ~ } } & \\ { \| _ { \mathrm { ~ L ~ P ~ } } \| _ { 2 } ^ { \infty } = \frac { \mu } { \tau } \exp } & { \quad \mathrm { ~ L _ { 1 } ~ P - \mu ~ } } & \\ { \| _ { \mathrm { ~ L ~ P ~ } } \| _ { 2 } ^ { \infty } = \frac { \mu } { \tau } \exp } & { \quad \mathrm { ~ L _ { 1 } ~ P ~ } } & \\ { \| _ { \mathrm { ~ L ~ P ~ } } \| _ { 2 } ^ { \infty } = \frac { \mu } { \tau } \exp } & { \quad \mathrm { ~ L _ { 1 } ~ P ~ } } & \\ { \| _ { \mathrm { ~ L ~ P ~ } } \| _ { 2 } ^ { \infty } = \frac { \mu } { \tau } \exp } & { \quad \mathrm { ~ L _ { 1 } ~ P ~ } } & \\ { \| _ { \mathrm { ~ L ~ P ~ } } \| _ { 2 } ^ { \infty } = \frac { \mu } { \tau } \exp } & { \quad \mathrm { ~ L _ { 1 } ~ P ~ } } & \\ { \| _ { \mathrm { ~ L ~ P ~ } } \| _ { 2 } ^ { \infty } = \frac { \mu } { \tau } \exp } & { \quad \mathrm { ~ L _ { 1 } ~ P ~ } } & \\ { \| _ { \mathrm { ~ L ~ P ~ } } \| _ { 2 } ^ { \infty } = \frac { \mu } { \tau } \exp } & { \quad \mathrm { ~ L _ { 1 } ~ P ~ } } & \\ { \| _ { \mathrm { ~ L ~ P ~ } } \| _ { 2 } ^ { \infty } = \frac { \mu } { \tau } \exp } & { \quad \mathrm { ~ L _ { 1 } ~ P ~ } } & \\ { \| _ { \mathrm { ~ L ~ P ~ } } \| _ { 2 } ^ { \infty } = \frac { \mu } { \tau } \exp } & { \quad \mathrm { ~ L _ { 1 } ~ P ~ } } & \\  \| _ { \mathrm { ~ L ~ P ~ } } \| _ { 2 } ^ { \infty } = \frac { \mu } { \tau } \ \end{array}
$$

与此相应的识别该文法活前缀的有限自动机如图6.10所示。

不难看出在 $I _ { 1 } , I _ { 2 } , I _ { 9 }$ 中存在移进-归约冲突，因而这个表达式文法不是LR(0)文法，也就不能构造LR(0)分析表，现在分别考查这3个项目集(状态)中的冲突是否能用SLR(1)方法解决。

在 $I _ { 1 }$ 中：

$$
S ^ { \prime } {  } E ^ { \mathbf { \prime } }
$$

$$
E {  } E \cdot + T
$$

由于 $\operatorname { F O L L O W } ( S ^ { \prime } ) = \{ \# \}$ ，而 $S ^ { \prime } {  } E$ ·是唯一的接受项目.所以当且仅当遇到句子的结束符#时才被接受。又因 $\{ \neq \} \cap \{ + \} = \emptyset$ ，因此 $I _ { 1 }$ 中的冲突可解决。

![](images/41946868b0bdd1b3506b2ad35685d8cb80e7433405d060361cc78b584b682649.jpg)  
图6.10 识别表达式文法活前缀的 DFA

在 $I _ { 2 }$ 中：

$$
\begin{array} { l } { E \to T \cdot } \\ { T \to T \cdot \ * _ { \mathbb { X } } F } \end{array}
$$

可计算非终结符E的FOLLOW集为

$$
\mathrm { F O L L O W } ( E ) = \{ + , ) , \# \}
$$

这样 $\mathrm { F O L L O W } ( E ) \bigcap \{ * \} = \{ + , ) , \# \} \bigcap \{ * \} = \emptyset$ ，因此当面临输入符为十、)或#时，则用产生式E→T进行归约；当面临输入符为\*时，则移进；其他情况则报错。

在 $I _ { 9 }$ 中：

$$
\begin{array} { l } { E \to E + T \ \cdot } \\ { T \to T \ \cdot \ \times \ F } \end{array}
$$

与 $I _ { 2 }$ 中的情况类似，因归约项目的左部非终结符E的后跟符集合FOLLOW(E)={+，)，#}与移进项目圆点后终结符不相交，所以冲突可以用SLR(1)方法解决，与 $I _ { 2 }$ 不同的只是在面临输入符为+、)或#时用产生式E→E+T归约。

由以上考查可知，该文法在 $I _ { 1 } , I _ { 2 } , I _ { 9 }$ 三个项目集(状态)中存在的移进-归约冲突都可以用SLR(1)方法解决，因此该文法是 SLR(1)文法。可构造其相应的SLR(1)分析表。

SLR(1)分析表的构造与LR(0)分析表的构造类似，仅在含有冲突的项目集中分别进行处理。但进一步分析可以发现如下事实，例如在状态 $I _ { 3 }$ 中，只有一个归约项目T→F·，按照SLR(1)方法，在该项目中没有冲突，所以可以保持原来LR(0)的处理方法，不论当前面临的输入符号是什么，都将用产生式T→F进行归约。显然T的后跟符没有(符号，如果当前面临输入符是(，也进行归约显然是错误的，然而这是输入串不合法的错误，在此照常归约虽不报错，但此处的错误在作进一步LR(0)分析时仍能被发现，只不过是把错误的发现推迟到下一步而已。如果对所有归约项目都采取SLR(1)的处理思想，即对所有非终结符都求出其FOLLOW集合，这样仅当归约项目在面临的输入符号包含在该归约项目左部非终结符的FOLLOW集合中时，才采取用该产生式归约的动作，则这种处理就可以通过某些不该归约的动作而提前发现错误。对于这样构造的SLR(1)分析表，不妨称它为改进的SLR(1)分析表。改进的 SLR(1)分析表的构造方法如下：

假设已构造出文法的LR(0)项目集规范族和计算出所有非终结符的FOLLOW集合。

项目集规范族为 $C = \{ I _ { 0 } , I _ { 1 } , \cdots , I _ { n } \}$ ,其中 $I _ { k }$ 为项目集的名字，k为状态名，令包含 $S ^ { \prime } \to \cdot S$ 项目的集合 $I _ { k }$ 的下标k为分析器的初始状态，求出所有非终结符的FOLLOW集。

改进的SLR(1)分析表的动作(ACTION)表和状态转换(GOTO)表的构造步骤如下：

(1) 若项目 $A \to \alpha \cdot a \beta$ 属于 $I _ { \textit { k } }$ ，且转换函数 $\mathrm { G O } \left( { { I } _ { k } } \mathrm { ~ , ~ } \alpha \right) = { { I } _ { j } }$ ，当a为终结符时，则置$\operatorname { A C T I O N } [ k , \alpha ]$ 为 ${ \mathrm { S } } _ { j }$ 。

(2) 若项目 $A \to \alpha \ \cdot$ 属于 $I _ { k }$ ，则对a为任何终结符或#，且满足 $\alpha \in \operatorname { F O L L O W } ( A )$ 时，置$\mathrm { A C T I O N } [ k , a ] = r _ { j } , j$ 为产生式 $A \to \alpha$ 在文法 $G ^ { \prime }$ 中的编号。

(3) 若 $\operatorname { G O } ( I _ { k } , A ) = I _ { j }$ ,则置 GOTO[k， $A \beth = j$ ，其中A为非终结符，j为某一状态号。

(4) 若项目 $S ^ { \prime } {  } S \cdot$ 属于 $I _ { k }$ ，则置ACTION[k，#]=acc，表示接受。

（5）凡不能用上述方法填入的分析表的元素，均应填上报错标志，在本书中用空白表示。

用上述步骤对算术表达式文法构造改进的SLR(1)分析表如表6.8所示。

表 6.8 改进的 SLR(1)分析表
<table><tr><td rowspan=2 colspan=1>状态</td><td rowspan=1 colspan=6>ACTION</td><td rowspan=1 colspan=3>GOTO</td></tr><tr><td rowspan=1 colspan=1>i</td><td rowspan=1 colspan=1>十</td><td rowspan=1 colspan=1> $^ { \ast }$ </td><td rowspan=1 colspan=1>(</td><td rowspan=1 colspan=1>へ</td><td rowspan=1 colspan=1>#</td><td rowspan=1 colspan=1>E</td><td rowspan=1 colspan=1> $T$ </td><td rowspan=1 colspan=1>F</td></tr><tr><td rowspan=6 colspan=1>01234567891011</td><td rowspan=1 colspan=1> $S _ { 5 }$ </td><td rowspan=1 colspan=1> $S _ { 6 }$  $r _ { 2 }$  $r _ { 4 }$ </td><td rowspan=1 colspan=1> $S _ { 7 }$  $r _ { 4 }$ </td><td rowspan=1 colspan=1> $S _ { 4 }$ </td><td rowspan=6 colspan=1> $r _ { 2 }$  $r _ { 4 }$  $r _ { 6 }$  $S _ { 1 1 }$  $r _ { 1 }$  $r _ { 3 }$  $r _ { 5 }$ </td><td rowspan=6 colspan=1> $a c c$  $r _ { 2 }$  $r _ { 4 }$  $r _ { 6 }$  $r _ { 1 }$  $r _ { 3 }$  $r _ { 5 }$ </td><td rowspan=6 colspan=1>18</td><td rowspan=6 colspan=1>229</td><td rowspan=6 colspan=1>33310</td></tr><tr><td rowspan=1 colspan=1> $S _ { 5 }$  $S _ { 5 }$ </td><td rowspan=3 colspan=1> $r _ { 6 }$  $S _ { 6 }$ </td><td rowspan=5 colspan=1> $r _ { 6 }$  $S _ { 7 }$  $r _ { 3 }$  $r _ { 5 }$ </td><td rowspan=5 colspan=1> $S _ { 4 }$  $S _ { 4 }$  $S _ { 4 }$ </td></tr><tr><td rowspan=1 colspan=1> $S _ { 5 }$ </td></tr><tr><td rowspan=3 colspan=1></td></tr><tr><td rowspan=1 colspan=1> $r _ { 1 }$ </td></tr><tr><td rowspan=1 colspan=1> $r _ { 3 }$  $r _ { 5 }$ </td></tr></table>

SLR(1)分析器用表6.8的 SLR(1)分析表对符号串 $i + i \ast i$ #进行分析时栈的变化过程，如表6.9所示。

表 6.9 对输入串 i+i\* i #的 SLR(1)分析过程
<table><tr><td>步骤</td><td>状态栈</td><td>符号栈</td><td>输入串</td><td>ACTION</td><td>GOTO</td></tr><tr><td>(1)</td><td>0</td><td>#</td><td> $i + i \ast i \neq$ </td><td> $S _ { 5 }$ </td><td></td></tr><tr><td>(2)</td><td>05</td><td>#i</td><td> $+ i * i \neq$ </td><td> $r _ { 6 }$ </td><td>3</td></tr><tr><td>(3)</td><td>03</td><td>#F</td><td> $+ i * i \neq$ </td><td> $r _ { 4 }$ </td><td>2</td></tr><tr><td>(4)</td><td>02</td><td>#T</td><td> $+ i * i \neq$ </td><td> $r _ { 2 }$ </td><td>1</td></tr><tr><td>(5)</td><td>01</td><td>#E</td><td>+i*i#</td><td> $S _ { 6 }$ </td><td></td></tr><tr><td>(6)</td><td>016</td><td>#E+</td><td>i*i#</td><td> $S _ { 5 }$ </td><td></td></tr><tr><td>(7)</td><td>0165</td><td>#E+i</td><td>*i#</td><td> $r _ { 6 }$ </td><td>3</td></tr><tr><td>(8)</td><td>0163</td><td>#E+F</td><td>*i#</td><td> $r _ { 4 }$ </td><td>9</td></tr><tr><td>(9)</td><td>0169</td><td>#E+T</td><td>*i#</td><td> $S _ { 7 }$ </td><td></td></tr><tr><td>(10)</td><td>01697</td><td>#E+T*</td><td>i#</td><td> $S _ { 5 }$ </td><td></td></tr><tr><td>(11)</td><td>016975</td><td>#E+T*i</td><td>#</td><td> $r _ { 6 }$ </td><td>10</td></tr><tr><td>(12)</td><td>01697(10)</td><td>#E+T*F</td><td>#</td><td> $r _ { 3 }$ </td><td>9</td></tr><tr><td>(13)</td><td>0169</td><td>#E+T</td><td>#</td><td> $r _ { 1 }$ </td><td>1</td></tr><tr><td>(14)</td><td>01</td><td>#E</td><td>#</td><td>acc</td><td></td></tr></table>

尽管采用SLR(1)方法能够对某些LR(0)项目集规范族中存在动作冲突的项目集通过用向前查看一个符号的办法来解决冲突，但是仍有许多文法构造的LR(0)项目集规范族存在的动作冲突不能用SLR(1)方法解决。

例如，文法 $G ^ { \prime }$ 为  
(0) $S ^ { \prime } {  } S$   
(1) $S {  } a A d$   
(2) $S {  } b A c$   
(3) $S {  } a e c$   
(4) $S {  } b e d$   
(5) $A \to e$

首先用 $S ^ { \prime } \to \cdot S$ 作为初态集的项目，然后用闭包函数和转换函数构造识别文法 $G ^ { \prime }$ 的活前缀的有限自动机DFA，如图6.11所示，可以发现在项目集 $I _ { 5 }$ 和 $I _ { 7 }$ 中存在移进和归约冲突。

![](images/c39d338c55df2466fb19292a644eb950eb6714faec4d8e3b8b32398f883e4613.jpg)  
图 6.11 LR(0)识别 G′的活前缀的 DFA

$$
\begin{array} { c c } { { I _ { 5 } : S {  } \alpha e ~ ^ { \bullet } ~ c ~ } } & { { I _ { 7 } : S {  } b e ~ ^ { \bullet } ~ d } } \\ { { } } & { { } } \\ { { A {  } e ~ ^ { \bullet } } } & { { A {  } e ~ ^ { \bullet } } } \end{array}
$$

$$
\operatorname { F O L L O W } ( A ) = \{ c , d \}
$$

$$
\begin{array} { r } { \ddag \pm \ I _ { 5 } \Psi , \mathrm { F O L L O W } ( A ) \bigcap \{ c \} = \{ c , d \} \bigcap \{ c \} \neq \emptyset _ { \circ } } \end{array}
$$

$$
\nmid \ m _ { \pm } I _ { \tau } \oplus \ l , \mathrm { F O L L O W } ( A ) \bigcap \{ d \} = \{ c , d \} \bigcap \{ d \} \neq \emptyset _ { \circ }
$$

因此 $I _ { 5 }$ 和 $I _ { 7 }$ 中的冲突不能用SLR(1)方法解决，只能考虑用下面将要介绍的LR(1)方法解决。

## 6.4 LR(1)分析

由于用SLR(1)方法解决动作冲突时，对于归约项目 $A \to \alpha ^ { \mathrm { ~ * ~ } }$ ，只要当前面临输入符为$a \in \operatorname { F O L L O W } ( A )$ 时，就确定采用产生式 $A \to \alpha$ 进行归约，但是如果栈里的符号串为 $\beta \alpha$ ，归约后变为 $\beta A$ ，再移进当前符a，则栈里变为 $\beta A a$ ，而实际上 $\beta A a$ 未必为文法规范句型的活前缀。

例如，在识别表达式文法的活前缀DFA(见图6.10)中，在项目集 $I _ { 2 }$ 中存在移进-归约冲突，即 $\{ E {  } T \bullet , T {  } T \bullet \ast F \}$ ，若栈顶状态为2，栈中符号为#T，当前输入符为），而)属FOLLOW(E)中，这时按SLR(1)方法应用产生式E→T进行归约，归约后栈顶符号为#E，而再加当前符)后，栈中为#E)，不是表达式文法规范句型的活前缀。因此可以看出，SLR(1)方法虽然相对于LR(0)有所改进，但仍然存在着多余归约，也说明SLR(1)方法向前查看一个符号的方法仍不够确切。LR(1)方法恰好是要解决SLR(1)方法在某些情况下存在的无效归约问题。

现在再看图 6.11在 $I _ { 5 } , I _ { 7 }$ 项目集中的移进-归约冲突，不能用SLR(1)方法解决的原因如下。

先看 $I _ { 5 }$ 中的情况。

$$
\begin{array} { r l } & { I _ { 5 } : \ S \to \alpha e \ \bullet \ c } \\ & { \qquad \ A \to e \ \bullet } \\ { \mathop { \mathbb { E } } | } & { \ S ^ { \prime } \Rightarrow S \Rightarrow \alpha A d \Rightarrow \alpha e d } \\ & { \ \bullet ^ { \prime } \Rightarrow S \Rightarrow \alpha e c } \end{array}
$$

这两个最右推导已包括了活前缀为a的所有句型，因此不难看出，对活前缀 $\alpha e$ 来说，当面临输入符号c时应移进，面临d时应用产生式A→e归约。因为 $S ^ { \prime } { \Rightarrow } S _ { \underset { R } { \Rightarrow } } ^ { \prime } { \alpha } A c$ ,所以 aAc不是该文法的规范句型。这也说明了并不是FOLLOW(A)的每个元素在含A的所有句型中在A的后面都会出现，例中 $d$ 只在规范句型aAd中A的后面出现，因此面临的输入符为d才应归约。

再看在 $I _ { 7 }$ 中的情况。

$$
\begin{array} { r l } & { I _ { 7 } : S  b e \bullet d } \\ & { \qquad A  e \bullet } \\ { \overrightarrow { \Pi } \quad } & { S ^ { \prime } \Rightarrow S \Rightarrow b A c \Rightarrow b e c } \\ & { \qquad B ^ { \prime } \Rightarrow S \Rightarrow b e d } \end{array}
$$

这两个最右推导包含了活前缀为b的所有句型，可见FOLLOW(A)中的c只能跟在句
