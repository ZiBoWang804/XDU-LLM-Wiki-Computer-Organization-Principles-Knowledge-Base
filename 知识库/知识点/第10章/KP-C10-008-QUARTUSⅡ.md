---
id: KP-C10-008
title: QUARTUS Ⅱ
aliases:
  - KP-C10-008
chapter: 第10章
topic: 设计语言与工具
type: concept
section_code: 10.2.4
source_refs:
  - ../../资料整理稿/教材/课本-计算机组成与设计-425-497/课本-计算机组成与设计-425-497.md

prerequisites:
  - KP-C10-007

related_points:
  - KP-C10-007
contrast_with: []
status: seeded_from_textbook
updated: 2026-05-20
---

# QUARTUS Ⅱ

## 定义

本知识点对应教材第10章 `10.2.4` 小节，当前版本是从教材整理稿沉淀出的首轮规范草稿，后续仍可继续精炼。

## 课程资料中的表述

- 正如前面提到的那样，每一个FPGA/CPLD厂家都会为自己的产品提供开发环境。在这里，仅简单说明QUARTUSⅡ。其他还有许多厂家提供开发平台，此处不予说明。
- QUARTUSⅡ是由厂家Altera提供的集成开发软件。它是早已广泛使用的MAXplus的更新换代产品，具有更好的性能。
- QUARTUSⅡ的模块化的编译器包括 功能模块的分析及综合器（Analysis&Synthesis）、适配器（Fitter）、装配器（Assembler）、时序分析器（TimingAnalyzer）、设计辅助模块(Design Assistant）、EDA网表文件生成器(EDA NetlistWriter）、编译数据库接口(CompilerDatabaseInterface)等模块。
- 此外，QUARTUSⅡ还包含构建复杂系统时所需要的LPM(功能模件库)。该库中功能模块很丰富，在系统设计过程中可很方便地调用。
- QUARTUSⅡ设计工具全面支持VHDL或Verilog设计流程,其内部包含VHDL或Verilog逻辑综合器。同时,QUARTUSⅡ也支持第三方的综合工具和仿真工具。在FPGA基础上，利用QUARTUSⅡ进行设计开发的流程与图10-1相似，现简略说明如下。
- （1）为设计建一个文件夹。文件夹用英文命名。
- （2）设计输入。
- QUARTUSⅡ软件在File菜单中选择New 选项。再在窗口引导下完成VHDL文件的输人。

## 结构 / 规则 / 公式

当前建议先回读对应教材整理稿，提炼本节中的核心结构、规则或公式。

## 易混点 / 易错点

- 当前页面为首轮种子页，易混点仍需结合后续整理逐步补充。

## 常见关联场景

- 来自教材第10章 `10.2.4` 小节的核心内容入口。

## 相关知识点

- [[KP-C10-007]]

## 出处

- [教材整理稿片段](../../资料整理稿/教材/课本-计算机组成与设计-425-497/课本-计算机组成与设计-425-497.md)
