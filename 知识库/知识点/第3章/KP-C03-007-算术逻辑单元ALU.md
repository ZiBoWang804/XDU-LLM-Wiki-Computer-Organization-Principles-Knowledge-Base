---
id: KP-C03-007
title: 算术逻辑单元ALU
aliases:
  - KP-C03-007
chapter: 第3章
topic: 算术逻辑单元
type: structure
section_code: 3.2.2
source_refs:
  - ../../资料整理稿/教材/计算机组成与设计-第3章-59-95/计算机组成与设计-第3章-59-95.md

prerequisites:
  - KP-C03-006

related_points:
  - KP-C03-006
contrast_with: []
status: seeded_from_textbook
updated: 2026-05-20
---

# 算术逻辑单元ALU

## 定义

本知识点对应教材第3章 `3.2.2` 小节，当前版本是从教材整理稿沉淀出的首轮规范草稿，后续仍可继续精炼。

## 课程资料中的表述

- 前人将算术运算、逻辑运算以至于移位功能结合到一起，研制出算术逻辑单元(ALU)集成电路。其中，中规模集成电路74181是一种4位的算术逻辑单元电路。
- 74181的引线如图3-26所示。74181有正逻辑工作的芯片，也有负逻辑工作的芯片，
- 图3-26所画的是工作在正逻辑的。74181的运算功能列于表3-8中。
- 由表3-8可以看到，74181有很多功能，在芯片上的控制信号的控制下，可实现各种算术运算和逻辑运算，这里不再做仔细说明。在此要强调的是74181内部已集成了在本章前面图3-3所示的先行进位电路，使74181的4位加法的延迟时间很小。同时，为了提高级联工作的速度，74181可以输出 $\mathrm { G } _ { \mathfrak { i } + \mathfrak { z } } ^ { * }$ 和 $\mathrm { P } _ { \mathrm { i } + 3 } ^ { \ast }$ ，即芯片上的G和P。
- 图3-264位ALU74181引线
- 表3-874181的运算功能
- <table><tr><td>操作选择</td><td colspan="3">运算功能</td></tr><tr><td> $\mathbf { S } _ { 3 } \mathbf { S } _ { 2 } \mathbf { S } _ { 1 } \mathbf { S } _ { 0 }$ </td><td rowspan="2">M=1</td><td colspan="2">M=0 算术运算</td></tr><tr><td>逻辑运算</td><td>Cn=1无进位</td><td>Cn=0有进位</td></tr><tr><td>0000</td><td>F=A</td><td>F=A</td><td>F=A加1</td></tr><tr><td>0001</td><td>F=A+B</td><td>F=A+B</td><td>F=(A+B)加1</td></tr><tr><td>0010</td><td>F=AB</td><td>F=A+B</td><td>F=(A+B)加1</td></tr><tr><td>0011</td><td>F=0</td><td>F减1</td><td>F=0</td></tr><tr><td>0100</td><td>F=AB</td><td>F=A加AB</td><td>F=A加AB加1</td></tr><tr><td>0101</td><td>F=B</td><td>F=(A+B)加 AB</td><td>F（A+B)加AB加1</td></tr><tr><td>0110</td><td>F=AOB</td><td>F=A减B减1</td><td>F=A减B</td></tr><tr><td>0111</td><td>F=AB</td><td>F=AB减1</td><td>F=AB</td></tr><tr><td>1000</td><td>F=A+B</td><td>F=A+AB</td><td>F=A加AB加1</td></tr><tr><td>1001</td><td>F=AB</td><td>F=A+B</td><td>F=A加B加1</td></tr><tr><td>1010</td><td>F=B</td><td>F=(A+B)加AB</td><td>F=(A+B)加AB加1</td></tr><tr><td>1011</td><td>F=AB</td><td>F=AB减1</td><td>F= AB</td></tr><tr><td>1100</td><td>F=1</td><td>F=2A</td><td>F=A加A加1</td></tr><tr><td>1101</td><td>F=A+B</td><td>F=(A+B)加A</td><td>F=(A+B)加A加1</td></tr><tr><td>1110</td><td>F=A+B</td><td>F=(A+B)加A</td><td>F=(A+B)加A加1</td></tr><tr><td>1111</td><td>F-A</td><td>F=A减1</td><td>F=A</td></tr></table>
- 单独一片74181只能实现4位的算术或逻辑运算。显然，4位运算的精度太低，但

## 结构 / 规则 / 公式

当前建议先回读对应教材整理稿，提炼本节中的核心结构、规则或公式。

## 易混点 / 易错点

- 当前页面为首轮种子页，易混点仍需结合后续整理逐步补充。

## 常见关联场景

- 来自教材第3章 `3.2.2` 小节的核心内容入口。

## 相关知识点

- [[KP-C03-006]]

## 出处

- [教材整理稿片段](../../资料整理稿/教材/计算机组成与设计-第3章-59-95/计算机组成与设计-第3章-59-95.md)

## 关联题型索引

- [KP-C03-007-题型索引](../../反向题型索引/知识点/KP-C03-007-题型索引.md)
