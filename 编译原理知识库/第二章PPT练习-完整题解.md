---
type: 题解页
chapter: 第2章 文法和语言
knowledge_points:
- 推导与归约
- Chomsky分类
- 语法树与二义性
exam_points:
- kp: 推导与归约
  name: 第2章 PPT 练习（文法⇄语言）
  level: 必考
  weight: 0
  qtype: 题型2/3
---

# 第二章 PPT练习 — 完整题解

> 来源：`第二章ppt练习.docx`（PPT 课堂练习，第二章 文法和语言）
> 涵盖：13 题 — 文法与语言互求、文法类型、推导与语法树、短语/直接短语/句柄/素短语、二义性
> 对应知识点：[[02-文法和语言]]；对应题型：[[期末复习专题]] 题型2/3/4
> 答案版式同 [[教材习题_第2章]]、[[第二章文法和语言作业-完整题解]]

---

## 第1题
> G[S]：VN={S}，VT={0,1}，P={S→0S1，S→01}，则 L(G)=？
> （附选择题）文法 G 所描述的语言是____的集合：
> A 文法词汇表 V 中所有符号组成的符号串　B V* 中所有符号串
> C 由开始符号推导出的所有符号串　D 由识别符推导出的所有终结符号串

**答案**：$L(G) = \{0^n 1^n \mid n \ge 1\}$；选择题选 **D**。

**解**：每用一次 S→0S1 就在左右各包一层 0/1，最后用 S→01 收尾：

```
S ⇒ 0S1 ⇒ 00S11 ⇒ … ⇒ 0ⁿ⁻¹S1ⁿ⁻¹ ⇒ 0ⁿ1ⁿ
```

故语言 = n≥1 个 0 后跟 n 个 1。选择题：语言定义 = **开始符号能推出的全部终结符号串**（C 说的是句型，含非终结符）。

---

## 第2题
> 已知语言 L={aⁿbbⁿ | n≥1}（如 abb、aabbb、aaabbbb…），下述文法中（　）可以产生 L。
> A　Z→aZb|aAb|b，A→aAb|b　B　Z→aAb，A→b
> C　Z→AbB，A→aA|a，B→bB|b　D　Z→aAb，A→aAb|b

**答案**：**D**。

**解**：D：$Z \Rightarrow aAb$，$A \Rightarrow a^{n-1}Ab^{n-1}$ 递归，末步 A→b ⇒ $a^n b b^n$：
n=1：$aAb \Rightarrow abb$；n=2：$aaAbb \Rightarrow aabbb$ ✓。
排除：A 含 Z→b（语言含 b，不符）；B 只有 abb（无 n≥2）；C 是 $a^+b^+$。

---

## 第3题
> G：VN={I,D,L}，VT={0~9, a~z}，P={I→L|IL|ID，L→a|b|…|z，D→0|1|…|9}。则 L(G)=？

**答案**：**字母开头、由字母和数字组成的全部非空串**（标识符）。

**解**：I→L 得首字符为字母；I→IL、I→ID 向右任意接字母/数字 ⇒ $L(G)=\{w \mid w = l\,x_1\cdots x_k,\ l\in[a..z],\ x_i\in[a..z]\cup[0..9],\ k\ge 0\}$。**2 型**（语言为正规语言）。

---

## 第4题
> 以下文法描述的语言是什么？属于哪类文法？
> (a) G[S]：S→Aa，A→bA|a
> (b) G[S]：S→aSBC|abC，CB→BC，bB→bb，bC→bc，cC→cc

**解 (a)**：A 推出 $b^n a\ (n\ge 0)$，再由 S→Aa 尾接 a ⇒ $L(G)=\{b^n aa \mid n \ge 0\}$ = {aa, baa, bbaa, …}。
**类型**：右部形式混用（S→Aa 是左线性形、A→bA 是右线性形）⇒ **2 型**（上下文无关）。语言本身是正规语言。

**解 (b)**：经典上下文有关文法：$L(G)=\{a^n b^n c^n \mid n \ge 1\}$。
n=2 的推导：

