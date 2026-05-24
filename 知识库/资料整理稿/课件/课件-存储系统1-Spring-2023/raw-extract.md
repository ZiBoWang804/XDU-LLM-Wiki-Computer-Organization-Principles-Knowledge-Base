# 计算机组成与结构

# —存储系统1

李瑞 教授

蒋志平 讲师

计算机科学与技术学院

# 温故

- 简述补码(booth)法乘法原理?   
- 原码除法中，商符号怎么定？余数符号怎么定？  
- 简述原码恢复余数除法？   
- 简述加减交替除法，以及它的工作原理？  
- 简述补码除法的运算规则?   
- 简述浮点加减法的步骤?   
- 简述浮点乘除法的步骤?

# 7 存储系统

- 存储系统的层次结构  
- 通用寄存器  
- Cache   
- 主存（一级）  
- 外存储（二级）  
- 脱机/离线/网络存储（三级）

Primary storage   
![](images/321533afbc255fab12d431bc9453f5a0cfcc7c7a127e0bdbb4a79d13b7f57411.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph LR
    A["Central processing unit"] --> B["Logic unit"]
    A --> C["Registers"]
    A --> D["Cache memory"]
    E["Memory bus"] --> F["Main memory\nRandom access memory\n256-1024 MB"]
```
</details>

Input/output channels

Secondary storage   
![](images/171b6f292e96647dd7d611c3ab09451391142e91180ed85a76fcd2e32cbf9f97.jpg)

<details>
<summary>text_image</summary>

Mass storage device
Hard disk
20-120 GB
</details>

Off-line storage   
![](images/a0199b4998bca19951fdd4bb7396d4bdc9550c33a0572f3caa08047c6ab48ab9.jpg)

<details>
<summary>text_image</summary>

Removable media drive
CD-RW, DVD-RW drive

Removable medium
CD-RW
650 MB
</details>

Tertiary storage   
![](images/45fca664585bff6c68c84dd33a8d1aae4973cf5560a1231055945e23635a589d.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    A["Removable media drive"] --> B["Removable medium"]
    B --> C["Robotic access system"]
    C --> D["Removable medium"]
```
</details>

# 关于存储的所有描述...

- 物理类型  
- 容量  
- 性能  
- 可靠性  
- 功耗   
- 价格

# 存储类型

- 半导体  
- 寄存器、Cache、内存、闪存、SSD、EEPROM  
- 磁性  
- 硬盘、罗盘、磁带   
- 光学

• CD / DVD / BD -ROM   
• CD-R/RW, DVD-R/RW

# 存储类型

\- 已有系统的尝试整合优化

- RAID   
- SSD   
- Cache + HD   
- Cache + SSD   
- Cache + SSD + HD

\- 还有什么存储类型?

# 存储类型

# - 纸/屏幕啊

- “纸带”、条码、二维码、答题卡...   
- Screen/Camera-Communication

# 容量

容量 = 存储单元数 × 每个存储单元的位数

$$
1 \mathrm{B} = 8 \mathrm{b} \quad \mathrm{b} = \text {bit} \quad \mathrm{B} = \text {Byte}
$$

$$
1 \mathrm{KB} = 2 ^ {\wedge} 1 0 \text {Byte} \quad \mathrm{KB} = \text {KiloByte}
$$

$$
1 \mathrm{MB} = 2 ^ {\wedge} 2 0 \text {   Byte   } \quad \mathrm{MB} = \text { MegaByte }
$$

$$
1 \mathrm{GB} = 2 ^ {\wedge} 3 0 \text {Byte} \quad \mathrm{GB} = \text {GigaByte}
$$

$$
1 \mathrm{TB} = 2 ^ {\wedge} 4 0 \text {Byte} \quad \mathrm{TB=TeraByte}
$$

$$
1 \mathrm{PB} = 2 ^ {\wedge} 5 0 \text {Byte} \quad \mathrm{PB=PetaByte}
$$

$$
1 E B = 2 ^ {6} 0 \text {   Byte   } \quad E B = E x a B y t e
$$

$$
1 Z B = 2 ^ {7} 0 \text {Byte} \quad Z B = Z e t t a B y t e
$$

$$
1 \mathrm{YB} = 2 ^ {\wedge} 8 0 \mathrm{Byte} \quad \mathrm{YB} = \text {YottaByte}
$$

# 容量

<table><tr><td>类型</td><td>容量(高性能专业工作站)</td></tr><tr><td>CPU 寄存器</td><td>&lt; 10KB</td></tr><tr><td>CPU Cache (L1, L2, L3)</td><td>&lt; 30MB</td></tr><tr><td>内存</td><td>&lt; 1T</td></tr><tr><td>外存(SSD + Harddisk)</td><td>&lt; 1P</td></tr></table>

# 性能

我们需要快速的存储，

但是

如何定义快速？

# 性能

# “快”，是一个复合的指标

# - 存取时间

- 对存储器中某一个单元的数据进行一次读/写的时间  
- 不同类型存储的存取时间？

# - 存取周期

- 存取周期 = 存取时间 + “预热时间” + “结束时间”;  
- 不同类型存储的存取周期？

# 性能

# - 存取带宽

- 单位时间里存储器可以读出的字节数  
- 最大理论存取速度 v.s 最小理论存取速度  
- 不同类型存储的存取带宽？

# - 随机访问速度

- 对“任意目标数据块”的存取时间  
- 不同类型存储的随机访问速度?

# 性能

\- 读/写速率比

- 存储器的读/写速度一般都不相同，  
- 不同类型存储的读写速率比?

\- 存取粒度

- 存储器读/写操作的最小单元尺寸  
- 不同类型存储的存取粒度?

# 性能

一架A380货机...

大约可以装1.8亿个microSD卡...

如果microSD容量是1TB,

则这架飞机的容量是180EB....

如果，从NY飞到LA用大约5个小时...

则这架飞机的存取速度可达10PB/s !!

![](images/9f998fc6a944539091c38afc7cf2c3ffcf63e39a15d4d828179f7005c2183783.jpg)

<details>
<summary>text_image</summary>

JUST
JOKING
</details>

![](images/e294d5aa32e331c34adbbaed2150fc581dde6685c9db4cdaafcab50fc1673de7.jpg)

<details>
<summary>text_image</summary>

1024GB TF card
Premium+►
</details>

# 性能

- 但人肉运输数据是真的！！！  
• Amazon Snowball : 80TB/23kg   
• Amazon SnowMobile: 100PB/TRUCK!

![](images/bf8ccc9db14af99a8e56da59fd83e7ab4432f7f0ae7c0b98b6ec1888b9e45cb8.jpg)

<details>
<summary>natural_image</summary>

Man in suit adjusting a tablet device (no visible text or symbols)
</details>

![](images/6c1678b6118fed8b30c56108b74387ecd617fadd62db3b2125365dbd7fb460d8.jpg)

<details>
<summary>natural_image</summary>

White semi-truck parked on a road with a shipping container and sunset sky in the background (no visible text or symbols)
</details>

# 可靠性

• MTBF (Mean Time between Failure):

\- 可维修部件

\- MTTF (Mean Time to Failure):

\- 不可维修部件

• Days in Use for SSD:

\- SSD的使用时间最相关

• Terabytes Written for SSD (TBW):

\- SSD生命周期内最大可写入数据量, QLC < MLC \~ SLC

# 功耗

- 低功耗，可以减少对电源的要求，并提高可靠性。  
- 但实际上，与直觉相反...  
- Cache > Memory > SSD > harddrive

# 7.2主存储器

# 主存储器

\- 随机读写存储器(RAM)

\- 静态/动态RAM

\- 只读存储器(ROM)

# 随机读写存储器RAM

---- RANDOM ACCESS MEMORY

- SRAM 静态随机读写存储器  
- DRAM 动态随机读写存储器

- 常规RAM芯片，其外部有地址引线、数据引线和控制信号引线。  
- 地址引线在芯片内部译码，选中芯片内部的相应存储单元。  
- 某静态RAM芯片上有n条地址线时，地址线上所能表示的地址编码就有 $2^{n}$ 种。这就意味着该芯片内部有 $2^{n}$ 个存储单元。

# 随机读写存储器RAM

\- SRAM，目前主流的实现方式，是基于MOSFET

![](images/1f3edf47da3150e9628f4a59cbb631d91b5841092ca40cba0c067a83334f133c.jpg)

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

![](images/2bf5da4a484bafe3492199f18f5ca0b5077ea8a313b7058fd5741741f8a06455.jpg)

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
![](images/6731cf63f4fc846318fc7177f6ebc4c7028d2eb1e75b2ead6e07d77c1c74ac64.jpg)

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

![](images/412eb8a4c85deece5ded6747a85f1ede6b47505ba9442cc83aac15854d9d4b15.jpg)

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

![](images/6b99e0147d76e654af043f027552a41fae7e80e3b8f8b405bd15f8527ed9e525.jpg)

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

6T SRAM基本存储单元

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

# 随机读写存储器RAM

![](images/31e8210e63121c5f0863e44374eef0a636004f1ff6c886e0f6ff21ccb29c280a.jpg)

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
    T1 --> A
    T2 --> B
```
</details>

6T SRAM基本存储单元

![](images/009c814115f29aafa6763e866830bf6db37481679ac0c0581c7608a9d8875aef.jpg)

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
    style A fill:#f9f,stroke:#333
    style B fill:#f9f,stroke:#333
    style T1 fill:#ccf,stroke:#333
    style T2 fill:#ccf,stroke:#333
    style Gnd fill:#cfc,stroke:#333
    note right of A
        Cross
```
</details>

4T2R SRAM基本存储单元

# 随机读写存储器RAM

![](images/5c5cd9457614f9e0e7c8e53d9e4fca75c1c426574d2419bd6c75479ec1071397.jpg)

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

![](images/4507858c42d7ac529da82e8471796b4ad54c4711e4a3e11b3aeb0f19566a7036.jpg)

<details>
<summary>natural_image</summary>

Microscopic view of rod-shaped bacterial cells with visible cell walls and internal structures (no text or labels)
</details>

65 nm [Bai04]

![](images/5d9f6660f2d2d265aeea65e496b9a0532ba8ae366bd7e2dd2f0063bbbb8f6244.jpg)

<details>
<summary>natural_image</summary>

Microscopic view of rectangular structures with dashed outlines, no visible text or symbols
</details>

45 nm [Mistry07]

![](images/7648e855af4638a9e35965d714e5f3c50084db206c84d94f169a57e378557992.jpg)  
32 nm [Natarajan08]

![](images/6ee75d5610b35a6fbc3632a7483e2e0b295f744d6d97c38ef9d719a23923114e.jpg)

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
• 3T-DRAM

![](images/e870fc41598319c3ae1c108850c3e69c8054eb42583f667128a04cb7521cd187.jpg)

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

![](images/bbfc636faf9aa0b8278d669046e0420bc79ec87e2ca02f0316efe6c3d36f0019.jpg)

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
• 3T-DRAM (reading is non-destructive)

![](images/152b59d0b79e6ae39ab15e0c2163aed6d0281ffbea3d10ec0bc20df5e26a6e27.jpg)

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

![](images/e52afb1c1cb6694597fba3050044634a5c41b80f0c72c7e09673bfcb0a9f34b9.jpg)

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
• 1T-DRAM (reading is destructive)

![](images/7986a65f42b8da2348000649173bef6dc317a796118e64a044280a57a77991b0.jpg)

<details>
<summary>text_image</summary>

WL
BL
M₁
Cₛ
CBL
</details>

![](images/d3be9281634d791953275a24100d8efe7f39222a6dcbf35b781ed74985b6fbcd.jpg)

<details>
<summary>text_image</summary>

WL Write 1 Read 1
X GND
BL sensing
</details>

# 随机读写存储器RAM

• SRAM v.s DRAM?

- SRAM基于互锁6T结构，通电时初始保持（静态）；  
- DRAM基于电容，会漏电（动态）需要定时充电；

\- 充电如何实现？

\- 读出来再写进去!

# 随机读写存储器RAM

![](images/9b76442b2edf2f94c47d6cb9b9d477d80353cd06e8f6cfe1aa977ead08f16ced.jpg)

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

![](images/bcd145ccd8a33721eb7d90ff8c1868675bc4ef67b801ad2ef770957aa771e995.jpg)

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

![](images/c2a12418eb08e687d1141b977d63f3dbcc42a4eff91932df3464b43335a4ebf6.jpg)

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
    Z1 --> AA1["○"]
    Z2 --> AA2["○"]
```
</details>

(b)   
RAM芯片内部的两种译码方式

# 存储器基本组成

![](images/6745019cf9008fa73b93dd06d3131b8aba1a29d3eb45aa61e33213d861c22e37.jpg)

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

![](images/ce1f8cb16acdf97b780cfd6dfb8d4e34401a48a080388c06e148f543b8eaf023.jpg)

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

![](images/aadc613969821c89e351326ee9459aaf7bd7a40f40226147da63a522fe2d479c.jpg)

<details>
<summary>text_image</summary>

CPU周期
地址
数据
WR
</details>

(a)

![](images/e141b17972bd958c95c8231b0652db65052248c33ba60c933afcf20c1438a20c.jpg)

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

![](images/9a88834723502b755f6e4b4c041976c4d3b3d56f292ea9700d4fedec9056d1f7.jpg)

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

A0 \~ A12为13条地址信号线

D0 \~ D7为8条双向数据线

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

\- 利用 8K×8bit 的 SRAM, 构成 32KB 内存。

![](images/83e15bfcd724c0c4e7b790780e49586eff9782f56bbf1309349fe6934d3373af.jpg)

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
![](images/c05c1974baac8adbceb0500333dfcda3ee3b8d23381a41d9662d45058831e3f2.jpg)

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

![](images/9241f92ead7d02d4bf29f45bdbb85a6a44b52c02f1374bb12ef69dc6825ffea9.jpg)

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

![](images/fa3e54ae68e8496c86fd79b27fce3edcbe795776e2fd6c5fd13b3e19d85ffaff.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    subgraph_Memory_Days["Memory D0~D7"]
        A0["A0"] --> D0["D0~D7"]
        A10["A10"] --> D0
        MEMW_MEMW["MEMW"] --> D0
        MEMR_MEMR["MEMR"] --> D0
    end

    subgraph_Data_Days["Data D8~D15"]
        A0["A0"] --> D0_D0["D0~D7"]
        A10["A10"] --> D0_D0
        MEMW_MEMW["MEMW"] --> D0_D0
        MEMR_MEMR["MEMR"] --> D0_D0
    end

    subgraph_Decoder["74LS138 Y0"]
        E1["E̅E̅Y0"] --> AND["&"]
        E2["E̅CBA"] --> AND
        AND --> OR["≥1"]
        OR --> OR
    end

    D0_D0 -->|CS| D0_D7
    D0_D7 -->|CS| D0_D8
    D0_D8 -->|CS| D0_D9
    D0_D9 -->|CS| D0_D15
    A18["A18"] --> NOT1["1"]
    A19["A19"] --> NOT2["≥1"]
    A17["A17"] --> NOT3["≥1"]
    NOT1 --> OR
    NOT2 --> OR
    NOT3 --> OR
    NOT4["A14"] --> NOT5["≥1"]
    NOT6["A11"] --> NOT7["≥1"]
    NOT7 --> OR
```
</details>

# 8086的内存接口

■ 8086 CPU是16位处理器。  
■ 系统总线的数据线16位，即 $D_{0} \sim D_{15}$ 。  
■ 内存奇偶分体。

- \~BHE(\~代表低电位)  
• A $_{0}$

<table><tr><td>~BHE A0</td><td>操作</td><td>所用数据线</td></tr><tr><td>0 0</td><td>从偶地址开始读/写一个字</td><td>AD15 ~ AD0</td></tr><tr><td>0 1</td><td>从奇地址读/写一个字节</td><td>AD15 ~ AD8</td></tr><tr><td>1 0</td><td>从偶地址读/写一个字节</td><td>AD7 ~ AD0</td></tr><tr><td>1 1</td><td>无效</td><td>无</td></tr></table>

8086 系统  
![](images/fe740d0501dd06ce3fbf17deb0b7aba72706ed7d6134621e44de2243bb41b129.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
    subgraph Bus
        D0i["D₀i<<D₇"] --> D0iD7["D₀i<<D₇"]
        A1i["A₁i<<A₁₁"] --> A0iA10["A₀i<<A₁₀"]
        MEMR["MEMR"] --> OE["OE"]
        MEMW["MEMW"] --> WE["WE"]
    end

    subgraph Bus
        D8i["D₈i<<D₁₅"] --> D0iD7["D₀i<<D₇"]
        A1i["A₁i<<A₁₁"] --> A0iA10["A₀i<<A₁₀"]
        MEMR["MEMR"] --> OE2["OE"]
        MEMW["MEMW"] --> WE2["WE"]
    end

    subgraph Bus
        D1i["D₁I"] --> iD1["iD1"]
        A1i --> iD1
        MEMR --> iD1
        MEMW --> iD1
    end

    subgraph Bus
        BHE["BHE"] --> G["G"]
        A19["A₁₉"] --> G2A["G̅2A"]
        A18["A₁₈"] --> G2B["G̅2B"]
        A17["A₁₇"] --> G2A
        A16["A₁₆"] --> G2B
        A15["A₁₅"] --> G2A
        A14["A₁₄"] --> G2B
        A13["A₁₃"] --> G2A
        A12["A₁₂"] --> G2B
    end

    subgraph Bus
        G2A --> Y0["Y₀"]
        G2B --> Y0
        C["C"] --> Y0
        B["B"] --> Y0
        A["A"] --> Y0
    end

    style Bus fill:#f9f,stroke:#333,stroke-width:2px
    style Bus fill:#ccf,stroke:#333,stroke-width:2px
```
</details>

# 简单练习一下(后场)

\- 将4片6264连接到8086系统，要求其内存范围70000h\~77FFFh。