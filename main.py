import random
import string
import time
import re


def generate_random_identifier(length=8):
    """ランダムな識別子を生成"""
    first_char = random.choice(string.ascii_lowercase)
    rest_chars = ''.join(random.choices(string.ascii_lowercase + string.digits + '_', k=length-1))
    return first_char + rest_chars


def generate_random_value():
    """ランダムな値を生成"""
    value_type = random.choice(['int', 'str', 'bool', 'list'])
    if value_type == 'int':
        return random.randint(0, 1000)
    elif value_type == 'str':
        return f'"{generate_random_identifier(5)}"'
    elif value_type == 'bool':
        return random.choice(['True', 'False'])
    else:
        return f'[{", ".join(str(random.randint(0, 100)) for _ in range(random.randint(1, 5)))}]'


def generate_random_operation():
    """ランダムな操作を生成"""
    operations = [
        lambda: f"print({generate_random_value()})",
        lambda: f"{generate_random_identifier()} = {generate_random_value()}",
        lambda: f"result = {random.randint(1, 100)} {random.choice(['+', '-', '*', '//', '%'])} {random.randint(1, 100)}",
        lambda: f"if {random.choice(['True', 'False'])}:\n        pass",
        lambda: f"for i in range({random.randint(1, 10)}):\n        pass",
    ]
    return random.choice(operations)()


def generate_random_function():
    """ランダムな関数を生成"""
    func_name = generate_random_identifier()
    num_params = random.randint(0, 3)
    params = [generate_random_identifier(6) for _ in range(num_params)]

    code = f"def {func_name}({', '.join(params)}):\n"
    code += f'    """偶発的に生成された関数"""\n'

    num_statements = random.randint(1, 5)
    for _ in range(num_statements):
        code += f"    {generate_random_operation()}\n"

    code += f"    return {generate_random_value()}\n"
    return code


def generate_random_class():
    """ランダムなクラスを生成"""
    class_name = generate_random_identifier().capitalize()
    code = f"class {class_name}:\n"
    code += f'    """偶発的に生成されたクラス"""\n'

    num_methods = random.randint(1, 3)
    for _ in range(num_methods):
        method_name = generate_random_identifier()
        code += f"    def {method_name}(self):\n"
        num_statements = random.randint(1, 3)
        for _ in range(num_statements):
            code += f"        {generate_random_operation()}\n"
        code += f"        return {generate_random_value()}\n\n"

    return code


def generate_code(num_functions=3, num_classes=2):
    """偶発的なコードを生成"""
    code = "# 偶発的に生成されたコード\n\n"

    for _ in range(num_functions):
        code += generate_random_function() + "\n\n"

    for _ in range(num_classes):
        code += generate_random_class() + "\n"

    return code


def fix_division_by_zero(code):
    """ゼロ除算エラーを修正"""
    import re
    # // 0 や % 0 を // 1 や % 1 に置き換え
    code = re.sub(r'//\s*0\b', '// 1', code)
    code = re.sub(r'%\s*0\b', '% 1', code)
    code = re.sub(r'/\s*0\b', '/ 1', code)
    return code


def fix_syntax_error(code):
    """簡単な構文エラーを修正"""
    lines = code.split('\n')
    fixed_lines = []

    for i, line in enumerate(lines):
        fixed_lines.append(line)

        # コロンで終わる行（関数定義、クラス定義、if/for文など）
        if line.strip().endswith(':'):
            # 現在の行のインデントレベルを取得
            current_indent = len(line) - len(line.lstrip())

            # 次の行をチェック
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                # 次の行が空行または適切にインデントされていない場合
                if not next_line.strip() or len(next_line) - len(next_line.lstrip()) <= current_indent:
                    # 適切なインデントでpassを追加
                    fixed_lines.append(' ' * (current_indent + 4) + 'pass')
            else:
                # 最後の行の場合、passを追加
                fixed_lines.append(' ' * (current_indent + 4) + 'pass')

    return '\n'.join(fixed_lines)


def execute_generated_code(code, max_retries=3):
    """生成されたコードを実行（エラー時は修正して再実行）"""
    print("=" * 60)
    print("生成されたコードを実行します...")
    print("=" * 60)

    current_code = code
    retry_count = 0

    while retry_count < max_retries:
        try:
            exec(current_code)
            print("\n" + "=" * 60)
            print("実行完了")
            print("=" * 60)
            return True
        except ZeroDivisionError as e:
            retry_count += 1
            print(f"\n[エラー {retry_count}/{max_retries}] ゼロ除算エラー: {e}")
            print("コードを修正して再実行します...")
            current_code = fix_division_by_zero(current_code)
            print("\n修正後のコード:")
            print(current_code)
            print("\n")
        except SyntaxError as e:
            retry_count += 1
            print(f"\n[エラー {retry_count}/{max_retries}] 構文エラー: {e}")
            print("コードを修正して再実行します...")
            current_code = fix_syntax_error(current_code)
            print("\n修正後のコード:")
            print(current_code)
            print("\n")
        except Exception as e:
            retry_count += 1
            print(f"\n[エラー {retry_count}/{max_retries}] 実行エラー: {type(e).__name__}: {e}")
            if retry_count < max_retries:
                print("別のコードを生成して再試行します...")
                current_code = generate_code()
                print("\n新しく生成されたコード:")
                print(current_code)
                print("\n")
            else:
                print("最大再試行回数に達しました。")
                return False

    print("\n" + "=" * 60)
    print("最大再試行回数に達しましたが、エラーが解決しませんでした。")
    print("=" * 60)
    return False


