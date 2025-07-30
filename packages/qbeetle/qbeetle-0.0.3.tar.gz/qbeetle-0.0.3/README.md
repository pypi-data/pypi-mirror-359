
<center>
    <img src="logo.png" width="100"/>
</center>

<center>
<h1>beetle (甲壳虫) </h1>
</center>


<p align="center">
  <a style="text-decoration:none">
    <img alt="Static Badge" src="https://img.shields.io/badge/version-0.0.1-blue">
  </a>

  <a style="text-decoration:none">
    <img src="https://img.shields.io/badge/License-MIT-blue" alt="MIT"/>
  </a>

  <a style="text-decoration:none">
    <img src="https://img.shields.io/badge/Platform-Win32%20|%20Linux%20|%20macOS-blue" alt="Platform Win32 | Linux | macOS"/>
  </a>
</p>

<p align="center">
  <a href="" target="_blank">
    <img alt="Static Badge" src="https://img.shields.io/badge/github-blue?logo=github&logoColor=f7cb4f">
  </a>

  <a href="" target="_blank">
    <img alt="Static Badge" src="https://img.shields.io/badge/gitee-blue?logo=gitee&logoColor=f7cb4f">
  </a>
</p>

# 简介

`beetle` 是一个PyQt和Pyside项目开发框架。可以帮助你快速的创建、运行和编译项目，
并且还包含一些辅助开发工具来提高开发效率。

`fbs` 是一个另外一个框架， 它为打包、创建安装程序和对应用程序进行签名提供了强大的环境。 但是， `fbs`的开源版本支持的python版本为3.6， 
以至于python的新特性，以及很多更新版本的包和模块都无法使用。 

`beetle` 想解决这些问题，并提供了很多新的特性。

还是要感谢 `fbs`， 它还是为PyQt和Pyside项目开发提供了很多的遍历， `beetle` 也在很多方面借鉴了 `fbs`。

# 开发计划

开发一个工具`beetle`, 类似于fbs，预计具备如下功能:

- [x] template_list 资源库中的项目模板列表
- [x] update_template 从 Beetle 的官方项目模板库更新到本地项目模板库
- [x] add_template 向 Beetle 添加新的客户定义的项目模板
- [x] delete_template 删除 Beetle 的客户自定义项目模板。
- [x] startproject 新建、初始化项目
- [ ] ui文件转py文件
- [ ] 生成国际化（i18n）所需的ts文件
- [ ] ts文件转qm
- [ ] qrc 文件更新
- [ ] qrc 文件转py文件
- [x] run 从源代码运行应用
- [x] freeze, 将代码编译为独立的可执行文件(可选 `PyInstaller` 或 `nuitka`)
- [x] installer, 为应用创建安装程序
- [ ] test, 执行自动化测试(基于pytest)
- [x] clean, 删除以前的生成输出



# 安装

beetle 可以从 PyPi 通过 pip 安装：

```commandline
pip install qbeetle
```


# 文档

请看 beetle [使用文档](https://beetle-tool.github.io/beetle-doc/)