```
S ⇒ aSBC ⇒ aabCBC ⇒ aabBCC ⇒ aabbCC ⇒ aabbcC ⇒ aabbcc
```

（aSBC 造一层 BC；CB→BC 把 B 全换到左；bB→bb、bC→bc、cC→cc 逐个配对。）

**类型**：CB→BC 等规则形如 $\alpha B\beta \to \alpha\gamma\beta$ ⇒ **1 型（上下文有关）**，不是上下文无关文法。

---

## 第5题
> G：S→iSeS | iS | i（i 代表 if，e 代表 else）。
> (1) VN、VT；(2) 句子 iiiei 的最左推导、最右推导、语法树；(3) 证明二义；(4) 几型文法？

**解 (1)**：$V_N=\{S\}$，$V_T=\{i, e\}$。

**解 (2)** 句子 iiiei（i i i e i）有两棵语法树——

**推导 A**（根用 S→iSeS）：

```
最左：S ⇒ iSeS ⇒ iiSeS ⇒ iiieS ⇒ iiiei      （用产生式: S→iSeS, S→iS, S→i, S→i）
最右：S ⇒ iSeS ⇒ iSei ⇒ iiSei ⇒ iiiei
```

**推导 B**（根用 S→iS）：

```
最左：S ⇒ iS ⇒ iiSeS ⇒ iiieS ⇒ iiiei        （用产生式: S→iS, S→iSeS, S→i, S→i）
最右：S ⇒ iS ⇒ iiSeS ⇒ iiSei ⇒ iiiei
```

语法树（A 与 B 的区别在根部）：

```
    A:  S                B:  S
       /|\                  / \
      i S e S              i   S
        | |                    /|\
        i S                  i S e S
          |                    |   |
          i                    i   i
```

**解 (3)**：句子 iiiei 对应**两棵不同的语法树**（两条不同的最左推导），故 **G 是二义文法**——这正是"悬挂 else"现象的根源。

**解 (4)**：右部含多个符号且含非终结符、无左右线性限制 ⇒ **2 型（上下文无关）**。

---

## 第6题
> 例：G[E]：E→E+T|T，T→T\*F|F，F→(E)|i。求句型 i\*i+i 的短语、直接短语和句柄。

**答案**：

| 类型 | 内容 |
|---|---|
| 短语 | i₁、i₂、i₃、i₁\*i₂、i₁\*i₂+i₃（共 5 个） |
| 直接短语 | i₁、i₂、i₃（均 F→i 一步） |
| **句柄** | **i₁**（最左直接短语） |

**解**（用定义 $S \Rightarrow^* \alpha A\delta$ 且 $A \Rightarrow^+ \beta$）：$i_1$ 相对 F（F⇒i）、$i_2$ 相对 F、$i_3$ 相对 F 都是**直接短语**；$i_1*i_2$ 相对 T（$T \Rightarrow^+ i_1*i_2$）；整个 $i_1*i_2+i_3$ 相对 E。
反例：$i_2+i_3$ **不是**短语——虽然 $E \Rightarrow^+ i_2+i_3$，但不存在形如 $E \Rightarrow^* i_1*E$ 的推导，上下文对不上。

---

## 第7题
> G：S→aAcB|Bd，A→AaB|c，B→bScA|b。写出句型 aAaBcbbdcc 的语法树，并指出短语、直接短语、句柄。

**解**（推导，每步可任选最左/最右；这里按从左到右）：

```
S ⇒ aAcB            [S→aAcB]
  ⇒ aAaBcB          [A→AaB]      （A、B 两个子结点保持为叶）
  ⇒ aAaBcbScA       [B→bScA]     （句型末的 B 展开）
  ⇒ aAaBcbBdcA      [S→Bd]
  ⇒ aAaBcbbdcA      [B→b]
  ⇒ aAaBcbbdcc      [A→c]
```

**语法树**：

```
                S
       /      / \  \
      a      A   c  B
            / \      /|\
           A  a  B  b S c A
           |        /|    |
           c       B d    c
                   |
                   b
```

