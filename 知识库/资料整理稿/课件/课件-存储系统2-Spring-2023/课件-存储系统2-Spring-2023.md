---
title: 课件-存储系统2-Spring-2023
type: courseware_draft
category: 课件
source_file: 存储系统2--Spring.2023.pdf
source_relative: 资料/课件/存储系统2--Spring.2023.pdf
source_path: D:\wzb\计算机组成原理\资料\课件\存储系统2--Spring.2023.pdf
raw_markdown: D:\wzb\计算机组成原理\知识库\资料整理稿\课件\课件-存储系统2-Spring-2023\raw-extract.md
assets_dir: D:\wzb\计算机组成原理\知识库\资料整理稿\课件\课件-存储系统2-Spring-2023\images
status: extracted
extract_backend: mineru
extract_model: vlm
extract_language: ch
extract_formula: true
extract_table: true
extract_is_ocr: false
extract_ocr_reason: prior_extract_text_ok
extract_ocr_signal_summary: {"char_count": 30227, "line_count": 1598, "cjk_count": 3066, "image_ref_count": 66, "replacement_char_count": 0, "formula_token_count": 42}
---

# 课件-存储系统2-Spring-2023

## 来源

- 分类：`课件`
- 原始文件：`存储系统2--Spring.2023.pdf`
- 原始相对路径：`资料/课件/存储系统2--Spring.2023.pdf`
- 原始绝对路径：`D:\wzb\计算机组成原理\资料\课件\存储系统2--Spring.2023.pdf`

## 后续处理建议

- 从本整理稿中提取稳定知识点
- 检查公式、表格、结构图的提取效果
- 必要时补单独图像解读稿
- 如发现资料错误，转入勘误或分歧

## 内容导读（基于整理稿归纳）

本讲开始进入主存储器内部结构，围绕 RAM、SRAM、DRAM 的工作原理展开，是后续做存储芯片分析与 8086 接口题的基础。

## 关键知识点

- RAM 的基本分类及其在主存中的角色。
- SRAM 与 DRAM 的结构差异、速度/成本/集成度取舍。
- 字线、位线、地址译码等基本电路概念。

## 典型例题 / 思考题

- 解释 SRAM 和 DRAM 的工作原理及优缺点。
- 说明字线和位线各自的作用。
- 说明一维/二维地址译码机构的设计动机。

## 例题理解层（基于课件整理）

### 题目簇 1：SRAM 与 DRAM 原理与比较

- 原题/原问：
  - 解释 SRAM 和 DRAM 的工作原理及优缺点
  - 说明一维/二维地址译码机构的设计动机
- 题意：理解SRAM（静态RAM，用触发器存储）和DRAM（动态RAM，用电容存储）的工作原理、刷新机制、以及地址译码方式的差异。
- 所考知识点：
  - SRAM：用6管触发器存储1位，不需刷新，速度快，集成度低，成本高
  - DRAM：用1管+1电容存储1位，需定期刷新（典型64ms），速度慢，集成度高，成本低
  - DRAM刷新方式：集中刷新、分散刷新、异步刷新
  - 一维译码：n位地址→2^n条线，适合小容量
  - 二维译码：行列各n/2位→2×2^(n/2)条线，大幅减少译码线数
- 解题关注点：
  - SRAM适合Cache（快但贵），DRAM适合主存（慢但便宜且密度高）
  - DRAM刷新期间不能读写（集中刷新有"死区"）
  - 二维译码的优势：10位地址一维需1024条线，二维只需64条
- 题型归类建议：原理解释题 + 比较分析题
- 备注：信息完整，SRAM/DRAM对比是高频考点

## 提取结果

# 计算机组成与结构

# —存储系统2

李瑞 教授

蒋志平 讲师

计算机科学与技术学院

# 温故

- 简述存储系统金字塔结构
- 简述“存取时间”和“存取周期”，举例对比
- 简述“存取带宽”和“随机访问速度”，举例对比
- 简述”读/写速率比”和“存取粒度”，举例对比
- 简述可靠性MTBF和MTTF两个指标，举例对比
- 按功耗/bit排序，存储系统的功耗排序是？
- SRAM、DRAM是什么？S与D指代什么内涵？
- SRAM的工作原理?
- DRAM的工作原理?
- 字线的作用？位线的作用？

# 7.2主存储器

# 主存储器

- 随机读写存储器(RAM)

- 静态/动态RAM

- 只读存储器(ROM)

# 随机读写存储器RAM

---- RANDOM ACCESS MEMORY

- SRAM 静态随机读写存储器
- DRAM 动态随机读写存储器

- 常规RAM芯片，其外部有地址引线、数据引线和控制信号引线。
- 地址引线在芯片内部译码，选中芯片内部的相应存储单元。
- 某静态RAM芯片上有n条地址线时，地址线上所能表示的地址编码就有 $2^{n}$ 种。这就意味着该芯片内部有 $2^{n}$ 个存储单元。

# 随机读写存储器RAM

- SRAM，目前主流的实现方式，是基于MOSFET

