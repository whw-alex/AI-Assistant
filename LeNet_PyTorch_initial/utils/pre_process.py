#!/usr/bin/python3

"""
# -*- coding: utf-8 -*-

# @Time     : 2020/8/28 17:42
# @File     : pre_process.py

"""
import torchvision


def normal_transform():
    normal = torchvision.transforms.Compose([
        torchvision.transforms.ToTensor(),
    ])
    return normal

def data_augment_transform():
    data_augment = torchvision.transforms.Compose([
        # 随机切割
        # torchvision.transforms.RandomSizedCrop(10, interpolation=2),
        # 随机水平翻转 概率为0.5
        # torchvision.transforms.RandomHorizontalFlip,
        # 随机垂直翻转 概率为0.5
        # torchvision.transforms.RandomVerticalFlip,
        torchvision.transforms.ToTensor(),
    ])
    return data_augment