class Individual:
    """遺伝的アルゴリズムの個体（プログラムコード）"""

    def __init__(self, code=None):
        self.code = code if code else generate_code()
        self.fitness = 0

    def evaluate_fitness(self):
        """適応度を評価"""
        score = 0

        # 実行可能性チェック
        start_time = time.time()
        try:
            exec(self.code, {}, {})
            score += 100  # 実行成功
            execution_time = time.time() - start_time
            # 実行時間が短いほど高得点（最大20点）
            score += max(0, 20 - int(execution_time * 100))
        except ZeroDivisionError:
            score += 30  # ゼロ除算は修正可能なので部分点
        except SyntaxError:
            score += 10  # 構文エラーは低得点
        except:
            score += 20  # その他のエラーは少し部分点

        # コードの複雑さ（関数とクラスの数）
        num_functions = self.code.count('def ')
        num_classes = self.code.count('class ')
        score += (num_functions + num_classes * 2) * 5

        # コードの長さ（適度な長さを評価）
        lines = len([l for l in self.code.split('\n') if l.strip()])
        if 20 <= lines <= 50:
            score += 10

        self.fitness = score
        return score

    def extract_functions(self):
        """コードから関数を抽出"""
        pattern = r'(def \w+\([^)]*\):(?:\n    .*)*)'
        return re.findall(pattern, self.code, re.MULTILINE)

    def extract_classes(self):
        """コードから関数を抽出"""
        pattern = r'(class \w+:(?:\n    .*)*?)(?=\n(?:def |class |\Z))'
        return re.findall(pattern, self.code, re.MULTILINE)


def selection(population, tournament_size=3):
    """トーナメント選択で親を選択"""
    tournament = random.sample(population, tournament_size)
    return max(tournament, key=lambda ind: ind.fitness)


def crossover(parent1, parent2):
    """交叉：2つの親から子を生成"""
    child_code = "# 偶発的に生成されたコード（遺伝的交叉）\n\n"

    # 親1と親2から関数とクラスを抽出
    funcs1 = parent1.extract_functions()
    funcs2 = parent2.extract_functions()
    classes1 = parent1.extract_classes()
    classes2 = parent2.extract_classes()

    # 関数を混ぜる
    all_funcs = funcs1 + funcs2
    if all_funcs:
        selected_funcs = random.sample(all_funcs, min(3, len(all_funcs)))
        for func in selected_funcs:
            child_code += func + "\n\n"

    # クラスを混ぜる
    all_classes = classes1 + classes2
    if all_classes:
        selected_classes = random.sample(all_classes, min(2, len(all_classes)))
        for cls in selected_classes:
            child_code += cls + "\n\n"

    # 子が空の場合は新しいコードを生成
    if len(child_code.strip()) < 50:
        child_code = generate_code()

    return Individual(child_code)


def mutate(individual, mutation_rate=0.2):
    """突然変異：コードをランダムに変更"""
    if random.random() < mutation_rate:
        mutation_type = random.choice(['add_function', 'add_class', 'modify'])

        if mutation_type == 'add_function':
            # 新しい関数を追加
            individual.code += "\n" + generate_random_function()
        elif mutation_type == 'add_class':
            # 新しいクラスを追加
            individual.code += "\n" + generate_random_class()
        elif mutation_type == 'modify':
            # 既存の関数の一部を置き換え
            funcs = individual.extract_functions()
            if funcs:
                old_func = random.choice(funcs)
                new_func = generate_random_function()
                individual.code = individual.code.replace(old_func, new_func, 1)


def genetic_algorithm(population_size=10, generations=5):
    """遺伝的アルゴリズムでコードを進化"""
    print("=" * 60)
    print("遺伝的アルゴリズムを開始します")
    print(f"個体数: {population_size}, 世代数: {generations}")
    print("=" * 60)

    # 初期個体群を生成
    population = [Individual() for _ in range(population_size)]

    # 各世代で進化
    for generation in range(generations):
        print(f"\n【第{generation + 1}世代】")

        # 適応度を評価
        for individual in population:
            individual.evaluate_fitness()

        # 適応度でソート
        population.sort(key=lambda ind: ind.fitness, reverse=True)

        # 統計を表示
        best_fitness = population[0].fitness
        avg_fitness = sum(ind.fitness for ind in population) / len(population)
        print(f"最高適応度: {best_fitness:.2f}")
        print(f"平均適応度: {avg_fitness:.2f}")
        print(f"最良個体のコード（最初の5行）:")
        print('\n'.join(population[0].code.split('\n')[:5]))

        # 最終世代でなければ次世代を生成
        if generation < generations - 1:
            new_population = []

            # エリート保存（上位2個体）
            new_population.extend(population[:2])

            # 残りを交叉と突然変異で生成
            while len(new_population) < population_size:
                parent1 = selection(population)
                parent2 = selection(population)
                child = crossover(parent1, parent2)
                mutate(child)
                new_population.append(child)

            population = new_population

    print("\n" + "=" * 60)
    print("進化完了！最良個体のコード:")
    print("=" * 60)
    print(population[0].code)

    return population[0]


def main():
    mode = input("モードを選択してください (1: 通常, 2: 遺伝的アルゴリズム): ")

    if mode == "2":
        best_individual = genetic_algorithm(population_size=10, generations=5)
        print("\n最良個体を実行します:\n")
        execute_generated_code(best_individual.code)
    else:
        print("偶発的なコードを生成します...\n")
        generated_code = generate_code()
        print(generated_code)
        print("\n")
        execute_generated_code(generated_code)


if __name__ == "__main__":
    main()
