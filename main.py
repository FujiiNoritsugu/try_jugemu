import random
import string
import time
import re
import os
import math
from datetime import datetime
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# 生成されたコードを保存するディレクトリ
GENERATED_CODES_DIR = Path("generated_codes")
GENERATED_CODES_DIR.mkdir(exist_ok=True)


def generate_random_identifier(length=8):
    """ランダムな識別子を生成"""
    first_char = random.choice(string.ascii_lowercase)
    rest_chars = "".join(
        random.choices(string.ascii_lowercase + string.digits + "_", k=length - 1)
    )
    return first_char + rest_chars


def generate_random_value():
    """ランダムな値を生成"""
    value_type = random.choice(["int", "str", "bool", "list"])
    if value_type == "int":
        return random.randint(0, 1000)
    elif value_type == "str":
        return f'"{generate_random_identifier(5)}"'
    elif value_type == "bool":
        return random.choice(["True", "False"])
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
    code = re.sub(r"//\s*0\b", "// 1", code)
    code = re.sub(r"%\s*0\b", "% 1", code)
    code = re.sub(r"/\s*0\b", "/ 1", code)
    return code


def fix_syntax_error(code):
    """簡単な構文エラーを修正"""
    lines = code.split("\n")
    fixed_lines = []

    for i, line in enumerate(lines):
        fixed_lines.append(line)

        # コロンで終わる行（関数定義、クラス定義、if/for文など）
        if line.strip().endswith(":"):
            # 現在の行のインデントレベルを取得
            current_indent = len(line) - len(line.lstrip())

            # 次の行をチェック
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                # 次の行が空行または適切にインデントされていない場合
                if (
                    not next_line.strip()
                    or len(next_line) - len(next_line.lstrip()) <= current_indent
                ):
                    # 適切なインデントでpassを追加
                    fixed_lines.append(" " * (current_indent + 4) + "pass")
            else:
                # 最後の行の場合、passを追加
                fixed_lines.append(" " * (current_indent + 4) + "pass")

    return "\n".join(fixed_lines)


def evaluate_code_with_llm(original_code, improved_code):
    """LLMを使って元のコードと改善されたコードを評価"""
    print("\n" + "=" * 60)
    print("LLMを使ってコードを評価しています...")
    print("=" * 60)

    try:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print("警告: ANTHROPIC_API_KEY が設定されていません")
            return None

        client = Anthropic(api_key=api_key)

        prompt = f"""以下の2つのPythonコードを比較評価してください。

# 元のコード（ランダム生成）
```python
{original_code}
```

# 改善されたコード
```python
{improved_code}
```

# 評価基準
1. **実用性** (1-10点): 実際に役立つ機能を持っているか
2. **可読性** (1-10点): コードが読みやすく理解しやすいか
3. **保守性** (1-10点): 変更や拡張がしやすいか
4. **創造性** (1-10点): 元のランダムコードから創造的な変換がされているか

# 出力形式
以下の形式で評価を出力してください：

## 評価スコア
- 実用性: [元: X点 → 改善: Y点] ([改善/維持/低下])
- 可読性: [元: X点 → 改善: Y点] ([改善/維持/低下])
- 保守性: [元: X点 → 改善: Y点] ([改善/維持/低下])
- 創造性: [元: X点 → 改善: Y点] ([改善/維持/低下])
- **総合**: [元: XX点 → 改善: YY点]

## 主な改善点
- [改善点1]
- [改善点2]
- [改善点3]

## 推奨事項
[このコードが実用的かどうか、さらに改善の余地があるか]"""

        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )

        evaluation = message.content[0].text

        print("\n" + "=" * 60)
        print("📊 評価結果:")
        print("=" * 60)
        print(evaluation)
        print("=" * 60)

        return evaluation

    except Exception as e:
        print(f"LLMでの評価中にエラーが発生しました: {e}")
        return None


