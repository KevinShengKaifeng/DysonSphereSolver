一个简单的戴森球计划Solver，可以列出产出任意产品在某产量下所需要搭建的生产线和原材料，并且可以选择是否使用稀有材料、是否使用增产剂（默认增产剂Ⅲ）以及是否在产线中包含增产剂部分，并且支持中英两种语言输出。

translation.txt是中文单词的汉化翻译。

item.txt是配方列表，包含了所有材料配方，目前还未包含建筑配方，可以在配方表中某行前加上‘#’注释掉该配方，以避免使用这一配方。

solver.py是解析器代码，PRODUCTION_EFFICIENCY列表中的参数是各生产建筑的生产效率，默认是全部为最高级建筑的效率。
使用DynsonSphereSolver().print_production_chain()函数来打印产物的产线和原材料使用，如：
print_production_chain("universe_matrix", 10, use_rare_resource=True, use_proliferator=True, include_proliferator_usage=False)
可以打印10个/秒白糖生产，在使用稀有材料和增产剂的情况下，不包括增产剂生产，所需的产线。
输出格式为：
宇宙矩阵|10.0|矩阵研究站|120.0
代表生产10个/s宇宙矩阵，需要120个矩阵研究站（生产建筑后带*代表使用了稀有配方）