（叶序列从左到右：a A a B c b b d c c ✓）

**答案**：

| 类型 | 内容 | 来源 |
|---|---|---|
| 短语 | aAaBcbbdcc、AaB、bbdcc、bd、b、c | 各子树叶串 |
| 直接短语 | **AaB**（A→AaB 一步）、**b**（B→b 一步）、**c**（A→c 一步） | 右部原样出现 |
| **句柄** | **AaB** | 最左直接短语 |

注：句型中的叶型非终结符 A、B（树中未展开）各自不构成短语。

---

## 第8题
> 已知字母表 T={a,b}，为下列语言构造文法：
> ① {ε}　② {a,b}　③ {aⁿ|n≥1}　④ {aⁿbⁿ|n≥0}　⑤ {aⁿbᵐ|n,m≥0}
> ⑥ {aⁿbⁿcⁱ|n≥1,i≥0}　⑦ {aᵐbⁿaⁿbᵐ|n,m≥1}　⑧ {abⁿabⁿ⁻¹|n≥1}　⑨ {WcWᴿ|W∈(a|b)\*}

**答案**（均为 2 型，① 除外可视为含 ε 规则的 2 型）：

| # | 文法 | 说明 |
|---|---|---|
| ① | S→ε | 只有空串 |
| ② | S→a\|b | 两个单字符 |
| ③ | S→aS\|a | a 的正数次幂 |
| ④ | S→aSb\|ε | 每层包一对 a,b |
| ⑤ | S→aS\|bS\|ε | 任意 a,b 串（= (a\|b)\*） |
| ⑥ | S→AB，A→aAb\|ab，B→cB\|ε | A 造 aⁿbⁿ(n≥1)，B 造 cⁱ |
| ⑦ | S→aSb\|aXb，X→bXa\|ba | 外层 aᵐ…bᵐ，内层 bⁿaⁿ |
| ⑧ | S→aX，X→bXb\|ba | 造 bⁿ…bⁿ⁻¹ 配对 |
| ⑨ | S→aSa\|bSb\|c | 左右对称回文夹 c |

**解（⑦为例）**：$a^m b^n a^n b^m$（n,m≥1）= 外面包 m 层 a…b，核心是 $b^n a^n$：S→aSb 递归 m 次，基步 aXb，X→bXa|ba 造 $b^n a^n$。验证 m=1,n=2：$S \Rightarrow aXb \Rightarrow abXab \Rightarrow abbaab$ = a b² a² b ✓。

**解（⑧为例）**：$ab^n a b^{n-1}$：S→aX 造前导 a，X→bXb 递归造 b…b 配对、基步 ba：n=2 时 $X \Rightarrow bXb \Rightarrow bbab$ ⇒ S = abbab ✓。

---

## 第9题
> G[A]：A→0B|1C，B→1|1A|0BB，C→0|0A|1CC。写出它定义的语言描述。

**答案**（PPT 已给）：**由 0、1 组成且 0 与 1 个数相同的非空串**，即 $L(G)=\{w\in\{0,1\}^+ \mid w 中 0 的个数 = 1 的个数\}$。

**解**：每条产生式保持 0/1 计数差：0B（+1 个 0 交给 B 平衡）、1A、0BB（一个 0 由两个 B 分摊）、1CC 同理；B→1、C→0 收尾补差。最小串 01、10；ε 不在语言中。

---

## 第10题
> 给出语言描述，构造文法：由算符 +、\*、(、) 和运算对象 a 构成的算术表达式的集合。

**答案 1（无二义）**：

```
G[E]: E→E+T|T    T→T*F|F    F→(E)|a
```

**答案 2（二义，与答案 1 等价）**：

```
G[E]: E→E+E|E*E|(E)|a
```

**解**：答案 1 用 E/T/F 三级体现了 + 与 \* 的优先级及左结合 ⇒ 无二义；答案 2 同语言但 $a+a*a$ 有两棵语法树 ⇒ 二义。考试写答案 1 更稳（可加一句"无二义"）。

---