def improve_code_with_llm(code):
    """LLMを使ってランダムなコードを意味のあるコードに改善"""
    print("\n" + "=" * 60)
    print("LLMを使ってコードを改善しています...")
    print("=" * 60)

    try:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print("警告: ANTHROPIC_API_KEY が設定されていません")
            print("元のコードをそのまま返します")
            return code

        client = Anthropic(api_key=api_key)

        prompt = f"""以下のランダムに生成されたPythonコードを、意味のある実用的なコードに改善してください。

元のコード:
```python
{code}
```

要件:
1. 元のコードの構造（関数名、クラス名）をできるだけ活かす
2. 実際に役立つ機能を持つコードにする
3. コメントやdocstringを充実させる
4. **絶対にエラーが出ないようにする**

重要な制約:
- **未定義の変数や関数を絶対に使用しないこと**
- **外部ライブラリをインポートしないこと（標準ライブラリのみ使用可）**
- **すべての関数とクラスは定義後に必ず呼び出すこと**
- **定義した関数やクラスのメソッドは、パラメータなしで呼び出せるようにデフォルト引数を設定すること**
- **コード内で未定義のグローバル変数を参照しないこと**
- **インデントエラーや構文エラーが発生しないようにすること**

実行例:
```python
# 正しい例
def greet(name="World"):
    return f"Hello, {{name}}!"

# 関数を呼び出す
result = greet()
print(result)
```

以下の形式で出力してください：

## 改善点
[改善点の箇条書き]

## 改善されたコード
```python
[改善されたPythonコード（必ず実行可能で、エラーが出ないこと）]
```"""

        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = message.content[0].text

        # 改善点とコードを分離
        improvements = ""
        improved_code = ""

        # 正規表現でコードブロックを抽出
        code_block_pattern = r"```python\s*(.*?)\s*```"
        code_blocks = re.findall(code_block_pattern, response_text, re.DOTALL)

        if code_blocks:
            # 最後のコードブロックを取得（通常は「改善されたコード」のブロック）
            improved_code = code_blocks[-1].strip()
        else:
            # コードブロックが見つからない場合、## 改善されたコード 以降を取得
            if "## 改善されたコード" in response_text:
                parts = response_text.split("## 改善されたコード")
                code_part = parts[1].strip()
                # 単純にマーカーを削除
                improved_code = (
                    code_part.replace("```python", "")
                    .replace("```", "")
                    .strip()
                )
            else:
                # それでもダメなら全体からマーカーを削除
                improved_code = (
                    response_text.replace("```python", "")
                    .replace("```", "")
                    .strip()
                )

        # 改善点を抽出
        if "## 改善点" in response_text and "## 改善されたコード" in response_text:
            parts = response_text.split("## 改善されたコード")
            improvements = parts[0].replace("## 改善点", "").strip()

        # コードが空または短すぎる場合のチェック
        if not improved_code or len(improved_code) < 10:
            print("\n⚠️  LLMのレスポンスからコードを抽出できませんでした")
            print("\n=== LLMの生のレスポンス ===")
            print(response_text)
            print("=" * 60)
            print("\n元のコードを返します")
            return code

        # 改善点を表示
        if improvements:
            print("\n" + "=" * 60)
            print("📝 改善点:")
            print("=" * 60)
            print(improvements)
            print("=" * 60)

        print("\n改善されたコード:")
        print(improved_code)
        print("\n" + "=" * 60)

        # 改善されたコードの構文をチェック
        is_valid, error_msg = validate_code_syntax(improved_code)
        if not is_valid:
            print(f"\n⚠️  改善されたコードに構文エラーがあります: {error_msg}")
            print("\n=== デバッグ情報: 抽出されたコードの最初の10行 ===")
            for i, line in enumerate(improved_code.split("\n")[:10], 1):
                print(f"{i:3d}: {line}")
            print("=" * 60)
            print("\n=== LLMの生のレスポンス（最初の500文字） ===")
            print(response_text[:500])
            print("..." if len(response_text) > 500 else "")
            print("=" * 60)
            print("\n元のコードを返します")
            return code
        else:
            print("\n✅ 改善されたコードの構文チェックが完了しました")

        return improved_code

    except Exception as e:
        print(f"LLMでの改善中にエラーが発生しました: {e}")
        print("元のコードをそのまま返します")
        return code


def validate_code_syntax(code):
    """コードの構文を検証"""
    try:
        compile(code, "<string>", "exec")
        return True, None
    except SyntaxError as e:
        return False, f"行{e.lineno}: {e.msg}"
    except Exception as e:
        return False, str(e)