![](images/558789258477196532c20cf1594df47884920a9db218ac82c3b488f73605c110.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    b --> c
    b --> e
    c --> e
    e --> c
```
</details>

开关状态时:

b 高电平，e-c 导通

b 低电平，e-c 截止

![](images/a70f44fea6fba09e589559bf4eef7ea97cdb48ae590ce31932fe0b23072b6e75.jpg)

<details>
<summary>text_image</summary>

MOSFET - Canal N
G
D
S
VGS
Vcc
</details>

# 随机读写存储器RAM

- SRAM原理图——基本存储单元
![](images/89fbdd48fbe271ea3f03b541985c14f5a19ca5825852f0dd09c1d589e03b290f.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    b --> c
    b --> e
    c --> e
```
</details>

开关状态:

b 高电平，e-c 导通
b 低电平，e-c 截止

![](images/a766a6defca490395dddf9a1981a796a6df8e1c510e8d8d46bf72d0ce45889dc.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    Vcc --> A
    Vcc --> B
    T1 --> A
    T1 --> B
    T2 --> A
    T2 --> B
    Gnd --> A
    Gnd --> B
```
</details>

状态‘1’:

T1 导通、T2截止

A点低 B点高

状态 ‘0’:

T1截止、T2导通

A点高 B点低

# 随机读写存储器RAM

![](images/fe3d9f472d5eb65c733da0e0c17fb2ef4f8670ddc883173c64c9cf0578eac841.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    A["位线1"] --> B["T1"]
    C["位线2"] --> D["Gnd"]
    E["Vcc"] --> F["A"]
    G["B"] --> H["B"]
    I["字线"] --> J["T2"]
    K["地线"] --> L["地线"]
    style A fill:#f9f,stroke:#333
    style C fill:#f9f,stroke:#333
    style E fill:#ccf,stroke:#333
    style G fill:#ccf,stroke:#333
    style I fill:#ccf,stroke:#333
    style K fill:#ccf,stroke:#333
    style L fill:#ccf,stroke:#333
```
</details>

写入‘1’: 字线高

位线1 低、位线2 高

A点低 B点高

T1 导通、T2 截止

写入‘0’: 字线高

位线1 高、位线2 低

A点高 B点低

T1截止、T2导通

保持: 字线低

T1、T2 状态维持

读出: 字线高

位线1低、位线2高 -- ‘1’

位线1高、位线2低 - ‘0’

6T SRAM基本存储单元

# 随机读写存储器RAM

![](images/c0149b36ec2ea26608bf1877d6c4ad41475848965544322c535ace403a1a948e.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    Vcc --> A
    Vcc --> B
    A --> T1
    A --> T2
    B --> T2
    Gnd --> T2
    style A fill:#f9f,stroke:#333
    style B fill:#f9f,stroke:#333
    style T1 fill:#fff,stroke:#000
    style T2 fill:#fff,stroke:#000
    note right of A
        Cross
    end
```
</details>

6T SRAM基本存储单元

![](images/f4af81aa513de496d65c24aa7ca0728a4290c4cfa4d7fc40072d035bf9a66516.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    Vcc --> A
    A --> T1
    A --> B
    B --> T2
    T2 --> Gnd
    Gnd --> A
```
</details>

4T2R SRAM基本存储单元

# 随机读写存储器RAM

![](images/465368cc361de73c445e1722bace1bf4b8ea166d92898ff4fb5640a14c2ba607.jpg)

<details>
<summary>text_image</summary>

WL
M2
VDD
M4
Q
M5
Q̅
M1
M3
M6
BL
BL
</details>

![](images/551dd8163cf55fee4b87d1906e6f85965461b5096eb9c8025c01cdbf73051a6c.jpg)

<details>
<summary>natural_image</summary>

Microscopic view of rod-shaped bacterial cells with visible cell walls and internal structures (no text or labels)
</details>

65 nm [Bai04]

![](images/3c6855b940ca5571a283057bc2687f6a7ccd980e6823a632ae0ee08551e0f131.jpg)

<details>
<summary>natural_image</summary>

Microscopic view of rectangular structures with dashed outlines, no visible text or symbols
</details>

45 nm [Mistry07]

![](images/6a94ed3d80ce02b07491b9258b2c9434b7a04aedb4dd6ef12526e739dc5f9160.jpg)
32 nm [Natarajan08]

![](images/13931f6bf56154f5ad0e1bfceed4f68374d7f90885f302330ecc3befffc9b98b.jpg)

<details>
<summary>text_image</summary>

VDD
M2 M4
Q
M1 M3
GND
WL
M5 M6
BL BL
</details>

# 随机读写存储器RAM

- DRAM的基本存储单元
- 3T-DRAM

![](images/bd902bbd1e040a63509c2d308435b597cbbd7377dc5f717b781684d98c8b4758.jpg)

<details>
<summary>text_image</summary>

BL 1
WWL
RWL
M₁
X
M₂
Cₛ
M₃
BL 2
</details>

![](images/4a46a920a92078b94da16b56e92a13871ff3f697b36473b2623d139f7c8808f6.jpg)

<details>
<summary>text_image</summary>

WWL
RWL
X
V_DD 2 V_T
BL1
V_DD
BL2
V_DD 2 V_T
DV
</details>

# 随机读写存储器RAM

- DRAM的基本存储单元
- 3T-DRAM (reading is non-destructive)

![](images/bb2133e01b89236463926feeb05687adda55715d57eeb2513de7044edfda399d.jpg)

<details>
<summary>text_image</summary>

BL 1
WWL
RWL
M₁
X
M₂
Cₛ
M₃
BL 2
</details>

![](images/7a137bcac32b152cc76c9c3eebcf533bc5e48e196557278dcdb5d7e67f473307.jpg)

<details>
<summary>text_image</summary>

WWL
RWL
X
V_DD 2 V_T
BL1
V_DD
BL2
V_DD 2 V_T
DV
</details>

# 随机读写存储器RAM

- DRAM的基本存储单元
- 1T-DRAM (reading is destructive)

![](images/e2032717ac54d9076507d5f4d1dd35774aaf6731275296fc4d7201faa9b4404a.jpg)

<details>
<summary>text_image</summary>

WL
BL
M₁
Cₛ
CBL
</details>

![](images/3380a7e50935d957914061dc5d64e0abc677aa58c032d55460ded03f7a75c29c.jpg)

<details>
<summary>text_image</summary>

WL Write 1 Read 1
X GND
BL sensing
</details>

# 随机读写存储器RAM

- SRAM v.s DRAM?

- SRAM基于互锁6T结构，通电时初始保持（静态）；
- DRAM基于电容，会漏电（动态）需要定时充电；

- 充电如何实现？

- 读出来再写进去!

# 随机读写存储器RAM

![](images/ebc57e4638797cf093e99eaec693941753ab8b337e1af765caea759b08c1f022.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    A["位线"] --> B["基本存储单元"]
    C["字线"] --> B
    D["位线"] --> B
```
</details>

基本存储单元简图

# 随机读写存储器RAM

![](images/afa742920145d55806f3019c7600ee401f6f46134252c54303f3d2dd302d3098.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph LR
    A0["A0"] --> D["地址译码器"]
    A1["A1"] --> D
    An-1["An-1"] --> D
    D --> 0["0"]
    D --> 1["1"]
    D --> 2["2"]
    D --> 3["3"]
    D --> 2n-2["2^n-2"]
    D --> 2n-1["2^n-1"]
    0 --> O1["○"]
    1 --> O2["○"]
    2 --> O3["○"]
    3 --> O4["○"]
    2n-2 --> O5["○"]
    2n-1 --> O6["○"]
```
</details>

(a)

![](images/dfd52eef937dd954aab341afe33c11ca08317e1e3b6cfbd9c7e10fdba8a67752.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    A0["A0"] --> B["行地址译码器"]
    An1["An-1"] --> B
    Am1["Am-1"] --> B
    B --> C0["0"]
    B --> C1["1"]
    C0 --> D1["○"]
    C1 --> D2["○"]
    D1 --> E1["○"]
    D2 --> E2["○"]
    E1 --> F1["→"]
    E2 --> F2["→"]
    F1 --> G1["○"]
    F2 --> G2["○"]
    G1 --> H1["○"]
    G2 --> H2["○"]
    H1 --> I1["→"]
    H2 --> I2["→"]
    I1 --> J1["○"]
    I2 --> J2["○"]
    J1 --> K1["○"]
    J2 --> K2["○"]
    K1 --> L1["○"]
    K2 --> L2["○"]
    L1 --> M1["○"]
    L2 --> M2["○"]
    M1 --> N1["○"]
    M2 --> N2["○"]
    N1 --> O1["○"]
    N2 --> O2["○"]
    O1 --> P1["○"]
    O2 --> P2["○"]
    P1 --> Q1["○"]
    P2 --> Q2["○"]
    Q1 --> R1["○"]
    Q2 --> R2["○"]
    R1 --> S1["○"]
    R2 --> S2["○"]
    S1 --> T1["○"]
    S2 --> T2["○"]
    T1 --> U1["○"]
    T2 --> U2["○"]
    U1 --> V1["○"]
    U2 --> V2["○"]
    V1 --> W1["○"]
    V2 --> W2["○"]
    W1 --> X1["○"]
    W2 --> X2["○"]
    X1 --> Y1["○"]
    X2 --> Y2["○"]
    Y1 --> Z1["○"]
    Y2 --> Z2["○"]
```
</details>

(b)
RAM芯片内部的两种译码方式

# 存储器基本组成

![](images/56ed76a9ad5c55deb6fbfcdae368af3e0b38c43a284d5b1612e17d2541c339c0.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    A["AB"] --> B["MAR"]
    B --> C["译码器"]
    C --> D["存储阵列"]
    D --> E["读放电路\n写驱动电路"]
    E --> F["MDR"]
    F --> G["DB"]
    style A fill:#99CCFF,stroke:#333
    style G fill:#99CCFF,stroke:#333
    note right of C 0: "2^n-1"
    note right of D 0: "存储阵列"
    note right of E 0: "读放电路\n写驱动电路"
    note right of F 0: "MDR"
    note left of G DB
```
</details>

# CPU与主存通信

![](images/be2b575ca8350b3d5b1cf3a3bca9b98f5a56e9dfda52912d9ce13f01428ceebd.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    CPU["CPU"] -->|R/W| MDR["MDR"]
    CPU -->|ready| MM["MM"]
    CPU -->|R/W| AR["AR"]
    CPU -->|ready| MDR
    CPU -->|R/W| ABus["Abus 地址总线"]
    CPU -->|ready| DBus["DBus 数据总线"]
    CPU -->|ready| CBus["CBus 控制总线"]
    CPU -->|R/W| AR
    CPU -->| ready| MDR
    CPU -->| ready| MAR["MAR"]
    CPU -->|AR 地址寄存器| AR
    CPU -->|AR 数据寄存器| AR
```
</details>

![](images/915bd14e17259bbf3e299b12d01a2beca54ddd3f9b22b9be1e9439fa4039101a.jpg)

<details>
<summary>text_image</summary>

CPU周期
地址
数据
WR
</details>

(a)

![](images/bd5c486f8efdbc0363b635978bd56c01ccc888438c522c32d05bb04437594ea3.jpg)

<details>
<summary>text_image</summary>

M写周期
地址
CS
数据
WR
</details>

(b)

# CPU写内存时序

# 内存写时序

■ 在选芯片时应留有30%的余量。
■ 快速的CPU使用慢速的存储器时，需要采取措施。

# 6264 SRAM芯片

![](images/2c32d27ed988f634724de8e7e1b2f5420eff679bf8c0bfbbc5838d596a32492e.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    A["D₀ ~ D₇"] --> B["A₀ ~ A₁₂"]
    B --> C["OE"]
    B --> D["WE"]
    B --> E["CS"]
```
</details>

8K \* 8b

A0 ~ A12为13条地址信号线

D0 ~ D7为8条双向数据线

CS片选信号的引线，当片选信号同时有效时，即 $\overline{\mathbf{CS}} = 0$ ，时，才能选中该芯片。

OE为输出允许信号。只有当OE=0，

即其有效时，才允许该芯片将某单元的数据送到芯片外部的D0～D7上。

WE是写允许信号。

当 $\overline{WE}=0$ 时，允许将数据写入芯片；当 $\overline{WE}=1$ 时，允许芯片的数据读出。

- 拼接多个芯片，构造连续大存储
- 怎么拼?

- 字扩展
- 位扩展
- 字位同时扩展

- 利用 8K×8bit 的 SRAM, 构成 32KB 内存。

![](images/d1b7062208c56b2e5f831371ad807b6aac7321161e6bf2558838774e3de7d64c.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    A["A19"] --> B["&"]
    C["A18"] --> B
    D["A17"] --> E["E"]
    F["A16"] --> G["EA"]
    H["A15"] --> I["C"]
    J["A14"] --> K["B"]
    L["A13"] --> M["A"]
    N["74LS138"] --> O["&"]
    P["D0~D7"] --> Q["OE"]
    R["D0~D7"] --> S["OE"]
    T["D0~D7"] --> U["OE"]
    V["D0~D7"] --> W["OE"]
    X["D0~D7"] --> Y["OE"]
    Z["D0~D7"] --> AA["OE"]
    AB["D0~D7"] --> AC["OE"]
    AD["D0~D7"] --> AE["OE"]
    AF["D0~D7"] --> AG["OE"]
    AH["D0~D7"] --> AI["OE"]
    AJ["D0~D7"] --> AK["OE"]
    AL["D0~D7"] --> AM["OE"]
    AN["D0~D7"] --> AO["OE"]
    AP["D0~D7"] --> AQ["OE"]
    AR["D0~D7"] --> AS["OE"]
    AT["D0~D7"] --> AU["OE"]
    AV["D0~D7"] --> AW["OE"]
    AX["D0~D7"] --> AY["OE"]
    AZ["D0~D7"] --> BA["OE"]
    BB["D0~D7"] --> BC["OE"]
    BD["D0~D7"] --> BE["OE"]
    BF["D0~D7"] --> BG["OE"]
    BH["D0~D7"] --> BI["OE"]
    BJ["D0~D7"] --> BK["OE"]
    BL["D0~D7"] --> BLA["OE"]
    BN["D0~D7"] --> BO["OE"]
    BP["D0~D7"] --> BPB["OE"]
    BPB --> BPCC["OE"]
    BPCC --> BPCCB["OE"]
    BPCC --> BPCCC["OE"]
    BPCC --> BPCCD["OE"]
    BPCC --> BPCCE["OE"]
    BPCC --> BPCCF["OE"]
    BPCC --> BPCCG["OE"]
    BPCC --> BPCCH["OE"]
    BPCC --> BPCCI["OE"]
    BPCC --> BPCCJ["OE"]
    BPCC --> BPCCK["OE"]
    BPCC --> BPCCL["OE"]
    BPCC --> BPCCM["OE"]
    BPCC --> BPCCN["OE"]
    BPCC --> BPCCO["OE"]
    BPCC --> BPCCP["OE"]
    BPCC --> BPCCQ["OE"]
    BPCC --> BPCCQC["OE"]
    BPCC --> BPCCQF["OE"]
    BPCC --> BPCCQG["OE"]
    BPCC --> BPCCQH["OE"]
    BPCC --> BPCCQI["OE"]
    BPCC --> BPCCQJ["OE"]
    BPCC --> BPCCQK["OE"]
    BPCC --> BPCCQL["OE"]
    BPCC --> BPCCQK["OE"]
    BPCC --> BPCCQKQ["OE"]
```
</details>

存储器字扩展连接电路图

<table><tr><td> $A_{19}$ </td><td> $A_{18}$ </td><td> $A_{17}$ </td><td> $A_{16}$ </td><td> $A_{15}$ </td><td> $A_{14}$ </td><td> $A_{13}$ </td><td> $A_{12}$ </td><td>...</td><td> $A_0$ </td></tr><tr><td>1</td><td>1</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>x</td><td>...</td><td>x</td></tr><tr><td>1</td><td>1</td><td>0</td><td>0</td><td>0</td><td>0</td><td>1</td><td>x</td><td>...</td><td>x</td></tr><tr><td>1</td><td>1</td><td>0</td><td>0</td><td>0</td><td>1</td><td>0</td><td>x</td><td>...</td><td>x</td></tr><tr><td>1</td><td>1</td><td>0</td><td>0</td><td>0</td><td>1</td><td>1</td><td>x</td><td>...</td><td>x</td></tr></table>

.13

$$
\mathbf {D} _ {0} \sim \mathbf {D} _ {7}
$$

$$
\mathbf {A _ {0}} \sim \mathbf {A _ {1 2}}
$$

$$
\overline {{\mathbf {O E}}}
$$

$$
\overline {{\text {WE}}}
$$

$$
\overline {{\mathbf {C S}}}
$$

$$
\mathbf {D} _ {0} \sim \mathbf {D} _ {7}
$$

$$
\mathbf {A _ {0}} \sim \mathbf {A _ {1 2}}
$$

$$
\overline {{\mathbf {O E}}}
$$

$$
\overline {{\text { WE }}}
$$

$$
\overline {{\mathbf {C S}}}
$$

74LS138
![](images/fe9ca0e3b5f5e64df3df9d0baf9c1b00f453e0aba48f44f8df7c6c9639bd2ee5.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    A19["A19"] --> &[&]
    A18["A18"] --> &
    A17["A17"] --> E["E"]
    A16["A16"] --> E["E"]
    A15["A15"] --> E["E"]
    A14["A14"] --> C["C"]
    A13["A13"] --> B["B"]
    A --> A
    E --> Y0["Y0"]
    E --> Y1["Y1"]
    E --> Y2["Y2"]
    C --> Y3["Y3"]
    B --> A
    Y0 --> C0000["C0000 ~ C1FFF"]
    Y1 --> C2000["C2000 ~ C3FFF"]
    Y2 --> C4000["C4000 ~ C5FFF"]
    Y3 --> C6000["C6000 ~ C7FFF"]
```
</details>

![](images/1567c1e52ab8b22483b9b6fe0823db0e58003f1b84ce1b20d468b03d85f8b7f2.jpg)

$$
\mathbf {D _ {0}} \sim \mathbf {D _ {7}}
$$

$$
\mathbf {A _ {0}} \sim \mathbf {A _ {1 2}}
$$

$$
\overline {{\mathbf {O E}}}
$$

$$
\overline {{\text { WE }}}
$$

$$
\overline {{\mathbf {C S}}}
$$

$$
\mathbf {D _ {0}} \sim \mathbf {D _ {7}}
$$

$$
\mathbf {A _ {0}} \sim \mathbf {A _ {1 2}}
$$

$$
\overline {{\mathbf {O E}}}
$$

$$
\overline {{\text { WE }}}
$$

$$
\overline {{\mathbf {C S}}}
$$

存储器字扩展连接电路图■利用 8K×8bit 的 SRAM，构成 8K×16bit 内存。

内存位扩展连接

![](images/8b3202fa8362fd299d047a7386f141b1cd3de0fa5eb65fd200650b56948b2b02.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    subgraph_Memory_Days["Memory Data"]
        D0_7["D0~D7"] --> D0_7_D7["D0~D7"]
        A0_A0["A0"] --> D0_7_D7
        A10_A10["A10"] --> D0_7_D7
        MEMW_MEMW_MEMR["MEMW/MEMR"] --> D0_7_D7
        MEMR_MEMR["MEMR"]
    end

    subgraph_Control_Days["Control Signals"]
        D8_15["D8~D15"] --> D0_15_D0_D0_D7["D0~D7"]
        A0_A0["A0"] --> D0_15_D0_D0_D7
        A10_A10["A10"] --> D0_15_D0_D7
        MEMW_MEMW_MEMR["MEMW/MEMR"] --> D0_15_D0_D7
    end

    D8_15 --> AND["&"]
    A0_A0 --> AND
    A10_A10 --> AND
    MEMW_MEMR["MEMR"]
    A18["A18"] --> NOT1["1"]
    NOT1 --> OR1["≥1"]
    NOT1 --> OR1
    NOT1 --> Y0["Y0"]
    NOT1 --> E["E"]
    NOT1 --> E_bar["E̅"]
    NOT1 --> C["C"]
    NOT1 --> B["B"]
    NOT1 --> A["A"]
    A --> 4["4"]

    D0_7_D7 --> CS["CS"]
    D0_7_D7 --> WE["WE"]
    D0_7_D7 --> OE["OE"]
    D0_7_D7 --> WEbar["WE"]
    D0_7_D7 --> OEbar["OE"]

    D8_15 --> CS
    D8_15 --> WE
    D8_15 --> OE
    D8_15 --> WEbar
    D8_15 --> WE
    D8_15 --> Y0
    D8_15 --> Y0
    D8_15 --> Y0
    D8_15 --> Y0
    D8_15 --> Y0
    D8_15 --> Y0
    D8_15 --> Y0
    D8_15 --> Y0
    D8_15 --> Y0
    D8_15 --> Y0
    D8_15 --> Y
```
</details>

# 8086的内存接口

■ 8086 CPU是16位处理器。
■ 系统总线的数据线16位，即 $D_{0}$ $\sim D_{15}$
■ 内存奇偶分体。

- ~BHE(~代表低电位)
- A $_{0}$

<table><tr><td>~BHE A0</td><td>操作</td><td>所用数据线</td></tr><tr><td>0 0</td><td>从偶地址开始读/写一个字</td><td>AD15 ~ AD0</td></tr><tr><td>0 1</td><td>从奇地址读/写一个字节</td><td>AD15 ~ AD8</td></tr><tr><td>1 0</td><td>从偶地址读/写一个字节</td><td>AD7 ~ AD0</td></tr><tr><td>1 1</td><td>无效</td><td>无</td></tr></table>

8086 系统
![](images/cf4746da65be4bccd97d45a632e46852865041227c01dfda2be47be9ca277922.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    subgraph Bus
        A1["Address D0i<<D7"] --> B1["D0i<<D7"]
        A2["A1i<<A11"] --> B2["A0i<<A10"]
        MEMR["MEMR"] --> B3["OE"]
        MEMW["MEMW"] --> B4["WE"]
    end
    subgraph Bus
        C1["Address D8i<<D15"] --> D1["D0i<<D7"]
        A3["A1i<<A11"] --> D2["A0i<<A10"]
        MEMR["MEMR"] --> D3["OE"]
        MEMW["MEMW"] --> D4["WE"]
    end
    subgraph Bus
        E1["Address D1"] --> F1["iD1"]
        G1["Address G"] --> H1["G2A"]
        I1["Address Y0"] --> J1["G2B"]
    end
    B1 --> CS["CS"]
    D1 --> CS
    F1 --> CS
    J1 --> CS
    CS --> iD1["iD1"]
    B4 --> iD1
    D3 --> iD1
    B4 --> B7["&"]
    B7 --> G7["G"]
    B7 --> G8["G2A"]
    B7 --> G9["Y0"]
    G7 --> Y7
    G9 --> Y6
    style Bus fill:#f9f,stroke:#333
    style Bus fill:#ccf,stroke:#333
```
</details>

# 简单练习一下

- 将4片6264连接到8086系统，要求其内存范围70000h~77FFFh。

# 80386/486内存接口

# 80386、80486 的内存接口

■ 32位处理器。
■ 地址信号： $A_{2} \sim A_{31}$
■ 存储体选择信号： $\overline{\mathbf{BE}}_0 \sim \overline{\mathbf{BE}}_3$ （对应4个存储体）
■ 32位数据信号： $D_{0} \sim D_{31}$

# 80386/486内存接口

在80486系统中，利用4片容量为128 K×8 bit的SRAM芯片构成512 KB的内存

![](images/93b84f8d430a8f6cf61b9ba60191dab0b0405acd00404c23157c79f41026790d.jpg)

80386、80486系统中内存分体组织

# 80386/486内存接口

控制信号编码表示的总线周期

<table><tr><td>M/IO</td><td>D/C</td><td>W/R</td><td>总线周期</td></tr><tr><td>0</td><td>0</td><td>0</td><td>中断响应</td></tr><tr><td>0</td><td>0</td><td>1</td><td>停机</td></tr><tr><td>0</td><td>1</td><td>0</td><td>I/O读</td></tr><tr><td>0</td><td>1</td><td>1</td><td>I/O写</td></tr><tr><td>1</td><td>0</td><td>0</td><td>取指令操作码</td></tr><tr><td>1</td><td>0</td><td>1</td><td>保留</td></tr><tr><td>1</td><td>1</td><td>0</td><td>存储器读</td></tr><tr><td>1</td><td>1</td><td>1</td><td>存储器写</td></tr></table>

# 80486

# 内存芯片连接图

![](images/bf0ecf8dbf02a504e1fd0e25d0f0b6a5240649a038687bbe38547e4498443b89.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    A["74F138 Decoder"] -->|+5 V| B["74F138 Chip"]
    A -->|≥1| C["30-bit Memory Chip"]
    A -->|≥1| D["30-bit Output Chip"]
    A -->|≥1| E["Output DI24~DI31"]
    A -->|≥1| F["Output DI24~DI31"]
    A -->|≥1| G["Output DI24~DI31"]
    A -->|≥1| H["Output DI24~DI31"]
    A -->|≥1| I["Output DI24~DI31"]
    A -->|≥1| J["Output DI24~DI31"]
    A -->|≥1| K["Output DI24~DI31"]
    A -->|≥1| L["Output DI24~DI31"]
    A -->|≥1| M["Output DI24~DI31"]
    A -->|≥1| N["Output DI24~DI31"]
    A -->|≥1| O["Output DI24~DI31"]
    A -->|≥1| P["Output DI24~DI31"]
    A -->|≥1| Q["Output DI24~DI31"]
    A -->|≥1| R["Output DI24~DI31"]
    A -->|≥1| S["Output DI24~DI31"]
    A -->|≥1| T["Output DI24~DI31"]
    A -->|≥1| U["Output DI24~DI31"]
    A -->|≥1| V["Output DI24~DI31"]
    A -->|≥1| W["Output DI24~DI31"]
    A -->|≥1| X["Output DI24~DI31"]
    A -->|≥1| Y["Output DI24~DI31"]
    A -->|≥1| Z["Output DI24~DI31"]
    A -->|≥1| AA["Output DI24~DI31"]
    A -->|≥1| AB["Output DI24~DI31"]
    A -->|≥1| AC["Output DI24~DI31"]
    A -->|≥1| AD["Output DI24~DI31"]
    A -->|≥1| AE["Output DI24~DI31"]
    A -->|≥1| AF["Output DI24~DI31"]
    A -->|≥1| AG["Output DI24~DI31"]
    A -->|≥1| AH["Output DI24~DI31"]
    A -->|≥1| AI["Output DI24~DI31"]
    A -->|≥1| AJ["Output DI24~DI31"]
    A -->|≥1| AK["Output DI24~DI31"]
    A -->|≥1| AL["Output DI24~DI31"]
    A -->|≥1| AM["Output DI24~DI31"]
    A -->|≥1| AN["Output DI24~DI31"]
    A -->|≥1| AO["Output DI24~DI31"]
    A -->|≥1| AP["Output DI24~DI31"]
    A -->|≥1| AQ["Output DI24~DI31"]
    A -->|≥1| AR["Output DI24~DI31"]
    A -->|≥1| AS["Output DI24~DI31"]
    A -->|≥1| AT["Output DI24~DI31"]
    A -->|≥1| AU["Output DI24~DI31"]
    A -->|≥1| AV["Output DI24~DI31"]
    A -->|≥1| AW["Output DI24~DI31"]
    A -->|≥1| AX["Output DI24~DI31"]
    A -->|≥1| AY["Output DI24~DI31"]
    A -->|≥1| AZ["Output DI24~DI31"]
    A -->|≥1| BA["Output DI24~DI31"]
    A -->|≥1| BB["Output DI24~DI31"]
    A -->|≥1| BC["Output DI24~DI31"]
    A -->|≥1| BD["Output DI24~DI31"]
    A -->|≥1| BE["Output DI24~DI31"]
    A -->|≥1| BF["Output DI24~DI31"]
    A -->|≥1| BG["Output DI24~DI31"]
    A -->|≥1| BH["Output DI24~DI31"]
    A -->|≥1| BI["Output DI24~DI31"]
    A -->|≥1| BJ["Output DI24~DI31"]
    A -->|≥1| BK["Output DI24~DI31"]
```
</details>

# 80486

# 内存芯片连接图

![](images/bdb9439a06908cec1c1d5a8244cde565608218282ec4b7ef7a0c59fe009e0b2c.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    subgraph_Bit_1["2"]
        A1["A51"] -->|1| OR1["≥1"]
        A2["A50"] -->|1| OR1
        A3["A29"] -->|1| OR1
        A4["A28"] -->|1| OR1
        A5["A27"] -->|1| OR1
        A6["A26"] -->|1| OR1
        A7["A25"] -->|1| OR1
        A8["A24"] -->|1| OR1
        A9["A23"] -->|1| OR1
        A10["A22"] -->|1| OR1
        A11["A21"] -->|1| OR1
        A12["A20"] -->|1| OR1
        A13["A19"] -->|1| OR1
    end

    subgraph_Bit_2["1"]
        B1["21400000H~2147FFFFH"]
    end

    subgraph_Bit_3["31"]
        C1["≥1"]
        D1["≥1"]
        E1["≥1"]
        F1["≥1"]
        G1["≥1"]
        H1["≥1"]
        I1["≥1"]
        J1["≥1"]
        K1["≥1"]
        L1["≥1"]
        M1["≥1"]
        N1["≥1"]
        O1["≥1"]
        P1["≥1"]
        Q1["≥1"]
        R1["≥1"]
        S1["≥1"]
        T1["≥1"]
        U1["≥1"]
        V1["≥1"]
        W1["≥1"]
        X1["≥1"]
        Y1["≥1"]
        Z1["≥1"]
    end

    subgraph_Bit_4["4"]
        AA1["A29"] -->|1| OR2["≥1"]
        AB2["A28"] -->|1| OR2
        AC2["A27"] -->|1| OR2
        AD2["A26"] -->|1| OR2
        AE2["A25"] -->|1| OR2
        AF2["A24"] -->|1| OR2
        AG2["A23"] -->|1| OR2
        AH2["A22"] -->|1| OR2
        AI2["A21"] -->|1| OR2
        AJ2["A20"] -->|1| OR2
        AK2["A19"] -->|1| OR2

    end

    subgraph Data_Timing_Dots
        D0["D0~D7"] --> D0a["D0~D7"]
        D0b["D0~D7"] --> D0c["D0~D7"]
        D0d["D0~D7"] --> D0e["D0~D7"]
        D0f["D0~D7"] --> D0g["D0~D7"]
        D0h["D0~D7"] --> D0i["D0~D7"]
        D0j["D0~D7"] --> D0k["D0~D7"]
        D0l["D0~D7"] --> D0m["D0~D7"]
        D0n["D0~D7"] --> D0o["D0~D7"]
        D0p["D0~D7"] --> D0q["D0~D7"]
    end

    Note: Data_Timing_Dots are labeled as 'XXXXXX' with values in red text.
```
</details>

# Pentium处理器内存接口

# Pentium处理器的内存组织

■ 32位处理器。
■ 地址信号： $A_{3} \sim A_{31}$
■ 存储体选择信号： $\overline{\mathbf{BE}}_0 \sim \overline{\mathbf{BE}}_7$ （对应8个存储体）
■ 64位数据信号： $D_{0} \sim D_{63}$

# DRAM的典型工作形态

■ 64K×1bit
■ 行地址选定RAS
■ 列地址CAS
■ 读写切换只使用WE控制
■ 工作过程

· 读
·写
- 刷新

![](images/5a8a232aafc0779531b754052cf9f76699183f80a91b18fec056613a4f83ac69.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    A["ADDRESS"] --> B["Row latch CLOCK"]
    C["RAS"] --> B
    B --> D["Row decoder"]
    D --> E["Memory array"]
    E --> F["Sense and refresh amplifiers"]
    F --> G["DATA"]
    H["CLOCK Column latch"] --> I["Column decoder"]
    I --> E
    J["CAS"] --> H
    style A fill:#f9f,stroke:#333
    style C fill:#f9f,stroke:#333
    style H fill:#ccf,stroke:#333
    style J fill:#ccf,stroke:#333
```
</details>

# DRAM的典型工作形态

■ 64K×1bit
■ 行地址选定RAS
■ 列地址CAS
■ 读写切换只使用WE控制
■ 工作过程

· 读
·写
- 刷新

![](images/31ace833aa7f8b1298123c4415457da8ca455f60bdc4297d228e774c9b9c92f5.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph LR
    A["A0 ~ A7"] --> B["RAS"]
    A --> C["CAS"]
    A --> D["WE"]
    B --> E["DIN"]
    C --> F["DOUT"]
```
</details>

# DRAM的典型工作形态

读数据
![](images/2b9018f41627e0e4b4423a2301c927b804437fb5c30c2b18f70ab1c8441acc4e.jpg)

<details>
<summary>text_image</summary>

RAS
CAS
A₀ ~ A₇
行地址
列地址
WE
DOUT
①②
③④
读出数据
</details>

# DRAM的典型工作形态

写数据
![](images/229983070c20414995e92b8b782c78c31f722bb219fe49cd2b5ac84e3333e4e3.jpg)

<details>
<summary>text_image</summary>

提前写
RAS
CAS
A₀ ~ A₇ 行地址 列地址
WE
DIN ①② ③⑤ ⑥ ⑦
有效写入数据
</details>

# DRAM的典型工作形态

![](images/51c22e855080c30e54a844e123edbafe5bbf6afb3a3bf4d707cc65ec0ca9c90b.jpg)

<details>
<summary>text_image</summary>

刷新（行刷新）
RAS
CAS
A₀ ~ A₇
行地址
</details>

# SDRAM: Synchronized DRAM

- 同步机制

- 同步时钟
- SDRAM内部采用流水线
- 减少握手开销

- 内部组织结构

- 多个存储体(Bank): 2个, 4个, ……

- 读写方式

- 突发(Burst)读写功能

- 连续传输所涉及到存储单元（列）的数量。

# SDRAM: Synchronized DRAM

![](images/3dc0e8d4fe957854c5b17f60470b5f8b3f0375fe56c0e69afa1d28a3f2975e10.jpg)

# DDR SDRAM: Double Data Rate SDRAM

- 时钟double
- 在信号上升和下降沿都传输信息

- DDR 3 SDRAM
- 时钟8倍

- DDR 2 SDRAM

- 时钟4倍

![](images/25757d9c0f658d80b38d2694ef27b00ecf511c4d666c944dc78e74bc03b23633.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    A["CK#"] --> B["T0"]
    B --> C["T1"]
    C --> D["T2"]
    D --> E["T3"]
    E --> F["T4"]
    F --> G["T5"]
    G --> H["T6"]

    I["CK"] --> J["Command"]
    J --> K["READ"]
    K --> L["NOP"]
    L --> M["NOP"]
    M --> N["NOP"]
    N --> O["NOP"]
    O --> P["NOP"]
    P --> Q["NOP"]

    R["DQS, DQS#"] --> S["DQ"]
    S --> T["CL = 3 (AL = 0)"]

    U["DO n"] --> V["DO n + 1"]
    V --> W["DO n + 2"]
    W --> X["DO n + 3"]
```
</details>

# 其它RAM变种

- PSRAM, Pseudo-static RAM
- 内置刷新电路，外部伪装成SRAM
- NVRAM, Non-Volatile RAM

- 基于电池
- SRAM自带电池...

- 基于Flash
- 掉电之前，赶紧写到Flash

- FeRAM
- 铁基存储...

# SRAM v.s DRAM

# • SRAM

- 用稳态电路存信息，不需刷新
相对于DRAM，速度快、集成度低、功耗大、成本高

# DRAM

- 用暂态电路（电容）存信息，需刷新
- 地址采用复用技术，分行列两次加载， $\overline{RAS}$ 、 $\overline{CAS}$
相对于SRAM，速度慢、集成度高、功耗小、成本低
- 刷新（再生）方法：集中式、分散式、异步式
- 刷新控制电路：刷新计数器、刷新/访存裁决、刷新控制逻辑，是CPU和DRAM的接口

# ROM, all kinds of ROMs...

■ 特点：存储信息的非易失性。
■ 分类:

- 掩膜型Mask ROM
- 可编程ROM

# OTP-ROM

- 可擦可编程ROM

- EPROM
E2PROM: 并行、串行

- 闪速(Flash)存储器

- 或非型（NOR）阵列
- 与非型（NAND）阵列

# Mask ROM

- 工厂使用Mask工艺制
造，所以称为Mask ROM
- 有连接，高压被接地，
下方测得低电压，代表0
- 反之，代表1

- 水平是字线
- 垂直是位线

![](images/728ce9a7dad0cb8d0722e9287d4c7ccb656f951510b440b3e59f834c684b4684.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    A["曝光"] --> B["镀下一层膜"]
    B --> C["显影"]
    C --> D["蚀刻"]
    D --> E["去光阻"]
    E --> F["镀膜基板"]
    F --> G["光阻"]
    G --> H["曝光光源"]
    H --> I["掩膜版"]
    I --> J["光阻"]
    J --> K["镀膜"]
    K --> L["玻璃基板"]
    L --> M["显影"]
    M --> N["蚀刻"]
    N --> O["去光阻"]
    O --> P["镀膜基板"]
    P --> Q["光阻"]
    Q --> R["镀下一层膜"]
    R --> S["显影"]
    S --> T["蚀刻"]
    T --> U["去光阻"]
```
</details>

![](images/4a1c9a1602f5228514e6d8025bcb5bde6445f903a16281d1131b1a420dd65df8.jpg)

<details>
<summary>text_image</summary>

Word
lines from
decoder
44
0
1
0
</details>

# Mask ROM

- 一个8x4 ROM的例子

- word2输出为1010
- 物理连接在生产时固定，无法修改(ROM)

![](images/d9ff8cad092d47054314a4ef7770b31569c79aa4eb50434d329ffa8cd7778bfa.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    A["enable"] --> B["3×8 decoder"]
    C["A0"] --> B
    D["A1"] --> B
    E["A2"] --> B
    B --> F["word line"]
    B --> G["data line"]
    F --> H["Q3"]
    G --> I["Q2"]
    H --> J["Q1"]
    I --> K["Q0"]
    L word0 --> M["3×8 decoder"]
    N word1 --> M
    O word2 --> M
    P programmable connection --> M
    style M fill:#f9f,stroke:#333,stroke-width:2px
```
</details>

# OTP ROM: One-time Programmable ROM

- 每一个bit位点都有一个fuse
- 根据是否烧熔fuse编程1/0
- 其实，理论上，可以非常多次编程，只是。。。

![](images/436374766c0125712252f5ed0c69c85af7cb53f04195b9b122cf79eb5a2befe7.jpg)

<details>
<summary>text_image</summary>

Fuses to
burn out
Word
lines from
decoder
</details>

# EPROM: Erasable programmable ROM

- 使用Floating gate Avalanche-injected MOS (FAMOS)
- 正高压(+20v)于Control和Drain，编程0；
- UV照射20分钟，擦除，编程1；

- 为什么用UV?

![](images/e39f57c225be87ff01de89429f494519639724e2b7eed8574577302639c3eb97.jpg)

<details>
<summary>text_image</summary>

Control
Gate
S
G
D
N+
N+
</details>

![](images/a233ed1a383b3c94bd4115e72d1e41ac659a177f75342709f3b6ae0b4ad2464b.jpg)

<details>
<summary>text_image</summary>

Control
Gate
G
Floating
Gate
S
CFG
D
CFS
N+
N+
</details>

![](images/76ef69539a765cde4d1f71453fa447eed6e67f2076f247a23e13fac8cbbaa711.jpg)

<details>
<summary>text_image</summary>

80
356
04
20MPB
S4 16
C12
70
N1992
80
356
04
20MPB
S4 16
C12
70
N1992
80
356
04
20MPB
S4 16
C12
70
N1992
80
356
04
20MPB
S4 16
C12
70
N1987
80
356
04
20MPB
S4 16
C12
70
N1987
80
356
04
20MPB
S4 16
C12
70
N1987
80
356
04
20MPB
S4 16
C12
70
N1879
80
356
04
20MPB
S4 16
C12
70
N1879
80
356
04
20MPB
S4 16
C12
70
N1879
80
356
04
20MPB
S4 16
C12
70
N1992
</details>

# Flash Memory

- 是EEPROM的扩展

- 相同的floating gate结构
- 相同的读写持久性

- 主要改进

- 快速擦除（块擦除）

- 分Negate-OR和Negate-AND两类型

- NOR读取快，擦除慢，容量小
- NAND容量大，读写速度差小
- 适合作文件系统

# Flash Memory

- 是EEPROM的扩展

- 相同的floating gate结构
- 相同的读写持久性

- 主要改进

- 快速擦除（块擦除）

- Negate-OR和Negate-AND两类型

- NOR随机读取快，擦除慢，容量小
- 存储BIOS
- NVRAM

- NAND块读取，容量大，读写速度差小
- 适合作文件系统

NAND Flash || NOR Flash
![](images/a3bf01cde81e537a2e1e04d2ccfa2180a5c47a34e41dc375892ba3a78e51212b.jpg)

<details>
<summary>text_image</summary>

bit line
cell
NAND Flash
</details>

![](images/90b5ca6e0a4609f24ab6ce8d4e60f223f8cdfd493bd556a8065a98c7df86d619.jpg)

<details>
<summary>text_image</summary>

bit line
cell
NOR Flash
</details>

# EPROM/EEPROM连接

![](images/e5a594b3139b1144c14ba5de98ff72f56c1036f17cb7e9dbc5a845fd9a700107.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph LR
    A["地址"] --> B["有效地址"]
    B --> C["CE"]
    C --> D["OE"]
    D --> E["D₀~D₇"]
    E --> F["有效数据"]
```
</details>

![](images/7ccc1984bd443e6bd785bea15a53de53f396149206a3541f6fbf9d33635d734d.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    A["总线信号"] --> B["MEMR"]
    B --> C["1"]
    C --> D["C G2A"]
    D --> E["Y0"]
    F["2764"] --> G["LS138"]
    H["总线信号"] --> I["&"]
    I --> J["G2B"]
    J --> K["A19 A18 A17 A16"]
    I --> L["A16 A14 A13"]
    M["总线信号"] --> N["D0 D̂D7"]
    N --> O["D0 CE"]
    O --> P["A0 A1"]
    O --> Q["A0 VCC"]
    O --> R["A1 VPP"]
    O --> S["A12 PGM"]
    O --> T["A12 GN"]
    U["总线信号"] --> V["&"]
    V --> W["LS138"]
    X["总线信号"] --> Y["2764"]
    Z["总线信号"] --> AA["5V"]
    AB["总线信号"] --> AC["C"]
```
</details>

# 持久性v.s可写性

![](images/bb194141921520fe154a4fd03c36a9d879b54ac0c4529623b1c7988a0dc82e17.jpg)

# 其他存储器

- 多端口存储器
- 多体交叉存储器
- 相联存储器

# 多端口存储器

■ 应用：处理机之间的快速数据交换。
■ 分类:

- 双端口
- 三端口
- 四端口
●
■ ■ ■ ■ ■ ■

■ 双端口存储器

![](images/d567e6aed8cf086302f98556fd20fd1ac00847f6929f9c9e5d86c3082daf6f6b.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    A["CPU"] <--> B["存储器"]
    C["μP"] <--> B
    D["I/O"] <--> B
    B --> E["I/O"]
    style B fill:#f9f,stroke:#333
```
</details>

# 多端口存储器

# ■读/写操作

- 地址信号 $\Rightarrow \mathbf{AD}_0 \sim \mathbf{AD}_7$
- $\overline{\mathbf{CS}}$ 下降沿锁存地址于芯片内部。

- 在CS和OE同时为低电平时，相应地址单元中的内容被读出。

![](images/23ad220c6095501e7a325453f9803b2fdbaec0031dc1cb96e07105ff79eaf53f.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph LR
    A["AD0A"] --> B["DS1609"]
    C["AD7A"] <-- B
    D["OE_A"] --> B
    E["WE_A"] --> B
    F["CS_A"] --> B
    G["OE_B"] <-- B
    H["WE_B"] <-- B
    I["CS_B"] <-- B
    B --> J["AD0B"]
    B --> K["AD7B"]
```
</details>

![](images/0dd4b087b109130b5f6cd5f57fc2b792530a89930704cc93e04a9dc512e8c1f6.jpg)

<details>
<summary>text_image</summary>

AD₀ ~ AD₇
地址
数据
CS
OE
</details>

# 多端口存储器

# ■读/写操作

- 允许:

- 对不同存储单元：

- 同时读。

- 同时写。

- 对同一存储单元：

- 同时读。

- 一个端口写，另一端口读。

- 不允许:

- 两个端口同时对同一存储单元写数据

- 消除竞争

![](images/159a3cd088a07eab124b842ef84476cd4300bfcd2d00dde8ebf5d65001172299.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph LR
    A["AD0A"] --> B["DS1609"]
    C["AD7A"] <-- B
    D["OE_A"] --> B
    E["WE_A"] --> B
    F["CS_A"] --> B
    G["OE_B"] <-- B
    H["WE_B"] <-- B
    I["CS_B"] <-- B
    B --> J["AD0B"]
    B --> K["AD7B"]
```
</details>

# 多端口存储器

# ■竞争的消除

- 一边只写、一边只读
信号灯

![](images/2b36a3ae321da5da6045eaf58565de1b22ef2f1d0c3f8e3469e4b2382e7f97e5.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph LR
    A["AD0A"] --> B["A状态"]
    C["AD7A"] --> D["B状态"]
    B --> E["AD0B"]
    D --> F["AD7B"]
    G["OE_A"] --> H["DS1609"]
    I["WE_A"] --> H
    J["CS_A"] --> H
    K["OE_B"] --> H
    L["WE_B"] --> H
    M["CS_B"] --> H
```
</details>

![](images/1e6b92c96c443d1d5a11b0bb6a0f677df96da12779ad812aee13bc2b44cb1192.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    A["读对方状态"] --> B{写?}
    B -->|Y| C["延时"]
    B -->|N| D["写自己的写状态"]
    D --> E["读对方状态"]
    E --> F{写?}
    F -->|Y| C
    F -->|N| G["写数据到完"]
    G --> H["去掉自己写状态"]
```
</details>

某一端口的写过程

# 多端口存储器

双端口存储器常用的场合：

■ CPU←→ DMA设备 或
CPU←→ IOP(IO处理机) }并行访问内存

■ 多机系统:

![](images/3e2fb35c1511a63a0fd74cf46d27c66874a5d453f8baed13b5f82e12745aaecf.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph LR
    A["CPU"] <--> B["双端口存储器"]
    B <--> C["CPU"]
```
</details>

■ CPU内部：通用寄存器为运算器的两个输入端同时提供操作数。
■ 多级存储体系：Cache采用双端口结构。

![](images/251a4274868cf7e6d