## 第11题
> 以下文法描述的语言是什么？属于几型文法？
> 1）S→bSc|bc　2）S→BC，B→bCc|bc，C→dC|c　3）S→fBC，B→bB|b，C→c

**解 1)**：$S \Rightarrow bSc \Rightarrow \cdots \Rightarrow b^n c^n$ ⇒ $L=\{b^n c^n \mid n \ge 1\}$；**2 型**（语言非正规）。

**解 2)**：$C=\{d^k c \mid k \ge 0\}$；$B=\{bc\} \cup \{b d^m c c \mid m \ge 0\}$；$S=BC$ ⇒
$L=\{b c d^k c \mid k \ge 0\} \cup \{b d^m c c d^k c \mid m,k \ge 0\}$（如 bcc、bcdc、bdcc、bddcc…）。
右部无限制单 NT 形式（B→bCc 两端带终结符）⇒ **2 型**。

**解 3)**：$B \Rightarrow b^m\ (m \ge 1)$，$C=c$ ⇒ $L=\{f b^m c \mid m \ge 1\}$；右部 fBC 含**两个相邻非终结符** ⇒ **2 型**。

---

## 第12题
> 根据语言写出文法：
> 1）$L=\{b^n c^m d^{2m} \mid n,m \ge 0\}$　2）$L=\{b^{2n} c^n \mid n \ge 1\}$　3）$L=\{b c^n b \mid n \ge 0\}$

**答案**：

```
1)  S → A B      A → bA | ε      B → cBdd | ε
2)  S → bbSc | bbc
3)  S → bAb      A → cA | ε
```

**解（2）**：每层造一对 b（两侧各一）配一个 c：$S \Rightarrow bbSc \Rightarrow \cdots \Rightarrow b^{2n} c^n$，基步 bbc（n=1）。
**解（1）**：A 造 bⁿ，B 造每来一个 c 配两个 d：$B \Rightarrow c^m d^{2m}$。**解（3）**：首尾各一个 b，中间 cⁿ。均 **2 型**（1、3 含 ε 规则）。

---

## 第13题
> G：S→W，W→U|WjU，U→G|U+G，G→)W\*|(
> (1) 终结符集与非终结符集；(2) 句型 G+Gj( 的最左推导和语法树；
> (3) 句型的短语、直接短语、句柄；(4) 几型文法？句型的素短语和最左素短语。

**解 (1)**：$V_N=\{S, W, U, G\}$，$V_T=\{ j, +, ), *, ( \}$。

**解 (2)** 最左推导（句型 G+Gj(）：

```
S ⇒ W ⇒ WjU ⇒ UjU ⇒ U+GjU ⇒ G+GjU ⇒ G+GjG ⇒ G+Gj(
```

语法树：

```
        S
        |
        W
      / | \
     W  j  U
     |      |
     U      G
   / | \    |
  U  +  G   (
  |
  G
```

叶序列：G + G j ( ✓

**解 (3)**：

| 类型 | 内容 |
|---|---|
| 短语 | G（首位）、(、G+G、G+Gj(（全句型） |
| 直接短语 | **G**（U→G 一步）、**(**（G→( 一步） |
| **句柄** | **G** |

（句型中部的 G 是未展开的叶型非终结符，不构成短语。）

**解 (4)**：**2 型（上下文无关）**；素短语 = **G+G**、**(**；**最左素短语 = G+G**（G 无终结符不是素短语；G+Gj( 含更小素短语）。

---

## 速查：本套题 ↔ 期末题型

| PPT 题 | 考点 | [[期末复习专题]] |
|---|---|---|
| 1、2、3 | 文法→语言、语言→文法 | 题型2、3 |
| 4、5、11、12 | 语言↔文法、文法类型 | 题型2、3 |
| 6、7、13(2)(3) | 推导、语法树、短语/句柄/素短语 | 题型4 |
| 5(3)、13(3) | 二义性证明 | 题型3 |
| 9、10 | 语言描述、文法构造 | 题型2、3 |

#编译原理 #PPT练习 #第2章 #完整题解
