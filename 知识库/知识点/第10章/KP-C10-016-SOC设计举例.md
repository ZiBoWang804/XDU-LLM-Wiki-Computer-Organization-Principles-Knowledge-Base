---
id: KP-C10-016
title: SOC设计举例
aliases:
  - KP-C10-016
chapter: 第10章
topic: SOC设计
type: mechanism
section_code: 10.4.4
source_refs:
  - ../../资料整理稿/教材/课本-计算机组成与设计-425-497/课本-计算机组成与设计-425-497.md

prerequisites:
  - KP-C10-015

related_points:
  - KP-C10-015
contrast_with: []
status: seeded_from_textbook
updated: 2026-05-20
---

# SOC设计举例

## 定义

本知识点对应教材第10章 `10.4.4` 小节，当前版本是从教材整理稿沉淀出的首轮规范草稿，后续仍可继续精炼。

## 课程资料中的表述

- 在这里，将要说明基于FPGA的SOC设计。设计步骤在本节的前面已经说明。这里要强调的是现阶段设计构成SOC的方案有多种。第一种是基于FPGA嵌人IP硬核的SOC系统，即在FPGA中事先植人嵌人式系统处理器，目前最常用的嵌人式处理器大多采用了含有ARM的32位知识产权处理器核的器件。第二种是基于FPGA嵌人IP软核的SOC系统，目前最有代表性的软核处理器分别是Altera公司的NiosⅡ核，以及Xilinx公司的MicroBlaze核。第三种是基于HardCopy技术的SOC系统，HardCopy就是利用原有的FPGA开发工具，将成功实现于FPGA器件上的SOC系统直接转化为ASIC。
- 设计SOC必须有平台的支持，在设计平台的支持下，国内外许多单位已成功地将51单片机、Nios、MicroBlaze、ARM和MIPSRISC等多种处理器内核嵌入到各种可编程逻辑器件中并实现了SOC的设计。其中在国内应用最多的要数Xilinx公司和Altera公司所提供的开发平台。
- Xilinx提供了针对MicroBlaze核应用系统开发的集成开发环境MDK，该开发环境包含了用于硬件描述和系统生成的PlatformGenerator、用于软件设计和编译的MicroBlazeIDE。调试可通过FPGA配置JTAG接口进行，无需任何附加的调试硬件，配合FoundationISE4.2和FPGA目标板即可进行全功能开发。MDK还包含了UART、GPIO、Watchdog、Timer/Counter、EMC和中断控制等基本处理器外设库。同时，用户还可以添加兼容于OPB总线标准的任意IP核。Xilinx最近推出的系统生成器工具，可以直接连接使用第三方的MATLAB和Simulink系统工具。
- Altera的QUARTUSI为设计者提供了功能齐全的开发平台。QUARTUSⅡ包括功能模块分析/综合器、适配器、装配器、时序分析器。EDA网表生成器、设计辅助模块及编辑数据接口等组成的编译器；还包括设计中十分有用的参数化模块库LPM。值得一提的是，在QUARTUSⅡ之下,利用Matlab和Altera 公司的DSPBuilder,设计者可以为 Nios I软核处理器设计各种类型的DSP硬件加速器，并以指令的方式加人NiosⅡ的指令集，从而可以构建自己的DSP处理器系统。QUARTUSI还可以利用第三方所提供的综合工具。同时，QUARTUSⅡ也支持第三方所提供的仿真工具。
- 因此，就目前情况而言，设计基于FPGA的SOC还是根据需求，采用上述某家公司的开发工具，同时采用其提供的合适型号的FPGA，这样做比较省事，可达到事半功倍的效果。
- 下面以 AItera的QUARTUSⅡ为支撑平台，简要地说明基于FPGA的 SOC设计过程。由于利用了Altera的QUARTUSⅡ的开发工具，显然，在前面设计方案论证时已经决定在SOC中要使用Nios处理器及Altera 所提供的IP核。只有用到的IP核Altera暂不能提供时，才考虑使用第三方提供的或者自行开发。
- 基于 NiosⅡ处理器核的 SOC 框架图如图10-22所示。
- 图10-22以 NIOSⅡ为核心构成 SOC

## 结构 / 规则 / 公式

当前建议先回读对应教材整理稿，提炼本节中的核心结构、规则或公式。

## 易混点 / 易错点

- 当前页面为首轮种子页，易混点仍需结合后续整理逐步补充。

## 常见关联场景

- 来自教材第10章 `10.4.4` 小节的核心内容入口。

## 相关知识点

- [[KP-C10-015]]

## 出处

- [教材整理稿片段](../../资料整理稿/教材/课本-计算机组成与设计-425-497/课本-计算机组成与设计-425-497.md)