def execute_generated_code(code, max_retries=5, show_traceback=True):
    """生成されたコードを実行（エラー時は修正して再実行）"""
    print("=" * 60)
    print("生成されたコードを実行します...")
    print("=" * 60)

    # 事前に構文チェック
    is_valid, error_msg = validate_code_syntax(code)
    if not is_valid:
        print(f"⚠️  構文エラーが検出されました: {error_msg}")
        print("構文エラーを修正します...")
        code = fix_syntax_error(code)
        is_valid, error_msg = validate_code_syntax(code)
        if not is_valid:
            print(f"❌ 構文エラーの修正に失敗しました: {error_msg}")
            print("\n問題のコード:")
            print(code)
            return False

    current_code = code
    retry_count = 0

    while retry_count < max_retries:
        try:
            exec(current_code)
            print("\n" + "=" * 60)
            print("✅ 実行完了")
            print("=" * 60)
            return True
        except ZeroDivisionError as e:
            retry_count += 1
            print(f"\n[エラー {retry_count}/{max_retries}] ゼロ除算エラー: {e}")
            if show_traceback:
                import traceback
                print("詳細なエラー情報:")
                traceback.print_exc()
            print("コードを修正して再実行します...")
            current_code = fix_division_by_zero(current_code)
            print("\n修正後のコード:")
            print(current_code)
            print("\n")
        except SyntaxError as e:
            retry_count += 1
            print(f"\n[エラー {retry_count}/{max_retries}] 構文エラー: {e}")
            if show_traceback:
                import traceback
                print("詳細なエラー情報:")
                traceback.print_exc()
            print("コードを修正して再実行します...")
            current_code = fix_syntax_error(current_code)
            print("\n修正後のコード:")
            print(current_code)
            print("\n")
        except NameError as e:
            retry_count += 1
            print(f"\n[エラー {retry_count}/{max_retries}] 名前エラー（未定義の変数/関数）: {e}")
            if show_traceback:
                import traceback
                print("詳細なエラー情報:")
                traceback.print_exc()
            print("LLMが生成したコードに未定義の変数や関数が含まれている可能性があります")
            print("\n問題のコード:")
            print(current_code)
            if retry_count < max_retries:
                print("\n別のコードを生成して再試行します...")
                current_code = generate_code()
                print("\n新しく生成されたコード:")
                print(current_code)
                print("\n")
            else:
                print("❌ 最大再試行回数に達しました。")
                return False
        except Exception as e:
            retry_count += 1
            print(
                f"\n[エラー {retry_count}/{max_retries}] 実行エラー: {type(e).__name__}: {e}"
            )
            if show_traceback:
                import traceback
                print("詳細なエラー情報:")
                traceback.print_exc()
            print("\n問題のコード:")
            print(current_code)
            if retry_count < max_retries:
                print("\n別のコードを生成して再試行します...")
                current_code = generate_code()
                print("\n新しく生成されたコード:")
                print(current_code)
                print("\n")
            else:
                print("❌ 最大再試行回数に達しました。")
                return False

    print("\n" + "=" * 60)
    print("❌ 最大再試行回数に達しましたが、エラーが解決しませんでした。")
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
        num_functions = self.code.count("def ")
        num_classes = self.code.count("class ")
        score += (num_functions + num_classes * 2) * 5

        # コードの長さ（適度な長さを評価）
        lines = len([l for l in self.code.split("\n") if l.strip()])
        if 20 <= lines <= 50:
            score += 10

        self.fitness = score
        return score

    def extract_functions(self):
        """コードから関数を抽出"""
        pattern = r"(def \w+\([^)]*\):(?:\n    .*)*)"
        return re.findall(pattern, self.code, re.MULTILINE)

    def extract_classes(self):
        """コードから関数を抽出"""
        pattern = r"(class \w+:(?:\n    .*)*?)(?=\n(?:def |class |\Z))"
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
        mutation_type = random.choice(["add_function", "add_class", "modify"])

        if mutation_type == "add_function":
            # 新しい関数を追加
            individual.code += "\n" + generate_random_function()
        elif mutation_type == "add_class":
            # 新しいクラスを追加
            individual.code += "\n" + generate_random_class()
        elif mutation_type == "modify":
            # 既存の関数の一部を置き換え
            funcs = individual.extract_functions()
            if funcs:
                old_func = random.choice(funcs)
                new_func = generate_random_function()
                individual.code = individual.code.replace(old_func, new_func, 1)


def genetic_algorithm(population_size=10, generations=5, use_llm=False):
    """遺伝的アルゴリズムでコードを進化"""
    print("=" * 60)
    print("遺伝的アルゴリズムを開始します")
    print(f"個体数: {population_size}, 世代数: {generations}")
    if use_llm:
        print("LLM改善: 有効")
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
        print("\n".join(population[0].code.split("\n")[:5]))

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

    # LLMで改善する場合
    if use_llm:
        original_code = population[0].code
        improved_code = improve_code_with_llm(original_code)
        population[0].code = improved_code

        # 改善されたコードを評価
        evaluate_code_with_llm(original_code, improved_code)

    # コードを保存
    mode_name = "GA+LLM" if use_llm else "GA"
    save_generated_code(population[0].code, mode_name, population[0].fitness)

    return population[0]


