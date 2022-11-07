import queue
from unicodedata import category

ITEM_CATEGORY = ["natural_resource", "material", "components", "end_product", "rare"]
PRODUCTION_BUILDING = ["arc_smelter", "assembline_machine", "oil_refinery", "chemical_plant", "particle_collider", "matrix_lab"]
PRODUCTION_EFFICIENCY = [2, 1.5, 1, 2, 1, 1]


class DysonSphereSolver:
    def __init__(self) -> None:
        self.items = self.parse_items()
        self.translation = self.parse_translation()

    @staticmethod
    def parse_items():
        with open("items.txt", 'r', encoding='utf-8') as item_file:
            items_dict = {}
            while True:
                line = item_file.readline()
                if line.startswith("#") or line == "\n": continue
                if not line: break
                values = line.removesuffix("\n").split("\t")
                values = [v for v in values if v]
                
                item_name, item_category = values[0], int(values[1])
                if item_name in items_dict:
                    if (isinstance(items_dict[item_name]['category'], list) and item_category in items_dict[item_name]['category']) or items_dict[item_name]['category'] == item_category:
                        pass
                    else:
                        if isinstance(items_dict[item_name]['category'], list):
                            items_dict[item_name]['category'].append(item_category)
                        else:
                            items_dict[item_name]['category'] = [items_dict[item_name]['category'], item_category]
                    if len(values) > 2:
                            items_dict[item_name]['recipe'].append(values[2:])
                else:
                    items_dict[item_name] = {}
                    items_dict[item_name]['category'] = item_category
                    items_dict[item_name]['recipe'] = []
                    if len(values) > 2:
                        # items_dict[item_name]['production_building'] = values[2]
                        # items_dict[item_name]['production_time'] = values[3]
                        items_dict[item_name]['recipe'].append(values[2:])
                
        return items_dict

    @staticmethod
    def parse_translation():
        with open("translation.txt", 'r', encoding='utf-8') as translation_file:
            translation_dict = {}
            while True:
                line = translation_file.readline()
                if line.startswith("#") or line == "\n": continue
                if not line: break
                values = line.removesuffix("\n").replace(' ', '\t').split("\t")
                values = [v for v in values if v]
                translation_dict[values[0]] = values[1]
        return translation_dict

    def recipe_use_rare_resource(self, recipe):
        used_items = recipe[3::2]
        for item in used_items:
            if self.items[item]['category'] == 4:
                return True
        return False

    def solve_recipe(self, target, quantity, use_rare_resource=False, use_proliferator=False):
        if use_proliferator:
            quantity *= 4/5
        
        cate = self.items[target]['category']
        if (isinstance(cate, list) and 0 in cate) or cate == 0 or cate == 4:
            return []
        if isinstance(cate, list) and 4 in cate and use_rare_resource:
            return []
        
        recipes = self.items[target]['recipe']
        using_rare_resource = False
        if not use_rare_resource:
            valid_recipe = [recipe for recipe in recipes if not self.recipe_use_rare_resource(recipe)][0]
        else:
            rare_recipes = [recipe for recipe in recipes if self.recipe_use_rare_resource(recipe)]
            if rare_recipes:
                valid_recipe = rare_recipes[0]
                using_rare_resource = True
            else:
                valid_recipe = recipes[0]
        
        building_name = PRODUCTION_BUILDING[int(valid_recipe[0])] + ('*' if using_rare_resource else '')
        building_quant = float(valid_recipe[1]) / PRODUCTION_EFFICIENCY[int(valid_recipe[0])]
        ret = [(building_name, building_quant)] + list(zip(valid_recipe[3::2], valid_recipe[2::2]))
        for i in range(len(ret)):
            ret[i] = [ret[i][0], float(ret[i][1]) * quantity]
        return ret

    def print_production_chain(self, target, quantity=1, use_rare_resource=False, use_proliferator=False, translate=True, print_out=True, include_proliferator_usage=True):
        if target not in self.items:
            raise NotImplementedError("item {} not in the item list".format(target))
        
        production_chain = []
        proliferator_usage = 0
        task_queue = queue.Queue()
        task_queue.put([target, quantity])
        while not task_queue.empty():
            task = task_queue.get()
            solved_recipe = self.solve_recipe(task[0], task[1], use_rare_resource, use_proliferator)
            if not solved_recipe:
                production_chain.append(task)
            else:
                production_chain.append(task + solved_recipe[0])
                proliferator_usage += sum([recipe_quant for recipe_name, recipe_quant in solved_recipe[1:]])
                for next_task in solved_recipe[1:]:
                    task_queue.put(next_task)
        if target == "proliferator_3":
            proliferator_usage += quantity  # proliferate the output
        proliferator_usage = proliferator_usage / 75 * 1.2958  # proliferator also need to be proliferated, 1.2958 is the summation of a geometric series.

        if use_proliferator and target != "proliferator_3" and include_proliferator_usage:
            proliferator_production_chain = self.print_production_chain('proliferator_3', proliferator_usage, use_rare_resource, True, translate, False, False)
            production_chain += proliferator_production_chain

        # combine different entries of the same item
        production_chain_dict = {}
        for item in production_chain:
            if item[0] not in production_chain_dict:
                production_chain_dict[item[0]] = item
            else:
                previous = production_chain_dict[item[0]]
                previous[1] += item[1]
                if len(previous) > 2:
                    assert previous[2] == item[2]
                    previous[3] += item[3]
                production_chain_dict[item[0]] = previous
        production_chain = [production_chain_dict[key] for key in production_chain_dict]
        production_chain = sorted(production_chain, key=lambda item: 999 + ord(item[0][0]) if len(item) == 2 else (0 if item[2].removesuffix('*') == "matrix_lab" else (1 if item[2].removesuffix('*') == "assembline_machine" else ord(item[2][0]))))
        if target == "proliferator_3" and include_proliferator_usage:
            production_chain.append(["proliferator_3", proliferator_usage])

        if print_out:
            for item in production_chain:
                item_name= self.translation[item[0]] if (item[0] in self.translation and translate) else item[0]
                production_rate = item[1]
                if len(item) == 2:
                    print(u"{:<25}\t|{:.1f}".format(item_name, production_rate))
                else:
                    if item[2].endswith('*'):
                        building_name = self.translation[item[2].removesuffix('*')] + '*' if (item[2].removesuffix('*') in self.translation and translate) else item[2]
                    else:
                        building_name = self.translation[item[2]] if (item[2] in self.translation and translate) else item[2]
                    building_quant = item[3]
                    print(u"{:<25}\t|{:.1f}\t|{:<12}\t|{:.1f}".format(item_name, production_rate, building_name, building_quant))
        return production_chain



if __name__ == "__main__":
    solver = DysonSphereSolver()
    # ret = solver.solve_recipe("organic_crystal", 2, use_proliferator=True)
    # ret = solver.print_production_chain("solar_sail", 150, use_rare_resource=True, use_proliferator=True, include_proliferator_usage=False)
    # ret = solver.print_production_chain("small_carrier_rocket", 4, use_rare_resource=True, use_proliferator=True)
    ret = solver.print_production_chain("universe_matrix", 10, use_rare_resource=True, use_proliferator=True, include_proliferator_usage=False)
    # ret = solver.print_production_chain("deuteron_fuel_rod", 10, use_rare_resource=True, use_proliferator=True, include_proliferator_usage=False)
    # ret = solver.print_production_chain("solar_sail", 300, use_rare_resource=True, use_proliferator=True, include_proliferator_usage=True)
    # ret = solver.print_production_chain("proliferator_3", 90, use_rare_resource=True, use_proliferator=True)
    pass