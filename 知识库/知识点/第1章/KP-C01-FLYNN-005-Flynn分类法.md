---
id: KP-C01-FLYNN-005
title: Flynn 分类法
aliases:
  - KP-C01-FLYNN-005
  - Flynn 分类法
chapter: 第1章
topic: 计算机分类
type: comparison
source_refs:
  - ../../资料整理稿/教材/计算机组成与设计-第1章-1-28/计算机组成与设计-第1章-1-28.md
prerequisites: []
related_points:
  - KP-C01-PERF-006
contrast_with: []
updated: 2026-05-20
---

# Flynn 分类法

## 定义

Flynn 分类法按照指令流和数据流的组合方式对计算机系统进行分类。

## 课程资料中的表述

教材在计算机分类部分给出 Flynn 分类法，典型类别包括：

- SISD
- SIMD
- MISD
- MIMD

## 结构 / 规则 / 公式

分类依据是两条维度：

- 指令流数量
- 数据流数量

通过二者组合得到四类典型结构。

## 易混点 / 易错点

- MISD 在实际系统中并不常见，但教材仍会作为理论类别给出。
- 不要把 Flynn 分类法和“按用途分类”混为一谈。

## 常见关联场景

- 分类比较题
- 并行系统基础概念题

## 相关知识点

- [[计算机性能描述与 Amdahl 定律]]

## 出处

- 教材整理稿第 1 章：`1.3.1 计算机的分类`

## 关联题型索引

- [KP-C01-FLYNN-005-题型索引](../../反向题型索引/知识点/KP-C01-FLYNN-005-题型索引.md)