def simulated_annealing(
    initial_temp=100.0, cooling_rate=0.95, min_temp=0.1, use_llm=False
):
    """シミュレーテッドアニーリングでコードを最適化"""
    print("=" * 60)
    print("シミュレーテッドアニーリングを開始します")
    print(f"初期温度: {initial_temp}, 冷却率: {cooling_rate}, 最低温度: {min_temp}")
    if use_llm:
        print("LLM改善: 有効")
    print("=" * 60)

    # 初期解を生成
    current_individual = Individual()
    current_individual.evaluate_fitness()
    best_individual = Individual(current_individual.code)
    best_individual.fitness = current_individual.fitness

    temperature = initial_temp
    iteration = 0

    print(f"\n初期解の適応度: {current_individual.fitness:.2f}")
    print(f"初期コード（最初の5行）:")
    print("\n".join(current_individual.code.split("\n")[:5]))

    # 温度が最低温度に達するまで繰り返し
    while temperature > min_temp:
        iteration += 1

        # 新しい解を生成（突然変異）
        new_individual = Individual(current_individual.code)
        mutate(new_individual, mutation_rate=0.3)  # 突然変異率を少し高めに設定
        new_individual.evaluate_fitness()

        # 適応度の差分を計算
        delta = new_individual.fitness - current_individual.fitness

        # メトロポリス基準で受理判定
        if delta > 0:
            # 改善した場合は必ず受理
            current_individual = new_individual
            accept_reason = "改善"
        else:
            # 悪化した場合は確率的に受理
            acceptance_probability = math.exp(delta / temperature)
            if random.random() < acceptance_probability:
                current_individual = new_individual
                accept_reason = f"確率的受理 (p={acceptance_probability:.4f})"
            else:
                accept_reason = None

        # 最良解を更新
        if current_individual.fitness > best_individual.fitness:
            best_individual = Individual(current_individual.code)
            best_individual.fitness = current_individual.fitness
            print(
                f"\n[反復 {iteration}] 🌟 最良解更新! 適応度: {best_individual.fitness:.2f}, 温度: {temperature:.2f}"
            )

        # 10回ごとに進捗を表示
        if iteration % 10 == 0:
            if accept_reason:
                print(
                    f"[反復 {iteration}] 温度: {temperature:.2f}, 現在: {current_individual.fitness:.2f}, "
                    f"最良: {best_individual.fitness:.2f}, 状態: {accept_reason}"
                )
            else:
                print(
                    f"[反復 {iteration}] 温度: {temperature:.2f}, 現在: {current_individual.fitness:.2f}, "
                    f"最良: {best_individual.fitness:.2f}, 状態: 棄却"
                )

        # 温度を下げる
        temperature *= cooling_rate

    print("\n" + "=" * 60)
    print(f"最適化完了！総反復回数: {iteration}")
    print(f"最良解の適応度: {best_individual.fitness:.2f}")
    print("=" * 60)
    print("最良解のコード:")
    print("=" * 60)
    print(best_individual.code)

    # LLMで改善する場合
    if use_llm:
        original_code = best_individual.code
        improved_code = improve_code_with_llm(original_code)
        best_individual.code = improved_code

        # 改善されたコードを評価
        evaluate_code_with_llm(original_code, improved_code)

    # コードを保存
    mode_name = "SA+LLM" if use_llm else "SA"
    save_generated_code(best_individual.code, mode_name, best_individual.fitness)

    return best_individual


# ============================================================
# Q学習によるコード最適化
# ============================================================


def extract_state(individual):
    """個体から状態を抽出（離散化された特徴量）"""
    # 関数数、クラス数、コード行数、適応度を離散化
    num_functions = individual.code.count("def ")
    num_classes = individual.code.count("class ")
    num_lines = len([l for l in individual.code.split("\n") if l.strip()])
    fitness = individual.fitness

    # カテゴリに離散化
    func_category = min(num_functions // 2, 4)  # 0-4のカテゴリ
    class_category = min(num_classes // 1, 3)  # 0-3のカテゴリ
    lines_category = min(num_lines // 10, 5)  # 0-5のカテゴリ
    fitness_category = min(int(fitness // 50), 5)  # 0-5のカテゴリ

    return (func_category, class_category, lines_category, fitness_category)


def apply_action(individual, action):
    """行動を個体に適用して新しい個体を生成"""
    new_individual = Individual(individual.code)

    if action == "add_function":
        # 関数を追加
        new_individual.code += "\n" + generate_random_function()
    elif action == "remove_function":
        # 関数を削除
        funcs = new_individual.extract_functions()
        if funcs:
            func_to_remove = random.choice(funcs)
            new_individual.code = new_individual.code.replace(func_to_remove, "", 1)
    elif action == "add_class":
        # クラスを追加
        new_individual.code += "\n" + generate_random_class()
    elif action == "remove_class":
        # クラスを削除
        classes = new_individual.extract_classes()
        if classes:
            class_to_remove = random.choice(classes)
            new_individual.code = new_individual.code.replace(class_to_remove, "", 1)
    elif action == "modify_operator":
        # 演算子をランダムに変更
        operators = ["+", "-", "*", "//", "%"]
        for old_op in operators:
            if f" {old_op} " in new_individual.code:
                new_op = random.choice([op for op in operators if op != old_op])
                new_individual.code = new_individual.code.replace(
                    f" {old_op} ", f" {new_op} ", 1
                )
                break
    elif action == "mutate":
        # 既存の突然変異を適用
        mutate(new_individual, mutation_rate=1.0)  # 必ず変異
    # "no_action"の場合は何もしない

    # 構文チェック: エラーがあれば元の個体を返す
    is_valid, error_msg = validate_code_syntax(new_individual.code)
    if not is_valid:
        # 構文エラーが発生した場合は元の個体を返す
        return Individual(individual.code)

    return new_individual


class QTable:
    """Q-tableを管理するクラス"""

    def __init__(self, actions, learning_rate=0.1, discount_factor=0.9):
        self.q_table = {}  # (state, action) -> Q値
        self.actions = actions
        self.learning_rate = learning_rate  # 学習率 α
        self.discount_factor = discount_factor  # 割引率 γ

    def get_q_value(self, state, action):
        """Q値を取得（未登録の場合は0）"""
        return self.q_table.get((state, action), 0.0)

    def update_q_value(self, state, action, reward, next_state):
        """Q値を更新（Q学習の更新式）"""
        current_q = self.get_q_value(state, action)
        # 次状態での最大Q値を取得
        max_next_q = max(
            [self.get_q_value(next_state, a) for a in self.actions], default=0.0
        )
        # Q学習の更新式: Q(s,a) ← Q(s,a) + α[r + γ・max Q(s',a') - Q(s,a)]
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )
        self.q_table[(state, action)] = new_q

    def get_best_action(self, state):
        """状態における最良の行動を選択"""
        q_values = {action: self.get_q_value(state, action) for action in self.actions}
        max_q = max(q_values.values())
        # 最大Q値を持つ行動をランダムに選択（同値の場合に備えて）
        best_actions = [action for action, q in q_values.items() if q == max_q]
        return random.choice(best_actions)

    def choose_action(self, state, epsilon):
        """ε-greedy方策で行動を選択"""
        if random.random() < epsilon:
            # εの確率でランダム探索
            return random.choice(self.actions)
        else:
            # 1-εの確率で最良行動を選択
            return self.get_best_action(state)


def q_learning(episodes=50, max_steps=20, use_llm=False):
    """Q学習でコードを最適化"""
    print("=" * 60)
    print("Q学習を開始します")
    print(f"エピソード数: {episodes}, 最大ステップ数: {max_steps}")
    if use_llm:
        print("LLM改善: 有効")
    print("=" * 60)

    # 行動空間の定義
    actions = [
        "add_function",
        "remove_function",
        "add_class",
        "remove_class",
        "modify_operator",
        "mutate",
        "no_action",
    ]

    # Q-tableの初期化
    q_table = QTable(actions, learning_rate=0.1, discount_factor=0.9)

    # 最良個体を記録
    best_individual = None
    best_fitness = -float("inf")

    # ε-greedy用のパラメータ
    epsilon_start = 1.0  # 初期探索率
    epsilon_end = 0.1  # 最終探索率
    epsilon_decay = (epsilon_start - epsilon_end) / episodes

    # 各エピソードで学習
    for episode in range(episodes):
        epsilon = max(epsilon_end, epsilon_start - epsilon_decay * episode)

        # 初期状態（ランダムなコードを生成）
        current_individual = Individual()
        current_individual.evaluate_fitness()
        current_state = extract_state(current_individual)

        episode_reward = 0
        episode_best_fitness = current_individual.fitness

        print(f"\n【エピソード {episode + 1}/{episodes}】探索率ε: {epsilon:.3f}")

        # 各ステップで行動を選択して学習
        for step in range(max_steps):
            # ε-greedyで行動を選択
            action = q_table.choose_action(current_state, epsilon)

            # 行動を適用
            next_individual = apply_action(current_individual, action)
            next_individual.evaluate_fitness()
            next_state = extract_state(next_individual)

            # 報酬を計算（適応度の差分）
            reward = next_individual.fitness - current_individual.fitness

            # Q値を更新
            q_table.update_q_value(current_state, action, reward, next_state)

            # 累積報酬
            episode_reward += reward

            # エピソード内の最良適応度を更新
            if next_individual.fitness > episode_best_fitness:
                episode_best_fitness = next_individual.fitness

            # 全体の最良個体を更新
            if next_individual.fitness > best_fitness:
                best_fitness = next_individual.fitness
                best_individual = Individual(next_individual.code)
                best_individual.fitness = best_fitness
                print(
                    f"  [ステップ {step + 1}] 🌟 最良個体更新! 行動: {action}, 適応度: {best_fitness:.2f}"
                )

            # 次の状態へ遷移
            current_individual = next_individual
            current_state = next_state

        print(
            f"  エピソード報酬: {episode_reward:.2f}, 最高適応度: {episode_best_fitness:.2f}"
        )

        # 10エピソードごとに学習済みQ値の統計を表示
        if (episode + 1) % 10 == 0:
            avg_q = (
                sum(q_table.q_table.values()) / len(q_table.q_table)
                if q_table.q_table
                else 0.0
            )
            print(f"  学習済みQ値数: {len(q_table.q_table)}, 平均Q値: {avg_q:.2f}")

    print("\n" + "=" * 60)
    print("Q学習完了！")
    print(f"最良個体の適応度: {best_fitness:.2f}")
    print("=" * 60)
    print("最良個体のコード:")
    print("=" * 60)
    print(best_individual.code)

    # LLMで改善する場合
    if use_llm:
        original_code = best_individual.code
        improved_code = improve_code_with_llm(original_code)
        best_individual.code = improved_code

        # 改善されたコードを評価
        evaluate_code_with_llm(original_code, improved_code)

    # コードを保存
    mode_name = "Q-Learning+LLM" if use_llm else "Q-Learning"
    save_generated_code(best_individual.code, mode_name, best_fitness)

    return best_individual


# ============================================================
# コード保存・ロード機能
# ============================================================


def save_generated_code(code, mode_name, fitness=None):
    """生成されたコードをファイルに保存"""
    # タイムスタンプ付きのファイル名を生成
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"code_{mode_name}_{timestamp}.py"
    filepath = GENERATED_CODES_DIR / filename

    # メタデータをコメントとして追加
    metadata = f"""# 生成コードメタデータ
# モード: {mode_name}
# 生成日時: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
    if fitness is not None:
        metadata += f"# 適応度: {fitness:.2f}\n"
    metadata += "# " + "=" * 58 + "\n\n"

    # コードを保存
    full_content = metadata + code

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(full_content)

    print("\n" + "=" * 60)
    print("💾 生成されたコードを保存しました")
    print("=" * 60)
    print(f"保存先: {filepath}")
    print("=" * 60)

    return filepath


def list_saved_codes():
    """保存されたコードの一覧を表示"""
    code_files = sorted(GENERATED_CODES_DIR.glob("code_*.py"), key=lambda p: p.stat().st_mtime, reverse=True)

    if not code_files:
        print("\n保存されたコードはありません。")
        return []

    print("\n" + "=" * 60)
    print("💾 保存されたコード一覧")
    print("=" * 60)

    for i, filepath in enumerate(code_files, 1):
        # ファイルからメタデータを読み取る
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # メタデータを抽出
        mode_name = "不明"
        timestamp = "不明"
        fitness = "N/A"

        for line in lines:
            if line.startswith("# モード:"):
                mode_name = line.split(":", 1)[1].strip()
            elif line.startswith("# 生成日時:"):
                timestamp = line.split(":", 1)[1].strip()
            elif line.startswith("# 適応度:"):
                fitness = line.split(":", 1)[1].strip()

        print(f"{i}. {filepath.name}")
        print(f"   モード: {mode_name}")
        print(f"   生成日時: {timestamp}")
        print(f"   適応度: {fitness}")
        print()

    print("=" * 60)
    return code_files


def load_saved_code():
    """保存されたコードをロードして返す"""
    code_files = list_saved_codes()

    if not code_files:
        return None

    try:
        choice = input("\nロードするコードの番号を入力してください (0: キャンセル): ")
        choice_num = int(choice)

        if choice_num == 0:
            print("キャンセルしました。")
            return None

        if 1 <= choice_num <= len(code_files):
            selected_file = code_files[choice_num - 1]

            # ファイルを読み込む
            with open(selected_file, "r", encoding="utf-8") as f:
                full_content = f.read()

            # メタデータ部分を除去（最初の空行までをスキップ）
            lines = full_content.split("\n")
            code_start = 0
            for i, line in enumerate(lines):
                if not line.startswith("#") and line.strip() == "":
                    code_start = i + 1
                    break

            code = "\n".join(lines[code_start:])

            print("\n" + "=" * 60)
            print(f"✅ コードをロードしました: {selected_file.name}")
            print("=" * 60)

            return code
        else:
            print("無効な番号です。")
            return None

    except ValueError:
        print("無効な入力です。")
        return None
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None


# ============================================================
# ハイブリッド最適化（GA + SA + Q学習）
# ============================================================


def hybrid_optimization(use_llm=False):
    """ハイブリッド最適化: 遺伝的アルゴリズム → シミュレーテッドアニーリング → Q学習"""
    print("=" * 60)
    print("ハイブリッド最適化を開始します")
    print("手法: 遺伝的アルゴリズム → シミュレーテッドアニーリング → Q学習")
    if use_llm:
        print("LLM改善: 有効")
    print("=" * 60)

    # フェーズ1: 遺伝的アルゴリズム（大域的探索）
    print("\n" + "🧬 " * 30)
    print("【フェーズ1: 遺伝的アルゴリズム】")
    print("目的: 多様なコード構造を生成し、大域的に探索")
    print("🧬 " * 30)

    # 初期個体群を生成
    population_size = 10
    generations = 5
    population = [Individual() for _ in range(population_size)]

    # 各世代で進化
    for generation in range(generations):
        print(f"\n【GA 第{generation + 1}/{generations}世代】")

        # 適応度を評価
        for individual in population:
            individual.evaluate_fitness()

        # 適応度でソート
        population.sort(key=lambda ind: ind.fitness, reverse=True)

        # 統計を表示
        best_fitness = population[0].fitness
        avg_fitness = sum(ind.fitness for ind in population) / len(population)
        print(f"  最高適応度: {best_fitness:.2f}, 平均適応度: {avg_fitness:.2f}")

        # 最終世代でなければ次世代を生成
        if generation < generations - 1:
            new_population = []
            new_population.extend(population[:2])  # エリート保存

            while len(new_population) < population_size:
                parent1 = selection(population)
                parent2 = selection(population)
                child = crossover(parent1, parent2)
                mutate(child)
                new_population.append(child)

            population = new_population

    ga_best = population[0]
    print(f"\n✅ GA完了: 最良適応度 = {ga_best.fitness:.2f}")

    # フェーズ2: シミュレーテッドアニーリング（局所最適化）
    print("\n" + "🔥 " * 30)
    print("【フェーズ2: シミュレーテッドアニーリング】")
    print("目的: GAの最良個体を起点に局所最適化")
    print("🔥 " * 30)

    # GAの最良個体を初期解として使用
    current_individual = Individual(ga_best.code)
    current_individual.fitness = ga_best.fitness
    best_individual = Individual(current_individual.code)
    best_individual.fitness = current_individual.fitness

    initial_temp = 100.0
    cooling_rate = 0.95
    min_temp = 0.1
    temperature = initial_temp
    iteration = 0

    print(f"\n初期解の適応度: {current_individual.fitness:.2f}")

    # 温度が最低温度に達するまで繰り返し
    while temperature > min_temp:
        iteration += 1

        # 新しい解を生成（突然変異）
        new_individual = Individual(current_individual.code)
        mutate(new_individual, mutation_rate=0.3)
        new_individual.evaluate_fitness()

        # 適応度の差分を計算
        delta = new_individual.fitness - current_individual.fitness

        # メトロポリス基準で受理判定
        if delta > 0 or random.random() < math.exp(delta / temperature):
            current_individual = new_individual

        # 最良解を更新
        if current_individual.fitness > best_individual.fitness:
            best_individual = Individual(current_individual.code)
            best_individual.fitness = current_individual.fitness
            if iteration % 10 == 0 or iteration <= 5:
                print(
                    f"  [SA 反復 {iteration}] 🌟 最良解更新! 適応度: {best_individual.fitness:.2f}"
                )

        # 温度を下げる
        temperature *= cooling_rate

    sa_best = best_individual
    print(f"\n✅ SA完了: 最良適応度 = {sa_best.fitness:.2f} (改善: +{sa_best.fitness - ga_best.fitness:.2f})")

    # フェーズ3: Q学習（学習ベース微調整）
    print("\n" + "🧠 " * 30)
    print("【フェーズ3: Q学習】")
    print("目的: 経験から学習し、効果的な行動で微調整")
    print("🧠 " * 30)

    # 行動空間の定義
    actions = [
        "add_function",
        "remove_function",
        "add_class",
        "remove_class",
        "modify_operator",
        "mutate",
        "no_action",
    ]

    # Q-tableの初期化
    q_table = QTable(actions, learning_rate=0.1, discount_factor=0.9)

    # SAの最良個体を初期解として使用
    best_individual_ql = Individual(sa_best.code)
    best_individual_ql.fitness = sa_best.fitness
    best_fitness_ql = best_individual_ql.fitness

    # ε-greedy用のパラメータ
    episodes = 30  # ハイブリッドでは短めに
    max_steps = 15
    epsilon_start = 0.5  # 既に良い解があるので探索率は低め
    epsilon_end = 0.1
    epsilon_decay = (epsilon_start - epsilon_end) / episodes

    # 各エピソードで学習
    for episode in range(episodes):
        epsilon = max(epsilon_end, epsilon_start - epsilon_decay * episode)

        # SAの最良解から開始（エピソード開始時は毎回リセット）
        current_individual = Individual(sa_best.code)
        current_individual.fitness = sa_best.fitness
        current_state = extract_state(current_individual)

        episode_improvements = 0

        # 各ステップで行動を選択して学習
        for step in range(max_steps):
            # ε-greedyで行動を選択
            action = q_table.choose_action(current_state, epsilon)

            # 行動を適用
            next_individual = apply_action(current_individual, action)
            next_individual.evaluate_fitness()
            next_state = extract_state(next_individual)

            # 報酬を計算（適応度の差分）
            reward = next_individual.fitness - current_individual.fitness

            # Q値を更新
            q_table.update_q_value(current_state, action, reward, next_state)

            # 全体の最良個体を更新
            if next_individual.fitness > best_fitness_ql:
                best_fitness_ql = next_individual.fitness
                best_individual_ql = Individual(next_individual.code)
                best_individual_ql.fitness = best_fitness_ql
                episode_improvements += 1
                if episode_improvements <= 3:  # 最初の3回だけ表示
                    print(
                        f"  [QL エピソード {episode + 1}, ステップ {step + 1}] 🌟 最良個体更新! 適応度: {best_fitness_ql:.2f}"
                    )

            # 次の状態へ遷移
            current_individual = next_individual
            current_state = next_state

        # 10エピソードごとに進捗表示
        if (episode + 1) % 10 == 0:
            print(f"  [QL エピソード {episode + 1}/{episodes}] 現在の最良適応度: {best_fitness_ql:.2f}")

    print(f"\n✅ Q学習完了: 最良適応度 = {best_individual_ql.fitness:.2f} (改善: +{best_individual_ql.fitness - sa_best.fitness:.2f})")

    # 最終結果のサマリー
    print("\n" + "=" * 60)
    print("ハイブリッド最適化完了！")
    print("=" * 60)
    print(f"GA最良適応度:     {ga_best.fitness:.2f}")
    print(f"SA最良適応度:     {sa_best.fitness:.2f} (+{sa_best.fitness - ga_best.fitness:.2f})")
    print(f"Q学習最良適応度:  {best_individual_ql.fitness:.2f} (+{best_individual_ql.fitness - sa_best.fitness:.2f})")
    print(f"総合改善:         +{best_individual_ql.fitness - ga_best.fitness:.2f}")
    print("=" * 60)
    print("最良個体のコード:")
    print("=" * 60)
    print(best_individual_ql.code)

    # LLMで改善する場合
    if use_llm:
        original_code = best_individual_ql.code
        improved_code = improve_code_with_llm(original_code)
        best_individual_ql.code = improved_code

        # 改善されたコードを評価
        evaluate_code_with_llm(original_code, improved_code)

    # コードを保存
    mode_name = "Hybrid+LLM" if use_llm else "Hybrid"
    save_generated_code(best_individual_ql.code, mode_name, best_individual_ql.fitness)

    return best_individual_ql


def main():
    mode = input(
        "モードを選択してください\n"
        "1: 通常\n"
        "2: 遺伝的アルゴリズム\n"
        "3: LLM改善\n"
        "4: 遺伝的アルゴリズム+LLM\n"
        "5: シミュレーテッドアニーリング\n"
        "6: シミュレーテッドアニーリング+LLM\n"
        "7: Q学習\n"
        "8: Q学習+LLM\n"
        "9: ハイブリッド (GA+SA+Q学習)\n"
        "10: ハイブリッド+LLM\n"
        "11: 保存されたコードを実行\n"
        "選択 (1-11): "
    )

    if mode == "2":
        best_individual = genetic_algorithm(
            population_size=10, generations=5, use_llm=False
        )
        print("\n最良個体を実行します:\n")
        execute_generated_code(best_individual.code, max_retries=10)
    elif mode == "4":
        best_individual = genetic_algorithm(
            population_size=10, generations=5, use_llm=True
        )
        print("\n最良個体（LLM改善済み）を実行します:\n")
        execute_generated_code(best_individual.code, max_retries=10)
    elif mode == "5":
        best_individual = simulated_annealing(
            initial_temp=100.0, cooling_rate=0.95, min_temp=0.1, use_llm=False
        )
        print("\n最良個体を実行します:\n")
        execute_generated_code(best_individual.code, max_retries=10)
    elif mode == "6":
        best_individual = simulated_annealing(
            initial_temp=100.0, cooling_rate=0.95, min_temp=0.1, use_llm=True
        )
        print("\n最良個体（LLM改善済み）を実行します:\n")
        # LLMで改善されたコードは再試行を増やす
        execute_generated_code(best_individual.code, max_retries=10)
    elif mode == "7":
        best_individual = q_learning(episodes=50, max_steps=20, use_llm=False)
        print("\n最良個体を実行します:\n")
        execute_generated_code(best_individual.code, max_retries=10)
    elif mode == "8":
        best_individual = q_learning(episodes=50, max_steps=20, use_llm=True)
        print("\n最良個体（LLM改善済み）を実行します:\n")
        execute_generated_code(best_individual.code, max_retries=10)
    elif mode == "9":
        best_individual = hybrid_optimization(use_llm=False)
        print("\n最良個体を実行します:\n")
        execute_generated_code(best_individual.code, max_retries=10)
    elif mode == "10":
        best_individual = hybrid_optimization(use_llm=True)
        print("\n最良個体（LLM改善済み）を実行します:\n")
        execute_generated_code(best_individual.code, max_retries=10)
    elif mode == "11":
        # 保存されたコードをロードして実行
        loaded_code = load_saved_code()
        if loaded_code:
            print("\nロードされたコードを実行します:\n")
            execute_generated_code(loaded_code, max_retries=10)
        else:
            print("コードがロードされませんでした。")
    elif mode == "3":
        print("偶発的なコードを生成します...\n")
        generated_code = generate_code()
        print("生成されたコード:")
        print(generated_code)
        print("\n")

        # LLMで改善
        improved_code = improve_code_with_llm(generated_code)

        # 改善されたコードを評価
        evaluate_code_with_llm(generated_code, improved_code)

        # コードを保存
        save_generated_code(improved_code, "LLM")

        # 改善されたコードを実行
        execute_generated_code(improved_code, max_retries=10)
    else:
        print("偶発的なコードを生成します...\n")
        generated_code = generate_code()
        print(generated_code)
        print("\n")

        # コードを保存
        save_generated_code(generated_code, "Normal")

        execute_generated_code(generated_code)


if __name__ == "__main__":
    main()
